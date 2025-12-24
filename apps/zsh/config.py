from enum import StrEnum
import json
import os
from pprint import pformat
import shutil
from pydantic import Field, model_validator
from pathlib import PosixPath
from typing import ClassVar, TextIO, override

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Label
from components.dict_modal import DictModal
from configuration.widget import ConfigurationWidget
from configuration.data import ConfigurationData


class ZshPluginManager(StrEnum):
    ZINIT = "zinit"


class ZshConfigData(ConfigurationData):
    CONFIG_FILE_NAME: ClassVar[str] = ".zshrc"

    backup_directory_path: PosixPath = Field(
        default_factory=lambda: PosixPath(os.getenv("HOME", "~"), ".local", "backups")
    )
    aliases: dict[str, str] = Field(
        default=dict(
            l="ls -lah",
            la="ls -lAh",
            ll="ls -l",
            ls="eza --icons=always",
            md="mkdir -p",
            vim="nvim",
            z="$EDITOR $HOME/.zshrc",
            zj="zellij",
            x=". $HOME/.zshrc",
            cat="bat",
            g="git",
        )
    )
    plugin_manager: ZshPluginManager = Field(default=ZshPluginManager.ZINIT)

    exports: dict[str, str] = Field(default=dict(EDITOR="`which nvim`"))

    @property
    def home_path(self):
        home_path = os.getenv("HOME")
        if home_path is None:
            home_path = "~"
        return home_path

    @property
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)

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

    def _escape_string(self, value: str) -> str:
        return json.dumps(value)[1:-1]

    def _config_aliases(self, config_file: TextIO) -> None:
        if len(self.aliases.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the aliases, they define 'commands' that will point to other commands themself, for example: A `g` alias is just an alias to `git`\n"""
        )
        aliases_raw: str = "\n".join(
            f'alias {alias_name}="{self._escape_string(alias_value)}"'
            for alias_name, alias_value in self.aliases.items()
        )
        _ = config_file.write(aliases_raw)
        _ = config_file.write("\n\n")

        self.logger.debug("Configured aliases %s", pformat(self.aliases))

    def _config_exports(self, config_file: TextIO) -> None:
        if len(self.exports.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the exports, they define variables that are accessible by other programs (plus the shell itself)\n# You can override this to whatever you want, for example: the EDITOR env variable will define what multiple programs\n# will use as their editor, for example `sudoedit` (the command to edit files as the super user)\n"""
        )

        exports_raw: str = "\n".join(
            f'export {export_name}="{self._escape_string(export_value)}"'
            for export_name, export_value in self.exports.items()
        )
        _ = config_file.write(exports_raw)
        _ = config_file.write("\n\n")

        self.logger.debug("Configured exports %s", pformat(self.aliases))

    def _install_plugin_manager(self, config_file: TextIO) -> None:
        if self.plugin_manager == ZshPluginManager.ZINIT:
            # shutil.copy()
            pass

    @override
    def config(self) -> bool:
        self.logger.info("Configuration: %s", pformat(dict(self)))

        if self.config_path.exists():
            self.logger.debug(f"Configuration file exists ({self.config_path})")
            self._backup_config()

            self.config_path.unlink()
            self.logger.debug(f"Removed config file ({self.config_path})")

        with open(self.config_path, "a+") as config_file:
            self._config_exports(config_file)
            self._config_aliases(config_file)
            # self._install_plugin_manager(config_file)

        return True


class ZshConfigWidget(ConfigurationWidget[ZshConfigData]):
    DEFAULT_CSS: str = """
    ZshConfigWidget > Horizontal {
        height: auto;
        width: auto;
        align: center middle;
    }

    ZshConfigWidget > Horizontal > Label {
        height: 100%;
        content-align: left middle;
    }

    ZshConfigWidget > Horizontal > * {
        width: 1fr;
    }

    ZshConfigWidget > Horizontal > Button {
        max-width: 30;
        margin: 0 2;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("Aliases")
            yield Button("Open Aliases List", id="alias-button")

        with Horizontal():
            yield Label("Exports")
            yield Button("Open Exports List", id="export-button")

    @on(Button.Pressed, "#alias-button")
    def open_aliases_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.aliases, name="Aliases"))

    @on(Button.Pressed, "#export-button")
    def open_export_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.exports, name="Exports"))
