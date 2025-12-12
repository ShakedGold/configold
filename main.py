import logging
import logging.config
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

    zellij_app = ZellijApp()
    _ = await zellij_app.install_and_configure()

    nvim_app = NVIMApp()
    _ = await nvim_app.install_and_configure()

    fzf_app = FZFApp()
    _ = await fzf_app.install_and_configure()

    zoxide_app = ZoxideApp()
    _ = await zoxide_app.install_and_configure()

    fd_app = FDApp()
    _ = await fd_app.install_and_configure()

    rg_app = RipGrepApp()
    _ = await rg_app.install_and_configure()

    zsh_app = ZshApp()
    _ = await zsh_app.install_and_configure()


if __name__ == "__main__":
    asyncio.run(main())
