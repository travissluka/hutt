# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase

class Yaml(CommandBase):
  name = "update_yaml"
  def __init__(self, **kwargs):
    pass

  @classmethod
  def parse(cls, **kwargs):
    return [cls(**kwargs["args"]),]

  def __repr__(self) -> str:
    return f"YamlCmd()"