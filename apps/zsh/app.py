from pathlib import PosixPath

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
            detail="The simple, modern shell that is posix compliant",
            configuration=Configuration(
                config_data=ZshConfigData(
                    config_path=self.config_path, backup_path=self.backup_directory_path
                ),
                widget=ZshConfigWidget(),
            ),
            link_path=PosixPath("bin", "zsh"),
        )

    @property
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)
