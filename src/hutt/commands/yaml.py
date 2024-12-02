# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
from ruamel.yaml import YAML

class YamlWrite(CommandBase):
  name = "hutt_yaml_write"

  def __init__(self, source, filename):
    super().__init__(source)
    self.filename = filename
    content = source.content[1:]

    # error checking on input parameters
    self.content = YAML().load("\n".join(content))

  @classmethod
  def parseBlock(cls, source, **kwargs):
    return [cls(source, **kwargs["args"]),]

  @classmethod
  def parseInline(cls, source, args):
    raise NotImplementedError("YamlWrite.parseInline() not implemented")

  def _execute(self):
    yaml = YAML()
    with open(self.filename, "w") as f:
      yaml.dump(self.content, f)
    return True

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:50] + "..." if len(contentStr) > 50 else contentStr
    return f"YamlWrite( {self.filename}, content={contentStr} )"

## ---------------------------------------------------------------

class YamlSet(CommandBase):
  name = "hutt_yaml_set"

  def __init__(self, source, filename, key, value, method="merge", parent=None):
    super().__init__(source)
    self.filename = filename
    self.method = method
    self.parent = parent

    # error checking on input parameters
    _methods = ["merge", "replace"]
    if method not in _methods:
      raise ValueError(f"Invalid method: {method}. Method must be one of {_methods}")

  @classmethod
  def parseBlock(cls, source, **kwargs):
    return [cls(source, key="key", value="value", **kwargs["args"]),]

  def _execute(self):
    raise NotImplementedError("YamlSet.execute() not implemented")

  def __repr__(self) -> str:
    return f"YamlSet( {self.filename}, method={self.method} )"

  ## ---------------------------------------------------------------

class YamlComment(CommandBase):
  name = "hutt_yaml_comment"

  def __init__(self, source, filename, id,  mode="toggle"):
    super().__init__(source)
    self.filename = filename
    self.id = id
    self.mode = mode

    # error checking on input parameters
    modes = ["toggle", "enable", "disable"]
    if mode not in modes:
      raise ValueError(f"Invalid mode: {mode}. Mode must be one of {modes}")

  def _execute(self):
    raise NotImplementedError("YamlComment.execute() not implemented")

  def __repr__(self) -> str:
    return f"YamlComment( {self.filename}, id={self.id}, mode={self.mode} )"
