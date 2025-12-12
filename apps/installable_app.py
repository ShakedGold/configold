import os
import logging
import pathlib
import shutil
from pythonjsonlogger import jsonlogger
from pathlib import PosixPath
from typing import override

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Switch

from configuration import Configuration
import utils


class InstallableApp(Widget):
    DEFAULT_CSS: str = r"""
    #evenly_spaced {
        height: 5;
    }
    #evenly_spaced Label {
        height: 100%;
        content-align: center middle;
        padding: 1;
    }
    #detail {
        color: gray;
    }
    #should_install {
        border: none none;
        background: transparent;
        padding: 0 1 0 2;
    }
    #should_install_container {
        width: auto;
        height: 100%;
        align-vertical: middle;
    }
    #config {
        background: transparent;
    }
    """

    BINARIES: dict[str, str | None] = {}
    BINARY_NAME: str = ""
    CWD: str = ""
    RELATIVE_TARGET_DIRECTORY: str = ".local/bin"

    should_install: reactive[bool] = reactive(True)

    def __init__(
        self,
        label: str,
        detail: str,
        configuration: Configuration,
        should_install: bool = True,
    ) -> None:
        super().__init__()
        self.label: str = label
        self.detail: str = detail
        self.should_install = should_install
        self.configuration: Configuration = configuration

        self.styles.max_height = 20
        self.styles.height = "auto"
        self.styles.border = ("round", "white")

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

        self._validate_binaries()
        self._log_paths()

    @property
    def home_path(self):
        home_path = os.getenv("HOME")
        if home_path is None:
            home_path = "~"
        return home_path

    @property
    def full_source_directory(self):
        full_cwd = os.getcwd()
        return PosixPath(full_cwd, type(self).CWD)

    @property
    def full_source_path(self):
        return PosixPath(self.full_source_directory, type(self).BINARY_NAME)

    @property
    def full_target_directory_path(self):
        return PosixPath(self.home_path, type(self).RELATIVE_TARGET_DIRECTORY)

    @property
    def full_target_path(self):
        return PosixPath(self.full_target_directory_path, type(self).BINARY_NAME)

    def _validate_binaries(self):
        for binary_name in type(self).BINARIES.keys():
            binary_path = utils.find_executable(binary_name)
            if binary_path is None:
                raise ValueError("BINARY NOT FOUND: ", binary_name)

            type(self).BINARIES[binary_name] = binary_path

    def _log_paths(self):
        self.logger.debug(f"home_path: {self.home_path}")
        self.logger.debug(f"full_source_path: {self.full_source_path}")
        self.logger.debug(f"full_source_directory: {self.full_source_directory}")
        self.logger.debug(
            f"full_target_directory_path: {self.full_target_directory_path}"
        )
        self.logger.debug(f"full_target_path: {self.full_target_path}")

    @override
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Horizontal(
                Container(
                    Switch(self.should_install, animate=False, id="should_install"),
                    id="should_install_container",
                ),
                Label(self.label),
                id="label_container",
            ),
            Label(self.detail, id="detail"),
            id="evenly_spaced",
        )
        with Collapsible(title="Configuration", id="config"):
            yield Label("CONFIG")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "should_install":
            self.should_install = event.value

    def get_binary_path(self, binary_name: str) -> str:
        binary_path: str | None = type(self).BINARIES.get(binary_name, None)

        if binary_path is None:
            raise ValueError(
                "Binary not found while running! this is weird and should not happen, the binary's name: ",
                binary_name,
            )

        return binary_path

    async def _install(self) -> bool:
        raise NotImplementedError

    async def install(self) -> bool:
        self.logger.debug(
            f"Making sure that the target directory exists ({self.full_target_directory_path})"
        )
        self.full_target_directory_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("Installing application")
        did_install = await self._install()
        if not did_install:
            self.logger.warning(
                f"The binary: {type(self).BINARY_NAME} did not install correctly"
            )
            if self.full_source_path.exists():
                shutil.rmtree(self.full_source_path.as_posix())
            return False

        self.logger.info("Installed successfully")
        return True

    async def configure(self) -> bool:
        self.logger.info("Configuring application")
        raise NotImplementedError

    async def install_and_configure(self) -> bool:
        did_install = await self.install()
        did_configure = await self.configure()

        return did_install and did_configure
