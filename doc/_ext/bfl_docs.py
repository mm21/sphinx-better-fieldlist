"""
Sphinx extension for this documentation: before/after examples and the configuration
reference.

Directives generate MyST markup, so they must be used from MyST documents.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import re
from typing import Any, Callable, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.pycode import ModuleAnalyzer
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import ExtensionMetadata

from sphinx_better_fieldlist.config import PREFIX, Config

__all__ = [
    "ExampleDirective",
    "ConfigReferenceDirective",
    "setup",
]

CLASS_EXAMPLE = "bfl-example"
"""
Class of the container holding an example.
"""

_RST_NO_INDEX = re.compile(r"^(?P<indent>\s*)\.\. (auto\w+|py:\w+)::.*$")
"""
Matches an rst directive which accepts `:no-index:`.
"""

_MYST_NO_INDEX = re.compile(r"^\s*(`{3,}|:{3,})\{(auto\w+|py:\w+)\}.*$")
"""
Matches a MyST directive which accepts `:no-index:`.
"""

_MYST_AUTODOC2 = re.compile(r"^\s*(`{3,}|:{3,})\{autodoc2-object\}.*$")
"""
Matches a MyST `autodoc2-object` directive, whose content is TOML.
"""

_RST_C = re.compile(r"^\s*\.\. c:\w+::", re.MULTILINE)
_MYST_C = re.compile(r"^\s*(`{3,}|:{3,})\{c:\w+\}", re.MULTILINE)

_C_NAMESPACE = "before"
"""
Namespace of C declarations in the "before" copy, since C directives don't support
`:no-index:`.
"""

_CONFIG_NAME = re.compile(r"`(\w+)`")
"""
Matches a config field name in a docstring.
"""


class ExampleDirective(SphinxDirective):
    """
    Renders an example's source, followed by its content as rendered without the
    extension ("Before") and with it ("After").

    The "before" copy is not indexed, to avoid duplicate object warnings; with
    `:no-index:`, neither is the "after" copy, e.g. for objects documented elsewhere.
    The displayed source omits options added to avoid indexing.
    """

    has_content = True
    option_spec: ClassVar[dict[str, Callable[[str], Any]] | None] = {
        "pyobject": directives.unchanged_required,
        "syntax": lambda arg: directives.choice(arg, ("myst", "rst")),
        "no-index": directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        syntax = self.options.get("syntax", "myst")
        content = "\n".join(self.content)

        if pyobject := self.options.get("pyobject"):
            source, language = _get_python_source(pyobject.split()), "python"
        else:
            source, language = content, "markdown" if syntax == "myst" else "rst"

        literal = nodes.literal_block(source, source, language=language)

        before = _add_no_index(content, syntax)
        after = (
            _add_no_index(content, syntax) if "no-index" in self.options else content
        )
        if syntax == "rst":
            before, after = _wrap_rst(before), _wrap_rst(after)

        container = nodes.container("", literal, classes=[CLASS_EXAMPLE])
        container += nodes.rubric("", "Before")
        container += self.parse_text_to_nodes(_wrap_disable(before))
        container += nodes.rubric("", "After")
        container += self.parse_text_to_nodes(after)
        self.set_source_info(container)

        return [container]


class ConfigReferenceDirective(SphinxDirective):
    """
    Renders a `confval` for each config value, documented by the docstrings of the
    `Config` dataclass.
    """

    def run(self) -> list[nodes.Node]:
        analyzer = ModuleAnalyzer.for_module(Config.__module__)
        attr_docs = analyzer.find_attr_docs()
        names = {config_field.name for config_field in dataclasses.fields(Config)}

        def link(match: re.Match[str]) -> str:
            name = match.group(1)
            return f"{{confval}}`{PREFIX}{name}`" if name in names else match.group(0)

        blocks: list[str] = []
        for config_field in dataclasses.fields(Config):
            if config_field.default_factory is not dataclasses.MISSING:
                default = config_field.default_factory()
            else:
                default = config_field.default

            doc = "\n".join(attr_docs[(Config.__name__, config_field.name)]).strip()
            blocks.append(
                "\n".join(
                    [
                        f"```{{confval}} {PREFIX}{config_field.name}",
                        f":type: `{config_field.type}`",
                        f":default: `{default!r}`",
                        "",
                        _CONFIG_NAME.sub(link, doc),
                        "```",
                    ]
                )
            )

        return self.parse_text_to_nodes("\n\n".join(blocks))


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive("bfl-example", ExampleDirective)
    app.add_directive("bfl-config-reference", ConfigReferenceDirective)

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _get_python_source(names: list[str]) -> str:
    """
    Get source of each top-level object given by its qualified name, including any
    overloads and decorators.
    """
    sources: list[str] = []

    for name in names:
        module_name, _, obj_name = name.rpartition(".")
        module_source = inspect.getsource(importlib.import_module(module_name))
        lines = module_source.splitlines()

        spans = [
            (
                min([node.lineno, *(d.lineno for d in node.decorator_list)]),
                node.end_lineno or node.lineno,
            )
            for node in ast.parse(module_source).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            and node.name == obj_name
        ]
        assert spans, f"Object not found: {name}"

        start = min(span[0] for span in spans)
        end = max(span[1] for span in spans)
        sources.append("\n".join(lines[start - 1 : end]))

    return "\n\n\n".join(sources)


def _add_no_index(content: str, syntax: str) -> str:
    """
    Add options to directives so the objects they describe aren't indexed.
    """
    lines: list[str] = []

    for line in content.splitlines():
        lines.append(line)

        if syntax == "rst":
            if match := _RST_NO_INDEX.match(line):
                lines.append(f"{match.group('indent')}   :no-index:")
        elif _MYST_NO_INDEX.match(line):
            lines.append(":no-index:")
        elif _MYST_AUTODOC2.match(line):
            lines.append("no_index = true")

    result = "\n".join(lines)

    if syntax == "rst" and _RST_C.search(result):
        result = (
            f".. c:namespace-push:: {_C_NAMESPACE}\n\n{result}\n\n"
            ".. c:namespace-pop::"
        )
    elif syntax == "myst" and _MYST_C.search(result):
        result = (
            f"```{{c:namespace-push}} {_C_NAMESPACE}\n```\n\n{result}\n\n"
            "```{c:namespace-pop}\n```"
        )

    return result


def _wrap_rst(content: str) -> str:
    fence = _get_fence(content, "`")
    return f"{fence}{{eval-rst}}\n{content}\n{fence}"


def _wrap_disable(content: str) -> str:
    fence = _get_fence(content, "`")
    return f"{fence}{{better-fieldlist-disable}}\n\n{content}\n{fence}"


def _get_fence(content: str, char: str) -> str:
    """
    Get a fence longer than any in the content.
    """
    longest = max(
        (len(run) for run in re.findall(rf"{re.escape(char)}+", content)), default=0
    )
    return char * max(3, longest + 1)
