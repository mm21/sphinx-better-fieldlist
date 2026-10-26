"""
Tests with documentation generators and HTML output.
"""

from __future__ import annotations

import re
from typing import Any

from bfl_testing import (
    Build,
    BuildResult,
    check_snapshot,
    get_fields,
    get_items,
    requires_latest_sphinx,
)
from docutils import nodes

EXAMPLE = '''\
"""
Example module.
"""

from __future__ import annotations


class Foo:
    """
    Example class.

    :param a: Param ``a``
    :param b: Param ``b``
    :param c: Param ``c``
    """

    def __init__(self, a: int, b: str, c: int | None = None):
        pass

    def bar(self, d: list[int], *args: str, e: bool = False, **kwargs) -> list[int]:
        """
        Example method.

        :param d: Param ``d``
        :param args: Variadic args
        :param e: Keyword-only param ``e``

            With a second paragraph.
        :param f: Passed via ``kwargs``
        :returns: Return value
        :raises ValueError: If an invalid value is passed
        :raises TypeError: If an invalid type is passed
        """
        return d

    def baz(self, g, h=None):
        """
        Untyped method.

        :param g: Param ``g``
        :type g: int
        :param h: Param ``h``
        :returns: Return value
        :rtype: str
        """


def qux(i: int) -> None:
    """
    Example function.

    :param i: Param ``i``
    :returns: Nothing
    """
'''

_AUTODOC_SOURCE = """\
.. automodule:: example
   :members:
"""

_AUTODOC2_CONF: dict[str, Any] = {
    "autodoc2_packages": ["example.py"],
    "autodoc2_render_plugin": "myst",
    "myst_enable_extensions": ["fieldlist"],
}

_AUTODOC2_SOURCE = """\
.. toctree::

   apidocs/index
"""


def test_autodoc(build: Build):
    result = build(
        _AUTODOC_SOURCE,
        modules={"example": EXAMPLE},
        extensions=["sphinx.ext.autodoc", "sphinx_better_fieldlist"],
    )
    _check_example(result, "index")


def test_autodoc2(build: Build):
    result = build(
        _AUTODOC2_SOURCE,
        modules={"example": EXAMPLE},
        extensions=["myst_parser", "autodoc2", "sphinx_better_fieldlist"],
        **_AUTODOC2_CONF,
    )
    _check_example(result, "apidocs/example/example")


def test_html(build: Build):
    result = build(
        """\
        .. py:function:: f(a: int)

           :param a: A
        """,
        buildername="html",
    )
    outdir = result.app.outdir

    assert (outdir / "_static" / "sphinx-better-fieldlist.css").exists()

    html = (outdir / "index.html").read_text()
    assert "_static/sphinx-better-fieldlist.css" in html
    assert re.search(r'<dl class="[^"]*\bbfl-list\b', html)
    assert '<span class="bfl-name">' in html


def test_html_no_css(build: Build):
    result = build(
        """\
        .. py:function:: f(a: int)

           :param a: A
        """,
        buildername="html",
        better_fieldlist_css=False,
    )
    outdir = result.app.outdir

    assert not (outdir / "_static" / "sphinx-better-fieldlist.css").exists()
    assert "sphinx-better-fieldlist.css" not in (outdir / "index.html").read_text()


@requires_latest_sphinx
def test_snapshot_autodoc(build: Build):
    result = build(
        _AUTODOC_SOURCE,
        modules={"example": EXAMPLE},
        extensions=["sphinx.ext.autodoc", "sphinx_better_fieldlist"],
    )
    check_snapshot("autodoc", _format_fields(result, "index"))


@requires_latest_sphinx
def test_snapshot_autodoc2(build: Build):
    result = build(
        _AUTODOC2_SOURCE,
        modules={"example": EXAMPLE},
        extensions=["myst_parser", "autodoc2", "sphinx_better_fieldlist"],
        **_AUTODOC2_CONF,
    )
    check_snapshot("autodoc2", _format_fields(result, "apidocs/example/example"))


def _check_example(result: BuildResult, docname: str):
    fields = get_fields(result.get_desc("example.Foo", docname))
    assert get_items(fields["Parameters"]) == [
        ("a", "Param a"),
        ("b", "Param b"),
        ("c", "Param c"),
    ]

    fields = get_fields(result.get_desc("example.Foo.bar", docname))
    assert get_items(fields["Parameters"]) == [
        ("d", "Param d"),
        ("args", "Variadic args"),
        ("e", "Keyword-only param e\n\nWith a second paragraph."),
        ("f", "Passed via kwargs"),
    ]
    assert get_items(fields["Raises"]) == [
        ("ValueError", "If an invalid value is passed"),
        ("TypeError", "If an invalid type is passed"),
    ]
    assert _get_paragraph(fields["Returns"]) == "Return value"

    fields = get_fields(result.get_desc("example.Foo.baz", docname))
    assert get_items(fields["Parameters"]) == [
        ("g (int)", "Param g"),
        ("h", "Param h"),
    ]
    assert _get_paragraph(fields["Returns"]) == "Return value"
    assert _get_paragraph(fields["Return type"]) == "str"

    fields = get_fields(result.get_desc("example.qux", docname))
    assert get_items(fields["Parameters"]) == [("i", "Param i")]
    assert _get_paragraph(fields["Returns"]) == "Nothing"


def _get_paragraph(field: nodes.field) -> str:
    """
    Get text of a field left as Sphinx renders it: a single paragraph.
    """
    body = field.children[1]
    assert len(body.children) == 1
    paragraph = body.children[0]
    assert isinstance(paragraph, nodes.paragraph), body.pformat()
    return paragraph.astext()


def _format_fields(result: BuildResult, docname: str) -> str:
    """
    Format field lists of each object description as pseudo-XML.
    """
    sections: list[str] = []
    for name in ("Foo", "Foo.bar", "Foo.baz", "qux"):
        desc = result.get_desc(f"example.{name}", docname)
        fields = get_fields(desc)
        field_list = next(iter(fields.values())).parent
        sections.append(f"# example.{name}\n\n{field_list.pformat()}")
    return "\n".join(sections)
