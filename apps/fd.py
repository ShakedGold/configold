from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration, ConfigurationData


class FDApp(TarballApp):
    """
    Installer for fd: `find` replacer
    """

    BINARY_NAME: str = "fd"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="An actually usable find that follow f-cking gnu",
            configuration=Configuration(config_data=ConfigurationData()),
            link_path=PosixPath("fd"),
            strip_components=True,
        )

    @override
    async def configure(self, config: Configuration) -> bool:
        return True
