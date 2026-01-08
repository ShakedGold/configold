from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp
from .config_data import ZellijConfigData
from .config_widget import ZellijConfigWidget
from configuration import Configuration


class ZellijApp(TarballApp):
    """
    An installer for the zellij terminal multiplexer application
    """

    BINARY_NAME: str = "zellij"
    CWD: str = consts.BINARIES_PATH

    def __init__(self, configuration: ZellijConfigData | None = None) -> None:
        super().__init__(
            detail="The new terminal multiplexer on the block",
            configuration=Configuration(
                config_data=ZellijConfigData(
                    backup_directory_path=self.backup_directory_path
                )
                if configuration is None
                else configuration,
                widget=ZellijConfigWidget(),
            ),
            link_path=PosixPath("zellij"),
        )
