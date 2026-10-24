"""
Helpers for tests.
"""

from __future__ import annotations

import inspect
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import pytest
import sphinx
from docutils import nodes
from sphinx import addnodes
from sphinx.testing.util import SphinxTestApp

SNAPSHOTS_PATH = Path(__file__).parent / "snapshots"

LATEST_SPHINX = (9, 2)
"""
Sphinx version which snapshots are generated with; older versions are only checked
structurally.
"""

requires_latest_sphinx = pytest.mark.skipif(
    sphinx.version_info[:2] < LATEST_SPHINX,
    reason=f"Snapshots require Sphinx >= {'.'.join(map(str, LATEST_SPHINX))}",
)


@dataclass
class BuildResult:
    app: SphinxTestApp

    @property
    def warnings(self) -> str:
        warning = self.app.warning
        assert hasattr(warning, "getvalue")
        return warning.getvalue()

    def get_doctree(self, docname: str = "index") -> nodes.document:
        """
        Get doctree as read, before references are resolved.
        """
        return self.app.env.get_doctree(docname)

    def get_resolved_doctree(self, docname: str = "index") -> nodes.document:
        kwargs: dict[str, Any] = {}
        if "tags" in inspect.signature(self.app.env.get_and_resolve_doctree).parameters:
            kwargs["tags"] = self.app.tags
        return self.app.env.get_and_resolve_doctree(docname, self.app.builder, **kwargs)

    def get_desc(self, fullname: str, docname: str = "index") -> addnodes.desc:
        """
        Get object description by its signature's full name.
        """
        return find_desc(self.get_doctree(docname), fullname)


class Build(Protocol):
    def __call__(
        self,
        source: str,
        *,
        modules: dict[str, str] | None = None,
        files: dict[str, str] | None = None,
        extensions: list[str] | None = None,
        buildername: str = "dummy",
        **confoverrides: Any,
    ) -> BuildResult: ...


def find_desc(doctree: nodes.Node, fullname: str) -> addnodes.desc:
    for desc in doctree.findall(addnodes.desc):
        for signature in desc.children:
            if not isinstance(signature, addnodes.desc_signature):
                continue
            name = signature.get("fullname")
            if module := signature.get("module"):
                name = f"{module}.{name}"
            if fullname in (name, signature.get("fullname")):
                return desc

            # other domains, e.g. C
            desc_name = next(signature.findall(addnodes.desc_name), None)
            if desc_name is not None and desc_name.astext() == fullname:
                return desc
    raise AssertionError(f"Description not found: {fullname}")


def get_fields(desc: addnodes.desc) -> dict[str, nodes.field]:
    """
    Get fields of description (excluding nested descriptions) by name.
    """
    content = desc.children[-1]
    assert isinstance(content, addnodes.desc_content)

    fields: dict[str, nodes.field] = {}
    for field_list in content.children:
        if isinstance(field_list, nodes.field_list):
            for field in field_list.children:
                assert isinstance(field, nodes.field)
                fields[field.children[0].astext()] = field
    return fields


def get_items(field: nodes.field) -> list[tuple[str, str]]:
    """
    Get (term, definition) text for each item of a field converted to a definition list.
    """
    body = field.children[1]
    assert len(body.children) == 1
    deflist = body.children[0]
    assert isinstance(deflist, nodes.definition_list), body.pformat()
    assert "bfl-list" in deflist["classes"]

    items: list[tuple[str, str]] = []
    for item in deflist.children:
        assert isinstance(item, nodes.definition_list_item)
        term, definition = item.children
        assert isinstance(term, nodes.term)
        assert isinstance(definition, nodes.definition)
        items.append((term.astext(), definition.astext()))
    return items


def get_terms(field: nodes.field) -> list[nodes.term]:
    return list(field.findall(nodes.term))


def check_snapshot(name: str, actual: str):
    """
    Compare against snapshot, or update it if `BFL_UPDATE_SNAPSHOTS` is set; see
    "Snapshots" in `README.md`.
    """
    path = SNAPSHOTS_PATH / f"{name}.txt"

    if os.environ.get("BFL_UPDATE_SNAPSHOTS"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual)
        return

    assert path.exists(), f"Snapshot missing, set BFL_UPDATE_SNAPSHOTS=1: {path}"
    assert actual == path.read_text()
