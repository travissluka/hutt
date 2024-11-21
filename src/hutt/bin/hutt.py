# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click

from .run import _run
from .yaml import _yaml

@click.group()
@click.version_option()
def cli():
  """Helpful Utility for Testing Tutorials"""
  pass

cli.add_command(_run)
cli.add_command(_yaml)