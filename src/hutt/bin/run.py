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
  help="Specify the log file",
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
    "--test-number",
    type=int,
    default=None,
    help="Run a specific test number and exit.")
def _run(filename, workdir, resume, logfile, ignore_error, list_tests, test_number):
  """Run the tutorial from a given markdown file."""

  # Ensure mutually exclusive options
  if sum([resume, list_tests, test_number is not None]) > 1:
    raise click.UsageError("Options --resume, --list-tests, and --test-number are mutually exclusive.")

  # Set default logfile if not provided
  if logfile is None:
    logfile = os.path.join(workdir, "hutt.log")

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
    print("\nList of tests:")
    for cmd in commands:
      if cmd.index:
        print(f"  {cmd.index}: {cmd}")
      else:
        print(f"  {cmd}")
    return

  # run a specific test number
  if test_number is not None:
    if test_number < 1 or test_number > numCommands:
      raise click.UsageError(f"Test number {test_number} is out of range. Valid range is 1 to {numCommands}.")
    commands = [cmd for cmd in commands if cmd.index == test_number]

  # run the commands
  msg=f"\nRunning tutorial at {filename} ({numCommands} commands)"
  print(f"\033[1m\033[93m{msg}\033[0m\033[0m")
  for command in commands:
    try:
      success = command.execute()
    except Exception as e:
      success = False
      print(f"\033[91mError executing command number {command.index} \033[0m")
      print(f"\033[91m{e}\033[0m")

    if (not success and not ignore_error):
      break

  # finalize any backend systems
  Command.finalize()