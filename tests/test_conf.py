from __future__ import annotations

import pytest

from management_commands.conf import settings


def test_configure_paths_raises_improperly_configured_with_invalid_command_key() -> None:  # fmt: skip
    # Arrange.
    paths = {
        "*command_a": "module_a.Command",
        "command_b": "module_b.Command",
    }

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_paths(paths)

    assert exc_info.value.code == "paths.key"


def test_configure_paths_raises_improperly_configured_with_invalid_command_value() -> None:  # fmt: skip
    # Arrange.
    paths = {
        "command_a": "module_a.Command",
        "command_b": "*module_b.Command",
    }

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_paths(paths)

    assert exc_info.value.code == "paths.value"


def test_configure_modules_raises_improperly_configured_with_invalid_module() -> None:
    # Arrange.
    modules = [
        "*module_a",
        "module_b",
    ]

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_modules(modules)

    assert exc_info.value.code == "modules.item"


def test_configure_submodules_prepends_management_commands_to_submodules_if_not_included() -> None:  # fmt: skip
    # Arrange.
    submodules = [
        "submodule_a",
        "submodule_b",
    ]

    # Act.
    configured_submodules = settings.configure_submodules(submodules)

    # Assert.
    assert configured_submodules == [
        "management.commands",
        "submodule_a",
        "submodule_b",
    ]


def test_configure_submodule_does_not_move_management_commands_if_already_included() -> None:  # fmt: skip
    # Arrange.
    submodules = [
        "submodule_a",
        "management.commands",
        "submodule_b",
    ]

    # Act.
    configured_submodules = settings.configure_submodules(submodules)

    # Assert.
    assert configured_submodules == submodules


def test_configure_submodules_raises_improperly_configured_with_invalid_module() -> None:  # fmt: skip
    # Arrange.
    submodules = [
        "*submodule_a",
        "submodule_b",
    ]

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_submodules(submodules)

    assert exc_info.value.code == "submodules.item"


def test_configure_aliases_raises_improperly_configured_with_invalid_key() -> None:
    # Arrange.
    aliases = {
        "*alias_a": ["command_a"],
        "alias_b": ["command_b"],
    }

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_aliases(aliases)

    assert exc_info.value.code == "aliases.key"


def test_configure_aliases_raises_improperly_configured_with_empty_command_expressions() -> None:  # fmt: skip
    # Arrange.
    aliases = {
        "alias": [""],
    }

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_aliases(aliases)

    assert exc_info.value.code == "aliases.empty"


def test_configure_aliases_raises_improperly_configured_with_self_reference() -> None:
    # Arrange.
    aliases = {
        "alias_a": ["alias_b"],
        "alias_b": ["alias_b"],
    }

    # Act & assert.
    with pytest.raises(settings.ImproperlyConfigured) as exc_info:
        settings.configure_aliases(aliases)

    assert exc_info.value.code == "aliases.self_reference"
