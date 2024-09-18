from __future__ import annotations

import re
from functools import cache, partial
from itertools import chain
from typing import Any

import nox

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


@cache
def load_dev_dependencies() -> list[str]:
    project: dict[str, Any] = nox.project.load_toml("pyproject.toml")["project"]

    optional_dependencies: dict[str, list[str]] = project["optional-dependencies"]

    return optional_dependencies["dev"]


def match_dev_dependencies(*patterns: str) -> list[str]:
    dev_dependencies = load_dev_dependencies()

    return list(
        chain.from_iterable(
            filter(partial(re.match, pattern), dev_dependencies) for pattern in patterns
        ),
    )


nox.options.sessions = ["ruff", "mypy", "pytest"]


@nox.session(tags=["build"])
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
    session.install("build")

    session.run("python", "-m", "build")
    session.run("rm", "-rf", "dist", external=True)


@nox.session(tags=["lint"])
@nox.parametrize(
    "command",
    [
        "check",
        "format",
    ],
)
def ruff(session: nox.Session, command: str) -> None:
    session.install(
        *match_dev_dependencies(
            r"^ruff ~=",
        ),
    )

    extra_options = session.posargs or []

    session.run("ruff", command, *extra_options, ".")


@nox.session(tags=["lint"])
def mypy(session: nox.Session) -> None:
    session.install(
        *match_dev_dependencies(
            r"^django\-stubs\[compatible-mypy\] ~=",
        ),
        "-e",
        ".",
    )

    extra_options = session.posargs or ["--ignore-missing-imports"]

    session.run("mypy", *extra_options, ".")


@nox.session(tags=["test"])
@nox.parametrize(
    ("django", "python"),
    [
        (django, python)
        for django, pythons in DJANGO_PYTHONS.items()
        for python in pythons
    ],
)
def pytest(session: nox.Session, django: str) -> None:
    session.install(
        *match_dev_dependencies(
            r"^pytest(-[\w\-]+)? ~=",
        ),
        f"django == {django}.*",
        "-e",
        ".",
    )

    extra_options = session.posargs or []

    session.run("pytest", *extra_options)
