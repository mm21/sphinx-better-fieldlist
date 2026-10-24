"""
Stage 1: create definition lists for grouped doc fields.

Wraps `make_field()` of Sphinx's doc field types, which receive each field's argument,
content and explicitly documented type. Grouped fields (e.g. "Parameters", "Raises") are
created as definition lists rather than bullet lists, and every field is tagged with its
kind so it can be found once the document is read.
"""

from __future__ import annotations

import functools
from typing import Any, Callable

from docutils import nodes
from docutils.nodes import Element, Node
from docutils.utils import get_source_line
from sphinx import addnodes
from sphinx.environment import BuildEnvironment
from sphinx.util.docfields import Field, GroupedField, TypedField

from ._nodes import (
    ATTR_ARG,
    ATTR_KIND,
    CLASS_LIST,
    CLASS_NAME,
    CLASS_TYPE,
    make_definition,
    make_inline,
    make_punct,
)
from .config import PREFIX

__all__ = [
    "install",
]

type _MakeField = Callable[..., nodes.field]

_MARKER = "_better_fieldlist_wrapped"
"""
Set on wrapped methods to make installation idempotent.
"""


def install():
    """
    Wrap `make_field()` of Sphinx's doc field types.

    This is process-wide; wrappers defer to the original method unless the extension is
    loaded for the build environment passed in.
    """
    for cls, wrapper in (
        (Field, None),
        (GroupedField, _make_grouped_field),
        (TypedField, _make_typed_field),
    ):
        orig = cls.__dict__["make_field"]
        if getattr(orig, _MARKER, False):
            continue
        setattr(cls, "make_field", _wrap(cls, orig, wrapper))


def _wrap(cls: type[Field], orig: _MakeField, convert: _MakeField | None) -> _MakeField:
    @functools.wraps(orig)
    def make_field(
        self: Field,
        types: dict[str, list[Node]],
        domain: str,
        items: Any,
        env: BuildEnvironment | None = None,
        inliner: Any = None,
        location: Element | None = None,
    ) -> nodes.field:
        if env is None or f"{PREFIX}domains" not in env.config:
            # extension not loaded for this environment
            return orig(self, types, domain, items, env, inliner, location)

        kind = f"{domain}:{self.name}"

        if convert is not None and _is_converted(self, cls, domain, kind, env):
            field = convert(self, types, domain, items, env, inliner, location)
        else:
            field = orig(self, types, domain, items, env, inliner, location)

        field[ATTR_KIND] = kind
        return field

    setattr(make_field, _MARKER, True)
    return make_field


def _is_converted(
    field_type: Field,
    cls: type[Field],
    domain: str,
    kind: str,
    env: BuildEnvironment,
) -> bool:
    """
    Check whether this field should be converted to a definition list.
    """
    # leave subclasses which override make_field() as-is since they may expect
    # Sphinx's structure
    for base in type(field_type).__mro__:
        if base is cls:
            break
        if "make_field" in base.__dict__:
            return False

    domains = env.config[f"{PREFIX}domains"]
    exclude_fields = env.config[f"{PREFIX}exclude_fields"]

    if domains is not None and domain not in domains:
        return False
    return kind not in exclude_fields


def _make_grouped_field(
    self: GroupedField,
    types: dict[str, list[Node]],
    domain: str,
    items: list[tuple[str, list[Node]]],
    env: BuildEnvironment,
    inliner: Any,
    location: Element | None,
) -> nodes.field:
    deflist = _make_deflist()

    for fieldarg, content in items:
        name = self.make_xrefs(
            self.rolename,
            domain,
            fieldarg,
            addnodes.literal_strong,
            env=env,
            inliner=inliner,
            location=location,
        )
        term = _make_term(fieldarg, name, location)
        deflist += nodes.definition_list_item("", term, make_definition(content))

    return _make_field_node(self, deflist)


def _make_typed_field(
    self: TypedField,
    types: dict[str, list[Node]],
    domain: str,
    items: list[tuple[str, list[Node]]],
    env: BuildEnvironment,
    inliner: Any,
    location: Element | None,
) -> nodes.field:
    deflist = _make_deflist()

    for fieldarg, content in items:
        # same as Sphinx: only env is passed when creating the argument's xref
        name = self.make_xrefs(
            self.rolename, domain, fieldarg, addnodes.literal_strong, env=env
        )
        term = _make_term(fieldarg, name, location)

        if fieldarg in types:
            # pop to avoid inserting the same nodes twice, as Sphinx does
            fieldtype = types.pop(fieldarg)

            if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                fieldtype = self.make_xrefs(
                    self.typerolename,
                    domain,
                    fieldtype[0].astext(),
                    addnodes.literal_emphasis,
                    env=env,
                    inliner=inliner,
                    location=location,
                )

            term += make_punct(": ")
            term += make_inline(CLASS_TYPE, *fieldtype)

        deflist += nodes.definition_list_item("", term, make_definition(content))

    return _make_field_node(self, deflist)


def _make_deflist() -> nodes.definition_list:
    return nodes.definition_list(classes=[CLASS_LIST])


def _make_term(fieldarg: str, name: list[Node], location: Element | None) -> nodes.term:
    term = nodes.term("", "", make_inline(CLASS_NAME, *name))
    term[ATTR_ARG] = fieldarg

    if location is not None:
        term.source, term.line = get_source_line(location)

    return term


def _make_field_node(
    field_type: GroupedField, deflist: nodes.definition_list
) -> nodes.field:
    return nodes.field(
        "",
        nodes.field_name("", field_type.label),
        nodes.field_body("", deflist),
    )
