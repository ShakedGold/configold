from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp


class FZFApp(TarballApp):
    """
    Installer for the fuzzy finder called fzf
    """

    BINARY_NAME: str = "fzf"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The fuzzy finder will find you anywhere",
            link_path=PosixPath("fzf"),
        )
