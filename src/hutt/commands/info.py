# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase

class Info(CommandBase):
  name = "_info"

  def __init__(self, source, title, level):
    self.source = source
    self.title = title
    self.level = level

  def execute(self):
    super().execute()
    print(f"\033[1m{self}\033[0m")
    return True

  def __str__(self) -> str:
    return f"{'#' * self.level} {self.title}"
