from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration


class ZellijApp(TarballApp):
    """
    An installer for the zellij terminal multiplexer application
    """

    BINARY_NAME: str = "zellij"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="The new terminal multiplexer on the block",
            configuration=Configuration(),
            link_path=PosixPath("zellij"),
        )

    @override
    async def configure(self) -> bool:
        return True
