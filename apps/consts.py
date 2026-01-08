import os
from pathlib import PosixPath
from typing import Final


BINARIES_PATH: Final[str] = "binaries"
RETURN_CODE_SUCCESS: Final[int] = 0
INSTALL_DIRECTORY: Final[PosixPath] = PosixPath(os.getenv("HOME", "~"), ".local", "bin")
