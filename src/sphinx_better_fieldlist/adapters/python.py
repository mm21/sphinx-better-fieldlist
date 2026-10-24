"""
Adapter for the Python domain.
"""

from __future__ import annotations

import re

from docutils import nodes
from sphinx import addnodes

from .._nodes import ATTR_FALLBACK
from .base import SignatureAdapter, SignatureParam, SignatureParams

__all__ = [
    "PythonAdapter",
]

_UNKNOWN_TEXT = "Unknown"
"""
Text for a type which isn't documented, consistent with static type checkers.
"""

_UNKNOWN_TARGET = "typing.Any"
"""
Target of xref for a type which isn't documented: an unannotated parameter or return is
implicitly `Any`.
"""

_XREF_DEFAULTS = frozenset({"None", "True", "False"})
"""
Default values to add xrefs to.
"""


_TEXT_PARAM = re.compile(r"[:=]")
"""
Matches a parameter given as text with an annotation or default.
"""


class PythonAdapter(SignatureAdapter):
    """
    Reads signatures created by the Python domain.
    """

    domain = "py"
    param_fields = frozenset({"parameter"})
    return_field = "returnvalue"
    rtype_field = "returntype"

    def get_params(self, signature: addnodes.desc_signature) -> SignatureParams | None:
        paramlist = _find_child(signature, addnodes.desc_parameterlist)
        if paramlist is None:
            return None

        params = SignatureParams()

        # traverse rather than iterate children since params may be nested in
        # desc_optional
        for parameter in paramlist.findall(addnodes.desc_parameter):
            if _is_separator(parameter):
                continue
            if (param := _read_param(parameter)) is None:
                # e.g. arglist as text if it couldn't be pseudo-parsed
                return None
            params.params[param.name] = param

        return params

    def get_return(self, signature: addnodes.desc_signature) -> list[nodes.Node] | None:
        returns = _find_child(signature, addnodes.desc_returns)
        if returns is None:
            return None
        return list(returns.children)

    def make_unknown(self) -> nodes.Node:
        return _make_xref(_UNKNOWN_TARGET, _UNKNOWN_TEXT, explicit=True)

    def process_signature(
        self, signature: addnodes.desc_signature, xref_defaults: bool
    ):
        if not xref_defaults:
            return

        for default in signature.findall(nodes.inline):
            if "default_value" not in default["classes"]:
                continue
            if len(default.children) != 1:
                continue

            text = default.children[0]
            if isinstance(text, nodes.Text) and text.astext() in _XREF_DEFAULTS:
                default.replace(text, _make_xref(text.astext(), text))

    def normalize_name(self, name: str) -> str:
        return name.lstrip("*")


def _is_separator(parameter: addnodes.desc_parameter) -> bool:
    """
    Check if parameter is a separator, i.e. "/" or "*".
    """
    return len(parameter.children) == 1 and isinstance(
        parameter.children[0], addnodes.desc_sig_operator
    )


def _read_param(parameter: addnodes.desc_parameter) -> SignatureParam | None:
    children = list(parameter.children)

    name_index = next(
        (
            i
            for i, child in enumerate(children)
            if isinstance(child, addnodes.desc_sig_name)
        ),
        None,
    )
    if name_index is None:
        return None

    raw_name = children[name_index].astext()

    if name_index == len(children) - 1 and _TEXT_PARAM.search(raw_name):
        # pseudo-parsed by Sphinx < 9 as text, e.g. "a: int = 1"
        return _read_text_param(raw_name)

    name = raw_name.lstrip("*")

    # prefix is an operator node if parsed, or part of the name if pseudo-parsed
    prefix = "".join(
        child.astext()
        for child in children[:name_index]
        if isinstance(child, addnodes.desc_sig_operator)
    )
    prefix += raw_name[: len(raw_name) - len(name)]

    param = SignatureParam(name=name, is_var_keyword=prefix == "**")
    rest = children[name_index + 1 :]

    # annotation is the name node following ":"
    for i, child in enumerate(rest):
        if isinstance(child, addnodes.desc_sig_punctuation) and child.astext() == ":":
            annotation = next(
                (c for c in rest[i + 1 :] if isinstance(c, addnodes.desc_sig_name)),
                None,
            )
            if annotation is not None:
                param.annotation = list(annotation.children)
            break

    for child in rest:
        if isinstance(child, nodes.inline) and "default_value" in child["classes"]:
            param.default = [child]
            break

    return param


def _read_text_param(text: str) -> SignatureParam:
    name_annotation, has_default, default = text.partition("=")
    raw_name, has_annotation, annotation = name_annotation.partition(":")
    raw_name = raw_name.strip()
    name = raw_name.lstrip("*")

    return SignatureParam(
        name=name,
        annotation=[nodes.Text(annotation.strip())] if has_annotation else None,
        default=[nodes.Text(default.strip())] if has_default else None,
        is_var_keyword=raw_name.startswith("**"),
    )


def _find_child[T: nodes.Element](
    signature: addnodes.desc_signature, cls: type[T]
) -> T | None:
    return next((child for child in signature.children if isinstance(child, cls)), None)


def _make_xref(
    target: str, content: str | nodes.Text, explicit: bool = False
) -> addnodes.pending_xref:
    text = content if isinstance(content, nodes.Text) else nodes.Text(content)
    xref = addnodes.pending_xref(
        "",
        text,
        refdomain="py",
        reftype="obj",
        reftarget=target,
        refexplicit=explicit,
        refspecific=False,
    )
    xref[ATTR_FALLBACK] = True
    return xref
