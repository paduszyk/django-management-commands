from __future__ import annotations

import nox
import nox_uv

DJANGO_PYTHONS = {
    "4.2": [
        "3.9",
        "3.10",
        "3.11",
        "3.12",
    ],
    "5.0": [
        "3.10",
        "3.11",
        "3.12",
    ],
    "5.1": [
        "3.10",
        "3.11",
        "3.12",
    ],
}

nox.options.sessions = ["ruff", "mypy", "pytest"]


@nox_uv.session(venv_backend="uv", tags=["build"])
@nox.parametrize(
    "python",
    [
        "3.9",
        "3.10",
        "3.11",
        "3.12",
    ],
)
def build(session: nox.Session) -> None:
    session.run("uv", "build")
    session.run("rm", "-rf", "dist", external=True)


@nox_uv.session(venv_backend="uv", uv_only_groups=["ruff"], tags=["lint"])
@nox.parametrize(
    "command",
    [
        "check",
        "format",
    ],
)
def ruff(session: nox.Session, command: str) -> None:
    extra_options = session.posargs or []

    session.run("ruff", command, *extra_options, ".")


@nox_uv.session(venv_backend="uv", uv_only_groups=["mypy"], tags=["lint"])
def mypy(session: nox.Session) -> None:
    extra_options = session.posargs or ["--ignore-missing-imports"]

    session.run("mypy", *extra_options, ".")


@nox_uv.session(venv_backend="uv", uv_groups=["pytest"], tags=["test"])
@nox.parametrize(
    ("django", "python"),
    [
        (django, python)
        for django, pythons in DJANGO_PYTHONS.items()
        for python in pythons
    ],
)
def pytest(session: nox.Session, django: str) -> None:
    session.install(f"django == {django}.*")

    extra_options = session.posargs or []

    session.run("pytest", *extra_options)
