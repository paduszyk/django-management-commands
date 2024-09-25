from __future__ import annotations

import re
from keyword import iskeyword
from typing import ClassVar

import appconf


def _is_identifier(s: str) -> bool:
    return s.replace("-", "_").isidentifier() and not iskeyword(s)


def _is_dotted_path(s: str, /, *, min_parts: int = 0) -> bool:
    if not (dotted_path_match := re.match(r"^[^\d\W]\w*(\.[^\d\W]\w*)*$", s)):
        return False

    parts = dotted_path_match.group().split(".")

    return len(parts) >= min_parts and all(map(_is_identifier, parts))


class ManagementCommandsConf(appconf.AppConf):  # type: ignore[misc]
    PATHS: ClassVar[dict[str, str]] = {}

    MODULES: ClassVar[list[str]] = []

    SUBMODULES: ClassVar[list[str]] = []

    ALIASES: ClassVar[dict[str, list[str]]] = {}

    class ImproperlyConfigured(Exception):
        def __init__(self, msg: str, code: str | None = None) -> None:
            super().__init__(msg)

            self.code = code

    def improperly_configured(
        self,
        msg: str,
        code: str | None = None,
    ) -> ImproperlyConfigured:
        msg = re.sub(
            rf"({'|'.join(dir(self))})",
            lambda m: f"{self._meta.prefixed_name(m.group(0))}",
            msg,
        )

        return self.__class__.ImproperlyConfigured(msg, code)

    def configure_paths(self, setting_value: dict[str, str]) -> dict[str, str]:
        for key, value in setting_value.items():
            if not _is_identifier(key):
                msg = (
                    f"invalid key {key!r} in PATHS; "
                    f"keys must be valid Python identifiers (with hyphens allowed)"
                )

                raise self.improperly_configured(msg, "paths.key")

            if not _is_dotted_path(value, min_parts=2):
                msg = (
                    f"invalid value for PATHS[{key!r}]; "
                    f"values must be valid absolute dotted paths with at least 2 parts"
                )

                raise self.improperly_configured(msg, "paths.value")

        return setting_value

    def _configure_path_list(
        self,
        setting_name: str,
        setting_value: list[str],
    ) -> list[str]:
        for index, item in enumerate(setting_value):
            if not _is_dotted_path(item):
                msg = (
                    f"invalid value for {setting_name.upper()}[{index}]; "
                    f"items must be valid absolute dotted paths"
                )

                raise self.improperly_configured(msg, f"{setting_name}.item")

        return setting_value

    def configure_modules(self, setting_value: list[str]) -> list[str]:
        return self._configure_path_list("modules", setting_value)

    def configure_submodules(self, setting_value: list[str]) -> list[str]:
        configured_value = self._configure_path_list("submodules", setting_value)

        if "management.commands" not in configured_value:
            configured_value.insert(0, "management.commands")

        return configured_value

    def configure_aliases(
        self,
        setting_value: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        for key, value in setting_value.items():
            if not _is_identifier(key):
                msg = (
                    f"invalid key {key!r} in ALIASES; "
                    f"keys must be valid Python identifiers (with hyphens allowed)"
                )

                raise self.improperly_configured(msg, "aliases.key")

            for index, item in enumerate(value):
                argv = item.split()

                try:
                    command = argv[0]
                except IndexError as exc:
                    msg = (
                        f"empty item found in ALIASES[{key!r}][{index}]; "
                        f"items must not be empty"
                    )

                    raise self.improperly_configured(msg, "aliases.empty") from exc

                if command == key:
                    msg = (
                        f"invalid value for ALIASES[{key!r}][{index}]; "
                        f"items must not refer to the aliases they are defined by"
                    )

                    raise self.improperly_configured(msg, "aliases.self_reference")

        return setting_value


settings = ManagementCommandsConf()
