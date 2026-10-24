"""
Tests for conversion of grouped fields to definition lists.
"""

from __future__ import annotations

from bfl_testing import Build, get_fields, get_items
from docutils import nodes

from sphinx_better_fieldlist import restructure

SOURCE = """\
.. py:function:: f(a, b)

   :param a: A
   :param b: B
   :raises ValueError: If invalid
   :raises TypeError: If wrong type
   :var x: X
"""


def test_grouped(build: Build):
    """
    Grouped fields are converted to definition lists.
    """
    fields = get_fields(
        build(SOURCE, better_fieldlist_signature_types=False).get_desc("f")
    )

    assert get_items(fields["Parameters"]) == [("a", "A"), ("b", "B")]
    assert get_items(fields["Raises"]) == [
        ("ValueError", "If invalid"),
        ("TypeError", "If wrong type"),
    ]
    assert get_items(fields["Variables"]) == [("x", "X")]


def test_single(build: Build):
    """
    A single item is still a definition list rather than collapsed to a paragraph.
    """
    result = build(
        """\
        .. py:function:: f(a)

           :param a: A
           :raises ValueError: If invalid
        """
    )
    fields = get_fields(result.get_desc("f"))

    assert get_items(fields["Parameters"]) == [("a: Unknown", "A")]
    assert get_items(fields["Raises"]) == [("ValueError", "If invalid")]


def test_term_structure(build: Build):
    """
    Term parts are wrapped in inlines with classes for styling.
    """
    result = build(
        """\
        .. py:function:: f(a: int = 1)

           :param a: A
        """
    )
    term = next(get_fields(result.get_desc("f"))["Parameters"].findall(nodes.term))

    assert [
        child["classes"] for child in term.children if isinstance(child, nodes.Element)
    ] == [
        ["bfl-name"],
        ["bfl-punct"],
        ["bfl-type"],
        ["bfl-punct"],
        ["bfl-default"],
    ]
    assert term.astext() == "a: int = 1"


def test_block_content(build: Build):
    """
    Block content is added directly to the definition rather than nested in a paragraph.
    """
    result = build(
        """\
        .. py:function:: f(a)

           :param a: First paragraph.

              Second paragraph.

              - Bullet
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]
    definition = next(field.findall(nodes.definition))

    assert [type(child) for child in definition.children] == [
        nodes.paragraph,
        nodes.paragraph,
        nodes.bullet_list,
    ]
    assert not list(definition.findall(nodes.inline))


def test_inline_content(build: Build):
    """
    Inline content is wrapped in a single paragraph.
    """
    result = build(
        """\
        .. py:function:: f(a)

           :param a: Some ``code`` and *emphasis*
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]
    definition = next(field.findall(nodes.definition))

    assert len(definition.children) == 1
    paragraph = definition.children[0]
    assert isinstance(paragraph, nodes.paragraph)
    assert paragraph.astext() == "Some code and emphasis"
    assert len(list(paragraph.findall(nodes.literal))) == 1


def test_no_content(build: Build):
    """
    A field without content gets an empty definition.
    """
    result = build(
        """\
        .. py:function:: f(a)

           :param a:
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("a: Unknown", "")]


def test_explicit_types(build: Build):
    """
    Types given by `:type:` or inline in `:param:` are included in the term.
    """
    result = build(
        """\
        .. py:function:: f(a, b)

           :param a: A
           :type a: int
           :param str b: B
        """,
        better_fieldlist_signature_types=False,
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("a: int", "A"), ("b: str", "B")]

    # simple types are cross-referenced
    xrefs = list(field.findall(nodes.term))[0].findall(nodes.Element)
    assert any(xref.get("reftarget") == "int" for xref in xrefs)


def test_c_domain(build: Build):
    """
    Domains without an adapter are converted, but not filled in from signatures.
    """
    result = build(
        """\
        .. c:function:: int sum(int a, int b)

           :param a: First operand
           :param b: Second operand
           :returns: Sum of operands
        """
    )
    fields = get_fields(result.get_desc("sum"))

    assert get_items(fields["Parameters"]) == [
        ("a", "First operand"),
        ("b", "Second operand"),
    ]

    # returns is left as-is
    body = fields["Returns"].children[1]
    assert isinstance(body.children[0], nodes.paragraph)
    assert not result.warnings


def test_domains(build: Build):
    """
    Only the configured domains are converted.
    """
    result = build(
        """\
        .. py:function:: f(a)

           :param a: A

        .. c:function:: int g(int b)

           :param b: B
        """,
        better_fieldlist_domains=["c"],
    )

    py_body = get_fields(result.get_desc("f"))["Parameters"].children[1]
    assert isinstance(py_body.children[0], nodes.paragraph)

    assert get_items(get_fields(result.get_desc("g"))["Parameters"]) == [("b", "B")]


def test_exclude_fields(build: Build):
    """
    Excluded fields are left as Sphinx renders them.
    """
    result = build(SOURCE, better_fieldlist_exclude_fields=["py:exceptions"])
    fields = get_fields(result.get_desc("f"))

    raises_body = fields["Raises"].children[1]
    assert isinstance(raises_body.children[0], nodes.bullet_list)

    get_items(fields["Parameters"])


def test_not_loaded(build: Build):
    """
    Fields are rendered as usual in a build without the extension, even though Sphinx's
    doc field types are patched process-wide.
    """
    restructure.install()

    result = build(SOURCE, extensions=[])
    fields = get_fields(result.get_desc("f"))

    body = fields["Parameters"].children[1]
    assert isinstance(body.children[0], nodes.bullet_list)
    assert not list(result.get_doctree().findall(nodes.definition_list))


def test_temp_attrs_removed(build: Build):
    """
    Attributes used while reading aren't persisted.
    """
    doctree = build(SOURCE).get_doctree()

    for node in doctree.findall(nodes.Element):
        assert "better_fieldlist_kind" not in node
        assert "better_fieldlist_arg" not in node


def test_overridden_make_field(build: Build):
    """
    Doc field types which override `make_field()` are left as-is, even if they call the
    base implementation.
    """
    result = build(
        """\
        .. py:myfunction:: f(a)

           :param a: A
        """,
        modules={
            "ext": """\
                from sphinx.domains.python import PyFunction, PyTypedField


                class MyTypedField(PyTypedField):
                    def make_field(self, *args, **kwargs):
                        return super().make_field(*args, **kwargs)


                class MyFunction(PyFunction):
                    doc_field_types = [
                        MyTypedField(
                            "parameter", label="Parameters", names=("param",)
                        ),
                    ]


                def setup(app):
                    app.add_directive_to_domain("py", "myfunction", MyFunction)
                """
        },
        extensions=["sphinx_better_fieldlist", "ext"],
    )
    body = get_fields(result.get_desc("f"))["Parameters"].children[1]

    assert isinstance(body.children[0], nodes.bullet_list)
    assert not list(body.findall(nodes.definition_list))
