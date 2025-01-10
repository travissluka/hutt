import hutt.commands.bash
from click.testing import CliRunner
from hutt.bin.hutt import cli
import tempfile
from textwrap import dedent

def run_markdown(markdown, exit_code=0):
  assert exit_code in [0, 1]
  with tempfile.TemporaryDirectory() as tmpdir:
    with tempfile.NamedTemporaryFile(mode='w', suffix=".md") as tmp:
      tmp.write(markdown)
      tmp.flush()
      runner = CliRunner()
      result = runner.invoke(cli, ['run', '--workdir', tmpdir, tmp.name])
      assert result.exit_code == exit_code

# ------------------------------------------------------------

def test_bash_get_physical_cores():
  cores = hutt.commands.bash.get_physical_cores()
  assert cores >= 1

def test_bash_empty():
  markdown = dedent("""
    # This is an empty test
    """)
  run_markdown(markdown)

def test_bash_inline():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_bash cmd='echo "Hello, World!"' -->
    """)
  run_markdown(markdown)

def test_bash_inline_timeout():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_bash cmd='sleep 5' timeout=1 -->
    """)
  run_markdown(markdown)

def test_bash_inline_exitcode():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_bash cmd='bash -c "exit 4"' exit_code=4 -->
    """)
  run_markdown(markdown)

def test_bash_block():
  markdown = dedent("""
    # Test Block

    > ```bash @hutt_bash
    > echo "Hello, World!"
    > # This is a comment
    > sleep 1
    > ```
    """)
  run_markdown(markdown)

## ------------------------------------------------------------
# Error cases

def test_bad_command():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_error -->
    """)
  run_markdown(markdown, exit_code=1)

def test_bash_inline_bad_cmd():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_bash cmd='foobar' -->
    """)
  run_markdown(markdown, exit_code=1)

def test_bash_inline_bad_arg():
  markdown = dedent("""
    # Test Inline
    <!-- @hutt_bash cmd='echo "Hello, World!"' badarg='foobar' -->
    """)
  run_markdown(markdown, exit_code=1)

