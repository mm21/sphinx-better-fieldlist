from dataclasses import replace

from pyprojkit import (
    DocConfig,
    MkinitConfig,
    ProjectConfig,
    PythonVersions,
    RequiresPython,
    SphinxConfig,
    create_recommended_tools,
)

config = ProjectConfig(
    packages="sphinx_better_fieldlist",
    requires_python=RequiresPython((3, 13)),
    pinned_python=PythonVersions(3, (13, 14)),
    tools=replace(
        create_recommended_tools(),
        doc=DocConfig(
            mkinit=MkinitConfig.create_recommended(),
            sphinx=SphinxConfig(copy_env_var="SPHINX_BETTER_FIELDLIST_DOCS_DIR"),
        ),
    ),
    typed=True,
    python_version_file=True,
    uv_build_backend=True,
)
