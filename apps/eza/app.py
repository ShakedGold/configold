from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp


class EzaApp(TarballApp):
    """
    Installer for fd: `find` replacer
    """

    BINARY_NAME: str = "eza"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="THE GLORIOUS ICONS ON LS ARE HERE",
            link_path=PosixPath("eza"),
        )
