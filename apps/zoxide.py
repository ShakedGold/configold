from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration


class ZoxideApp(TarballApp):
    """
    Installer for the zoxide directory changer
    """

    BINARY_NAME: str = "zoxide"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="This will change how you enter directories... (it's cool I promise)",
            configuration=Configuration(),
            link_path=PosixPath("zoxide"),
        )

    @override
    async def configure(self) -> bool:
        return True
