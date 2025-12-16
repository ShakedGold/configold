from textual.app import ComposeResult
from textual.widget import Widget
from configuration import ConfigurationData, ConfigurationWidget


class Configuration:
    def __init__(
        self, config_data: ConfigurationData, widget: ConfigurationWidget | None = None
    ) -> None:
        self.config_data: ConfigurationData = config_data
        self.widget: ConfigurationWidget | None = widget

    def compose(self) -> ComposeResult:
        if self.widget is None:
            return Widget().compose()

        return self.widget.compose()

    def config(self) -> bool:
        return self.config_data.config()
