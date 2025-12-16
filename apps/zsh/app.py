from ntpath import exists
from pprint import pformat
from dataclasses import asdict
from pathlib import PosixPath
import shutil
from typing import TextIO, override

from apps import consts
from apps.tarball import TarballApp
from apps.zsh.config import ZshConfigData, ZshConfigWidget
from configuration import Configuration


class ZshApp(TarballApp):
    """
    Installer for the shell zsh
    """

    BINARY_NAME: str = "zsh"
    CWD: str = consts.BINARIES_PATH
    CONFIG_FILE_NAME: str = ".zshrc"

    def __init__(self) -> None:
        super().__init__(
            detail="The simple, modern shell that is posix complient",
            configuration=Configuration(
                config_data=ZshConfigData(config_file=self.config_path),
                widget=ZshConfigWidget(),
            ),
            link_path=PosixPath("bin", "zsh"),
        )

    @property
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)

    # def _config_aliases(self, config_file: TextIO, config: ZshConfig) -> None:
    #     aliases_raw: str = "\n".join(
    #         f'alias {alias_name}="{alias_value}"'
    #         for alias_name, alias_value in config.aliases.items()
    #     )
    #     _ = config_file.write(aliases_raw)

    #     self.logger.debug("Configured aliases %s", pformat(config.aliases))

    def _backup_config(self) -> None:
        self.backup_directory_path.mkdir(parents=True, exist_ok=True)

        target_backup_path: str = PosixPath(
            self.backup_directory_path, type(self).CONFIG_FILE_NAME
        ).as_posix()

        _ = shutil.copy(
            self.config_path,
            target_backup_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_directory_path}])"
        )

    @override
    async def _configure(self, config: Configuration) -> bool:
        # zsh_config: ZshConfig = config
        # self.logger.info("Configuration: %s", pformat(asdict(zsh_config)))

        # if self.config_path.exists():
        #     self.logger.debug(f"Configuration file exists ({self.config_path})")
        #     self._backup_config()

        #     self.config_path.unlink()
        #     self.logger.debug(f"Removed config file ({self.config_path})")

        # with open(self.config_path, "a+") as config_file:
        #     self._config_aliases(config_file, zsh_config)

        return config.config()
