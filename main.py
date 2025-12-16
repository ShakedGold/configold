import asyncio
import logging
import logging.config
import sys
from textual.driver import Driver
from textual.types import CSSPathType
from textual.widgets import Button, Header
import yaml
from typing import Any, Type, override
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType

from apps.eza import EzaApp
from apps.fd import FDApp
from apps.fzf import FZFApp
from apps.installable_app import InstallableApp
from apps.nvim import NVIMApp
from apps.ripgrep import RipGrepApp
from apps.zellij import ZellijApp
from apps.zoxide import ZoxideApp
from apps.zsh import ZshApp


class MainApp(App):
    BINDINGS: list[BindingType] = [
        Binding("q", "quit", "Quit the application"),
        Binding("ctrl+c", "quit", "Quit the application"),
    ]

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.apps: list[InstallableApp] = [
            ZshApp(),
            ZellijApp(),
            NVIMApp(),
            FDApp(),
            FZFApp(),
            RipGrepApp(),
            ZoxideApp(),
            EzaApp(),
        ]

    @override
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="configold")
        for app in self.apps:
            yield app

        yield Button("DONE", id="finish")

    async def on_button_pressed(self, event: Button.Pressed):
        button: Button = event.button
        if button.id != "finish":
            return

        for app in self.apps:
            _ = await app.install_and_configure()

        sys.exit()


def setup_logger():
    with open("logger.yml", "r") as f:
        config: dict[str, Any] = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


async def main():
    setup_logger()

    app = MainApp()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
