# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
from ruamel.yaml import YAML
from io import StringIO
import re

MAX_CONTENT_STR_LEN = 70

## ---------------------------------------------------------------

def _deep_merge(dst, src):
  """ Merge two yaml files, overwriting shared values from src into dst """
  for k, v in src.items():
    if (k in dst and
        isinstance(dst[k], dict) and
        isinstance(v, dict)):
      _deep_merge(dst[k], v)
    # TODO handle optional appending to a list instead of replacing it
    # elif (k in dst and
    #       isinstance(dst[k], list) and
    #       isinstance(v, list)):
    #   dst[k].extend(x for x in v if x not in dst[k])
    else:
      # if v is null, skip merging it
      if v is not None:
        dst[k] = v
  return dst

## ---------------------------------------------------------------

def _block_to_dict(blockLang, blockText):
  """ Convert a block of text (assuming valid yaml) into a dictionary.
  Special handling of lines that contain yaml aliases (remove the alias and
  replace it with a special string, it will be put back before writing the file).
  """
  if blockLang != "yaml":
    raise ValueError(f"Expected block language to be \"yaml\" but got \"{blockLang}\".")

  # special handling of lines that contain yaml aliases
  processed_blockText = [line.replace("*", "^ALIAS^") for line in blockText]

  # parse as yaml
  return YAML().load("\n".join(processed_blockText))

## ---------------------------------------------------------------

def _read_yaml(filename):
  """ Read a yaml file and return the contents as a dictionary.
  Special handling of anchors (unused anchors are sometimes removed in
  ruamel.yaml). Create a temporary alias for each one append to a "_ANCHORS"
  section at the end. This section is removed before the file is written.
  """
  yaml = YAML()

  # read file
  with open(filename, "r") as f:
    lines = [line.rstrip('\n') for line in f.readlines()]

  # do special processing for anchors (unused anchors are sometimes removed in
  # ruamel.yaml). Create a temporary alias for each one append to a "_ANCHORS"
  # section at the end. This section is removed before the file is written.
  anchors = [word[1:] for line in lines for word in line.split() if word.startswith("&")]
  lines.append("_ANCHORS:")
  for i, anchor in enumerate(anchors):
    lines.append(f"  _a{i}: *{anchor}")

  # read the yaml
  return yaml.load("\n".join(lines))

## ---------------------------------------------------------------

def _write_yaml(filename, content):
  """ Write a dictionary to a yaml file.
  Special handling of aliases (replace them with the correct syntax).
  """
  yaml = YAML()

  # write the yaml content to an array of strings
  output = StringIO(newline="")
  yaml.dump(content, output)
  output_str = output.getvalue().splitlines()
  output.close()

  # special handling of aliases
  output_str = [line.replace("^ALIAS^", "*") for line in output_str]

  # special handling of anchors: remove all lines at and after "_ANCHORS:"
  if "_ANCHORS:" in output_str:
    output_str = output_str[:output_str.index("_ANCHORS:")]

  # write the yaml file
  with open(filename, "w") as f:
    f.write("\n".join(output_str))

## ---------------------------------------------------------------

class YamlWrite(CommandBase):
  """ Write a yaml file given an input block of text """
  name = "hutt_yaml_write"

  def __init__(self, source, filename):
    super().__init__(source)
    self.filename = filename
    content = source.content[1:]

    # error checking on input parameters
    self.content = YAML().load("\n".join(content))

  @classmethod
  def parseBlock(cls, source, **kwargs):
    return [cls(source, **kwargs["args"]),]

  @classmethod
  def parseInline(cls, source, args):
    raise NotImplementedError("YamlWrite.parseInline() not implemented")

  def _execute(self):
    yaml = YAML()
    with open(self.filename, "w") as f:
      yaml.dump(self.content, f)

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:MAX_CONTENT_STR_LEN] + "..." if len(contentStr) > MAX_CONTENT_STR_LEN else contentStr
    return f"{self.__class__.__name__}( {self.filename}, {contentStr} )"

## ---------------------------------------------------------------

class YamlMerge(CommandBase):
  """ Merge the given yaml section into an existing file.

  Note that lists are replaced, not appended to or merged.
  """

  name = "hutt_yaml_merge"

  def __init__(self, source, filename, content):
    super().__init__(source)
    self.filename = filename
    self.content = content

  @classmethod
  def parseInline(cls, source, args):
    # for now, only single "key/value" pairs are supported.
    # If you want something more complex, you should probably use a block.
    kvArgs = ("key", "value")
    if not all(k in args for k in kvArgs):
      raise ValueError(f"Expected arguments: {kvArgs}")

    # TODO handle value being an anchor

    # parse the key into a nested dictionary
    keys = args["key"].split(".")
    newdict = current = {}
    for k in keys[:-1]:
      current[k] = {}
      current = current[k]
    current[keys[-1]] = args["value"]
    args.pop("key")
    args.pop("value")
    return [cls(source, content=newdict, **args),]

  @classmethod
  def parseBlock(cls, source, blockLang, blockText, args):
    return [cls(source, content=_block_to_dict(blockLang, blockText), **args),]

  def _execute(self):
    # read source yaml file, merge new content, and write
    source = _read_yaml(self.filename)
    _deep_merge(source, self.content)
    _write_yaml(self.filename, source)

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:MAX_CONTENT_STR_LEN] + "..." if len(contentStr) > MAX_CONTENT_STR_LEN else contentStr
    return f"{self.__class__.__name__}( {self.filename}, {contentStr})"

## ---------------------------------------------------------------

class YamlAppend(CommandBase):
  """ Append one or more list items to a given section in an existing yaml file"""
  name = "hutt_yaml_append"

  RE_APPEND_TO = re.compile(r"\s*# append to (?P<listKey>\".*?\"|'.*?'|\S+)")

  def __init__(self, source, filename, listKey, content):
    super().__init__(source)
    self.filename = filename
    self.listKey = listKey.split(".")
    self.content = content

    # error checking on input parameters
    if not isinstance(self.content, list):
      raise ValueError(f"Expected content to be a list, but got {type(self.content)}")

  @classmethod
  def parseInline(cls, source, args):
    raise NotImplementedError("YamlAppend.parseInline() not implemented")

  @classmethod
  def parseBlock(cls, source, blockLang, blockText, args):
    # first line should be a comment telling us where to append
    match = cls.RE_APPEND_TO.match(blockText[0])
    if not match:
      raise ValueError(f"Expected first line to be a comment: # append to <listKey>")
    listKey = match.group("listKey").strip("\"'")
    return [cls(source, listKey=listKey, content=_block_to_dict(blockLang, blockText[1:]), **args),]

  def _execute(self):
    source = _read_yaml(self.filename)

    # find the list to append to
    current = source
    fullKey = None
    for k in self.listKey:
      fullKey = ".".join([fullKey, k]) if fullKey else k
      if k not in current:
        raise ValueError(f"Key \"{fullKey}\" not found in source yaml file")
      current = current[k]
    if not isinstance(current, list):
      raise ValueError(f"Key \"{fullKey}\" is not a list in source yaml file")
    current.extend(self.content)

    _write_yaml(self.filename, source)

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:MAX_CONTENT_STR_LEN] + "..." if len(contentStr) > MAX_CONTENT_STR_LEN else contentStr
    return f"{self.__class__.__name__}( {self.filename}, {contentStr} )"

## ---------------------------------------------------------------

class YamlComment(CommandBase):
  name = "hutt_yaml_comment"

  def __init__(self, source, filename, id,  mode="toggle"):
    super().__init__(source)
    self.filename = filename
    self.id = id
    self.mode = mode

    # error checking on input parameters
    modes = ["toggle", "enable", "disable"]
    if mode not in modes:
      raise ValueError(f"Invalid mode: {mode}. Mode must be one of {modes}")

  def _execute(self):
    raise NotImplementedError("YamlComment.execute() not implemented")

  def __repr__(self) -> str:
    return f"{self.__class__.__name__}( {self.filename}, id={self.id}, mode={self.mode} )"
