from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import PosixPath
from typing import TextIO

from utils.requirements.binary_requirements import BinaryRequirement


class ZshPluginManagerType(StrEnum):
    ZINIT = "ZInit"
    OMZ = "Oh My Zsh"


class ZshPluginManager(ABC):
    @abstractmethod
    def config_plugins(
        self,
        config_file: TextIO,
        resource_target_path: PosixPath,
        plugins: list[str | BinaryRequirement[str]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        raise NotImplementedError

    @abstractmethod
    def source(self, config_file: TextIO) -> None:
        raise NotImplementedError

    @abstractmethod
    def config_theme(
        self, config_file: TextIO, resource_target_path: PosixPath, theme: str
    ) -> None:
        raise NotImplementedError
