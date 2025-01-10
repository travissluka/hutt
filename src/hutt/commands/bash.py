# (C) Copyright 2024-2024 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from .base import CommandBase
from dataclasses import dataclass
import copy
import os
import re
import subprocess
import sys
import textwrap


def get_physical_cores():
  """ Get the number of physical cores on the system
  note this only works on linux systems
  """
  cores_per_socket = int(os.popen("lscpu | awk '/^Core\\(s\\) per socket:/ {print $4}'").read().strip())
  sockets = int(os.popen("lscpu | awk '/^Socket\\(s\\):/ {print $2}'").read().strip())
  return cores_per_socket * sockets


class BashSubsystem:
  RE_CMD_RET = re.compile(r"RUN_CMD_(?P<status>END|ERR|START)\s+(?:exit=(?P<exit>\d+))?")

  @dataclass
  class ReturnStatus():
    success: bool
    exit_code: int
    def __bool__(self):
      return self.success

  def __init__(self):
    self.process = None

  def __del__(self):
    if self.process:
      self.close()

  def initialize(self, env={}):
    print("\ninitializing bash subsystem...")

    # set up some environment variables ourselves
    np = get_physical_cores()
    env["NP"] = str(np)
    print(" - detected", np, "physical cores")

    # print out the environment variables
    print(" - environment variables:")
    env = {k: env[k] for k in sorted(env)}
    for k, v in env.items():
      print(f"   - {k}={v}")

    bash_header = textwrap.dedent(f"""\
      set -eu

      # set up our environment variables
      {";".join([f"{k}={v}" for k, v in env.items()])}

      # setup the log file
      mkdir -p $(dirname $LOG_FILE)
      touch $LOG_FILE

      run_cmd() {{
        # wrapper to run a command, log the output, and check the return code
        # note that we pull cmd from a global array, to get around issues with
        # quotes getting messed up when passing the command as a string
        local err_code=$1
        shift 1
        # echo "RUN_CMD cmd=$cmd" >> $LOG_FILE
        echo "RUN_CMD_START"
        "${{cmd[@]}}" >> $LOG_FILE 2>&1 \\
          || (exit_code=$?; [ $exit_code -eq $err_code ] \\
            || (echo "RUN_CMD_ERR exit=$exit_code" && exit 1))
        echo "RUN_CMD_END"
      }}
      """)

    if self.process:
      raise ValueError("Bash subsystem already initialized.")

    self.process = subprocess.Popen(
      ["bash"], text=True,
      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    self.process.stdin.write(bash_header)

  def close(self):
    print("closing bash subsystem...")
    if not self.process:
      raise ValueError("Bash subsystem not initialized.")
    self.process.terminate()
    self.process.wait()
    self.process = None

  def execute(self, command, exit_code=0):
    cmd = f"cmd=({command}); run_cmd {exit_code}\n"
    self.process.stdin.write(cmd)
    self.process.stdin.flush()

    # wait for the command to finish
    while True:
      output = self._waitRead()
      match = self.RE_CMD_RET.match(output)
      if match:
        retType = match.group("status")
        if retType == "END":
          return self.ReturnStatus(success=True, exit_code=0)
        elif retType == "ERR":
          return self.ReturnStatus(success=False, exit_code=int(match.group("exit")))

  def _waitRead(self):
    if not self.process:
      raise ValueError("Bash subsystem not initialized.")
    if self.process.poll() is not None:
      raise ValueError("Bash process has terminated.")

    output = self.process.stdout.readline()
    if output == "" and self.process.poll() is not None:
      # we usually get here if there has been an error in the script
      # (possibly an unbound variable?)
      # print everything there is in the stderr and exit
      print("\033[91m[ERROR]\033[0m")
      print("Error in script execution")
      while True:
        err = self.process.stderr.readline()
        if err == "":
          break
        print(err)
      sys.exit(1)
    return output

# ------------------------------------------------------------------------------

class BashCommand(CommandBase):
  name = "hutt_bash"
  subsystem = BashSubsystem()

  def __init__(self, source, cmd, timeout=None, exit_code=None):
    super().__init__(source)
    self.cmd = cmd.strip()
    self.timeout = timeout
    if timeout:
      if exit_code:
        raise ValueError("Cannot specify both timeout and exit_code.")
      exit_code = 124
    self.exit_code = exit_code if exit_code is not None else 0

  @classmethod
  def parseBlock(cls, source, blockLang, blockText, args={}):
    if blockLang != "bash":
      raise ValueError(f"Expected block language to be \"bash\" but got \"{blockLang}\".")
    # create a separate command for each line in the block
    commands = []
    lineNum = source.line
    for line in blockText:
      lineNum += 1
      if line.strip().startswith("#"):
        continue
      source2 = copy.copy(source)
      source2.line = lineNum
      commands.append(cls(source2, line, **args))
    return commands

  @classmethod
  def initialize(cls, env={}):
    super().initialize()
    cls.subsystem.initialize(env)

  @classmethod
  def finalize(cls):
    super().finalize()
    cls.subsystem.close()

  def _execute(self):
    # run the command
    cmd = self.cmd
    if self.timeout:
      cmd = f"timeout {self.timeout}s {cmd}"
    success = self.subsystem.execute(cmd, exit_code=self.exit_code)

    # check the return status
    if not success:
      raise RuntimeError(f"Command failed with exit code {success.exit_code}\n"
                          "See bash log for details")

  def __repr__(self) -> str:
    s = f"Bash( cmd=\"{self.cmd}\" "
    if self.timeout:
      s += f"timeout={self.timeout}"
    s += ")"
    return s

  def __str__(self) -> str:
    return f"{self.cmd}"