import logging
import logging.config
from types import CoroutineType
import yaml
import asyncio
from typing import Any, override
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType

from apps.fd import FDApp
from apps.fzf import FZFApp
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

    @override
    def compose(self) -> ComposeResult:
        raise NotImplementedError


def setup_logger():
    with open("logger.yml", "r") as f:
        config: dict[str, Any] = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


async def main():
    # app = MainApp()
    # app.run()

    setup_logger()

    app_installers: list[CoroutineType[Any, Any, bool]] = []

    # zellij_app = ZellijApp()
    # app_installers.append(zellij_app.install_and_configure())

    # nvim_app = NVIMApp()
    # app_installers.append(nvim_app.install_and_configure())

    # fzf_app = FZFApp()
    # app_installers.append(fzf_app.install_and_configure())

    # zoxide_app = ZoxideApp()
    # app_installers.append(zoxide_app.install_and_configure())

    # fd_app = FDApp()
    # app_installers.append(fd_app.install_and_configure())

    # rg_app = RipGrepApp()
    # app_installers.append(rg_app.install_and_configure())

    zsh_app = ZshApp()
    app_installers.append(zsh_app.install_and_configure())

    _ = await asyncio.gather(*app_installers)


if __name__ == "__main__":
    asyncio.run(main())
