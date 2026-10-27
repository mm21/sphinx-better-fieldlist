# sphinx-better-fieldlist

A Sphinx extension which renders the field lists of API documentation (Parameters,
Raises, Variables, ...) as definition lists, rather than bullet lists or paragraphs.

`````{bfl-example}
:pyobject: demo.overview.fetch
:syntax: rst

.. autofunction:: demo.overview.fetch
`````

## What it does

Sphinx renders a field with several items, such as Parameters, as a bullet list whose
items run the name, type and description together: `name (type) – description`. A field
with a single item is rendered as a paragraph instead, so its layout differs.

This extension renders each such field as a definition list: the term is the name and
type, as Sphinx renders them, and the definition is the description. This is the same
for a single item, and for every domain, such as Python, C and C++.

Fields which aren't lists, such as Returns and Return type, are left as Sphinx renders
them.

It works with [autodoc](inv:sphinx#usage/extensions/autodoc),
[autodoc2](https://sphinx-autodoc2.readthedocs.io/) and hand-written directives.

## Installation

```bash
pip install sphinx-better-fieldlist
```

Then add it to `extensions` in `conf.py`:

```python
extensions = [
    # ...
    "sphinx_better_fieldlist",
]
```

There's nothing else to set up, though the behavior can be adjusted with the
{doc}`configuration options <configuration>`. For autodoc2 with MyST, also enable
MyST's `fieldlist` extension so docstring field lists are parsed:

```python
myst_enable_extensions = ["fieldlist"]
```

```{toctree}
:hidden:
:caption: Examples

examples/parameters
examples/fields
examples/c-domain
examples/generators
```

```{toctree}
:hidden:
:caption: Reference

opting-out
configuration
compatibility
development
```
