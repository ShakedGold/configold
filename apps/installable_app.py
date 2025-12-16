import io
import os
import logging
import pathlib
import shutil
import sys
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
        should_install: bool = True,
        detail: str = "",
        configuration: Configuration | None = None,
    ) -> None:
        super().__init__()
        self.label: str = label
        self.detail: str = detail
        self.should_install = should_install
        self.configuration: Configuration | None = configuration

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

    @property
    def backup_directory_path(self) -> PosixPath:
        return PosixPath(self.home_path, ".local", "backups")

    def _validate_binaries(self):
        is_any_binary_missing: bool = False

        for binary_name in type(self).BINARIES.keys():
            binary_path = utils.find_executable(binary_name)
            if binary_path is None:
                self.logger.fatal(f"BINARY NOT FOUND: {binary_name}")
                is_any_binary_missing = True

            type(self).BINARIES[binary_name] = binary_path

        if is_any_binary_missing:
            sys.exit(1)

    def _log_paths(self):
        self.logger.debug(f"home_path: {self.home_path}")
        self.logger.debug(f"full_source_path: {self.full_source_path}")
        self.logger.debug(f"full_source_directory: {self.full_source_directory}")
        self.logger.debug(
            f"full_target_directory_path: {self.full_target_directory_path}"
        )
        self.logger.debug(f"full_target_path: {self.full_target_path}")
        self.logger.debug(f"backup_directory_path: {self.backup_directory_path}")

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

        if self.configuration is None or self.configuration.widget is None:
            return

        yield Collapsible(self.configuration.widget, title="Configuration", id="config")

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

    async def _configure(self, config: Configuration) -> bool:
        raise NotImplementedError

    async def configure(self, config: Configuration) -> bool:
        self.logger.info("Configuring application")
        result: bool = await self._configure(config)

        if not result:
            self.logger.error("Failed to configure application")
            return False

        self.logger.info("Successfully configured application")
        return True

    async def install_and_configure(self) -> bool:
        did_install = await self.install()

        if self.configuration is None:
            return did_install

        did_configure = await self.configure(self.configuration)

        return did_install and did_configure
