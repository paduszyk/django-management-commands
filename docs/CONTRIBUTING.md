# Contributing Guide

> **New to Open Source Contributions?**
>
> If this is your first time contributing to an open-source project, we highly recommend
> reviewing the official [GitHub documentation][github-documentation] or other relevant
> resources, such as [First Contributions][first-contributions].

We welcome contributions of all types. Whether you are a beginner or an experienced
developer, you can get involved by:

- opening issues;
- submitting pull requests (PRs);
- participating in discussions on existing issues and PRs.

When opening an issue or a PR, please use our forms and templates to adhere to the
provided guidelines and checklists.

## Issues

We welcome the submission of various types of issues, including:

- bug reports;
- feature requests;
- documentation updates;
- code refactoring and performance improvements.

Please use the specific [form][open-issue] corresponding to each issue type. If
your issue does not match any of the categories above, start with a blank template.

> Regardless of the issue type, you will be asked to confirm that you are familiar
> with this guide and the project's [Code of Conduct](#code-of-conduct), and to
> check that the issue is not a duplicate.

## Pull Requests

### Guidelines for Submitting PRs

To improve the chances of your PR being accepted, please adhere to the following
guidelines:

- **Atomic Changes**: Keep your PR focused on a single change or feature to make
  reviewing easier.

- **Local Validation**: After submission, the CI system will automatically test
  the package and run all necessary checks. However, it is strongly recommended
  to run all tests and Pre-commit checks locally to catch any issues before submitting
  a PR.

  > For more information, see [Nox](#nox) and [Pre-commit](#pre-commit).

- **Test Coverage and Documentation**: Ensure that your changes are thoroughly tested
  and update the documentation where applicable. The project aims for 100% test
  coverage, and we expect the same from all submitted PRs.

  > PRs lacking relevant tests will not be considered for merging.

- **PR Title**: PR titles must follow the [Conventional Commits][conventional-commits]
  specification and use standard commit [types][conventional-commit-types].

- **Commit Messages**: While commit messages are not strictly validated, it is recommended
  to provide a single commit per PR with a message that matches the PR title, in
  line with the "atomicity" principle.

- **Merging Strategy**: This project uses the "Squash and Merge" strategy for PRs.

  > Unlike most open-source projects on GitHub, we do not append the PR number to
  > the squashed commit message.

### Environment Setup

To contribute via a pull request, follow these steps to set up the development environment,
either [locally](#local-development) or through a [Dev Container](#development-in-a-dev-container).
The Dev Container option is strongly recommended as it ensures a consistent development
environment across all contributors.

#### Local Development

1. Fork the repository, clone it to your local machine, and navigate to the project's
   root directory.

2. Install Node packages:

   ```console
   npm ci
   ```

   > Ensure that Node.js is installed. If not, [download][node.js] and install the
   > latest release.

3. Install [`pyenv`][pyenv] and [`pyenv-virtualenv`][pyenv-virtualenv].

4. Install the necessary Python versions, as specified in [`pyproject.toml`][pyproject.toml]:

   ```console
   pyenv install <VERSION>
   ```

5. Create and activate a virtual environment:

   ```console
   pyenv virtualenv venv && pyenv activate venv
   ```

6. Install the package in development mode:

   ```console
   pip install -e ".[dev]"
   ```

7. Install the [Pre-commit][pre-commit] hooks:

   ```console
   pre-commit install --install-hooks
   ```

Once the setup is complete, you can run [Nox][nox] to ensure everything works:

```console
nox
```

> For more details, refer to the [Nox](#nox) section.

#### Development in a Dev Container

1. Ensure [Docker][docker] is installed on your machine.

2. Open the project in an Integrated Development Environment (IDE) that supports
   [Dev Containers][dev-containers].

3. Reopen the project inside the Dev Container when prompted.

This setup will install everything you need automatically, following the steps in
[Local Development](#local-development).

> For more details, please refer to the official Development Containers [documentation][dev-containers]
> and the project's Dev Container [configuration][devcontainer.json].

**Using Visual Studio Code?**

[![Open in VS Code](https://img.shields.io/badge/Dev_Container-open_in_VS_Code-007acc)][open-in-vs-code]

If so, click the badge above to get started!

## Nox

The project uses [Nox][nox] to build, lint, format, and type-check the package,
as well as to run tests across various Python and Django environments and measure
test coverage.

To list all available Nox sessions, run:

```console
nox -l
```

To perform a complete check, run:

```console
nox
```

> For more information, refer to the project's [`noxfile.py`][noxfile.py] and/or
> consult the Nox [documentation][nox].

### Coding Style

To check the Python code quality, format and type annotations, run the sessions
tagged with `lint`:

```console
nox -t lint
```

This will run the [`ruff`][ruff]'s linter and formatter and [`mypy`][mypy] to perform
a strict type-check.

### Tests

The package can be thoroughly tested by running the sessions tagged with `test`:

```console
nox -t test
```

This command will discover and run (via [`pytest`][pytest]) all tests across various
Python and Django environments and measure test coverage.

For quicker runs, you can test the package by running `pytest` directly:

```console
pytest
```

However, this only tests against versions of Python and Django that are pinned to
the active virtual environment. If your PR introduces changes that might affect
compatibility with older Python versions, remember to run the full test suite via
Nox sessions.

## Pre-commit

The project uses [Pre-commit][pre-commit] to ensure consistent quality and formatting
across the entire project.

In addition to the tools mentioned in the [Coding Style](#coding-style) section,
we use the following extra tools for assets not being a part of the source code:

- [`prettier`][prettier] for auto-formatting non-Python files;
- [`markdownlint-cli2`][markdownlint-cli2] for linting documentation files.

Pre-commit runs automatically on each commit, but to check everything before committing,
run:

```console
pre-commit run -a
```

> For more information, see the project's [`.pre-commit-config.yaml`][pre-commit-config]
> and the Pre-commit [documentation][pre-commit].

The mentioned tools can also be executed individually via `npx`:

```console
npx prettier --check .
npx markdownlint-cli2
```

## Code of Conduct

Please review and adhere to our [Code of Conduct][code-of-conduct].

We are committed to creating a welcoming and inclusive environment for all contributors.

## Thank You! <!-- markdownlint-disable-line -->

No contribution is too small &mdash; every bit helps! Together, we can build something
amazing.

Thank you for making this project better and for being a part of our open-source
community!

[code-of-conduct]: https://github.com/paduszyk/django-management-commands/blob/main/docs/CODE_OF_CONDUCT.md
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[conventional-commit-types]: https://github.com/commitizen/conventional-commit-types/blob/master/index.json
[dev-containers]: https://containers.dev
[devcontainer.json]: https://github.com/paduszyk/django-management-commands/blob/main/.devcontainer/devcontainer.json
[docker]: https://www.docker.com
[first-contributions]: https://github.com/firstcontributions/first-contributions
[github-documentation]: https://docs.github.com/en/get-started/quickstart/contributing-to-projects
[markdownlint-cli2]: https://github.com/DavidAnson/markdownlint-cli2
[mypy]: https://mypy.readthedocs.io/en/stable/
[node.js]: https://nodejs.org/
[nox]: https://github.com/wntrblm/nox
[noxfile.py]: https://github.com/paduszyk/django-management-commands/blob/main/noxfile.py
[open-in-vs-code]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/paduszyk/django-management-commands
[open-issue]: https://github.com/paduszyk/django-management-commands/issues/new/choose
[pre-commit]: https://pre-commit.com
[pre-commit-config]: https://github.com/paduszyk/django-management-commands/blob/main/.pre-commit-config.yaml
[prettier]: https://prettier.io
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv
[pyenv]: https://github.com/pyenv/pyenv
[pyproject.toml]: https://github.com/paduszyk/django-management-commands/blob/main/pyproject.toml
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
