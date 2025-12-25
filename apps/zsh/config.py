from abc import ABC, abstractmethod
from enum import StrEnum
import json
import os
from pprint import pformat
import shutil
from pydantic import Field
from pathlib import PosixPath
from typing import ClassVar, TextIO, override

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Label
from components.dict_modal import DictModal
from configuration.widget import ConfigurationWidget
from configuration.data import ConfigurationData


class ZshPluginManagerType(StrEnum):
    ZINIT = "zinit"
    OMZ = "omz"

class ZshPluginManager(ABC):
    @abstractmethod
    def config_plugins(self, config_file: TextIO, resource_target_path: PosixPath, plugins: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        raise NotImplementedError

    @abstractmethod
    def source(self, config_file: TextIO) -> None:
        raise NotImplementedError

    @abstractmethod
    def config_theme(self, config_file: TextIO, resource_target_path: PosixPath, theme: str) -> None:
        raise NotImplementedError

class ZinitPluginManager(ZshPluginManager):
    @override
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        config_file.writelines([
            f'ZINIT_HOME="{resource_target_path}/plugin_managers/zinit"\n',
            'source "${ZINIT_HOME}/zinit.zsh"\n\n',
        ])

    @override
    def config_plugins(self, config_file: TextIO, resource_target_path: PosixPath, plugins: list[str]) -> None:
        config_file.writelines([
            f'zinit light {resource_target_path}/plugins/{plugin_name}\n' for plugin_name in plugins
        ])

    @override
    def source(self, config_file: TextIO) -> None:
        # Needed to be sourced at initialization
        _ = config_file.write('# Since we need to source zinit before, we don\'t source it here\n\n')
        return

    @override
    def config_theme(self, config_file: TextIO, resource_target_path: PosixPath, theme: str) -> None:
        _ = config_file.write(f'zinit light {resource_target_path}/themes/{theme}\n')

class OmzPluginManager(ZshPluginManager):
    @override
    def init(self, config_file: TextIO, resource_target_path: PosixPath) -> None:
        config_file.writelines([
            f'export ZSH="{resource_target_path}/plugin_managers/oh-my-zsh"\n',
            'plugins=()\n\n',
        ])

    @override
    def config_plugins(self, config_file: TextIO, resource_target_path: PosixPath, plugins: list[str]) -> None:
        config_file.writelines([
            f"plugins+=({plugin_name})\n" for plugin_name in plugins
        ])

    @override
    def source(self, config_file: TextIO) -> None:
        config_file.writelines([
            'source "${ZSH}/oh-my-zsh.sh"',
            '\n',
            '\n',
        ])

    @override
    def config_theme(self, config_file: TextIO, resource_target_path: PosixPath, theme: str) -> None:
        _ = config_file.write(f'ZSH_THEME="{theme}/{theme}"\n')

PLUGIN_MANAGERS: dict[ZshPluginManagerType, type[ZshPluginManager]] = {
    ZshPluginManagerType.ZINIT: ZinitPluginManager,
    ZshPluginManagerType.OMZ: OmzPluginManager
}

def get_plugin_manager(plugin_manager_type: ZshPluginManagerType):
    return PLUGIN_MANAGERS.get(plugin_manager_type, ZinitPluginManager)()


class ZshConfigData(ConfigurationData):
    CONFIG_FILE_NAME: ClassVar[str] = ".zshrc"

    backup_directory_path: PosixPath = Field(
        default_factory=lambda: PosixPath(os.getenv("HOME", "~"), ".local", "backups")
    )
    resource_target_path: PosixPath = Field(
        default_factory=lambda: PosixPath(os.getenv("HOME", "~"), ".local", "share", "zsh", "resources")
    )

    aliases: dict[str, str] = Field(
        default=dict(
            l="ls -lah",
            la="ls -lAh",
            ll="ls -l",
            ls="eza --icons=always",
            md="mkdir -p",
            vim="nvim",
            z="$EDITOR $HOME/.zshrc",
            zj="zellij",
            x=". $HOME/.zshrc",
            cat="bat",
            g="git",
        )
    )
    exports: dict[str, str] = Field(default=dict(EDITOR="`which nvim`"))
    plugin_manager: ZshPluginManagerType = Field(default=ZshPluginManagerType.ZINIT)
    instant_prompt: bool = Field(default=True)
    plugins: list[str] = Field(default=['zsh-syntax-highlighting', 'zsh-autosuggestions', 'zsh-vi-mode', 'fzf-tab'])
    theme: str = Field(default='powerlevel10k')
    extra: str = Field(default='')

    @property
    def resources_path(self) -> PosixPath:
        return PosixPath(__file__, "..", "resources").resolve()

    @property
    def home_path(self):
        home_path = os.getenv("HOME")
        if home_path is None:
            home_path = "~"
        return home_path

    @property
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)

    def _backup_config(self) -> None:
        self.backup_directory_path.mkdir(parents=True, exist_ok=True)

        target_backup_directory_path: str = PosixPath(
            self.backup_directory_path, self.config_path.name
        ).as_posix()

        _ = shutil.copy(
            self.config_path,
            target_backup_directory_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_directory_path}])"
        )

    def _escape_string(self, value: str) -> str:
        return json.dumps(value)[1:-1]

    def _config_aliases(self, config_file: TextIO) -> None:
        if len(self.aliases.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the aliases, they define 'commands' that will point to other commands themself, for example: A `g` alias is just an alias to `git`\n"""
        )
        aliases_raw: str = "\n".join(
            f'alias {alias_name}="{self._escape_string(alias_value)}"'
            for alias_name, alias_value in self.aliases.items()
        )
        _ = config_file.write(aliases_raw)
        _ = config_file.write("\n\n")

        self.logger.debug("Configured aliases %s", pformat(self.aliases))

    def _config_exports(self, config_file: TextIO) -> None:
        if len(self.exports.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the exports, they define variables that are accessible by other programs (plus the shell itself)\n# You can override this to whatever you want, for example: the EDITOR env variable will define what multiple programs\n# will use as their editor, for example `sudoedit` (the command to edit files as the super user)\n"""
        )

        exports_raw: str = "\n".join(
            f'export {export_name}="{self._escape_string(export_value)}"'
            for export_name, export_value in self.exports.items()
        )
        _ = config_file.write(exports_raw)
        _ = config_file.write("\n")

        self.logger.debug("Configured exports %s", pformat(self.aliases))
    
    def _copy_resources(self) -> None:
        self.resource_target_path.mkdir(parents=True, exist_ok=True)

        _ = shutil.copytree(self.resources_path.as_posix(), self.resource_target_path.as_posix(), dirs_exist_ok=True)

    def _config_instant_prompt(self, config_file: TextIO) -> None:
        if not self.instant_prompt:
            return

        config_file.writelines([
            '# Use the instant prompt (this should be the very first line in your .zshrc)\n',
            f'if [[ -r "{self.resource_target_path}/instant-prompt.zsh" ]]; then\n',
            f'  source "{self.resource_target_path}/instant-prompt.zsh"\n',
            'fi',
            '\n\n'
        ])

    def _config_p10k_prompt(self, config_file: TextIO) -> None:
        _ = config_file.write(f'# Sourcing the p10k prompt\n')
        _ = config_file.write(f'[[ ! -f {self.resource_target_path}/prompt.zsh ]] || source {self.resource_target_path}/prompt.zsh\n\n')

        self.logger.debug('Using the premade p10k prompt')

    def _source_lib_files(self, config_file: TextIO) -> None:
        _ = config_file.write(f'# Sourcing library files (you can ignore this)\n')
        _ = config_file.write(f'source {self.resource_target_path}/plugin_managers/lib/lib.zsh {self.resource_target_path}\n\n')

        self.logger.debug('Sourced library scripts to align zinit and omz')

    def _init_plugin_manager(self, config_file: TextIO, plugin_manager: ZshPluginManager) -> None:
        _ = config_file.write('# Initialize your plugin manager here\n')
        plugin_manager.init(config_file, self.resource_target_path)

        self.logger.debug('Initialized plugin manager: %s', self.plugin_manager)

    def _config_theme(self, config_file: TextIO, plugin_manager: ZshPluginManager) -> None:
        _ = config_file.write('# Setup your theme here\n')
        plugin_manager.config_theme(config_file, self.resource_target_path, self.theme)

        self.logger.debug('Configured the shell theme: %s', self.theme)

    def _config_plugins(self, config_file: TextIO, plugin_manager: ZshPluginManager) -> None:
        _ = config_file.write('# Load all of the installed plugins\n')
        plugin_manager.config_plugins(config_file, self.resource_target_path, self.plugins)
        _ = config_file.write('\n')

        self.logger.debug('Configured zsh plugins: %s', pformat(self.plugins))

    def _source_plugin_manager(self, config_file: TextIO, plugin_manager: ZshPluginManager) -> None:
        _ = config_file.write('# Source your plugin manager here\n')
        plugin_manager.source(config_file)

        self.logger.debug('Sourced the plugin manager')

    def _config_extra(self, config_file: TextIO) -> None:
        _ = config_file.write('# Here you can put anything you want to add to your zshrc\n')
        _ = config_file.write(self.extra)

        self.logger.debug('Wrote the extra zshrc lines')

    @override
    def config(self) -> bool:
        self.logger.debug("Configuration: %s", pformat(dict(self)))

        if self.config_path.exists():
            self.logger.debug(f"Configuration file exists ({self.config_path})")
            self._backup_config()

            self.config_path.unlink()
            self.logger.debug(f"Removed config file ({self.config_path})")

        plugin_manager = get_plugin_manager(self.plugin_manager)

        self._copy_resources()
        with open(self.config_path, "a+") as config_file:
            if self.theme == 'powerlevel10k':
                self._config_instant_prompt(config_file)

            self._source_lib_files(config_file)
            self._init_plugin_manager(config_file, plugin_manager)
            self._config_theme(config_file, plugin_manager)
            self._config_exports(config_file)
            self._config_aliases(config_file)
            self._config_plugins(config_file, plugin_manager)
            self._source_plugin_manager(config_file, plugin_manager)

            if self.theme == 'powerlevel10k':
                self._config_p10k_prompt(config_file)

            self._config_extra(config_file)

        return True


class ZshConfigWidget(ConfigurationWidget[ZshConfigData]):
    DEFAULT_CSS: str = """
    ZshConfigWidget > Horizontal {
        height: auto;
        width: auto;
        align: center middle;
    }

    ZshConfigWidget > Horizontal > Label {
        height: 100%;
        content-align: left middle;
    }

    ZshConfigWidget > Horizontal > * {
        width: 1fr;
    }

    ZshConfigWidget > Horizontal > Button {
        max-width: 30;
        margin: 0 2;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("Aliases")
            yield Button("Open Aliases List", id="alias-button")

        with Horizontal():
            yield Label("Exports")
            yield Button("Open Exports List", id="export-button")

    @on(Button.Pressed, "#alias-button")
    def open_aliases_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.aliases, name="Aliases"))

    @on(Button.Pressed, "#export-button")
    def open_export_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.exports, name="Exports"))
