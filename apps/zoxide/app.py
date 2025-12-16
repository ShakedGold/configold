from pathlib import PosixPath

from apps import consts
from apps.tarball import TarballApp
from configuration import Configuration, ConfigurationData


class ZoxideApp(TarballApp):
    """
    Installer for the zoxide directory changer
    """

    BINARY_NAME: str = "zoxide"
    CWD: str = consts.BINARIES_PATH

    def __init__(self) -> None:
        super().__init__(
            detail="This will change how you enter directories... (it's cool I promise)",
            configuration=Configuration(config_data=ConfigurationData()),
            link_path=PosixPath("zoxide"),
        )
