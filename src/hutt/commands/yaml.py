# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase

class Yaml(CommandBase):
  name = "hutt_set_yaml"

  def __init__(self, source, **kwargs):
    super().__init__(source)
    pass

  @classmethod
  def parseBlock(cls, source, **kwargs):
    return [cls(source, **kwargs["args"]),]

  def _execute(self):
    raise NotImplementedError("YamlCmd.execute() not implemented")

  def __repr__(self) -> str:
    return f"YamlCmd()"