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

## YAML commands

### file create

write the following section of documentation out to a yaml file

> ```yaml @hutt_yaml_write filename="test.yaml"
> foo:
>   bar: 0
> alpha:
>   beta:
>     gamma: [delta, epsilon]
> ```

### updates

update a value, inline (`test.02.yaml`)
<!-- @hutt_yaml_set filename="test.yaml" key="foo.bar" value="2" -->
<!-- @hutt_bash cmd="cp test.yaml test.02.yaml" -->

update a value, block, with default method (`test.03.yaml`)

> ```yaml @hutt_yaml_set filename="test.yaml"
> foo:
>  bar: 3
> ```
<!-- @hutt_bash cmd="cp test.yaml test.03.yaml" -->

update a value, with the merge method (`test.04.yaml`)

```yaml @hutt_yaml_set filename="test.yaml" method="merge"
foo:
  test: 4
```
<!-- @hutt_bash cmd="cp test.yaml test.04.yaml" -->

update a value, with the replace method (`test.05.yaml`)

```yaml @hutt_yaml_set filename="test.yaml" method="replace"
foo:
  bar: 5
```
<!-- @hutt_bash cmd="cp test.yaml test.05.yaml" -->

create a new key

```yaml @hutt_yaml_set filename="test.yaml"
foo:
  newKey: 5
```
<!-- @hutt_bash cmd="cp test.yaml test.06.yaml" -->

Set with a different parent

```yaml @hutt_yaml_set filename="test.yaml" parent="foo"
bar: 7
```
<!-- @hutt_bash cmd="cp test.yaml test.07.yaml" -->

### commenting

```yaml @hutt_yaml_write filename="test2.yaml"
test:
 section: {}
```

toggle comments for a section
<!-- @hutt_yaml_comment filename="test2.yaml" id="section1" mode="toggle" -->
<!-- @hutt_bash cmd="cp test2.yaml test1.01.yaml" -->

<!-- @hutt_yaml_comment filename="test2.yaml" id="section2" mode="enable" -->
<!-- @hutt_bash cmd="cp test2.yaml test2.02.yaml" -->

<!-- @hutt_yaml_comment filename="test2.yaml" id="section3" mode="disable" -->
<!-- @hutt_bash cmd="cp test2.yaml test2.03.yaml" -->
