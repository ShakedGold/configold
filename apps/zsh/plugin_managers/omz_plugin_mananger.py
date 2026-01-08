from pathlib import PosixPath
from typing import TextIO, override
from .plugin_manager import ZshPluginManager
from utils.requirements.binary_requirements import BinaryRequirement


class OmzPluginManager(ZshPluginManager):
    @override
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        config_file.writelines(
            [
                f'export ZSH="{resource_target_path}/plugin_managers/oh-my-zsh"\n',
                "plugins=()\n\n",
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
            [f"plugins+=({plugin_name})\n" for plugin_name in plugins]
        )

    @override
    def source(self, config_file: TextIO) -> None:
        config_file.writelines(
            [
                'source "${ZSH}/oh-my-zsh.sh"',
                "\n",
                "\n",
            ]
        )

    @override
    def config_theme(
        self, config_file: TextIO, resource_target_path: PosixPath, theme: str
    ) -> None:
        _ = config_file.write(f'ZSH_THEME="{theme}/{theme}"\n')
