"""
Sphinx extension entry point.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from . import restructure
from .config import register_config
from .disable import DisableDirective

__all__ = [
    "setup",
]

_STATIC_PATH = Path(__file__).parent / "_static"
"""
Directory containing static files for HTML output.
"""

_CSS_FILE = "sphinx-better-fieldlist.css"

_DISABLE_DIRECTIVE = "better-fieldlist-disable"


def setup(app: Sphinx) -> ExtensionMetadata:
    register_config(app)
    restructure.install()

    app.add_directive(_DISABLE_DIRECTIVE, DisableDirective)
    app.connect("builder-inited", _add_css)

    return {
        "version": metadata.version("sphinx-better-fieldlist"),
        "env_version": 3,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _add_css(app: Sphinx):
    if app.builder.format != "html":
        return

    app.config.html_static_path.append(str(_STATIC_PATH))
    app.add_css_file(_CSS_FILE)
