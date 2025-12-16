from pydantic import Field
from pathlib import PosixPath
from typing import override

from textual.app import ComposeResult
from configuration.widget import ConfigurationWidget
from configuration.data import ConfigurationData


class ZshConfigData(ConfigurationData):
    config_file: PosixPath
    aliases: dict[str, str] = Field(default=dict(l="ls -la"))

    @override
    def config(self) -> bool:
        return True


class ZshConfigWidget(ConfigurationWidget):
    @override
    def compose(self) -> ComposeResult:
        raise NotImplementedError
