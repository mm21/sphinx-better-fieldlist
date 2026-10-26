# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import tomllib
from pathlib import Path

DOC_PATH = Path(__file__).parent

# make docs extension and example package importable
sys.path[:0] = [str(DOC_PATH / "_ext"), str(DOC_PATH)]

# -- Project information -------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sphinx-better-fieldlist"
copyright = "2026, mm21"
author = "mm21"

with open(DOC_PATH.parent / "pyproject.toml", "rb") as fh:
    release = tomllib.load(fh)["project"]["version"]

# -- General configuration -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.autodoc",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx_better_fieldlist",
    "bfl_docs",
]

exclude_patterns = ["_build"]

myst_enable_extensions = [
    "colon_fence",
    "fieldlist",
]

# show unqualified names in example signatures
add_module_names = False

# examples are documented explicitly rather than generating pages
autodoc2_packages = [
    {"path": "demo", "auto_mode": False},
]
autodoc2_render_plugin = "myst"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# -- Options for HTML output ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_baseurl = "https://mm21.github.io/sphinx-better-fieldlist/"

html_theme = "furo"

html_title = f"{project} {release}"

html_static_path = ["_static"]

html_css_files = ["bfl-docs.css"]

multi_line_parameter_list = True
