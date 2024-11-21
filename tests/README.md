# Testing

The following markdown is a test of HUTT

## Bash commands

This is a single inline command (it's a hidden comment!)
<!-- @hutt_bash cmd="echo Hello there" -->

This is a block command

```bash @hutt_bash
echo hello there as well
sleep 1
```

Test the sleep:
<!-- @hutt_bash cmd="xeyes" timeout=2 -->
```bash @hutt_bash timeout=2
xeyes
```

## Yaml updates

Update a value in a yaml file

<!-- @hutt_set_yaml filename="test.yaml" key="foo.bar" value="100" -->

```yaml @hutt_set_yaml filename="test.yaml" method="merge"
foo:
  bar: 20
```

```yaml @hutt_set_yaml filename="test.yaml" method="replace"
foo:
  bar: 20
```

```yaml @hutt_set_yaml filename="test.yaml" destination="foo"
bar: 30
```

