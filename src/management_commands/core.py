from __future__ import annotations

import contextlib
import importlib
import pkgutil
import typing
from contextlib import suppress

from django.apps.registry import apps
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from .conf import settings
from .exceptions import (
    CommandAppLookupError,
    CommandClassLookupError,
    CommandImportError,
    CommandTypeError,
)

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


def import_command_class(dotted_path: str) -> type[BaseCommand]:
    try:
        command_class: type = import_string(dotted_path)
    except ImportError as exc:
        raise CommandImportError(dotted_path) from exc

    if not (isinstance(command_class, type) and issubclass(command_class, BaseCommand)):
        raise CommandTypeError(command_class)

    return command_class


def iterate_modules(dotted_path: str) -> Iterator[str]:
    for _, name, is_pkg in pkgutil.iter_modules(
        importlib.import_module(dotted_path).__path__,
    ):
        if not is_pkg and not name.startswith("_"):
            yield name


def _discover_commands_in_module(module: str) -> list[str]:
    commands: list[str] = []
    try:
        files_in_dir = list(iterate_modules(module))
    except ImportError:  # module doesn't exist
        return commands

    for file in files_in_dir:
        with (
            contextlib.suppress(CommandImportError),
            contextlib.suppress(CommandTypeError),
        ):
            import_command_class(f"{module}.{file}.Command")
            commands.append(file)

    return commands


def get_commands_from_modules_and_submodules() -> dict[str, list[str]]:
    commands = {}
    for module in settings.MODULES:
        if module_commands := _discover_commands_in_module(module):
            commands[module] = module_commands

    for app in apps.get_app_configs():
        for submodule in settings.SUBMODULES:
            if app.name == "django.core" or submodule == "management.commands":
                continue

            if module_commands := _discover_commands_in_module(
                f"{app.name}.{submodule}",
            ):
                commands[app.name] = module_commands

    return commands


def get_command_paths(name: str, app_label: str | None = None) -> list[str]:
    if not app_label:
        app_names = [
            *(app_config.name for app_config in reversed(list(apps.get_app_configs()))),
            "django.core",
        ]

        modules_paths = [f"{module}.{name}.Command" for module in settings.MODULES]
    else:
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError as exc:
            raise CommandAppLookupError(app_label) from exc
        else:
            app_names = [app_config.name]

        modules_paths = []

    submodules_paths: list[str] = []
    for app_name in app_names:
        for submodule in settings.SUBMODULES:
            if app_name == "django.core" and submodule != "management.commands":
                continue

            submodules_paths.append(f"{app_name}.{submodule}.{name}.Command")

    return modules_paths + submodules_paths


def load_command_class(name: str, app_label: str | None = None) -> type[BaseCommand]:
    command_paths = get_command_paths(name, app_label)

    for command_path in command_paths:
        with suppress(CommandImportError, CommandTypeError):
            return import_command_class(command_path)

    raise CommandClassLookupError(name, app_label)
