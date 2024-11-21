# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click

from hutt.mdParser import parseMarkdown
from hutt import Command

@click.command(name="test")
@click.argument("filename")
def _test(filename):
  """Run the test suite."""
  click.echo(f"Running test suite on {filename}...")

  # parse the tutorial section into a list of commands
  commands = parseMarkdown(filename)
  numCommands = max((cmd.index for cmd in commands if cmd.index))

  # initialize any backend systems that the commands may need
  Command.initialize()

  # run the commands
  msg=f"Running tutorial {filename} ({numCommands} commands)"
  print(f"\033[1m\033[93m{msg}\033[0m\033[0m")
  for command in commands:
    if not command.execute():
      print(f"\033[91mError executing command number {command.index} \033[0m")
      break

  # finalize any backend systems
  Command.finalize()