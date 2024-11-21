# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from abc import ABC, abstractmethod
from typing import MutableMapping, Type

class CommandBase(ABC):
  name: str

  def __init_subclass__(cls):
    Command._register(cls)
    return super().__init_subclass__()

  @classmethod
  def initialize(cls):
    pass

  @classmethod
  def finalize(cls):
    pass

  @classmethod
  def parseInline(cls, *args, **kwargs):
    raise NotImplementedError()

  @classmethod
  def parseBlock(cls, *args, **kwargs):
    raise NotImplementedError()

  @abstractmethod
  def execute(self):
    pass

# ------------------------------------------------------------------------------

class __CommandFactory():
  _subclasses: MutableMapping[str, Type[CommandBase]] = {}

  def __call__(self, name: str):
    if name not in self._subclasses:
      raise ValueError(f"Command with name \"@{name}\" does not exist.")
    return self._subclasses[name]

  def _register(self, command: Type[CommandBase]):
    if command.name in self._subclasses:
      raise ValueError(f"Command with name \"{command.name} already exists.")
    self._subclasses[command.name] = command

  @property
  def list(self):
    return list(self._subclasses.keys())

  def initialize(self):
    for command in self._subclasses.values():
      command.initialize()

  def finalize(self):
    for command in self._subclasses.values():
      command.finalize()

# ------------------------------------------------------------------------------

Command = __CommandFactory()
"""Factory for creating command classes"""