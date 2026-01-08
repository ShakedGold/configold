from typing import override

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Switch

from .config_data import ZellijConfigData
from configuration import ConfigurationWidget
from configuration.widget import LabelWithTooltip


class ZellijConfigWidget(ConfigurationWidget[ZellijConfigData]):
    DEFAULT_CSS: str = """
    ZellijConfigWidget > Horizontal {
        height: auto;
        width: auto;
        align: center middle;
    }

    ZellijConfigWidget > Horizontal > Label {
        height: 100%;
        content-align: left middle;
    }

    ZellijConfigWidget > Horizontal > * {
        width: 1fr;
    }

    ZellijConfigWidget > Horizontal > Button {
        max-width: 30;
        margin: 0 2;
    }

    ZellijConfigWidget > Horizontal > Switch {
        max-width: 10;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield LabelWithTooltip(
                "Default Layout", str(self.config.descriptions.default_layout)
            )
            yield Input(self.config.default_layout, id="default-layout")

        with Horizontal():
            yield LabelWithTooltip(
                "Startup Tips", str(self.config.descriptions.startup_tips)
            )
            yield Switch(self.config.startup_tips, animate=False, id="startup-tips")

        with Horizontal():
            yield LabelWithTooltip(
                "Pane Frames", str(self.config.descriptions.pane_frames)
            )
            yield Switch(self.config.pane_frames, animate=False, id="pane-frames")

        with Horizontal():
            yield LabelWithTooltip(
                "Auto attach to session",
                str(self.config.descriptions.auto_attach_to_session),
            )
            yield Input(self.config.auto_attach_to_session, id="auto-attach")

        with Horizontal():
            yield LabelWithTooltip(
                "Theme",
                str(self.config.descriptions.theme),
            )
            yield Input(self.config.theme, id="theme")

    @on(Input.Blurred, "#default-layout")
    def default_layout_changed(self, layout_changed: Input.Blurred) -> None:
        self.config.default_layout = layout_changed.value

    @on(Switch.Changed, "#startup-tips")
    def startup_tips_changed(self, startup_tips_changed: Switch.Changed) -> None:
        self.config.startup_tips = startup_tips_changed.value

    @on(Switch.Changed, "#pane-frames")
    def pane_frames_changed(self, pane_frames_changed: Switch.Changed) -> None:
        self.config.pane_frames = pane_frames_changed.value

    @on(Input.Blurred, "#auto-attach")
    def auto_attach_changed(self, attach_changed: Input.Changed) -> None:
        self.config.auto_attach_to_session = attach_changed.value

    @on(Input.Blurred, "#theme")
    def theme_changed(self, theme_changed: Input.Changed) -> None:
        self.config.theme = theme_changed.value
