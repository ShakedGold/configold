# pyright: reportAttributeAccessIssue=false
import logging
from typing import Generic, TypeVar
from textual.visual import VisualType
from textual.widgets import Label, Static
from textual.widgets._label import LabelVariant

from configuration.data import ConfigurationData

T = TypeVar("T", bound=ConfigurationData)


class LabelWithTooltip(Label):
    def __init__(
        self,
        content: VisualType = "",
        tooltip: VisualType = "",
        *,
        variant: LabelVariant | None = None,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content,
            variant=variant,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.tooltip: VisualType = tooltip


class ConfigurationWidget(Static, Generic[T]):
    """
    Renders the configuration
    """

    DEFAULT_CSS: str = """
    ConfigurationWidget > Horizontal {
        margin: 1 0;
    }
    """

    def __init__(
        self,
        content: VisualType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

        self.config: T = ConfigurationData()  # pyright: ignore[reportArgumentType]
