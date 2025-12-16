import logging
from pydantic.main import BaseModel
from textual.widget import Widget


class ConfigurationWidget(Widget):
    """
    Renders the configuration
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
    ) -> None:
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )
