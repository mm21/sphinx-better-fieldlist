from pyprojkit import (
    ProjectConfig,
    PythonVersions,
    RequiresPython,
    create_recommended_tools,
)

config = ProjectConfig(
    packages="sphinx_better_fieldlist",
    requires_python=RequiresPython((3, 13)),
    pinned_python=PythonVersions(3, (13, 14)),
    tools=create_recommended_tools(),
    typed=True,
)
