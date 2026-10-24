"""
Interface for reading a domain's signatures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from docutils import nodes
from sphinx import addnodes

__all__ = [
    "SignatureParam",
    "SignatureParams",
    "SignatureAdapter",
]


@dataclass(kw_only=True)
class SignatureParam:
    """
    Parameter read from a signature.
    """

    name: str
    """
    Name without any `*`/`**` prefix.
    """

    annotation: list[nodes.Node] | None = None
    """
    Nodes making up the annotation, if any; owned by the signature.
    """

    default: list[nodes.Node] | None = None
    """
    Nodes making up the default value, if any; owned by the signature.
    """

    is_var_keyword: bool = False
    """
    Whether this is a variadic keyword parameter, e.g. `**kwargs`.
    """


@dataclass(kw_only=True)
class SignatureParams:
    """
    Parameters read from a signature.
    """

    params: dict[str, SignatureParam] = field(default_factory=dict)
    """
    Mapping of parameter name to parameter.
    """

    @property
    def has_var_keyword(self) -> bool:
        """
        Whether there's a variadic keyword parameter, which accepts arguments not in the
        signature.
        """
        return any(param.is_var_keyword for param in self.params.values())


class SignatureAdapter(ABC):
    """
    Reads parameters and return types from a domain's signatures.
    """

    domain: str
    """
    Name of domain, e.g. `"py"`.
    """

    param_fields: frozenset[str]
    """
    Field types documenting the signature's parameters, e.g. `"parameter"`.
    """

    return_field: str | None = None
    """
    Field type documenting the return value, if any.
    """

    rtype_field: str | None = None
    """
    Field type documenting the return type, if any.
    """

    @abstractmethod
    def get_params(self, signature: addnodes.desc_signature) -> SignatureParams | None:
        """
        Get parameters from signature, or `None` if they can't be read (e.g. there's no
        parameter list).
        """

    @abstractmethod
    def get_return(self, signature: addnodes.desc_signature) -> list[nodes.Node] | None:
        """
        Get nodes making up the return type, or `None` if not annotated.
        """

    @abstractmethod
    def make_unknown(self) -> nodes.Node:
        """
        Create node representing a type which isn't documented.
        """

    def process_signature(
        self, signature: addnodes.desc_signature, xref_defaults: bool
    ):
        """
        Hook to modify signature before its nodes are copied.
        """

    def normalize_name(self, name: str) -> str:
        """
        Normalize a documented argument name for lookup in the signature.
        """
        return name
