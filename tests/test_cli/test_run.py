import pytest
from click.testing import CliRunner
from hutt.bin.hutt import cli
from pathlib import Path

def test_run_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

def test_run_invalid_file():
    runner = CliRunner()
    result = runner.invoke(cli, ['nonexistent.md'])
    assert result.exit_code != 0
