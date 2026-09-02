from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django.core.management.base import BaseCommand

from management_commands.core import (
    get_command_paths,
    get_commands_from_modules_and_submodules,
    import_command_class,
    load_command_class,
)
from management_commands.exceptions import (
    CommandAppLookupError,
    CommandClassLookupError,
    CommandImportError,
    CommandTypeError,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_import_command_class_imports_command_if_dotted_path_points_to_base_command_subclass(
    mocker: MockerFixture,
) -> None:
    # Arrange.
    class Command(BaseCommand):
        pass

    # Mock.
    mocker.patch(
        "management_commands.core.import_string",
        return_value=Command,
    )

    # Act.
    command_class = import_command_class("module.Command")

    # Assert.
    assert command_class is Command


def test_import_command_class_raises_command_import_error_if_importing_from_dotted_path_fails(
    mocker: MockerFixture,
) -> None:
    # Mock.
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=ImportError,
    )

    # Act & assert.
    with pytest.raises(CommandImportError):
        import_command_class("module_does_not_exist.Command")


def test_import_command_class_raises_command_type_error_if_imported_class_is_not_a_subclass_of_base_command(
    mocker: MockerFixture,
) -> None:
    # Arrange.
    class NotABaseCommand:
        pass

    # Mock.
    mocker.patch(
        "management_commands.core.import_string",
        return_value=NotABaseCommand,
    )

    # Act & assert.
    with pytest.raises(CommandTypeError):
        import_command_class("module.Command")


def test_get_command_paths_returns_list_of_all_dotted_paths_to_command_classes_in_modules_and_submodules_if_app_label_unspecified(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.conf.settings",
        MODULES=[
            "module_a",
            "module_b",
        ],
        SUBMODULES=[
            "submodule_a",
            "submodule_b",
        ],
    )

    # Arrange.
    app_config_a_mock = mocker.Mock()
    app_config_a_mock.name = "app_a"
    app_config_b_mock = mocker.Mock()
    app_config_b_mock.name = "app_b"

    # Mock.
    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app_a": app_config_a_mock,
            "app_b": app_config_b_mock,
        },
    )

    # Act.
    command_paths = get_command_paths("command")

    # Assert.
    assert command_paths == [
        "module_a.command.Command",
        "module_b.command.Command",
        "app_b.submodule_a.command.Command",
        "app_b.submodule_b.command.Command",
        "app_a.submodule_a.command.Command",
        "app_a.submodule_b.command.Command",
    ]


def test_get_commands_from_modules_and_submodules_returns_dictionary_of_available_commands(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch.multiple(
        "management_commands.conf.settings",
        MODULES=[
            "module_a",
            "module_b",  # no commands
        ],
        SUBMODULES=[
            "submodule_a",
            "submodule_b",  # no commands
        ],
    )

    # Arrange.
    app_config_a_mock = mocker.Mock()
    app_config_a_mock.name = "app_a"
    app_config_b_mock = mocker.Mock()  # no commands
    app_config_b_mock.name = "app_b"

    class CommandA:
        pass

    class CommandB(BaseCommand):
        pass

    # Mock.
    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app_a": app_config_a_mock,
            "app_b": app_config_b_mock,
        },
    )

    def import_string_side_effect(dotted_path: str) -> type:
        if dotted_path == "module_a.command_a.Command":
            return CommandA
        if dotted_path == "module_a.command_b.Command":
            return CommandB
        if dotted_path == "app_a.submodule_a.command_a.Command":
            return CommandA
        if dotted_path == "app_a.submodule_a.command_b.Command":
            return CommandB

        raise ImportError

    mocker.patch(
        "management_commands.core.import_string",
        side_effect=import_string_side_effect,
    )

    def iterate_modules_side_effect(dotted_path: str) -> list[str]:
        if dotted_path == "module_a":
            return ["command_a", "command_b"]
        if dotted_path == "app_a.submodule_a":
            return ["command_a", "command_b"]
        raise ImportError

    mocker.patch(
        "management_commands.core.iterate_modules",
        side_effect=iterate_modules_side_effect,
    )

    # Act.
    commands = get_commands_from_modules_and_submodules()

    # Assert.
    assert set(commands.keys()) == {"module_a", "app_a"}
    assert commands["module_a"] == ["command_b"]
    assert commands["app_a"] == ["command_b"]


def test_get_command_paths_returns_list_of_dotted_paths_to_app_submodules_if_app_label_specified(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.conf.settings.SUBMODULES",
        [
            "submodule_a",
            "submodule_b",
        ],
    )

    # Arrange.
    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    mocker.patch(
        "management_commands.core.apps.app_configs",
        {
            "app": app_config_mock,
        },
    )

    # Act.
    command_paths = get_command_paths("command", app_label="app")

    # Assert.
    assert command_paths == [
        "app.submodule_a.command.Command",
        "app.submodule_b.command.Command",
    ]


def test_get_command_path_raises_command_app_lookup_error_if_app_label_refer_to_not_installed_app(
    mocker: MockerFixture,
) -> None:
    # Mock.
    mocker.patch("management_commands.core.apps.app_configs", {})

    # Act & assert.
    with pytest.raises(CommandAppLookupError):
        get_command_paths("command", app_label="app")


def test_load_command_class_returns_command_class_if_any_of_dotted_paths_points_to_base_command_subclass(
    mocker: MockerFixture,
) -> None:
    # Configure.
    mocker.patch(
        "management_commands.conf.settings.SUBMODULES",
        [
            "submodule_a",
            "submodule_b",
            "submodule_c",
        ],
    )

    # Arrange.
    class CommandA:
        pass

    class CommandB(BaseCommand):
        pass

    class CommandC:
        pass

    app_config_mock = mocker.Mock()
    app_config_mock.name = "app"

    # Mock.
    def import_string_side_effect(dotted_path: str) -> type:
        if dotted_path == "app.submodule_a.command.Command":
            return CommandA
        if dotted_path == "app.submodule_b.command.Command":
            return CommandB
        if dotted_path == "app.submodule_c.command.Command":
            return CommandC
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

    # Act.
    command_class = load_command_class("command")

    # Assert.
    assert command_class is CommandB


def test_load_command_class_raises_command_class_lookup_error_if_none_of_dotted_paths_points_to_base_command_subclass(
    mocker: MockerFixture,
) -> None:
    # Mock.
    mocker.patch(
        "management_commands.core.import_string",
        side_effect=ImportError,
    )

    # Act & assert.
    with pytest.raises(CommandClassLookupError):
        load_command_class("command")
