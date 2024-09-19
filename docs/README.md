# django-management-commands

[![Pre-commit.ci](https://results.pre-commit.ci/badge/github/paduszyk/django-management-commands/main.svg)][pre-commit.ci]
[![CI](https://img.shields.io/github/actions/workflow/status/paduszyk/django-management-commands/package-ci.yml?logo=github&label=CI)][ci]
[![Codecov](https://img.shields.io/codecov/c/github/paduszyk/django-management-commands?logo=codecov)][codecov]

[![Nox](https://img.shields.io/badge/%f0%9f%a6%8a-Nox-d85e00)][nox]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][ruff]
[![Mypy](https://img.shields.io/badge/type--checked-mypy-blue?logo=python)][mypy]
[![Prettier](https://img.shields.io/badge/code_style-Prettier-1e2b33?logo=prettier)][prettier]
[![Conventional Commits](https://img.shields.io/badge/Conventional_Commits-1.0.0-fa6673?logo=conventional-commits)][conventional-commits]

## Overview

`django-management-commands` is a plugin that provides enhanced flexibility for
defining, organizing, and executing Django commands.

While Django enforces certain conventions for [management commands][django-commands],
this package allows you to bypass these limitations. With `django-management-commands`,
you can define and manage commands outside the traditional `management.commands`
package, giving you greater freedom in structuring your project. This is especially
useful for developers working on large projects with multiple apps or complex command
structures, where organizing commands effectively is critical.

## Key Features

- **Flexible Command Location**: Define commands in any module, allowing you to
  organize your codebase more freely without relying on Django's default structure.

- **Custom Command Naming**: Assign names to commands independently of their submodules,
  enabling clearer and more intuitive command management.

- **Command Name Conflicts Resolution**: Resolve command name conflicts by referencing
  commands through app labels.

- **Enhanced Command Management**: Define, organize, and execute commands or aliases
  via your Django settings, simplifying complex command sequences and improving
  maintainability.

## Requirements

This package supports the following Python and Django versions:

| Python | Django        |
| :----- | :------------ |
| 3.9    | 4.2           |
| 3.10   | 4.2, 5.0, 5.1 |
| 3.11   | 4.2, 5.0, 5.1 |
| 3.12   | 4.2, 5.0, 5.1 |

Configuration is managed through [`django-appconf ~= 1.0`][django-appconf].

## Installation

To install the plugin, download and install it from [PyPI][pypi] using `pip`:

```console
pip install django-management-commands
```

You can also use any other dependency manager of your choice. Once installed, you
can access the plugin's features through the `management_commands` package.

> We recommend avoiding global or system-wide Python environments for package installation.
> Always use a virtual environment to manage your dependencies.

## Django Setup

To enable advanced command management features, update your project's starter script;
this file is likely named `manage.py`. Replace the line that refers to Django's
management utility:

```python
from django.core.management import execute_from_command_line
```

with:

```python
from management_commands.management import execute_from_command_line
```

That's it! No further steps are needed.

## Usage

### Running Commands

The plugin does not change how commands are executed, but rather how they are discovered.
Running commands works the same way as with Django's built-in utility.

Additionally, you can invoke commands registered from `INSTALLED_APPS` using a more
explicit notation that accounts for the app label:

```console
python manage.py <APP_LABEL>.<COMMAND>
```

This is particularly useful when multiple apps register commands with the same name.
If no app label is provided, the plugin attempts to auto-discover the command's
module and class in custom paths, modules, submodules, and aliases, as described
in the [Configuration](#configuration) section.

### Configuration

The plugin provides several optional settings to customize the discovery and execution
of Django commands via `DJANGO_SETTINGS_MODULE`.

#### `MANAGEMENT_COMMANDS_PATHS`

**Type:** `dict[str, str]`

**Default:** `{}`

This setting maps custom command names to their corresponding class paths, allowing
you to define commands outside the standard app structure.

Example:

```python
MANAGEMENT_COMMANDS_PATHS = {
    "mycommand": "mysite.commands.MyCommand",
}
```

You can now run the custom command `mycommand` implemented in the `MyCommand` class
from the `mysite.commands` module:

```console
python manage.py mycommand
```

> In Django, the class representing a command must be named `Command`. The plugin
> allows you to name it with any valid Python identifier, enabling multiple commands
> within a single module.

**Important Notes:**

- All keys and values must be valid Python identifiers and absolute dotted paths,
  respectively.
- Paths must point to command classes, not modules.
- Commands must subclass `django.core.management.base.BaseCommand`.
- This setting takes precedence over others when discovering commands.

#### `MANAGEMENT_COMMANDS_MODULES`

**Type:** `list[str]`

**Default:** `[]`

Specifies the modules where custom commands should be discovered.

Example:

```python
MANAGEMENT_COMMANDS_MODULES = [
    "mycommands",
]
```

When running:

```console
python manage.py mycommand
```

the utility will search for the `Command` class in the `mycommands.mycommand` module.

**Important Notes:**

- Items must be valid absolute dotted Python paths.
- Commands are discovered in modules in the order they are listed.

#### `MANAGEMENT_COMMANDS_SUBMODULES`

**Type:** `list[str]`

**Default:** `[]`

Defines submodules within app packages where commands should be discovered. Django's
default `management.commands` is automatically inserted at index 0 if not explicitly
included.

Example:

```python
MANAGEMENT_COMMANDS_SUBMODULES = [
    "commands",
]
```

This allows the utility to search for `Command` classes in both `myapp.management.commands.command`
and `myapp.commands.command` for an app installed from the `myapp` module.

**Important Notes:**

- Items must be valid absolute dotted Python paths (although at runtime, they are
  treated as relative paths appended to app names).

#### `MANAGEMENT_COMMANDS_ALIASES`

**Type:** `dict[str, list[str]]`

**Default:** `{}`

Allows the definition of shortcuts or aliases for sequences of Django commands.

Example:

```python
MANAGEMENT_COMMANDS_ALIASES = {
    "fullcheck": [
        "check --fail-level ERROR --deploy",
        "makemigrations --check --dry-run --no-input",
        "migrate --no-input",
    ],
}
```

You can now execute all the commands aliased by `fullcheck` with a single command:

```console
python manage.py fullcheck
```

Aliases can refer to commands defined in the `MANAGEMENT_COMMANDS_PATHS` setting
or other aliases.

**Important Notes:**

- Keys must be valid Python identifiers.
- Values should be command expressions with parsable arguments and options.
- Circular references within aliases are not allowed, as they lead to infinite recursion.

### Error Handling

#### Configuration Checks

The plugin performs basic validation of user settings, primarily checking command
names, aliases, and module paths. If any checks fail, the plugin raises an `ImproperlyConfigured`
error.

For more information, see the `management_commands.conf` module.

> The `ImproperlyConfigured` error here is distinct from the one in `django.core.exceptions`;
> the plugin's uses its own exception class defined with its configuration.

#### Custom Exceptions

The package includes custom exceptions for error handling:

- **`CommandImportError`**: raised if the command class import fails;

- **`CommandTypeError`**: raised if the imported command class is not a subclass
  of Django's `BaseCommand`;

- **`CommandClassLookupError`**: raised if a command cannot be discovered;

- **`CommandAppLookupError`**: raised when a command is referenced by app label,
  but the app with that label is not installed.

For more information, see the `management_commands.exceptions` module.

> Be sure to review these exceptions when debugging or reporting issues.

## Contributing

- This is an open-source project and welcomes all types of contributions.
- Contributors must adhere to our [Code of Conduct][code-of-conduct].
- For detailed contribution guidelines, please refer to our [Contributing Guide][contributing].

## License

Released under the [MIT license][license].

[ci]: https://github.com/paduszyk/django-management-commands/actions/workflows/package-ci.yml
[code-of-conduct]: https://github.com/paduszyk/django-management-commands/blob/main/docs/CODE_OF_CONDUCT.md
[codecov]: https://app.codecov.io/gh/paduszyk/django-management-commands
[contributing]: https://github.com/paduszyk/django-management-commands/blob/main/docs/CONTRIBUTING.md
[conventional-commits]: https://www.conventionalcommits.org/
[django-appconf]: https://github.com/django-compressor/django-appconf
[django-commands]: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
[license]: https://github.com/paduszyk/django-management-commands/blob/main/LICENSE
[mypy]: https://mypy.readthedocs.io
[nox]: https://nox.thea.codes/
[pre-commit.ci]: https://results.pre-commit.ci/latest/github/paduszyk/django-management-commands/main
[prettier]: https://prettier.io
[pypi]: https://pypi.org/project/django-management-commands/
[ruff]: https://docs.astral.sh/ruff/
