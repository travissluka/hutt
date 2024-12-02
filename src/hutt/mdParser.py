from typing import Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import re
from abc import ABC, abstractmethod

from hutt.commands.base import Command
from hutt.commands.info import Info

RE_MARKDOWN_HEADER = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.*)\s*$")
RE_COMMAND = re.compile(r"<!--\s+@(?P<command>\w+)(\s+(?P<args>.*))?\s+-->")
RE_COMMAND_BLOCK_START = re.compile(r"```(?P<lang>\w+)\s+@(?P<command>\w+)(\s+(?P<args>.*))?$")
RE_COMMAND_BLOCK_END = re.compile(r"```$")

RE_COMMAND_ARGS = re.compile(r"(?P<key>\w+)=(?P<value>\".*?\"|'.*?'|\S+)")

@dataclass
class MarkdownSource:
  filename: str
  line: int
  content: List[str] = field(default_factory=list)
  lineEnd: Optional[int] = None

  def __str__(self) -> str:
    return f"line {self.line} in {self.filename}"


@dataclass
class Token(ABC):
  source: MarkdownSource
  @abstractmethod
  def parse(self):
    pass


@dataclass
class Section(Token):
  title: str
  level: int

  def __repr__(self) -> str:
    return f"{self.source.line}: {'#' * self.level} {self.title}"

  def parse(self):
    return [ Info(self.source, self.title, self.level), ]


@dataclass
class CommandInlineToken(Token):
  command: str
  args: List[dict[str, str]] = field(default_factory=list)

  def __repr__(self) -> str:
    return f"{self.source.line}: <!-- @{self.command} {self.args} -->"

  def parse(self):
    commands = Command(self.command).parseInline(self.source, args=self.args)
    return commands


@dataclass
class CommandBlockToken(Token):
  lang: str
  command: str
  args: List[dict[str, str]] = field(default_factory=list)

  def __repr__(self) -> str:
    return f"{self.source.line}: ```{self.lang} @{self.command} {self.args}"

  def parse(self):
    commands = Command(self.command).parseBlock(self.source, args=self.args, blockLang=self.lang, blockText=self.source.content[1:])
    return commands


def parseMarkdown(markdownFile: str):
  """Parse a markdown file and return a tree of sections."""

  # check that file exists
  markdownFile = Path(markdownFile)
  if not markdownFile.exists():
    raise FileNotFoundError(f'File not found: {markdownFile}')

  # read the file
  with open(markdownFile, 'r') as file:
    lines = file.readlines()

  # parse the file and tokenize the markdown content
  tokens = _tokenizeMarkdown(markdownFile.absolute(), lines)

  # convert into Command classes
  commands = []
  for t in tokens:
    try:
      newCommands = t.parse()
    except Exception as e:
      e.args = (e.args[0] + f"\nError occurred while parsing token at line {t.source.line} in {t.source.filename}",) + e.args[1:]
      raise
    commands = commands + newCommands

  # give each command an index number (except for info commands)
  idx = 0
  for c in commands:
    if not isinstance(c, Info):
      idx += 1
      c.index = idx
    else:
      c.index = None

  return commands


def _tokenizeMarkdown(filename: str, lines: List[str]) -> List[Token]:
  # read the input file line by line, tokenizing the content
  tokens = []
  currentBlock = None
  lineNum = 0
  for line in lines:
    # remove extra spaces
    lineNum += 1
    line = line.strip()

    # helper functions
    def errIfInBlock():
      if currentBlock:
        raise ValueError(f"Command block started on line {currentBlock.lineStart} but never ended.")

    def parseArgs(args):
      if args:
        args = RE_COMMAND_ARGS.findall(args)
        args = {k: v.strip('"').strip("'") for k, v in args}
        return args
      else:
        return {}

    # save the source information for use later
    source = MarkdownSource(
      filename=filename,
      content=[line],
      line=lineNum
    )

    # check for markdown headers
    match =RE_MARKDOWN_HEADER.match(line)
    if match:
      tokens.append(Section(
        title=match.group('title'),
        level=len(match.group('hashes')),
        source=source,
      ))
      errIfInBlock()
      continue

    # remove block quotes and spaces
    line = line.strip().lstrip('>').strip()

    # check for a single command
    match = RE_COMMAND.match(line)
    if match:
      errIfInBlock()
      tokens.append(CommandInlineToken(
        command=match.group('command'),
        args=parseArgs(match.group('args')),
        source=source,
      ))
      continue

    # check for the start of a command block
    match = RE_COMMAND_BLOCK_START.match(line)
    if match:
      errIfInBlock()
      currentBlock = CommandBlockToken(
        lang=match.group('lang'),
        command=match.group('command'),
        args=parseArgs(match.group('args')),
        source=source,
      )
      continue

    # check for the end of a command block
    match = RE_COMMAND_BLOCK_END.match(line)
    if currentBlock and match:
      currentBlock.source.lineEnd = lineNum
      tokens.append(currentBlock)
      currentBlock = None
      continue

    # add the line to the current block
    if currentBlock:
      currentBlock.source.content.append(line)
  errIfInBlock()

  return tokens
