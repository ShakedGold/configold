from pathlib import PosixPath
from typing import TextIO, override
from .plugin_manager import ZshPluginManager
from utils.requirements.binary_requirements import BinaryRequirement


class ZinitPluginManager(ZshPluginManager):
    @override
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        config_file.writelines(
            [
                f'ZINIT_HOME="{resource_target_path}/plugin_managers/zinit"\n',
                'source "${ZINIT_HOME}/zinit.zsh"\n\n',
            ]
        )

    @override
    def config_plugins(
        self,
        config_file: TextIO,
        resource_target_path: PosixPath,
        plugins: list[str | BinaryRequirement[str]],
    ) -> None:
        config_file.writelines(
            [
                f"zinit light {resource_target_path}/plugins/{plugin_name}\n"
                for plugin_name in plugins
            ]
        )

    @override
    def source(self, config_file: TextIO) -> None:
        # Needed to be sourced at initialization
        _ = config_file.write(
            "# Since we need to source zinit before, we don't source it here\n\n"
        )
        return

    @override
    def config_theme(
        self, config_file: TextIO, resource_target_path: PosixPath, theme: str
    ) -> None:
        _ = config_file.write(f"zinit light {resource_target_path}/themes/{theme}\n")
