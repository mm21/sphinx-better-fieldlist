# Development

The project uses [uv](https://docs.astral.sh/uv/) and
[pyprojkit](https://github.com/mm21/pyprojkit); see the
[repository](https://github.com/mm21/sphinx-better-fieldlist) for details.

## Testing

- `uv run doit test` runs the test suite against the locked, latest Sphinx version.
- `uv run nox` runs it against each supported Python version, plus the older Sphinx
  versions in the `compat` sessions.

## Snapshots

Snapshot tests compare the field lists generated for an example module, via autodoc and
autodoc2, against pseudo-XML stored in `test/snapshots/`. They only run with the latest
Sphinx version, given by `LATEST_SPHINX` in `test/bfl_testing.py`.

When output changes intentionally, or after upgrading Sphinx (updating `LATEST_SPHINX`
for a new minor version), regenerate them with:

```bash
BFL_UPDATE_SNAPSHOTS=1 uv run pytest -k snapshot
```

Then review the changes with `git diff test/snapshots/`.

## Documentation

`uv run doit doc` builds this documentation into `__out__/doc/html`. The examples are
rendered from the modules in `doc/demo/` by the `bfl-example` directive, defined in
`doc/_ext/bfl_docs.py`, and the [configuration reference](configuration.md) is generated
from the docstrings of the extension's `Config` class.
