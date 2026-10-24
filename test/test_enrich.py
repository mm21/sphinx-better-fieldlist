"""
Tests for filling in field lists from signatures.
"""

from __future__ import annotations

from pathlib import Path

from bfl_testing import Build, find_desc, get_fields, get_items
from docutils import nodes
from sphinx import addnodes


def test_types_defaults(build: Build):
    result = build(
        """\
        .. py:function:: f(a: int, b, c: int | None = None, d=True)

           :param a: A
           :param b: B
           :param c: C
           :param d: D
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [
        ("a: int", "A"),
        ("b: Unknown", "B"),
        ("c: int | None = None", "C"),
        ("d: Unknown = True", "D"),
    ]
    assert not result.warnings


def test_variadic(build: Build):
    """
    Variadic parameters are matched with or without `*`/`**` prefix, and separators are
    skipped.
    """
    result = build(
        """\
        .. py:function:: f(a: int, /, b: str, *args: int, c: bool, **kwargs: str)

           :param a: A
           :param b: B
           :param args: Args
           :param c: C
           :param \\*\\*kwargs: Kwargs
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [
        ("a: int", "A"),
        ("b: str", "B"),
        ("args: int", "Args"),
        ("c: bool", "C"),
        ("**kwargs: str", "Kwargs"),
    ]


def test_keyword_only_separator(build: Build):
    result = build(
        """\
        .. py:function:: f(a, *, b: int = 1)

           :param b: B
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("b: int = 1", "B")]


def test_pseudo_parsed(build: Build):
    """
    Signatures which can't be parsed as Python are pseudo-parsed by Sphinx; the nodes
    are similar, but `*` prefixes are part of the name and params may be optional.
    """
    result = build(
        """\
        .. py:function:: f(a: int, *args[, b: str = 'x'])

           :param a: A
           :param args: Args
           :param b: B
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [
        ("a: int", "A"),
        ("args: Unknown", "Args"),
        ("b: str = 'x'", "B"),
    ]


def test_explicit_type_precedence(build: Build):
    """
    Explicitly documented types take precedence over the signature, but defaults are
    still added.
    """
    result = build(
        """\
        .. py:function:: f(a: int = 1)

           :param a: A
           :type a: float
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("a: float = 1", "A")]


def test_returns(build: Build):
    result = build(
        """\
        .. py:function:: f() -> list[int]

           :returns: R

        .. py:function:: g()

           :returns: R

        .. py:function:: h() -> int

           :returns: R
           :rtype: str
        """
    )

    assert get_items(get_fields(result.get_desc("f"))["Returns"]) == [
        ("list[int]", "R")
    ]
    assert get_items(get_fields(result.get_desc("g"))["Returns"]) == [("Unknown", "R")]

    # "Return type" takes precedence and is merged
    fields = get_fields(result.get_desc("h"))
    assert get_items(fields["Returns"]) == [("str", "R")]
    assert "Return type" not in fields


def test_returns_block_content(build: Build):
    result = build(
        """\
        .. py:function:: f() -> int

           :returns: First paragraph.

              Second paragraph.
        """
    )
    field = get_fields(result.get_desc("f"))["Returns"]
    definition = next(field.findall(nodes.definition))

    assert [type(child) for child in definition.children] == [
        nodes.paragraph,
        nodes.paragraph,
    ]


def test_rtype_only(build: Build):
    """
    "Return type" without "Returns" is left as-is.
    """
    result = build(
        """\
        .. py:function:: f()

           :rtype: int
        """
    )
    fields = get_fields(result.get_desc("f"))

    assert list(fields) == ["Return type"]
    assert fields["Return type"].children[1].astext() == "int"


def test_multiple_signatures(build: Build):
    """
    Types and defaults are only used if all signatures agree.
    """
    result = build(
        """\
        .. py:function:: f(a: int, b: int = 1, c: int = 1) -> int
                         f(a: int, b: str = 1, c: int = 2) -> str

           :param a: A
           :param b: B
           :param c: C
           :returns: R

        .. py:function:: g(a: int) -> int
                         g(a: int, b: int) -> int

           :param a: A
           :param b: B
           :returns: R
        """
    )

    fields = get_fields(result.get_desc("f"))
    assert get_items(fields["Parameters"]) == [
        ("a: int", "A"),
        ("b: Unknown = 1", "B"),
        ("c: int", "C"),
    ]
    assert get_items(fields["Returns"]) == [("Unknown", "R")]

    # missing from some signatures
    fields = get_fields(result.get_desc("g"))
    assert get_items(fields["Parameters"]) == [("a: int", "A"), ("b: Unknown", "B")]
    assert get_items(fields["Returns"]) == [("int", "R")]

    assert not result.warnings


def test_unmatched(build: Build):
    result = build(
        """\
        .. py:function:: f(a)

           :param b: B

        .. py:function:: g(a, **kwargs)

           :param b: B

        .. py:class:: C

           :param b: B
        """,
        show_warning_types=True,
    )

    assert get_items(get_fields(result.get_desc("f"))["Parameters"]) == [("b", "B")]
    assert get_items(get_fields(result.get_desc("g"))["Parameters"]) == [("b", "B")]
    assert get_items(get_fields(result.get_desc("C"))["Parameters"]) == [("b", "B")]

    # only warn if there's no **kwargs and signature can be read
    warnings = result.warnings.strip().splitlines()
    assert len(warnings) == 1
    assert "index.rst:3: WARNING: Documented parameter 'b' not found" in warnings[0]
    assert "signature of f" in warnings[0]
    assert "[better_fieldlist.unmatched_param]" in warnings[0]


def test_unmatched_suppressed(build: Build):
    result = build(
        """\
        .. py:function:: f(a)

           :param b: B
        """,
        suppress_warnings=["better_fieldlist.unmatched_param"],
    )

    assert not result.warnings


def test_module_qualified_warning(build: Build):
    result = build(
        """\
        .. py:module:: mod

        .. py:function:: f(a)

           :param b: B
        """
    )

    assert "signature of mod.f" in result.warnings


def test_xref_defaults(build: Build):
    result = build(
        """\
        .. py:function:: f(a=None, b=True, c=False, d=1)

           :param a: A
           :param b: B
           :param c: C
           :param d: D
        """
    )
    desc = result.get_desc("f")

    def get_targets(node: nodes.Element) -> list[str]:
        return [xref["reftarget"] for xref in node.findall(addnodes.pending_xref)]

    # signature and copies
    signature = desc.children[0]
    assert isinstance(signature, addnodes.desc_signature)
    assert get_targets(signature) == ["None", "True", "False"]
    assert get_targets(get_fields(desc)["Parameters"]) == [
        "typing.Any",
        "None",
        "typing.Any",
        "True",
        "typing.Any",
        "False",
        "typing.Any",
    ]


def test_config_disabled(build: Build):
    result = build(
        """\
        .. py:function:: f(a: int = None) -> int

           :param a: A
           :param b: B
           :returns: R
        """,
        better_fieldlist_signature_types=False,
        better_fieldlist_signature_defaults=False,
        better_fieldlist_merge_rtype=False,
        better_fieldlist_xref_defaults=False,
    )
    desc = result.get_desc("f")
    fields = get_fields(desc)

    assert get_items(fields["Parameters"]) == [("a", "A"), ("b", "B")]
    assert isinstance(fields["Returns"].children[1].children[0], nodes.paragraph)
    assert "None" not in [
        xref["reftarget"] for xref in desc.children[0].findall(addnodes.pending_xref)
    ]

    # no warnings since the signature isn't used
    assert not result.warnings


def test_signature_types_disabled(build: Build):
    """
    "Returns" and "Return type" are left as-is if signature types are disabled.
    """
    result = build(
        """\
        .. py:function:: f() -> int

           :returns: R
           :rtype: str
        """,
        better_fieldlist_signature_types=False,
    )
    fields = get_fields(result.get_desc("f"))

    assert list(fields) == ["Returns", "Return type"]
    assert isinstance(fields["Returns"].children[1].children[0], nodes.paragraph)
    assert fields["Return type"].children[1].astext() == "str"


def test_signature_defaults_only(build: Build):
    result = build(
        """\
        .. py:function:: f(a: int = 1)

           :param a: A
        """,
        better_fieldlist_signature_types=False,
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("a = 1", "A")]


def test_class(build: Build):
    """
    Class parameters are taken from its own signature, not those of its members.
    """
    result = build(
        """\
        .. py:class:: C(a: int, b: str = 'x')

           :param a: A
           :param b: B

           .. py:method:: m(c: float) -> bool

              :param c: C
              :returns: R
        """
    )

    assert get_items(get_fields(result.get_desc("C"))["Parameters"]) == [
        ("a: int", "A"),
        ("b: str = 'x'", "B"),
    ]

    fields = get_fields(result.get_desc("C.m"))
    assert get_items(fields["Parameters"]) == [("c: float", "C")]
    assert get_items(fields["Returns"]) == [("bool", "R")]


def test_resolve(build: Build, inventory: Path):
    """
    Xrefs created by this extension are resolved via intersphinx.
    """
    result = build(
        """\
        .. py:function:: f(a=True)

           :param a: A
        """,
        extensions=["sphinx.ext.intersphinx", "sphinx_better_fieldlist"],
        intersphinx_mapping={"python": ("https://docs.python.org/3", str(inventory))},
        nitpicky=True,
    )
    doctree = result.get_resolved_doctree()
    field = get_fields(find_desc(doctree, "f"))["Parameters"]

    refs = {ref.astext(): ref["refuri"] for ref in field.findall(nodes.reference)}
    assert refs == {
        "Unknown": "https://docs.python.org/3/library/typing.html#typing.Any",
        "True": "https://docs.python.org/3/library/constants.html#True",
    }
    assert not result.warnings


def test_resolve_fallback(build: Build):
    """
    Unresolved xrefs created by this extension are rendered as text without warnings.
    """
    result = build(
        """\
        .. py:function:: f(a=True)

           :param a: A
        """,
        nitpicky=True,
    )
    doctree = result.get_resolved_doctree()
    field = get_fields(find_desc(doctree, "f"))["Parameters"]

    assert get_items(field) == [("a: Unknown = True", "A")]
    assert not list(field.findall(addnodes.pending_xref))
    assert not result.warnings


def test_unparsed_signature(build: Build):
    """
    A signature which can't be pseudo-parsed is rendered as text by Sphinx, so it can't
    be read and documented params are left as-is without warnings.
    """
    result = build(
        """\
        .. py:function:: f(a[, b)

           :param a: A
           :param b: B
        """
    )
    field = get_fields(result.get_desc("f"))["Parameters"]

    assert get_items(field) == [("a", "A"), ("b", "B")]
    assert not result.warnings
