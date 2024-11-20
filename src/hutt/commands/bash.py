# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
import re

class Bash(CommandBase):
  name = "test_run"

  def __init__(self, cmd, timeout=None):
    self.cmd = cmd
    self.timeout = timeout

  @classmethod
  def parse(cls, **kwargs):
    commands = []

    if any(k in kwargs for k in ("blockText", "blockLang")):
      args = kwargs.get("args", {})
      for line in kwargs.get("blockText"):
        if line.startswith("#"):
          continue
        commands.append(cls(line, **args))
    else:
      commands.append(cls(**kwargs["args"]))

    return commands

  def __repr__(self) -> str:
    return f"Bash( cmd=\"{self.cmd}\" )"