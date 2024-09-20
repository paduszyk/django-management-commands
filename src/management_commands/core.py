from __future__ import annotations

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


def import_command_class(dotted_path: str) -> type[BaseCommand]:
    try:
        command_class: type = import_string(dotted_path)
    except ImportError as exc:
        raise CommandImportError(dotted_path) from exc

    if not (isinstance(command_class, type) and issubclass(command_class, BaseCommand)):
        raise CommandTypeError(command_class)

    return command_class


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
