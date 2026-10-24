# sphinx-better-fieldlist

Renders Sphinx field lists as definition lists, with types and defaults from signatures

[![Python versions](https://img.shields.io/pypi/pyversions/pyprojkit.svg)](https://pypi.org/project/pyprojkit)
[![PyPI](https://img.shields.io/pypi/v/pyprojkit?color=%2334D058&label=pypi%20package)](https://pypi.org/project/pyprojkit)
[![Tests](./badges/tests.svg?dummy=8484744)]()
[![Coverage](./badges/cov.svg?dummy=8484744)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

- [sphinx-better-fieldlist](#sphinx-better-fieldlist)
  - [Motivation](#motivation)
  - [Development](#development)
    - [Testing](#testing)
    - [Snapshots](#snapshots)

## Motivation

## Development

### Testing

- `uv run doit test`: runs the test suite against the locked (latest) Sphinx version
- `uv run nox`: runs the test suite against each supported Python version, plus older Sphinx versions (8.2, 7.4) via the `compat` sessions; these are supported on a best-effort basis

### Snapshots

Snapshot tests in `test/test_integration.py` compare the field lists generated for an example module (via autodoc and autodoc2) against pseudo-XML stored in `test/snapshots/`. They only run with the Sphinx version given by `LATEST_SPHINX` in `test/bfl_testing.py`, and are skipped for older versions.

Regenerate snapshots when output changes intentionally, or after upgrading Sphinx:

1. If Sphinx was upgraded to a new minor version, update `LATEST_SPHINX` to match
2. Regenerate snapshots:

   ```bash
   BFL_UPDATE_SNAPSHOTS=1 uv run pytest -k snapshot
   ```

3. Review changes with `git diff test/snapshots/` to confirm they're expected
4. Run `uv run doit test` to confirm the snapshots pass
