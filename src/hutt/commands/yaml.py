# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
from ruamel.yaml import YAML

def _deep_merge(dst, src):
  """ Merge two yaml files, overwriting shared values from src into dst """
  for k, v in src.items():
    if ( k in dst and
          isinstance(dst[k], dict) and
          isinstance(v, dict) ):
      _deep_merge(dst[k], v)
    else:
      dst[k] = v
  return dst

class YamlWrite(CommandBase):
  """ Write a yaml file given an input block of text """
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

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:50] + "..." if len(contentStr) > 50 else contentStr
    return f"YamlWrite( {self.filename}, {contentStr} )"

## ---------------------------------------------------------------

class YamlSet(CommandBase):
  """ Set a value in a yaml file """
  name = "hutt_yaml_set"

  def __init__(self, source, filename, content, method="merge", parent=None):
    super().__init__(source)
    self.filename = filename
    self.method = method
    self.parent = parent
    self.content = content

    # error checking on input parameters
    _methods = ["merge", "replace"]
    if method not in _methods:
      raise ValueError(f"Invalid method: {method}. Method must be one of {_methods}")

  @classmethod
  def parseInline(cls, source, args):
    # for now, only single "key/value" pairs are supported.
    # If you want something more complex, you should probably use a block.
    kvArgs = ("key", "value")
    if not all(k in args for k in kvArgs):
      raise ValueError(f"Expected arguments: {kvArgs}")

    # parse the key into a nested dictionary
    keys = args["key"].split(".")
    newdict = current = {}
    for k in keys[:-1]:
      current[k] = {}
      current = current[k]
    current[keys[-1]] = args["value"]
    args.pop("key")
    args.pop("value")
    return [cls(source, content=newdict, **args),]

  @classmethod
  def parseBlock(cls, source, blockLang, blockText, args):
    if blockLang != "yaml":
      raise ValueError(f"Expected block language to be \"yaml\" but got \"{blockLang}\".")

    newdict = YAML().load("\n".join(blockText))
    return [cls(source, content=newdict, **args),]

  def _execute(self):
    # read the yaml file
    yaml = YAML()
    with open(self.filename, "r") as f:
      source = yaml.load(f)

    # merge the newdict into the source
    if self.parent:
      raise NotImplementedError("YamlSet.execute() not implemented when parent is set")
    if self.method == "merge":
      _deep_merge(source, self.content)
    elif self.method == "replace":
      raise NotImplementedError("YamlSet.execute() not implemented for method=replace")

    # write the yaml file
    with open(self.filename, "w") as f:
      yaml.dump(source, f)

  def __repr__(self) -> str:
    contentStr = str(self.content)
    contentStr = contentStr[:50] + "..." if len(contentStr) > 50 else contentStr
    return f"YamlSet( {self.filename}, {contentStr}, method={self.method} )"

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
