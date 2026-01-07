import json
import os
import shutil
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import PosixPath
from pprint import pformat
from typing import ClassVar, TextIO, override

from pydantic import Field
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Select, Switch, TextArea

from components.dict_modal import DictModal
from components.list_modal import ListModal
from configuration.data import ConfigurationData
from configuration.widget import ConfigurationWidget, LabelWithTooltip
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


PLUGIN_MANAGERS: dict[ZshPluginManagerType, type[ZshPluginManager]] = {
    ZshPluginManagerType.ZINIT: ZinitPluginManager,
    ZshPluginManagerType.OMZ: OmzPluginManager,
}


def get_plugin_manager(plugin_manager_type: ZshPluginManagerType):
    return PLUGIN_MANAGERS.get(plugin_manager_type, ZinitPluginManager)()


class ZshConfigData(ConfigurationData):
    CONFIG_FILE_NAME: ClassVar[str] = ".zshrc"

    resource_target_path: PosixPath = Field(
        default_factory=lambda: PosixPath(
            os.getenv("HOME", "~"), ".local", "share", "zsh", "resources"
        )
    )

    aliases: dict[str, str | BinaryRequirement[str]] = Field(
        default=dict(
            l="ls -lah",
            la="ls -lAh",
            ll="ls -l",
            ls=BinaryRequirement("eza --icons=always", ["eza"]),
            md="mkdir -p",
            vim=BinaryRequirement("nvim", ["nvim"]),
            z="$EDITOR $HOME/.zshrc",
            zj=BinaryRequirement("zellij", ["zellij"]),
            x=". $HOME/.zshrc",
            cat=BinaryRequirement("bat", ["bat"]),
            g="git",
        )
    )
    "The aliases list (shortcuts for commands)"

    suffix_aliases: dict[str, str | BinaryRequirement[str]] = Field(
        default=dict(
            c=BinaryRequirement("bat -l c", ["bat"], must_have=False),
            py=BinaryRequirement("bat -l py", ["bat"], must_have=False),
            md=BinaryRequirement("bat", ["bat"], must_have=False),
            yaml=BinaryRequirement("bat -l yaml", ["bat"], must_have=False),
            yml=BinaryRequirement("bat -l yaml", ["bat"], must_have=False),
            json=BinaryRequirement("jless", ["jless"], must_have=False),
        )
    )
    "Like the aliases but at the end of a command instead of at the start"

    exports: dict[str, str | BinaryRequirement[str]] = Field(
        default=dict(EDITOR="`which nvim`")
    )
    "Exported variables that can be used anywhere (example: echo $VARIABLE_NAME)"

    plugin_manager: ZshPluginManagerType = Field(default=ZshPluginManagerType.ZINIT)
    "The plugin manager controls how the plugins are installed"

    instant_prompt: bool = Field(default=True)
    "If you use p10k, then display the prompt immedietly while zsh is loading"

    plugins: list[str | BinaryRequirement[str]] = Field(
        default=[
            "zsh-syntax-highlighting",
            "zsh-autosuggestions",
            "zsh-vi-mode",
            BinaryRequirement(value="fzf-tab", binaries=["fzf"]),
            "command-not-found",
        ],
    )
    "The list of plugins you want to use"

    theme: str = Field(default="powerlevel10k")
    "The theme you wish to use"

    history_options: dict[str, str] = Field(
        default={
            "HISTSIZE": "5000",
            "HISTFILE": "~/.zsh_history",
            "SAVEHIST": "$HISTSIZE",
            "HISTDUP": "erase",
            "options": "appendhistory sharehistory hist_ignore_space hist_ignore_all_dups hist_save_no_dups hist_ignore_dups hist_find_no_dups",
        }
    )
    "History options, like the size of the command list, and how and when to save them"

    zstyle: list[str | BinaryRequirement[str]] = Field(
        default=[
            "# Allow completions to be case insensitive\nzstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'",
            """# Make the autocomplete for ls colorful\nzstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}" """,
            "# Disable the default zsh completion menu\nzstyle ':completion:*' menu no",
            BinaryRequirement(
                "# Preview directory's content with eza when completing cd\nzstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'",
                ["fzf", "eza"],
            ),
            "# Enable group description colors\nzstyle ':completion:*:descriptions' format '[%d]'",
        ]
    )
    "Settings for zsh and it's plugins"

    evals: list[str] = Field(default=["fzf --zsh"])
    "Evaluations are shell code that is being executed inside the current script (basically a copy, paste and execute at once)"

    autoloads: list[str] = Field(
        default=["compinit", "zmv # A file mover with pattern matching"]
    )
    "Autoloads are extra functions that zsh export for you"

    extra: str = Field(default="")
    "Any extra zshrc configuration you want"

    recommended_extras: bool = Field(default=True)
    "My recommended extra zshrc configurations :)"

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
    @override
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)

    @override
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

    def _escape_string(self, value: str | BinaryRequirement[str]) -> str:
        return json.dumps(str(value))[1:-1]

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

    def _config_suffix_aliases(self, config_file: TextIO) -> None:
        if len(self.suffix_aliases.keys()) == 0:
            return

        _ = config_file.write(
            """\n# This is the suffix aliases, they are like aliases but can be at the end of the command you run\n# This can be used for many things, like: opening files with the correct program depending on the file type\n"""
        )
        aliases_raw: str = "\n".join(
            f'alias -s {alias_name}="{self._escape_string(alias_value)}"'
            for alias_name, alias_value in self.suffix_aliases.items()
        )
        _ = config_file.write(aliases_raw)
        _ = config_file.write("\n\n")

        self.logger.debug("Configured suffix aliases %s", pformat(self.suffix_aliases))

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

        _ = shutil.copytree(
            self.resources_path.as_posix(),
            self.resource_target_path.as_posix(),
            dirs_exist_ok=True,
        )

    def _config_instant_prompt(self, config_file: TextIO) -> None:
        if not self.instant_prompt:
            return

        config_file.writelines(
            [
                "# Use the instant prompt (this should be the very first line in your .zshrc)\n",
                f'if [[ -r "{self.resource_target_path}/instant-prompt.zsh" ]]; then\n',
                f'  source "{self.resource_target_path}/instant-prompt.zsh"\n',
                "fi",
                "\n\n",
            ]
        )

    def _config_p10k_prompt(self, config_file: TextIO) -> None:
        _ = config_file.write("# Sourcing the p10k prompt\n")
        _ = config_file.write(
            f"[[ ! -f {self.resource_target_path}/prompt.zsh ]] || source {self.resource_target_path}/prompt.zsh\n\n"
        )

        self.logger.debug("Using the premade p10k prompt")

    def _source_lib_files(self, config_file: TextIO) -> None:
        _ = config_file.write("# Sourcing library files (you can ignore this)\n")
        _ = config_file.write(
            f"source {self.resource_target_path}/plugin_managers/lib/lib.zsh {self.resource_target_path}\n\n"
        )

        self.logger.debug("Sourced library scripts to align zinit and omz")

    def _init_plugin_manager(
        self, config_file: TextIO, plugin_manager: ZshPluginManager
    ) -> None:
        _ = config_file.write("# Initialize your plugin manager here\n")
        plugin_manager.init(config_file, self.resource_target_path)

        self.logger.debug("Initialized plugin manager: %s", self.plugin_manager)

    def _config_theme(
        self, config_file: TextIO, plugin_manager: ZshPluginManager
    ) -> None:
        _ = config_file.write("# Setup your theme here\n")
        plugin_manager.config_theme(config_file, self.resource_target_path, self.theme)

        self.logger.debug("Configured the shell theme: %s", self.theme)

    def _config_plugins(
        self, config_file: TextIO, plugin_manager: ZshPluginManager
    ) -> None:
        _ = config_file.write("# Load all of the installed plugins\n")
        plugin_manager.config_plugins(
            config_file, self.resource_target_path, self.plugins
        )
        _ = config_file.write("\n")

        self.logger.debug("Configured zsh plugins: %s", pformat(self.plugins))

    def _source_plugin_manager(
        self, config_file: TextIO, plugin_manager: ZshPluginManager
    ) -> None:
        _ = config_file.write("# Source your plugin manager here\n")
        plugin_manager.source(config_file)

        self.logger.debug("Sourced the plugin manager")

    def _config_extra(self, config_file: TextIO) -> None:
        _ = config_file.write(
            "# Here you can put anything you want to add to your zshrc\n"
        )
        _ = config_file.write(self.extra)

        self.logger.debug("Wrote the extra zshrc lines")

    def _config_history(self, config_file: TextIO) -> None:
        _ = config_file.write("# History options\n")

        for key, value in self.history_options.items():
            if key == "options":
                _ = config_file.write(f"setopt {value}\n")
            else:
                _ = config_file.write(f"{key}={value}\n")

        _ = config_file.write("\n")

    def _config_zstyle(self, config_file: TextIO) -> None:
        _ = config_file.write(
            "# Zsh Styling, this is used for many options of the shell itself, from completions, to plugins\n"
        )

        config_file.writelines([str(style) + "\n" for style in self.zstyle])
        _ = config_file.write("\n")

    def _config_autoloads(self, config_file: TextIO) -> None:
        _ = config_file.write(
            "# Autoloads, these are extra functions that zsh exposes and you can enable\n"
        )

        config_file.writelines(
            [f"autoload -U {autoload}\n" for autoload in self.autoloads]
        )

        if "compinit" in self.autoloads:
            _ = config_file.write(
                "\n# compinit needs to run after it is autoloaded (to refresh the completions)\ncompinit\n"
            )

        _ = config_file.write("\n")

    def _config_evals(self, config_file: TextIO) -> None:
        _ = config_file.write("# Evaluations, for shell integrations and more\n")

        config_file.writelines(
            [f'eval "$({evaluation})"\n' for evaluation in self.evals]
        )
        _ = config_file.write("\n")

    def _config_recommended_extras(self, config_file: TextIO) -> None:
        _ = config_file.write("# Recommended extras for your configuration\n")

        if self.plugin_manager == ZshPluginManagerType.ZINIT:
            _ = config_file.write("zinit cdreplay -q\n")

        if "zsh-vi-mode" in self.plugins:
            _ = config_file.write(
                "\n# Only changing the escape key to `jk` in insert mode, we still\n# keep using the default keybindings `^[` in other modes\nZVM_VI_INSERT_ESCAPE_BINDKEY=jk\n"
            )

            _ = config_file.writelines(
                [
                    "ZVM_VI_HIGHLIGHT_BACKGROUND=#ffffff\n",
                    "ZVM_VI_HIGHLIGHT_FOREGROUND=#000000\n",
                ]
            )

        _ = config_file.write("\n")

    @override
    def _config(self) -> bool:
        plugin_manager = get_plugin_manager(self.plugin_manager)

        self._copy_resources()
        with open(self.config_path, "a+") as config_file:
            if self.theme == "powerlevel10k":
                self._config_instant_prompt(config_file)

            self._source_lib_files(config_file)
            self._init_plugin_manager(config_file, plugin_manager)
            self._config_theme(config_file, plugin_manager)
            self._config_exports(config_file)
            self._config_aliases(config_file)
            self._config_suffix_aliases(config_file)
            self._config_plugins(config_file, plugin_manager)
            self._source_plugin_manager(config_file, plugin_manager)

            if self.theme == "powerlevel10k":
                self._config_p10k_prompt(config_file)

            self._config_history(config_file)
            self._config_zstyle(config_file)
            self._config_autoloads(config_file)
            self._config_evals(config_file)
            if self.recommended_extras:
                self._config_recommended_extras(config_file)
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

    #instant-prompt {
        max-width: 10;
    }

    #extra-label {
        margin: 1 0;
    }

    #extra-area {
        width: 100%;
        height: auto;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            plugin_managers = list(ZshPluginManagerType)
            yield LabelWithTooltip(
                "Plugin Manager", self.config.descriptions.plugin_manager
            )
            yield Select(
                [
                    (plugin_manager_name, index)
                    for index, plugin_manager_name in enumerate(plugin_managers)
                ],
                allow_blank=False,
                id="plugin-manager",
            )

        with Horizontal():
            yield LabelWithTooltip("Theme", self.config.descriptions.theme)
            yield Input(value=self.config.theme, id="theme")

        with Horizontal():
            yield LabelWithTooltip(
                "Instant Prompt [b](only for p10k)[/]",
                str(self.config.descriptions.instant_prompt),
            )
            yield Switch(
                value=self.config.instant_prompt, animate=False, id="instant-prompt"
            )

        with Horizontal():
            yield LabelWithTooltip("Plugins", str(self.config.descriptions.plugins))
            yield Button("Open Plugins List", id="plugins-button")

        with Horizontal():
            yield LabelWithTooltip("Aliases", str(self.config.descriptions.aliases))
            yield Button("Open Aliases List", id="alias-button")

        with Horizontal():
            yield LabelWithTooltip("Exports", str(self.config.descriptions.exports))
            yield Button("Open Exports List", id="export-button")

        yield LabelWithTooltip(
            "Extra", str(self.config.descriptions.extra), id="extra-label"
        )
        yield TextArea.code_editor(
            text=self.config.extra,
            language="bash",
            placeholder="Type whatever zshrc that you want to add",
            id="extra-area",
        )

    @on(Select.Changed, "#plugin-manager")
    def plugin_manager_selection_changed(self, changed: Select.Changed) -> None:
        selected_plugin_manager = list(ZshPluginManagerType)[int(str(changed.value))]
        self.config.plugin_manager = selected_plugin_manager

    @on(Button.Pressed, "#alias-button")
    def open_aliases_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.aliases, name="Aliases"))

    @on(Button.Pressed, "#export-button")
    def open_export_list_modal(self) -> None:
        _ = self.app.push_screen(DictModal(self.config.exports, name="Exports"))

    @on(Button.Pressed, "#plugins-button")
    def open_export_list_modal(self) -> None:
        _ = self.app.push_screen(ListModal(self.config.plugins, name="Plugins"))

    @on(Input.Blurred, "#theme")
    def theme_changed(self, blurred: Input.Blurred):
        self.config.theme = blurred.value

    @on(Switch.Changed, "#instant-prompt")
    def instant_prompt_changed(self, changed: Switch.Changed):
        self.config.instant_prompt = changed.value

    @on(TextArea.SelectionChanged, "#extra-label")
    def extra_changed(self, selection_changed: TextArea.SelectionChanged) -> None:
        self.config.extra = selection_changed.text_area.text
