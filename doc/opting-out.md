# Opting out

## Specific objects or sections

The `better-fieldlist-disable` directive renders its content exactly as Sphinx would
without this extension. Use it to opt out specific objects, or whole sections of a
document. It applies to everything generated within it, including the output of autodoc
and autodoc2 directives.

In reStructuredText:

```rst
.. better-fieldlist-disable::

   .. autofunction:: demo.opting_out.legacy
```

In MyST, autodoc directives must be wrapped in `eval-rst`, as usual:

`````md
````{better-fieldlist-disable}
```{eval-rst}
.. autofunction:: demo.opting_out.legacy
```
````
`````

Which renders as:

````{better-fieldlist-disable}
```{eval-rst}
.. autofunction:: demo.opting_out.legacy
```
````

The content is wrapped in a container with the class `bfl-disabled`, which may be used
to style it.

## Showing an object twice

To render the same object both with and without the extension, e.g. for a comparison
like the [examples](examples/parameters.md), describe it once without indexing so Sphinx
doesn't warn about a duplicate object description:

- **autodoc and hand-written Python directives:** add the `:no-index:` option.

  ```rst
  .. better-fieldlist-disable::

     .. autofunction:: mymodule.myfunction
        :no-index:

  .. autofunction:: mymodule.myfunction
  ```

- **autodoc2:** set `no_index = true` in the body of `autodoc2-object`. To document
  objects only with `autodoc2-object`, without autodoc2 also generating pages for them
  under `apidocs`, set `auto_mode` to `False` for their package in `autodoc2_packages`.

  ````md
  ```{autodoc2-object} mymodule.myfunction
  no_index = true
  ```
  ````

  ```python
  autodoc2_packages = [{"path": "mymodule", "auto_mode": False}]
  ```

- **C and C++:** these directives don't support `:no-index:`, but the copy can be
  declared in a separate namespace with `c:namespace-push` and `c:namespace-pop` (or
  their `cpp:` equivalents), which doesn't change the name shown.

## Whole domains or field types

To leave a domain's field lists as Sphinx renders them, exclude it from
{confval}`better_fieldlist_domains`. To leave specific field types, such as Raises, add
them to {confval}`better_fieldlist_exclude_fields`.
