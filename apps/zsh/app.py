from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp
from .config_data import ZshConfigData
from .config_widget import ZshConfigWidget
from configuration import Configuration


class ZshApp(TarballApp):
    """
    Installer for the shell zsh
    """

    BINARY_NAME: str = "zsh"
    CWD: str = consts.BINARIES_PATH

    def __init__(self, configuration: ZshConfigData | None = None) -> None:
        super().__init__(
            detail="The simple, modern shell that is posix compliant",
            configuration=Configuration(
                config_data=ZshConfigData(
                    backup_directory_path=self.backup_directory_path
                )
                if configuration is None
                else configuration,
                widget=ZshConfigWidget(),
            ),
            link_path=PosixPath("bin", "zsh"),
        )
