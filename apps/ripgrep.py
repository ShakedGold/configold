from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration


class RipGrepApp(TarballApp):
    """
    Installer for rg (ripgrep), faster replacement from grep
    """

    BINARY_NAME: str = "rg"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The fastest grepping in the west",
            configuration=Configuration(),
            link_path=PosixPath("rg"),
            strip_components=True,
        )

    @override
    async def configure(self) -> bool:
        return True
