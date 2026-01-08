from typing import override

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Select, Switch, TextArea
from .config_data import ZshConfigData
from .plugin_managers import ZshPluginManagerType
from components.dict_modal import DictModal
from components.list_modal import ListModal
from configuration.widget import ConfigurationWidget, LabelWithTooltip


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
    def open_plugin_list_modal(self) -> None:
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
