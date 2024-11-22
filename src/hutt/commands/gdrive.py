# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
import gdown

class GdriveCommand(CommandBase):
  name = "hutt_gdrive"

  def __init__(self, source, id):
    super().__init__(source)
    self.id = id

  def _execute(self):
    gdown.download(id=self.id, quiet=True)
    return True

  def __str__(self):
    return f"Download from Gdrive id: {self.id}"