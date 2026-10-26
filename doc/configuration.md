# Configuration

Every option is set in `conf.py`, and is optional.

```{bfl-config-reference}
```

For example, to only convert Python field lists, and leave Raises as Sphinx renders it:

```python
better_fieldlist_domains = ["py"]
better_fieldlist_exclude_fields = ["py:exceptions"]
```

## Field types

Field types for {confval}`better_fieldlist_exclude_fields` are given as
`<domain>:<field type>`, where the field type is the name of Sphinx's doc field type.
For the Python domain, these are the fields which are converted:

| Field type | Fields | Label |
| --- | --- | --- |
| `py:parameter` | `:param:`, `:type:` (and aliases such as `:keyword:`) | Parameters |
| `py:variable` | `:var:`, `:ivar:`, `:cvar:`, `:vartype:` | Variables |
| `py:exceptions` | `:raises:` | Raises |
