from configuration import ConfigurationData, ConfigurationWidget


class Configuration:
    def __init__(
        self, config_data: ConfigurationData, widget: ConfigurationWidget | None = None
    ) -> None:
        self.config_data: ConfigurationData = config_data
        self.widget: ConfigurationWidget | None = widget

        if self.widget is None:
            return

        self.widget.config = self.config_data

    def config(self) -> bool:
        return self.config_data.config()
