"""
Tests for the `better-fieldlist-disable` directive.
"""

from __future__ import annotations

from bfl_testing import Build, find_desc, get_fields, get_items
from docutils import nodes
from sphinx import addnodes

_FUNCTION = """\
.. py:function:: {name}(a: int = None) -> int

   :param a: A
   :param b: B
   :returns: R
   :rtype: str
"""


def test_disable(build: Build):
    result = build(
        f"""\
.. better-fieldlist-disable::

{_indent(_FUNCTION.format(name="before"))}

{_FUNCTION.format(name="after")}
"""
    )
    doctree = result.get_doctree()

    container = next(doctree.findall(nodes.container))
    assert container["classes"] == ["bfl-disabled"]

    before = find_desc(doctree, "before")
    assert before.parent is container
    _check_disabled(before)

    fields = get_fields(before)
    assert list(fields) == ["Parameters", "Returns", "Return type"]
    assert isinstance(_get_body(fields["Parameters"]), nodes.bullet_list)

    # outside the directive is converted as usual
    fields = get_fields(result.get_desc("after"))
    assert get_items(fields["Parameters"]) == [("a: int = None", "A"), ("b", "B")]
    assert get_items(fields["Returns"]) == [("str", "R")]

    # no warning for unmatched param within directive
    warnings = result.warnings.strip().splitlines()
    assert len(warnings) == 1
    assert "signature of after" in warnings[0]

    for node in doctree.findall(nodes.Element):
        assert "better_fieldlist_disabled" not in node


def test_nested(build: Build):
    """
    Nested descriptions and nested directives are all disabled.
    """
    result = build(
        """\
        .. better-fieldlist-disable::

           .. py:class:: C(a: int)

              :param a: A

              .. better-fieldlist-disable::

                 .. py:method:: m(b: int)

                    :param b: B

              .. py:method:: n(c: int)

                 :param c: C

           .. py:function:: f(d: int)

              :param d: D

        .. py:function:: g(e: int)

           :param e: E
        """
    )

    for name in ("C", "C.m", "C.n", "f"):
        _check_disabled(result.get_desc(name))

    assert get_items(get_fields(result.get_desc("g"))["Parameters"]) == [
        ("e: int", "E")
    ]


def test_autodoc(build: Build):
    """
    Generated content is disabled, e.g. to compare before/after for the same object.
    """
    result = build(
        """\
        .. better-fieldlist-disable::

           .. autofunction:: example.f
              :no-index:

        .. autofunction:: example.f
        """,
        modules={"example": _example_module()},
        extensions=["sphinx.ext.autodoc", "sphinx_better_fieldlist"],
    )
    before, after = _get_descs(result.get_doctree(), "example.f")

    _check_disabled(before)
    assert list(get_fields(before)) == ["Parameters", "Returns"]
    assert get_items(get_fields(after)["Parameters"]) == [("a: int = None", "A")]
    assert not result.warnings


def test_autodoc2(build: Build):
    result = build(
        """\
        .. better-fieldlist-disable::

           .. autodoc2-object:: example.f

              no_index = true

        .. autodoc2-object:: example.f
        """,
        modules={"example": _example_module()},
        extensions=["autodoc2", "sphinx_better_fieldlist"],
        autodoc2_packages=[{"path": "example.py", "auto_mode": False}],
    )
    before, after = _get_descs(result.get_doctree(), "example.f")

    _check_disabled(before)
    assert get_items(get_fields(after)["Parameters"]) == [("a: int = None", "A")]
    assert not result.warnings


def test_myst(build: Build):
    result = build(
        """\
        .. toctree::

           page
        """,
        files={
            "page.md": """\
                # Page

                ::::{better-fieldlist-disable}
                :::{py:function} before(a: int)

                :param a: A
                :::
                ::::

                :::{py:function} after(a: int)

                :param a: A
                :::
                """
        },
        extensions=["myst_parser", "sphinx_better_fieldlist"],
        myst_enable_extensions=["colon_fence", "fieldlist"],
    )

    before = result.get_desc("before", "page")
    _check_disabled(before)
    assert isinstance(_get_body(get_fields(before)["Parameters"]), nodes.paragraph)
    assert get_items(get_fields(result.get_desc("after", "page"))["Parameters"]) == [
        ("a: int", "A")
    ]
    assert not result.warnings


def test_html(build: Build):
    result = build(
        f"""\
.. better-fieldlist-disable::

{_indent(_FUNCTION.format(name="f"))}
""",
        buildername="html",
    )
    html = (result.app.outdir / "index.html").read_text()

    assert 'class="bfl-disabled' in html
    assert "bfl-list" not in html


def _check_disabled(desc: addnodes.desc):
    """
    Check that description is rendered as Sphinx would.
    """
    assert not list(desc.findall(nodes.definition_list))
    assert not list(desc.findall(_is_bfl))

    # default xrefs aren't added
    signature = desc.children[0]
    assert isinstance(signature, addnodes.desc_signature)
    assert "None" not in [
        xref["reftarget"] for xref in signature.findall(addnodes.pending_xref)
    ]


def _is_bfl(node: nodes.Node) -> bool:
    if not isinstance(node, nodes.Element):
        return False
    classes: list[str] = node["classes"]
    return any(cls.startswith("bfl-") and cls != "bfl-disabled" for cls in classes)


def _get_body(field: nodes.field) -> nodes.Node:
    """
    Get the single child of a field's body.
    """
    body = field.children[1]
    assert isinstance(body, nodes.field_body)
    assert len(body.children) == 1
    return body.children[0]


def _get_descs(doctree: nodes.document, fullname: str) -> list[addnodes.desc]:
    descs = [
        desc
        for desc in doctree.findall(addnodes.desc)
        if find_desc(desc, fullname) is desc
    ]
    assert len(descs) == 2
    return descs


def _example_module() -> str:
    return '''\
        def f(a: int = None) -> int:
            """
            Example function.

            :param a: A
            :returns: R
            """
        '''


def _indent(text: str) -> str:
    return "\n".join(f"   {line}" if line else line for line in text.splitlines())
