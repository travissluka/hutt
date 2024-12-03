# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
from pathlib import Path
import textwrap
from datetime import date
import os

from hutt.mdParser import parseMarkdown
from hutt import Command

BANNER = textwrap.dedent(f"""
  ,--.  ,--.,--. ,--.,--------.,--------.
  |  '--'  ||  | |  |'--.  .--''--.  .--'
  |  .--.  ||  | |  |   |  |      |  |
  |  |  |  |'  '-'  '   |  |      |  |
  `--'  `--' `-----'    `--'      `--'
  Helpful Utility for Testing Tutorials (HUTT)
  (C) {str(date.today().year)} UCAR
""")

@click.command(name="run")
@click.argument(
  "filename", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option(
  "--workdir",
  default="./hutt_workdir",
  type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
  help="Set the working directory",
  show_default=True)
@click.option(
  "--resume",
  is_flag=True,
  help="Resume the tutorial from the last executed command.", )
@click.option(
  "--logfile",
  default=None,
  type=click.Path(dir_okay=False, writable=True, resolve_path=True),
  help="Specify the log file, default will be in the working directory",
  show_default=False)
@click.option(
  "--ignore-error",
  is_flag=True,
  help="Continue executing commands even if errors occur.")
@click.option(
  "-N",
  "--list-tests",
  is_flag=True,
  help="List all the tests in the markdown file and exit.")
@click.option(
    "-I",
    "--test-numbers",
    type=str,
    default=None,
    help="Run specific test numbers (comma separated) and exit.")
def _run(filename, workdir, resume, logfile, ignore_error, list_tests, test_numbers):
  """Run the tutorial from a given markdown file."""

  # Ensure mutually exclusive options
  if sum([resume, list_tests, test_numbers is not None]) > 1:
    raise click.UsageError("Options --resume, --list-tests, and --test-numbers are mutually exclusive.")

  # Set default logfile if not provided
  if logfile is None:
    logfile = os.path.join(workdir, "hutt_bash.log")

  # output info
  print(BANNER)
  click.echo(f"Input markdown file: {filename}")
  click.echo(f"Working directory: {workdir}")
  click.echo(f"Log file: {logfile}")
  if resume:
    raise NotImplementedError("Resume feature not implemented yet.")

  # parse the tutorial section into a list of commands
  commands = parseMarkdown(filename)
  numCommands = max((cmd.index for cmd in commands if cmd.index))

  # initialize any backend systems that the commands may need
  # change to the specified working directory
  Path(workdir).mkdir(parents=True, exist_ok=True)
  os.chdir(workdir)
  Command.initialize(env={
    "LOG_FILE": logfile,
    "SCRIPT_DIR": Path(filename).parent,
    "SCRIPT_PATH": filename,
    "WORK_DIR": workdir,})

  # list all the tests
  if list_tests:
    print("\033[1m\033[93m\nList of tests:\033[0m")
    for cmd in commands:
      if cmd.index:
        print(f"  [{cmd.index:>2} / L{cmd.source.line}]  {cmd}")
      else:
        print(f"\033[1m{cmd}\033[0m")
    return

  # run specific test numbers
  if test_numbers is not None:
    test_numbers = test_numbers.split(',')
    expanded_numbers = set()
    for num in test_numbers:
      if '-' in num:
        start, end = map(int, num.split('-'))
        expanded_numbers.update(range(start, end + 1))
      else:
        expanded_numbers.add(int(num))
    for num in expanded_numbers:
      if num < 1 or num > numCommands:
        raise click.UsageError(f"Test number {num} is out of range. Valid range is 1 to {numCommands}.")
    commands = [cmd for cmd in commands if cmd.index in expanded_numbers]

  # run the commands
  commandsFailed=0
  commandsRun=0
  msg=f"\nRunning tutorial at {filename} ({numCommands} commands)"
  print(f"\033[1m\033[93m{msg}\033[0m\033[0m")
  for command in commands:
    try:
      commandsRun += 1
      command.execute()
    except Exception as e:
      commandsFailed += 1
      print(f"\033[91m{e}\033[0m")

      if (not ignore_error):
        break
  print("")

  # finalize any backend systems
  Command.finalize()

  # print summary
  print("\n\033[1m\033[93mSummary:\033[0m", end=" ")
  if commandsFailed == 0:
    print(f"\033[92mAll {commandsRun} commands executed successfully.\033[0m")
  else:
    print(f"\033[91m{commandsFailed} of {commandsRun} commands failed.\033[0m")
  # else:
  # print(f"  Commands executed: {numCommands}")
  # print(f"  Commands failed: {failed}")