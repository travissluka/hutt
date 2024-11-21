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
  default=".",
  type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
  help="Set the working directory (default is current directory)."
)
def _run(filename, workdir):
  """Run the tutorial from a given markdown file."""

  # output info
  print(BANNER)
  click.echo(f"Input markdown file: {filename}")
  click.echo(f"Working directory: {workdir}")

  # parse the tutorial section into a list of commands
  commands = parseMarkdown(filename)
  numCommands = max((cmd.index for cmd in commands if cmd.index))

  # initialize any backend systems that the commands may need
  # change to the specified working directory
  Path(workdir).mkdir(parents=True, exist_ok=True)
  os.chdir(workdir)
  Command.initialize()

  # run the commands
  msg=f"\nRunning tutorial at {filename} ({numCommands} commands)"
  print(f"\033[1m\033[93m{msg}\033[0m\033[0m")
  for command in commands:
    if not command.execute():
      print(f"\033[91mError executing command number {command.index} \033[0m")
      break

  # finalize any backend systems
  Command.finalize()