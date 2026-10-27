"""
Extension configuration, registered with Sphinx as `better_fieldlist_*` values.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from types import NoneType

from sphinx.application import Sphinx

__all__ = [
    "PREFIX",
    "Config",
    "register_config",
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
