"""
Directive to disable the extension for its content.
"""

from __future__ import annotations

from docutils import nodes
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective

from ._nodes import ATTR_DISABLED, CLASS_DISABLED, TEMP_DATA_DISABLED

__all__ = [
    "DisableDirective",
]


class DisableDirective(SphinxDirective):
    """
    Renders its content as Sphinx would without this extension, e.g. to show a
    comparison or to opt out specific objects.

    Content is wrapped in a container with class `bfl-disabled`.
    """

    has_content = True

    def run(self) -> list[nodes.Node]:
        # set flag while parsing so fields are rendered by Sphinx; directives in the
        # content (including generated content, e.g. from autodoc) are run as part
        # of parsing
        temp_data = self.env.temp_data
        depth: int = temp_data.get(TEMP_DATA_DISABLED) or 0
        temp_data[TEMP_DATA_DISABLED] = depth + 1

        try:
            children = self.parse_content_to_nodes()
        finally:
            if depth:
                temp_data[TEMP_DATA_DISABLED] = depth
            else:
                del temp_data[TEMP_DATA_DISABLED]

        container = nodes.container("", *children, classes=[CLASS_DISABLED])
        self.set_source_info(container)

        # mark descriptions so they're skipped once the document is read
        for desc in container.findall(addnodes.desc):
            desc[ATTR_DISABLED] = True

        return [container]
