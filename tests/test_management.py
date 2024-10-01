from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from django.core.management import get_commands
from django.core.management.base import BaseCommand

from management_commands.management import execute_from_command_line

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(params=get_commands())
def django_core_command_name(request: pytest.FixtureRequest) -> str:
    return cast(str, request.param)


def test_execute_from_command_line_help_displays_paths_and_aliases(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Mock.
    mocker.patch.multiple(
        "management_commands.management.settings",
        PATHS={
            "command_a": "module.CommandA",
            "command_b": "module.CommandB",
        },
        ALIASES={
            "alias_a": [
                "command_a",
            ],
            "alias_b": [
                "command_b",
            ],
        },
    )

    # Act.
    execute_from_command_line(["manage.py", "--help"])
    captured = capsys.readouterr()

    # Assert.
    assert (
        "[django-management-commands: paths]\n"
        "    command_a\n"
        "    command_b\n"
        "\n"
        "[django-management-commands: aliases]\n"
        "    alias_a\n"
        "    alias_b\n"
        "\n"
    ) in captured.out


def test_execute_from_command_line_help_displays_modules_and_submodules(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Mock.
    mocker.patch.multiple(
        "management_commands.management.settings",
        MODULES=["module_a"],
        SUBMODULES=["submodule_a"],
    )

    # Arrange.
    app_config_a_mock = mocker.Mock()
    app_config_a_mock.name = "app_a"

    class CommandB(BaseCommand):
        pass

    # Mock.
    mocker.patch(
        "management_commands.core.apps.app_configs",
        {"app_a": app_config_a_mock},
    )

    def import_string_side_effect(dotted_path: str) -> type:
        if dotted_path == "module_a.command_b.Command":
            return CommandB
        if dotted_path == "app_a.submodule_a.command_b.Command":
            return CommandB

        raise ImportError

    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    def iterate_modules_side_effect(dotted_path: str) -> list[str]:
        if dotted_path == "module_a":
            return ["command_b"]
        if dotted_path == "app_a.submodule_a":
            return ["command_b"]
        raise ImportError

    mocker.patch(
        "management_commands.core.iterate_modules",
        side_effect=iterate_modules_side_effect,
    )

    # Act.

    execute_from_command_line(["manage.py", "--help"])
    captured = capsys.readouterr()

    # Assert.
    assert (
        "[django-management-commands: module_a]\n"
        "    command_b\n"
        "\n"
        "[django-management-commands: app_a]\n"
        "    command_b\n"
        "\n"
    ) in captured.out


def test_execute_from_command_line_falls_back_to_django_management_utility_if_command_name_is_not_passed(
    mocker: MockerFixture,
) -> None:
    # Mock.
    super_mock = mocker.patch("management_commands.management.super")

    # Act.
    execute_from_command_line(["manage.py"])

    # Assert.
    super_mock.return_value.execute.assert_called_once()


def test_execute_from_command_line_falls_back_to_django_management_utility_to_run_command_not_defined_in_settings(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        PATHS={},
        ALIASES={},
    )

    # Mock.
    super_mock = mocker.patch("management_commands.management.super")

    # Act.
    execute_from_command_line(["manage.py", "command"])

    # Assert.
    super_mock.return_value.execute.assert_called_once()


def test_execute_from_command_line_runs_command_from_path(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.management.settings.PATHS",
        {
            "command": "module.Command",
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "module.Command":
            return Command
        raise ImportError

    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "command"])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_uses_django_management_utility_to_run_command_from_path(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.management.settings.PATHS",
        {
            "command": "module.Command",
        },
    )

    # Mock.
    super_mock = mocker.patch("management_commands.management.super")

    # Act.
    execute_from_command_line(["manage.py", "command"])

    # Assert.
    super_mock.return_value.execute.assert_called_once()


def test_execute_from_command_lines_runs_all_commands_assigned_to_alias(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.management.settings.ALIASES",
        {
            "alias": [
                "command_a arg_a --option value_a",
                "command_b arg_b --option value_b",
            ],
        },
    )

    # Arrange.
    class CommandA(BaseCommand):
        pass

    class CommandB(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "app.management.commands.command_a.Command":
            return CommandA
        if dotted_path == "app.management.commands.command_b.Command":
            return CommandB
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_a_run_from_argv_mock = mocker.patch.object(
        CommandA,
        "run_from_argv",
        return_value=None,
    )
    command_b_run_from_argv_mock = mocker.patch.object(
        CommandB,
        "run_from_argv",
        return_value=None,
    )

    # Act.
    execute_from_command_line(["manage.py", "alias"])

    # Assert.
    command_a_run_from_argv_mock.assert_called_once_with(
        ["manage.py", "command_a", "arg_a", "--option", "value_a"],
    )
    command_b_run_from_argv_mock.assert_called_once_with(
        ["manage.py", "command_b", "arg_b", "--option", "value_b"],
    )


def test_execute_from_command_line_prefers_path_command_over_django_core_command(
    mocker: MockerFixture,
    django_core_command_name: str,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.management.settings.PATHS",
        {
            django_core_command_name: "module.Command",
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "module.Command":
            return Command
        raise ImportError

    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", django_core_command_name])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_prefers_path_command_over_alias(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        PATHS={
            "command": "module.CommandA",
        },
        ALIASES={
            "command": [
                "command_b",
            ],
        },
    )

    # Arrange.
    class CommandA(BaseCommand):
        pass

    class CommandB(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "module.CommandA":
            return CommandA
        if dotted_path == "app.management.commands.command_b.Command":
            return CommandB
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_a_run_from_argv_mock = mocker.patch.object(CommandA, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "command"])

    # Assert.
    command_a_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_prefers_alias_over_django_core_command(
    mocker: MockerFixture,
    django_core_command_name: str,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        ALIASES={
            django_core_command_name: [
                "command",
            ],
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    class DjangoCoreCommand(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "app.management.commands.command.Command":
            return Command
        if (
            dotted_path
            == f"django.core.management.commands.{django_core_command_name}.Command"
        ):
            return DjangoCoreCommand
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", django_core_command_name])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_resolves_django_core_commands_and_aliases_if_app_label_is_provided(
    mocker: MockerFixture,
    django_core_command_name: str,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        ALIASES={
            "alias": [
                f"app.{django_core_command_name}",
            ],
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    class DjangoCoreCommand(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == f"app.management.commands.{django_core_command_name}.Command":
            return Command
        if (
            dotted_path
            == f"django.core.management.commands.{django_core_command_name}.Command"
        ):
            return DjangoCoreCommand
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "alias"])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_runs_command_passed_with_explicit_app_label(
    mocker: MockerFixture,
) -> None:
    # Arrange.
    class Command(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "app.management.commands.command.Command":
            return Command
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "app.command"])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_runs_command_defined_in_path_when_referenced_by_alias(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        PATHS={
            "command": "module.Command",
        },
        ALIASES={
            "alias": [
                "command",
            ],
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "module.Command":
            return Command
        raise ImportError

    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "alias"])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_runs_command_defined_in_alias_via_other_alias(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        ALIASES={
            "alias_a": [
                "command",
            ],
            "alias_b": [
                "alias_a",
            ],
        },
    )

    # Arrange.
    class Command(BaseCommand):
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "app.management.commands.command.Command":
            return Command
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_run_from_argv_mock = mocker.patch.object(Command, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "alias_b"])

    # Assert.
    command_run_from_argv_mock.assert_called_once()


def test_execute_from_command_line_resolves_duplicate_command_names_based_on_order_of_installed_apps(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.management.settings",
        ALIASES={
            "alias": [
                "command",
            ],
        },
    )

    # Arrange.
    class CommandA(BaseCommand):
        pass

    class CommandB(BaseCommand):
        pass

    app_config_a_mock = mocker.Mock()
    app_config_a_mock.name = "app_a"
    app_config_b_mock = mocker.Mock()
    app_config_b_mock.name = "app_b"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type[BaseCommand]:
        if dotted_path == "app_a.management.commands.command.Command":
            return CommandA
        if dotted_path == "app_b.management.commands.command.Command":
            return CommandB
        raise ImportError

    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app_a": app_config_a_mock,
            "app_b": app_config_b_mock,
        },
    )
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    command_b_run_from_argv_mock = mocker.patch.object(CommandB, "run_from_argv")

    # Act.
    execute_from_command_line(["manage.py", "alias"])

    # Assert.
    command_b_run_from_argv_mock.assert_called_once()
