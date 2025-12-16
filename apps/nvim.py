from pathlib import PosixPath
from typing import override

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration, ConfigurationData


class NVIMApp(TarballApp):
    """
    Installer for the shell text editor: NVIM
    """

    BINARY_NAME: str = "nvim"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="THE BEST EDITOR ON THE PLANET",
            configuration=Configuration(config_data=ConfigurationData()),
            link_path=PosixPath("bin", "nvim"),
            strip_components=True,
        )

    @override
    async def configure(self, config: Configuration) -> bool:
        return True
