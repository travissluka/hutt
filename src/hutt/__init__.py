# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

"""Helpful Utility for Testing Tutorials

Package for reading tutorials that are written in markdown and converting them
to a format that can be run as a script. This package is intended to be used
with the `hutt` command line tool.
"""

from hutt.commands.base import Command

__all__ = [
    '__version__',
    'Command',]