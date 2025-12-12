from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration


class ZshApp(TarballApp):
    """
    Installer for the shell zsh
    """

    BINARY_NAME: str = "zsh"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The simple, modern shell that is posix complient",
            configuration=Configuration(),
            link_path=PosixPath("bin", "zsh"),
        )

    @override
    async def configure(self) -> bool:
        return True
