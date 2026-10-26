# Compatibility

## Versions

- **Python:** 3.13 or later.
- **Sphinx:** 9 is the primary target. 8.2 and 7.4 are supported on a best-effort basis:
  they're tested, but output may differ in details from Sphinx 9.

## Documentation generators

The extension works with any generator which uses Sphinx's domains, including
[autodoc](inv:sphinx#usage/extensions/autodoc),
[autodoc2](https://sphinx-autodoc2.readthedocs.io/) and hand-written directives; see the
[examples](examples/generators.md).

With autodoc2's MyST renderer, enable MyST's `fieldlist` extension so field lists in
docstrings are parsed:

```python
myst_enable_extensions = ["fieldlist"]
```

(sphinx-autodoc-typehints)=

## sphinx-autodoc-typehints

Types are only shown in field lists if they're documented explicitly.
[sphinx-autodoc-typehints](https://github.com/tox-dev/sphinx-autodoc-typehints) adds
types from signatures to field lists as `:type:` and `:rtype:` fields, so with both
extensions each parameter's term includes its type, e.g. `path (Path)`.

Its `typehints_defaults` option adds defaults too. With `"comma"` or `"braces"`, the
default is part of the term, e.g. `mode (str, default: 'r')`; with `"braces-after"`, it's
added to the description.
