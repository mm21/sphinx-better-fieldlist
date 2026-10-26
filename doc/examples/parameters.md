# Parameters

Each example shows the source, followed by the result as Sphinx renders it ("Before")
and with this extension ("After"). Examples are documented with autodoc unless stated
otherwise.

## Names

Each parameter is a term, with its description as the definition:

`````{bfl-example}
:pyobject: demo.parameters.names_only
:syntax: rst

.. autofunction:: demo.parameters.names_only
`````

## Types

A type documented with `:type:`, or inline as in `:param int x:`, is part of the term,
in the same form as Sphinx renders it:

`````{bfl-example}
:pyobject: demo.parameters.explicit_types
:syntax: rst

.. autofunction:: demo.parameters.explicit_types
`````

Types are only shown if documented explicitly. To show the types from signatures in
field lists, see {ref}`sphinx-autodoc-typehints`.

## Single parameter

Sphinx renders a field with a single item as a paragraph rather than a bullet list, so
its layout differs from fields with several items. With this extension, it's a
definition list like any other:

`````{bfl-example}
:pyobject: demo.parameters.single
:syntax: rst

.. autofunction:: demo.parameters.single
`````

## Multi-paragraph descriptions

Descriptions may contain any block content, such as several paragraphs or lists:

`````{bfl-example}
:pyobject: demo.parameters.multi_paragraph
:syntax: rst

.. autofunction:: demo.parameters.multi_paragraph
`````
