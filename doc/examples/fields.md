# Other fields

## Raises

Each exception is a term, with its description as the definition:

`````{bfl-example}
:pyobject: demo.fields.raises
:syntax: rst

.. autofunction:: demo.fields.raises
`````

As with parameters, a single exception is a definition list like any other:

`````{bfl-example}
:pyobject: demo.fields.raises_single
:syntax: rst

.. autofunction:: demo.fields.raises_single
`````

## Variables

Variables documented with `:ivar:`, `:cvar:` or `:var:` are rendered like parameters,
including types documented with `:vartype:`:

`````{bfl-example}
:pyobject: demo.fields.Connection
:syntax: rst

.. autoclass:: demo.fields.Connection
`````

## Returns

Returns and Return type aren't lists, so they're left as Sphinx renders them:

`````{bfl-example}
:pyobject: demo.fields.returns
:syntax: rst

.. autofunction:: demo.fields.returns
`````
