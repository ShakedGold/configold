import os
from pathlib import PosixPath
from typing import ClassVar, Literal, TextIO, override

from pydantic import Field

from configuration import ConfigurationData


class ZellijConfigData(ConfigurationData):
    CONFIG_NAME: ClassVar[str] = "zellij"
    CONFIG_FILE_NAME: ClassVar[str] = "config.kdl"

    default_layout: str | Literal["compact"] | Literal["default"] = Field(
        default="compact"
    )
    "The default layout of the bar (for example: the default layout is verbose, and shows all of the possible keybindings)"

    startup_tips: bool = Field(default=False)
    "Whether or not to show the startup tips upon opening zellij"

    auto_attach_to_session: str = Field(default="")
    "What session to attach when executing `zellij` (if empty then no session is attached to)"

    pane_frames: bool = Field(default=False)
    "Whether or not to show the pane frames (gaps)"

    theme: str = Field(default="catppuccin-macchiato")
    "The theme to select"

    def _config_theme(self, config_file: TextIO) -> None:
        _ = config_file.write("\n")
        _ = config_file.write(f'theme "{self.theme}"\n')

    def _config_startup_tips(self, config_file: TextIO) -> None:
        # The zellij default is true

        if not self.startup_tips:
            _ = config_file.write("show_startup_tips false\n")

    def _config_layout(self, config_file: TextIO) -> None:
        _ = config_file.write("\n")
        _ = config_file.write(f'default_layout "{self.default_layout}"\n')

    def _config_auto_attach(self, config_file: TextIO) -> None:
        if len(self.auto_attach_to_session) != 0:
            _ = config_file.write("\n")
            _ = config_file.writelines(
                [
                    "// Will auto attach to a session when executing `zellij`, or create a new one if the `session_name` does not exist\n",
                    "attach_to_session true\n",
                ]
            )
            _ = config_file.writelines(
                [
                    "// The default session name to attach to or create if it does not exist\n",
                    f'session_name "{self.auto_attach_to_session}"\n',
                ]
            )

    def _config_pane_frames(self, config_file: TextIO) -> None:
        # the zellij default is true

        if not self.pane_frames:
            _ = config_file.write("\n")
            _ = config_file.write("pane_frames false\n")

    @override
    def _config(self) -> bool:
        with open(self.config_path, "w+") as config_file:
            self._config_theme(config_file)
            self._config_startup_tips(config_file)
            self._config_layout(config_file)
            self._config_auto_attach(config_file)
            self._config_pane_frames(config_file)

        return True
