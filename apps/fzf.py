from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration


class FZFApp(TarballApp):
    """
    Installer for the fuzzy finder called fzf
    """

    BINARY_NAME: str = "fzf"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The fuzzy finder will find you anywhere",
            configuration=Configuration(),
            link_path=PosixPath("fzf"),
        )

    @override
    async def configure(self) -> bool:
        return True
