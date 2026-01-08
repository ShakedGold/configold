from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp


class TmuxApp(TarballApp):
    """
    Installer for tmux, the terminal multiplexer
    """

    BINARY_NAME: str = "tmux"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="Your normal terminal multiplexer",
            link_path=PosixPath("tmux"),
        )
