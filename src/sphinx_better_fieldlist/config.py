"""
Extension configuration, registered with Sphinx as `better_fieldlist_*` values.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from types import NoneType
from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config as SphinxConfig

__all__ = [
    "PREFIX",
    "Config",
    "register_config",
    "get_config",
]

PREFIX = "better_fieldlist_"
"""
Prefix of each config value as set in `conf.py`.
"""


@dataclass(frozen=True, kw_only=True)
class Config:
    """
    Container for config values; each field `name` is set in `conf.py` as
    `better_fieldlist_<name>`.
    """

    domains: list[str] | None = field(
        default=None, metadata={"types": (list, tuple, NoneType)}
    )
    """
    Domains whose field lists are converted to definition lists, e.g. `["py"]`; `None`
    for all domains.
    """

    exclude_fields: list[str] = field(
        default_factory=list, metadata={"types": (list, tuple)}
    )
    """
    Field types to leave as Sphinx renders them, given as `<domain>:<field type>`, e.g.
    `"py:exceptions"`.
    """

    signature_types: bool = field(default=True, metadata={"types": (bool,)})
    """
    Whether to copy parameter and return types from the signature. If disabled, the
    "Returns" field is left as-is regardless of `merge_rtype`.
    """

    signature_defaults: bool = field(default=True, metadata={"types": (bool,)})
    """
    Whether to copy parameter defaults from the signature.
    """

    merge_rtype: bool = field(default=True, metadata={"types": (bool,)})
    """
    Whether to convert the "Returns" field to a definition list whose term is the return
    type, merging in the "Return type" field if present. Requires `signature_types`.
    """

    xref_defaults: bool = field(default=True, metadata={"types": (bool,)})
    """
    Whether to add cross-references to `None`, `True` and `False` defaults.
    """

    css: bool = field(default=True, metadata={"types": (bool,), "rebuild": "html"})
    """
    Whether to add the bundled stylesheet to HTML output.
    """


def register_config(app: Sphinx):
    """
    Register config values with Sphinx.
    """
    for config_field in dataclasses.fields(Config):
        if config_field.default_factory is not dataclasses.MISSING:
            default = config_field.default_factory()
        else:
            default = config_field.default

        app.add_config_value(
            f"{PREFIX}{config_field.name}",
            default,
            config_field.metadata.get("rebuild", "env"),
            types=frozenset(config_field.metadata["types"]),
        )


def get_config(sphinx_config: SphinxConfig) -> Config:
    """
    Get config values from Sphinx's config.
    """
    kwargs: dict[str, Any] = {
        config_field.name: sphinx_config[f"{PREFIX}{config_field.name}"]
        for config_field in dataclasses.fields(Config)
    }
    return Config(**kwargs)
