"""
Sphinx extension entry point.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from . import enrich, restructure
from .config import get_config, register_config

__all__ = [
    "setup",
]

_STATIC_PATH = Path(__file__).parent / "_static"
"""
Directory containing static files for HTML output.
"""

_CSS_FILE = "sphinx-better-fieldlist.css"

_DOCTREE_READ_PRIORITY = 900
"""
Priority of `doctree-read` handler: run after other extensions' handlers (default 500)
so modifications to signatures are reflected in copies.
"""

_MISSING_REFERENCE_PRIORITY = 950
"""
Priority of `missing-reference` handler: run after intersphinx (500) and the Python
domain's builtin resolver (900) so xrefs are resolved if possible.
"""


def setup(app: Sphinx) -> ExtensionMetadata:
    register_config(app)
    restructure.install()

    app.connect("doctree-read", enrich.process_doctree, priority=_DOCTREE_READ_PRIORITY)
    app.connect(
        "missing-reference",
        enrich.resolve_fallback,
        priority=_MISSING_REFERENCE_PRIORITY,
    )
    app.connect("builder-inited", _add_css)

    return {
        "version": metadata.version("sphinx-better-fieldlist"),
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _add_css(app: Sphinx):
    if app.builder.format != "html" or not get_config(app.config).css:
        return

    app.config.html_static_path.append(str(_STATIC_PATH))
    app.add_css_file(_CSS_FILE)
