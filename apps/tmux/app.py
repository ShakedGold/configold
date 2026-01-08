from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp
from .config_data import TmuxConfigData
from .config_widget import TmuxConfigWidget
from configuration import Configuration, ConfigurationData


class TmuxApp(TarballApp):
    """
    Installer for tmux, the terminal multiplexer
    """

    BINARY_NAME: str = "tmux"
    CWD: str = consts.BINARIES_PATH

    def __init__(self, configuration: ConfigurationData | None = None) -> None:
        super().__init__(
            detail="Your normal terminal multiplexer",
            link_path=PosixPath("tmux"),
            configuration=Configuration(
                config_data=TmuxConfigData()
                if configuration is None
                else configuration,
                widget=TmuxConfigWidget(),
            ),
        )
