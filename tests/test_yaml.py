import hutt.commands.bash
from click.testing import CliRunner
from hutt.bin.hutt import cli
import tempfile
from textwrap import dedent
from ruamel.yaml import YAML

base_yaml={
  'foo': {'bar': 0, 'thing': 1},
  'alpha': {'beta': {'gamma': ['delta', 'epsilon']}}}

def run_markdown(markdown, result_yaml, exit_code=0):
  assert exit_code in [0, 1]
  yaml = YAML()

  with tempfile.TemporaryDirectory() as tmpdir:
    # write base yaml file
    yaml_file = f'{tmpdir}/test.yaml'
    with open(yaml_file, 'w') as f:
      yaml.dump(base_yaml, f)

    # run the hutt command
    with tempfile.NamedTemporaryFile(mode='w', suffix=".md") as tmp:
      tmp.write(markdown)
      tmp.flush()
      runner = CliRunner()
      result = runner.invoke(cli, ['run', '--workdir', tmpdir, tmp.name])
      assert result.exit_code == exit_code

    # parse the yaml file to check contents
    with open(yaml_file) as f:
      yaml_data = yaml.load(f)
    assert yaml_data == result_yaml

# --------------------------------------------------------------

def test_yaml_write():
  markdown = dedent("""
  ```yaml @hutt_yaml_write filename='test.yaml'
  foo: bar
  ``` """)
  run_markdown(markdown, {'foo': 'bar'})

def test_yaml_merge_inline_int():
  markdown="<!-- @hutt_yaml_merge filename='test.yaml' key='foo.bar' value='2' -->"
  result = base_yaml.copy()
  result['foo']['bar'] = 2
  run_markdown(markdown, result)

def test_yaml_merge_inline_dict():
  markdown="<!-- @hutt_yaml_merge filename='test.yaml' key='foo.bar' value='{\"a\":\"b\"}' -->"
  result = base_yaml.copy()
  result['foo']['bar']={'a':'b'}
  run_markdown(markdown, result)

def test_yaml_merge_block():
  markdown = dedent("""
    ```yaml @hutt_yaml_merge filename='test.yaml'
    foo:
      bar: 3
    ```""")
  result = base_yaml.copy()
  result['foo']['bar'] = 3
  run_markdown(markdown, result)

