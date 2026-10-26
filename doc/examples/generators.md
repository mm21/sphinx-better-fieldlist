# Documentation generators

The extension works on the field lists created by Sphinx's domains, so it doesn't
matter how an object's description was generated. Each example below renders the same
function, defined as:

```{literalinclude} ../demo/generators.py
:pyobject: resize
```

## autodoc

`````{bfl-example}
:syntax: rst

.. autofunction:: demo.generators.resize
`````

## autodoc2

With autodoc2's MyST renderer (`autodoc2_render_plugin = "myst"`), MyST's `fieldlist`
extension must be enabled so the field lists in docstrings are parsed:

```python
myst_enable_extensions = ["fieldlist"]
```

`````{bfl-example}
:no-index:

```{autodoc2-object} demo.generators.resize
```
`````

## Hand-written in reStructuredText

`````{bfl-example}
:syntax: rst
:no-index:

.. py:function:: resize(width: int, height: int | None = None, *, keep_ratio: bool = True) -> bool

   Resize the image.

   :param width: New width in pixels
   :param height: New height in pixels, or ``None`` to derive it from ``width``
   :param keep_ratio: Whether to preserve the aspect ratio
   :returns: Whether the image was changed
`````

## Hand-written in MyST

In MyST, leave a blank line between the directive's first line and the field list:
otherwise the fields are parsed as directive options.

`````{bfl-example}
:no-index:

````{py:function} resize(width: int, height: int | None = None, *, keep_ratio: bool = True) -> bool

Resize the image.

:param width: New width in pixels
:param height: New height in pixels, or ``None`` to derive it from ``width``
:param keep_ratio: Whether to preserve the aspect ratio
:returns: Whether the image was changed
````
`````
