import os
from pathlib import PosixPath
import shutil
from typing import Literal, TextIO, override

from pydantic import Field
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Label, Switch

from configuration import ConfigurationData, ConfigurationWidget, data
from configuration.widget import LabelWithTooltip


class ZellijConfigData(ConfigurationData):
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

    @property
    @override
    def config_path(self) -> PosixPath:
        return PosixPath(os.getenv("HOME", "~"), ".config", "zellij", "config.kdl")

    @override
    def _backup_config(self) -> None:
        self.backup_directory_path.mkdir(parents=True, exist_ok=True)

        target_backup_directory_path: str = PosixPath(
            self.backup_directory_path, self.config_path.name
        ).as_posix()

        _ = shutil.copy(
            self.config_path,
            target_backup_directory_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_directory_path}])"
        )

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
        self.logger.info(self.auto_attach_to_session)
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


class ZellijConfigWidget(ConfigurationWidget[ZellijConfigData]):
    DEFAULT_CSS: str = """
    ZellijConfigWidget > Horizontal {
        height: auto;
        width: auto;
        align: center middle;
    }

    ZellijConfigWidget > Horizontal > Label {
        height: 100%;
        content-align: left middle;
    }

    ZellijConfigWidget > Horizontal > * {
        width: 1fr;
    }

    ZellijConfigWidget > Horizontal > Button {
        max-width: 30;
        margin: 0 2;
    }

    ZellijConfigWidget > Horizontal > Switch {
        max-width: 10;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield LabelWithTooltip(
                "Default Layout", str(self.config.descriptions.default_layout)
            )
            yield Input(self.config.default_layout, id="default-layout")

        with Horizontal():
            yield LabelWithTooltip(
                "Startup Tips", str(self.config.descriptions.startup_tips)
            )
            yield Switch(self.config.startup_tips, animate=False, id="startup-tips")

        with Horizontal():
            yield LabelWithTooltip(
                "Pane Frames", str(self.config.descriptions.pane_frames)
            )
            yield Switch(self.config.pane_frames, animate=False, id="pane-frames")

        with Horizontal():
            yield LabelWithTooltip(
                "Auto attach to session",
                str(self.config.descriptions.auto_attach_to_session),
            )
            yield Input(self.config.auto_attach_to_session, id="auto-attach")

        with Horizontal():
            yield LabelWithTooltip(
                "Theme",
                str(self.config.descriptions.theme),
            )
            yield Input(self.config.theme, id="theme")

    @on(Input.Blurred, "#default-layout")
    def default_layout_changed(self, layout_changed: Input.Blurred) -> None:
        self.config.default_layout = layout_changed.value

    @on(Switch.Changed, "#startup-tips")
    def startup_tips_changed(self, startup_tips_changed: Switch.Changed) -> None:
        self.config.startup_tips = startup_tips_changed.value

    @on(Switch.Changed, "#pane-frames")
    def pane_frames_changed(self, pane_frames_changed: Switch.Changed) -> None:
        self.config.pane_frames = pane_frames_changed.value

    @on(Input.Blurred, "#auto-attach")
    def auto_attach_changed(self, attach_changed: Input.Changed) -> None:
        self.config.auto_attach_to_session = attach_changed.value

    @on(Input.Blurred, "#theme")
    def theme_changed(self, theme_changed: Input.Changed) -> None:
        self.config.theme = theme_changed.value
