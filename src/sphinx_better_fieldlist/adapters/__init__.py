"""
Adapters to read signatures of supported domains.
"""

__submodules__ = [
    "base",
    "python",
    "registry",
]

# isort: off
# <AUTOGEN_INIT>
from .base import (
    SignatureParam,
    SignatureParams,
    SignatureAdapter,
)
from .python import (
    PythonAdapter,
)
from .registry import (
    get_adapter,
)

__all__ = [
    "SignatureParam",
    "SignatureParams",
    "SignatureAdapter",
    "PythonAdapter",
    "get_adapter",
]
# </AUTOGEN_INIT>
