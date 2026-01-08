import os
from enum import StrEnum
from pathlib import PosixPath
import shutil
from typing import ClassVar, Literal, TextIO, override

from pydantic import BaseModel, Field
from configuration import ConfigurationData
from utils.requirements.binary_requirements import BinaryRequirement


class TmuxKeybindingType(StrEnum):
    NORMAL = ""
    GLOBAL = "-n"


class TmuxKeybinding(BaseModel):
    unbind: bool = Field(default=False)
    bind_type: TmuxKeybindingType = Field(default=TmuxKeybindingType.NORMAL)
    bind_value: str | BinaryRequirement[str] = Field(default="")


class TmuxConfigData(ConfigurationData):
    CONFIG_FILE_NAME: ClassVar[str] = ".tmux.conf"
    CONFIG_NAME: ClassVar[str] = "tmux"

    resource_target_path: PosixPath = Field(
        default_factory=lambda: PosixPath(
            os.getenv("HOME", "~"), ".local", "share", "tmux", "resources"
        )
    )

    prefix: str = Field(default="C-s")
    "The tmux prefix is used to 'prefix' any non global command (e.g. <PREFIX>+\" will by default split a window)"

    keybindings: dict[str, TmuxKeybinding] = Field(
        default={
            "r": TmuxKeybinding(
                unbind=True,
                bind_value="source-file ~/.tmux.conf",
            ),
            "M-h": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="select-pane -L"
            ),
            "M-l": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="select-pane -R"
            ),
            "M-j": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="select-pane -D"
            ),
            "M-k": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="select-pane -U"
            ),
            "M-s": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL,
                bind_value='split-window -h -c "#{pane_current_path}"',
            ),
            "M-v": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL,
                bind_value='split-window -v -c "#{pane_current_path}"',
            ),
            "M-x": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="kill-pane"
            ),
            "M-f": TmuxKeybinding(
                bind_type=TmuxKeybindingType.GLOBAL, bind_value="resize-pane -Z"
            ),
        }
    )
    "The keybindings that tmux will recognize"

    mouse_support: bool = Field(default=True)
    "Whether or not to have mouse support in tmux (for example: can resize windows with the mouse)"

    tpm: bool = Field(default=True)
    "The tmux plugin manager"

    plugins: list[str | BinaryRequirement[str]] = Field(default=["tmux-sensible"])
    "A list of all the plugins you wish to install"

    theme: str = Field(default="catppuccin")
    "The tmux theme"

    status_position: Literal["bottom"] | Literal["top"] = Field(default="top")
    "The position of the status bar on the screen"

    base_index: int = Field(default=1)
    "The starting index for tmux windows"

    scroll_vim_mode: bool = Field(default=True)
    "If the scroll mode in tmux has vim keybindings"

    def _copy_resources(self) -> None:
        self.resource_target_path.mkdir(parents=True, exist_ok=True)

        _ = shutil.copytree(
            self.resources_path.as_posix(),
            self.resource_target_path.as_posix(),
            dirs_exist_ok=True,
        )

    def _config_keybindings(self, config_file: TextIO) -> None:
        _ = config_file.write("# All of your keybindings for tmux\n")

        for bind_key, tmux_keybind in self.keybindings.items():
            if tmux_keybind.unbind:
                _ = config_file.write(f"unbind {bind_key}\n")

            _ = config_file.write("bind")
            if tmux_keybind.bind_type != TmuxKeybindingType.NORMAL:
                _ = config_file.write(" ")

            _ = config_file.write(
                f"{tmux_keybind.bind_type} {bind_key} {tmux_keybind.bind_value}\n"
            )

        _ = config_file.write("\n")

    def _convert_bool_to_tmux_value(
        self, boolean: bool
    ) -> Literal["on"] | Literal["off"]:
        return "on" if boolean else "off"

    def _config_prefix(self, config_file: TextIO) -> None:
        _ = config_file.write(
            "# The prefix is what you press before pressing another key to activate keybind\n"
        )
        _ = config_file.write(f"set -g prefix {self.prefix}\n\n")

    def _config_mouse_support(self, config_file: TextIO) -> None:
        # tmux's default is off

        if not self.mouse_support:
            return

        _ = config_file.write(
            "# The prefix is what you press before pressing another key to activate keybind\n"
        )
        _ = config_file.write(
            f"set -g mouse {self._convert_bool_to_tmux_value(self.mouse_support)}\n\n"
        )

    def _config_plugins(self, config_file: TextIO) -> None:
        if not self.tpm:
            return

        plugins_directory = PosixPath(self.resource_target_path, "plugins")

        config_file.writelines(
            [
                "# Setting the plugins directory to your installed one\n",
                f"set-environment -g TMUX_PLUGIN_MANAGER_PATH '{plugins_directory}'\n",
                "\n",
                "# Here you can define all of the plugins you want to install for tmux\n",
                "set -g @plugin 'tmux-plugins/tpm'\n",
            ]
        )

        config_file.writelines(
            [f"set -g @plugin 'tmux-plugins/{plugin}'\n" for plugin in self.plugins]
        )
        _ = config_file.write("\n")

    def _config_theme(self, config_file: TextIO) -> None:
        _ = config_file.write("# This is your theme, it defines how tmux should look\n")
        _ = config_file.write(f"set -g @plugin 'themes/theme-{self.theme}'\n")
        _ = config_file.write("\n")

    def _run_tpm(self, config_file: TextIO) -> None:
        tpm_path = PosixPath(self.resource_target_path, "tpm", "tpm")
        _ = config_file.write(f"run '{tpm_path}'\n")

    def _config_status_bar(self, config_file: TextIO) -> None:
        _ = config_file.write("# The status bar configuration\n")
        _ = config_file.write(f"set-option -g status-position {self.status_position}\n")

        _ = config_file.write("\n")

    def _config_base_index(self, config_file: TextIO) -> None:
        # The tmux default is 0

        if self.base_index == 0:
            return

        _ = config_file.write(
            "# The base index is the starting index of tmux windows\n"
        )
        _ = config_file.writelines(
            [
                f"set -g base-index {self.base_index}\n",
                f"set -g pane-base-index {self.base_index}\n",
                f"set-window-option -g pane-base-index {self.base_index}\n",
                "set-option -g renumber-windows on\n",
            ]
        )

        _ = config_file.write("\n")

    def _config_scroll_vim_mode(self, config_file: TextIO) -> None:
        # The tmux default is false
        if not self.scroll_vim_mode:
            return

        config_file.writelines(
            [
                "# Enabled vim mode for the scrolling in tmux\n",
                "set-window-option -g mode-keys vi\n",
                "bind-key -T copy-mode-vi v send -X begin-selection\n",
                "bind-key -T copy-mode-vi V send -X select-line\n",
            ]
        )
        _ = config_file.write("\n")

    @override
    def _config(self) -> bool:
        self._copy_resources()

        with open(self.config_path, "w+") as config_file:
            self._config_prefix(config_file)
            self._config_keybindings(config_file)
            self._config_mouse_support(config_file)
            self._config_status_bar(config_file)
            self._config_base_index(config_file)
            self._config_scroll_vim_mode(config_file)
            self._config_theme(config_file)
            self._config_plugins(config_file)
            self._run_tpm(config_file)

        return True
