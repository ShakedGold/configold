from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp


class RipGrepApp(TarballApp):
    """
    Installer for rg (ripgrep), faster replacement from grep
    """

    BINARY_NAME: str = "rg"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The fastest grepping in the west",
            link_path=PosixPath("rg"),
            strip_components=True,
        )
