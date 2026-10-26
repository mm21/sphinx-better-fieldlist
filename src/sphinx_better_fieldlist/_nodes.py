"""
Node classes and helpers for creating definition lists.
"""

from __future__ import annotations

from typing import Iterable

from docutils import nodes

TEMP_DATA_DISABLED = "better_fieldlist_disabled"
"""
Key in `env.temp_data` set while parsing the content of a `better-fieldlist-disable`
directive: the nesting depth of such directives.
"""

CLASS_LIST = "bfl-list"
CLASS_NAME = "bfl-name"
CLASS_PUNCT = "bfl-punct"
CLASS_TYPE = "bfl-type"
CLASS_DISABLED = "bfl-disabled"


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
    Create punctuation separating parts of a term, e.g. `" ("`.
    """
    return make_inline(CLASS_PUNCT, nodes.Text(text))


def _is_inline(node: nodes.Node) -> bool:
    if isinstance(node, nodes.Text):
        return True
    if isinstance(node, nodes.Inline):
        assert isinstance(node, nodes.Element)
        return all(_is_inline(child) for child in node.children)
    return False
