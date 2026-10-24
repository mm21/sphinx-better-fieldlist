"""
Registry of adapters by domain.
"""

from __future__ import annotations

from .base import SignatureAdapter
from .python import PythonAdapter

__all__ = [
    "get_adapter",
]

_ADAPTERS: dict[str, SignatureAdapter] = {
    adapter.domain: adapter for adapter in (PythonAdapter(),)
}
"""
Mapping of domain name to adapter.
"""


def get_adapter(domain: str) -> SignatureAdapter | None:
    """
    Get adapter for domain, if supported.
    """
    return _ADAPTERS.get(domain)
