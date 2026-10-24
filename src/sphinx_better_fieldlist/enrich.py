"""
Stage 2: fill in field lists from signatures once a document is read.

For each object description of a supported domain:

- Add types and defaults from the signature to parameter terms
- Convert the "Returns" field to a definition list whose term is the return type
- Add xrefs to default values in the signature

Signatures may have been modified by other extensions by this point, so copies reflect
those modifications.
"""

from __future__ import annotations

from typing import Iterable

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.locale import __
from sphinx.util import logging

from ._nodes import (
    ATTR_ARG,
    ATTR_FALLBACK,
    ATTR_KIND,
    CLASS_DEFAULT,
    CLASS_LIST,
    CLASS_TYPE,
    CLASS_UNKNOWN,
    TEMP_ATTRS,
    make_definition,
    make_inline,
    make_punct,
)
from .adapters.base import SignatureAdapter, SignatureParam, SignatureParams
from .adapters.registry import get_adapter
from .config import Config, get_config

__all__ = [
    "process_doctree",
    "resolve_fallback",
]

logger = logging.getLogger(__name__)


def process_doctree(app: Sphinx, doctree: nodes.document):
    """
    Handler for `doctree-read`.
    """
    config = get_config(app.config)

    for desc in doctree.findall(addnodes.desc):
        if (adapter := get_adapter(desc.get("domain", ""))) is not None:
            _Desc(desc, adapter, config).process()

    # remove attributes which are only needed while reading
    for node in doctree.findall(_has_temp_attrs):
        assert isinstance(node, nodes.Element)
        for attr in TEMP_ATTRS:
            if attr in node:
                del node[attr]


def resolve_fallback(
    app: Sphinx,
    env: BuildEnvironment,
    node: addnodes.pending_xref,
    contnode: nodes.TextElement,
) -> nodes.Node | None:
    """
    Handler for `missing-reference`: render unresolved xrefs created by this extension
    as their content, without a warning.
    """
    if node.get(ATTR_FALLBACK):
        return contnode
    return None


class _Desc:
    """
    Processes a single object description.
    """

    desc: addnodes.desc
    adapter: SignatureAdapter
    config: Config

    signatures: list[addnodes.desc_signature]

    def __init__(self, desc: addnodes.desc, adapter: SignatureAdapter, config: Config):
        self.desc = desc
        self.adapter = adapter
        self.config = config
        self.signatures = [
            child
            for child in desc.children
            if isinstance(child, addnodes.desc_signature)
        ]

    def process(self):
        for signature in self.signatures:
            self.adapter.process_signature(signature, self.config.xref_defaults)

        fields = list(self._get_fields())
        domain = self.adapter.domain

        if self.config.signature_types or self.config.signature_defaults:
            params = self._get_params()

            for field in fields:
                if field[ATTR_KIND] in {
                    f"{domain}:{name}" for name in self.adapter.param_fields
                }:
                    self._process_params(field, params)

        if (
            self.config.signature_types
            and self.config.merge_rtype
            and self.adapter.return_field is not None
        ):
            return_kind = f"{domain}:{self.adapter.return_field}"
            rtype_kind = f"{domain}:{self.adapter.rtype_field}"

            return_fields = [f for f in fields if f[ATTR_KIND] == return_kind]
            rtype_fields = [f for f in fields if f[ATTR_KIND] == rtype_kind]

            # merge "Return type" if unambiguous
            rtype_field = rtype_fields[0] if len(rtype_fields) == 1 else None

            for return_field in return_fields:
                self._process_return(return_field, rtype_field)
                rtype_field = None

    def _get_fields(self) -> Iterable[nodes.field]:
        """
        Get fields created by doc field types for this description, excluding those of
        nested descriptions.
        """
        content = next(
            (
                child
                for child in self.desc.children
                if isinstance(child, addnodes.desc_content)
            ),
            None,
        )
        if content is None:
            return

        # Sphinx only transforms field lists which are immediate children
        for field_list in content.children:
            if isinstance(field_list, nodes.field_list):
                for field in field_list.children:
                    if isinstance(field, nodes.field) and ATTR_KIND in field:
                        yield field

    def _get_params(self) -> list[SignatureParams] | None:
        """
        Get parameters of each signature, or `None` if any can't be read.
        """
        if not self.signatures:
            return None

        params = [self.adapter.get_params(sig) for sig in self.signatures]
        if any(p is None for p in params):
            return None

        return [p for p in params if p is not None]

    def _process_params(
        self, field: nodes.field, sig_params: list[SignatureParams] | None
    ):
        if sig_params is None:
            # can't read signature: leave terms as documented
            return

        for term in field.findall(nodes.term):
            if (arg := term.get(ATTR_ARG)) is None:
                continue

            name = self.adapter.normalize_name(arg)
            matches = [p.params.get(name) for p in sig_params]

            if all(m is None for m in matches):
                if not any(p.has_var_keyword for p in sig_params):
                    logger.warning(
                        __("Documented parameter %r not found in signature of %s"),
                        arg,
                        self._get_name(),
                        type="better_fieldlist",
                        subtype="unmatched_param",
                        location=term,
                    )
                continue

            self._process_term(term, matches)

    def _process_term(self, term: nodes.term, matches: list[SignatureParam | None]):
        has_type = any(
            CLASS_TYPE in child["classes"]
            for child in term.children
            if isinstance(child, nodes.Element)
        )

        # explicitly documented type takes precedence
        if self.config.signature_types and not has_type:
            annotation = _get_common([m.annotation if m else None for m in matches])

            term += make_punct(": ")
            term += self._make_type(annotation)

        if self.config.signature_defaults:
            default = _get_common([m.default if m else None for m in matches])

            if default is not None:
                term += make_punct(" = ")
                term += make_inline(CLASS_DEFAULT, *_copy(default))

    def _process_return(
        self, return_field: nodes.field, rtype_field: nodes.field | None
    ):
        field_body = return_field.children[1]
        assert isinstance(field_body, nodes.field_body)

        type_nodes: list[nodes.Node] | None
        if rtype_field is not None:
            # move content of "Return type" and remove it
            rtype_body = rtype_field.children[1]
            assert isinstance(rtype_body, nodes.field_body)

            type_nodes = list(_unwrap_paragraph(rtype_body.children))
            for node in type_nodes:
                node.parent.remove(node)

            rtype_field.parent.remove(rtype_field)
        elif self.signatures:
            returns = [self.adapter.get_return(sig) for sig in self.signatures]
            common = _get_common(returns)
            type_nodes = _copy(common) if common is not None else None
        else:
            type_nodes = None

        type_node = (
            make_inline(CLASS_TYPE, *type_nodes)
            if type_nodes is not None
            else self._make_type(None)
        )

        content = list(_unwrap_paragraph(field_body.children))
        for node in content:
            node.parent.remove(node)

        deflist = nodes.definition_list(
            "",
            nodes.definition_list_item(
                "", nodes.term("", "", type_node), make_definition(content)
            ),
            classes=[CLASS_LIST],
        )

        field_body.clear()
        field_body += deflist

    def _make_type(self, annotation: list[nodes.Node] | None) -> nodes.inline:
        if annotation is not None:
            return make_inline(CLASS_TYPE, *_copy(annotation))

        inline = make_inline(CLASS_TYPE, self.adapter.make_unknown())
        inline["classes"].append(CLASS_UNKNOWN)
        return inline

    def _get_name(self) -> str:
        signature = self.signatures[0]
        if not (fullname := signature.get("fullname")):
            return signature.astext()
        if module := signature.get("module"):
            return f"{module}.{fullname}"
        return fullname


def _get_common(
    candidates: list[list[nodes.Node] | None],
) -> list[nodes.Node] | None:
    """
    Get nodes if every candidate is present and has the same text, otherwise `None`.
    """
    if not candidates or any(c is None for c in candidates):
        return None

    texts = {_get_text(c) for c in candidates if c is not None}
    return candidates[0] if len(texts) == 1 else None


def _get_text(node_list: list[nodes.Node]) -> str:
    return "".join(node.astext() for node in node_list)


def _copy(node_list: list[nodes.Node]) -> list[nodes.Node]:
    return [node.deepcopy() for node in node_list]


def _unwrap_paragraph(children: list[nodes.Node]) -> list[nodes.Node]:
    """
    Get content of a field body, unwrapping the paragraph created by Sphinx.
    """
    if len(children) == 1 and isinstance(children[0], nodes.paragraph):
        return list(children[0].children)
    return list(children)


def _has_temp_attrs(node: nodes.Node) -> bool:
    return isinstance(node, nodes.Element) and any(attr in node for attr in TEMP_ATTRS)
