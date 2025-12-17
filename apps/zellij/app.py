from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration, ConfigurationData


class ZellijApp(TarballApp):
    """
    An installer for the zellij terminal multiplexer application
    """

    BINARY_NAME: str = "zellij"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The new terminal multiplexer on the block",
            link_path=PosixPath("zellij"),
        )
