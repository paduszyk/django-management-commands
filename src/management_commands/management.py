from __future__ import annotations

import sys
from typing import Any

from django.core.management import ManagementUtility as BaseManagementUtility
from django.core.management import call_command as base_call_command
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from .conf import settings
from .core import import_command_class, load_command_class

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class ManagementUtility(BaseManagementUtility):
    @override
    def main_help_text(self, commands_only: bool = False) -> str:
        usage = super().main_help_text(commands_only=commands_only)

        style = color_style()

        commands_usage = (
            [
                style.NOTICE("[django-management-commands: paths]"),
                *[f"    {path}" for path in paths],
                "",
            ]
            if (paths := settings.PATHS)
            else []
        )
        aliases_usage = (
            [
                style.NOTICE("[django-management-commands: aliases]"),
                *[f"    {alias}" for alias in aliases],
                "",
            ]
            if (aliases := settings.ALIASES)
            else []
        )

        usage_list = usage.split("\n")
        usage_list.append("")
        usage_list.extend(commands_usage)
        usage_list.extend(aliases_usage)

        return "\n".join(usage_list)

    @override
    def fetch_command(self, subcommand: str) -> BaseCommand:
        if dotted_path := settings.PATHS.get(subcommand):
            command_class = import_command_class(dotted_path)
        else:
            try:
                app_label, name = subcommand.rsplit(".", 1)
            except ValueError:
                app_label, name = None, subcommand

            command_class = load_command_class(name, app_label)

        return command_class()

    @override
    def execute(self) -> None:
        try:
            name = self.argv[1]
        except IndexError:
            super().execute()
        else:
            if name in settings.PATHS:
                utility = self.__class__([self.prog_name, name, *self.argv[2:]])
                super(ManagementUtility, utility).execute()
            elif alias_exprs := settings.ALIASES.get(name):
                for alias_expr in alias_exprs:
                    argv = alias_expr.split()

                    utility = ManagementUtility([self.prog_name, *argv])
                    utility.execute()
            else:
                super().execute()


def execute_from_command_line(argv: list[str] | None = None) -> None:
    utility = ManagementUtility(argv)
    utility.execute()


def call_command(command_name: str, *args: Any, **options: Any) -> Any:
    if isinstance(command_name, BaseCommand):
        return base_call_command(command_name, *args, **options)

    if dotted_path := settings.PATHS.get(command_name):
        command_class = import_command_class(dotted_path)
    elif command_name in settings.ALIASES:
        msg = "Running aliases from call_command is not supported"
        raise ValueError(msg)
    else:
        try:
            app_label, name = command_name.rsplit(".", 1)
        except ValueError:
            app_label, name = None, command_name

        command_class = load_command_class(name, app_label)

    command = command_class()

    return base_call_command(command, *args, **options)
