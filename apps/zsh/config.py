from dataclasses import asdict
from pprint import pformat
import shutil
from pydantic import Field
from pathlib import PosixPath
from typing import ClassVar, TextIO, override

from textual.app import ComposeResult
from configuration.widget import ConfigurationWidget
from configuration.data import ConfigurationData


class ZshConfigData(ConfigurationData):
    CONFIG_FILE_NAME: ClassVar[str] = ".zshrc"

    config_path: PosixPath
    backup_path: PosixPath
    aliases: dict[str, str] = Field(default=dict(l="ls -la"))

    def _backup_config(self) -> None:
        self.backup_path.mkdir(parents=True, exist_ok=True)

        target_backup_path: str = PosixPath(
            self.backup_path, type(self).CONFIG_FILE_NAME
        ).as_posix()

        _ = shutil.copy(
            self.config_path,
            target_backup_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_path}])"
        )

    def _config_aliases(self, config_path: TextIO) -> None:
        aliases_raw: str = "\n".join(
            f'alias {alias_name}="{alias_value}"'
            for alias_name, alias_value in self.aliases.items()
        )
        _ = config_path.write(aliases_raw)

        self.logger.debug("Configured aliases %s", pformat(self.aliases))

    @override
    def config(self) -> bool:
        self.logger.info("Configuration: %s", pformat(dict(self)))

        if self.config_path.exists():
            self.logger.debug(f"Configuration file exists ({self.config_path})")
            self._backup_config()

            self.config_path.unlink()
            self.logger.debug(f"Removed config file ({self.config_path})")

        with open(self.config_path, "a+") as config_file:
            self._config_aliases(config_file)

        return True


class ZshConfigWidget(ConfigurationWidget):
    @override
    def compose(self) -> ComposeResult:
        raise NotImplementedError
