# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from abc import ABC, abstractmethod
from typing import MutableMapping, Type
import sys

class CommandBase(ABC):
  name: str

  def __init_subclass__(cls):
    Command._register(cls)
    return super().__init_subclass__()

  def __init__(self, source):
    super().__init__()
    self.source = source

  @classmethod
  def initialize(cls, env={}):
    pass

  @classmethod
  def finalize(cls):
    pass

  @classmethod
  def parseInline(cls, source, args):
    return [cls(source, **args), ]

  @classmethod
  def parseBlock(cls, *args, **kwargs):
    raise NotImplementedError(f"Block parsing is not supported for {cls} command")

  def execute(self):
    print(f"  [{self.index:>2} / L{self.source.line}]  {self}  ", end="")
    sys.stdout.flush()

    try:
      res = self._execute()
      if not res:
        raise Exception("Command failed")
    except Exception as e:
      print("\033[91m[FAIL]\033[0m")
      raise e
    print("\033[92m[OK]\033[0m")
    return True

  @abstractmethod
  def _execute(self):
    """Execute the command.
    Returns:
      bool: True if the command executed successfully, False otherwise.

    Raises:
      Exception: If the command execution fails.
    """
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

  def initialize(self, env=None):
    for command in self._subclasses.values():
      command.initialize(env)

  def finalize(self):
    for command in self._subclasses.values():
      command.finalize()

# ------------------------------------------------------------------------------

Command = __CommandFactory()
"""Factory for creating command classes"""