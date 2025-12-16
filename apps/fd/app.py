from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp


class FDApp(TarballApp):
    """
    Installer for fd: `find` replacer
    """

    BINARY_NAME: str = "fd"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="An actually usable find that follow f-cking gnu",
            link_path=PosixPath("fd"),
            strip_components=True,
        )
