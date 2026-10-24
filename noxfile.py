import nox
from nox import Session
from pyprojkit import NoxFactory, load_config

test = NoxFactory().create_test_session()

_SPHINX_COMPAT: dict[str, list[str]] = {
    "8.2": ["sphinx~=8.2.0"],
    "7.4": ["sphinx~=7.4.0", "myst-parser~=4.0.0"],
}
"""
Older Sphinx versions supported on a best-effort basis, with requirements to install
over the locked environment; snapshot tests are skipped for these.
"""

_versions = load_config().pinned_versions
assert _versions is not None


@nox.session(python=[_versions.patch(v) for v in _versions.versions])
@nox.parametrize("sphinx", list(_SPHINX_COMPAT))
def compat(session: Session, sphinx: str):
    """
    Run tests with an older Sphinx version.
    """
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install(
        "uv",
        "sync",
        "--group=dev",
        "--frozen",
        f"--python={session.python}",
        env=env,
        external=True,
    )
    session.run_install(
        "uv",
        "pip",
        "install",
        f"--python={session.virtualenv.location}",
        *_SPHINX_COMPAT[sphinx],
        env=env,
        external=True,
    )
    session.run("pytest", *session.posargs)
