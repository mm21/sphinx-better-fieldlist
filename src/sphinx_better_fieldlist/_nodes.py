"""
Node attributes and helpers shared between stages.
"""

from __future__ import annotations

from typing import Iterable

from docutils import nodes

ATTR_KIND = "better_fieldlist_kind"
"""
Set on a `field` created by a doc field type: `<domain>:<field type>`, e.g.
`"py:parameter"`. Removed once processing is complete.
"""

ATTR_ARG = "better_fieldlist_arg"
"""
Set on a `term` created for a field argument: the argument as documented, e.g. `"a"`.
Removed once processing is complete.
"""

ATTR_FALLBACK = "better_fieldlist_fallback"
"""
Set on a `pending_xref` created by this extension: if it can't be resolved, its content
is rendered as-is without a warning.
"""

TEMP_ATTRS = (ATTR_KIND, ATTR_ARG)
"""
Attributes which are only used while reading a document.
"""

CLASS_LIST = "bfl-list"
CLASS_NAME = "bfl-name"
CLASS_PUNCT = "bfl-punct"
CLASS_TYPE = "bfl-type"
CLASS_DEFAULT = "bfl-default"
CLASS_UNKNOWN = "bfl-unknown"


def make_definition(content: Iterable[nodes.Node]) -> nodes.definition:
    """
    Create a definition holding a field's content, which is generally a single
    translatable `inline` holding the field body's children.

    Inline content is wrapped in a paragraph. Block content (e.g. multiple paragraphs)
    is added directly: the translatable `inline` is unwrapped by Sphinx's
    `RemoveTranslatableInline` transform, which moves its children to the end of its
    parent, leaving the blocks as children of the definition.
    """
    content = list(content)
    definition = nodes.definition()

    if not any(node.astext().strip() for node in content):
        return definition

    if all(_is_inline(node) for node in content):
        definition += nodes.paragraph("", "", *content)
    else:
        definition.extend(content)

    return definition


def make_inline(cls: str, *children: nodes.Node) -> nodes.inline:
    """
    Create an inline with the given class to hold part of a term.
    """
    return nodes.inline("", "", *children, classes=[cls])


def make_punct(text: str) -> nodes.inline:
    """
    Create punctuation separating parts of a term, e.g. `": "`.
    """
    return make_inline(CLASS_PUNCT, nodes.Text(text))


def _is_inline(node: nodes.Node) -> bool:
    if isinstance(node, nodes.Text):
        return True
    if isinstance(node, nodes.Inline):
        assert isinstance(node, nodes.Element)
        return all(_is_inline(child) for child in node.children)
    return False
