from pprint import pformat
import shutil
from pydantic import Field
from pathlib import PosixPath
from typing import TextIO, override

from textual.app import ComposeResult
from textual.widgets import Label, Static, Switch
from configuration.widget import ConfigurationWidget
from configuration.data import ConfigurationData


class ZshConfigData(ConfigurationData):
    config_path: PosixPath
    backup_path: PosixPath
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

    exports: dict[str, str] = Field(default=dict(EDITOR="`which nvim`"))

    def _backup_config(self) -> None:
        self.backup_path.mkdir(parents=True, exist_ok=True)

        target_backup_path: str = PosixPath(
            self.backup_path, self.config_path.name
        ).as_posix()

        _ = shutil.copy(
            self.config_path,
            target_backup_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_path}])"
        )

    def _config_aliases(self, config_file: TextIO) -> None:
        if len(self.aliases.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the aliases, they define 'commands' that will point to other commands themself, for example: the `g` alias is just an alias to `git`\n"""
        )
        aliases_raw: str = "\n".join(
            f'alias {alias_name}="{alias_value}"'
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
            f'export {export_name}="{export_value}"'
            for export_name, export_value in self.exports.items()
        )
        _ = config_file.write(exports_raw)
        _ = config_file.write("\n\n")

        self.logger.debug("Configured exports %s", pformat(self.aliases))

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

        return True


class ZshConfigWidget(ConfigurationWidget):
    def on_switch_changed(self, event: Switch.Changed) -> None:
        if not isinstance(self.config, ZshConfigData):
            self.logger.fatal(
                f"Wrong config data type: {type(self.config)}, should have been ZshConfigData"
            )
            return

    @override
    def compose(self) -> ComposeResult:
        if not isinstance(self.config, ZshConfigData):
            self.logger.fatal(
                f"Wrong config data type: {type(self.config)}, should have been ZshConfigData"
            )

        yield Static()
