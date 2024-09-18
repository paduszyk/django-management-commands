from __future__ import annotations

from django.core.management.base import BaseCommand


class ManagementCommandsException(Exception):
    msg: str

    def __init__(self, msg: str | None = None, **kwargs: str) -> None:
        super().__init__(
            msg
            if msg
            else (
                msg_template.format(**kwargs)
                if (msg_template := getattr(type(self), "msg", None)) and kwargs
                else ""
            ),
        )


class CommandClassLookupError(ManagementCommandsException):
    msg = "command {command_name!r} is not registered from {app_info}"

    def __init__(
        self,
        command_name: str | None = None,
        app_name: str | None = None,
    ) -> None:
        super().__init__(
            **(
                {
                    "command_name": command_name,
                    "app_info": (
                        f"the {app_name!r} app"
                        if app_name
                        else "any of the installed apps"
                    ),
                }
                if command_name
                else {}
            ),
        )


class CommandAppLookupError(ManagementCommandsException):
    msg = "app {app_name!r} is not installed"

    def __init__(self, app_name: str | None = None) -> None:
        super().__init__(**({"app_name": app_name} if app_name else {}))


class CommandImportError(ManagementCommandsException, ImportError):
    msg = "class {class_name!r} could not be imported from the {module_path!r} module"

    def __init__(self, command_class_path: str | None = None) -> None:
        super().__init__(
            **({"module_path": parts[0], "class_name": parts[1]})
            if (command_class_path and (parts := command_class_path.rsplit(".", 1)))
            else {},
        )


class CommandTypeError(ManagementCommandsException):
    msg = "class {class_path!r} is not a subclass of {base_command_class_path!r}"

    def __init__(self, class_: type | None = None) -> None:
        super().__init__(
            **(
                {
                    "class_path": self._class_path(class_),
                    "base_command_class_path": self._class_path(BaseCommand),
                }
                if class_
                else {}
            ),
        )

    @staticmethod
    def _class_path(class_: type) -> str:
        return f"{class_.__module__}.{class_.__qualname__}"
