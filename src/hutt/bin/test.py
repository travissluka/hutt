# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click

from hutt.mdParser import parseMarkdown

@click.command(name="test")
@click.argument("filename")
def _test(filename):
    """Run the test suite."""
    click.echo(f"Running test suite on {filename}...")
    commands = parseMarkdown(filename)
