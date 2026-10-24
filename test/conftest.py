from __future__ import annotations

import textwrap
import zlib
from pathlib import Path
from typing import Any, Callable

import pytest
from bfl_testing import Build, BuildResult
from sphinx.testing.util import SphinxTestApp

pytest_plugins = ["sphinx.testing.fixtures"]

_CONF = """\
import os
import sys

sys.path.insert(0, os.path.abspath("."))

extensions = {extensions!r}
"""

_INVENTORY_ENTRIES = [
    "typing.Any py:data 1 library/typing.html#$ -",
    "None py:data 1 library/constants.html#$ -",
    "True py:data 1 library/constants.html#$ -",
    "False py:data 1 library/constants.html#$ -",
    "ValueError py:exception 1 library/exceptions.html#$ -",
]
"""
Entries of a minimal local Python inventory, to test resolution without network access.
"""


@pytest.fixture(autouse=True)
def _rollback_sysmodules(rollback_sysmodules: None):
    """
    Unload modules imported by builds, since each build has its own source directory.
    """


@pytest.fixture
def build(tmp_path: Path, make_app: Callable[..., SphinxTestApp]) -> Build:
    """
    Create and build a project with the given `index.rst` content.
    """

    def build(
        source: str,
        *,
        modules: dict[str, str] | None = None,
        files: dict[str, str] | None = None,
        extensions: list[str] | None = None,
        buildername: str = "dummy",
        **confoverrides: Any,
    ) -> BuildResult:
        srcdir = tmp_path / "src"
        srcdir.mkdir()

        if extensions is None:
            extensions = ["sphinx_better_fieldlist"]

        (srcdir / "conf.py").write_text(_CONF.format(extensions=extensions))
        (srcdir / "index.rst").write_text(textwrap.dedent(source))

        for name, code in (modules or {}).items():
            (srcdir / f"{name}.py").write_text(textwrap.dedent(code))

        for path, content in (files or {}).items():
            (srcdir / path).parent.mkdir(parents=True, exist_ok=True)
            (srcdir / path).write_text(textwrap.dedent(content))

        app = make_app(buildername, srcdir=srcdir, confoverrides=confoverrides)
        app.build()

        return BuildResult(app)

    return build


@pytest.fixture
def inventory(tmp_path: Path) -> Path:
    """
    Path to a minimal local Python inventory.
    """
    path = tmp_path / "python.inv"
    header = (
        "# Sphinx inventory version 2\n"
        "# Project: Python\n"
        "# Version: 3\n"
        "# The remainder of this file is compressed using zlib.\n"
    )
    body = "".join(f"{entry}\n" for entry in _INVENTORY_ENTRIES)
    path.write_bytes(header.encode() + zlib.compress(body.encode()))
    return path
