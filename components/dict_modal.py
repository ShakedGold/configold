import logging
from typing import Text, override
from textual import on, highlight
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.dom import DOMNode
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from utils.requirements.binary_requirements import BinaryRequirement


class DictModal(ModalScreen):
    def __init__(
        self,
        data: dict[str, str | BinaryRequirement[str]],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)

        self.original_data: dict[str, str | BinaryRequirement[str]] = data.copy()
        self.data: dict[str, str | BinaryRequirement[str]] = data
        self.create_new_item: bool = False
        self.new_key: str | None = None
        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

    DEFAULT_CSS = """
    DictModal {
        align: center middle;
    }

    DictModal > Container {
        width: 80%;
        height: auto;
        max-height: 100%;
        border: thick $background 80%;
        background: $surface;
    }

    DictModal > Container > Container > Horizontal {
        width: auto;
        height: auto;
        margin: 1 0;
    }

    DictModal > Container > Container > Horizontal Input {
        max-height: 3;
        height: auto;
    }

    DictModal > Container > Container {
        overflow: auto;
    }

    #header {
        padding: 0 2;
        width: 1fr;
        height: 3;
        align: left middle;
    }
    #header > Label {
        width: 1fr;
    }

    #title {
        width: auto;
        height: 100%;
    }

    #title {
        content-align: left middle;
    }

    #footer {
        width: 1fr;
        height: auto;
        align: center middle;
    }
    #footer > Button {
        margin: 2 4;
    }

    .key { width: 1fr; height: 10; min-height: 10; }
    .value { width: 1fr; height: 10; min-height: 10; }
    """

    @override
    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal(id="header"):
                if self.name is not None:
                    yield Label(f"[b u]{self.name}[/]", id="title")
                yield Button("+", id="create", variant="primary")

            with Container():
                for key, value in self.data.items():
                    yield Horizontal(
                        Input(key, classes="key"),
                        Input(str(value), classes="value"),
                    )

                if self.create_new_item:
                    yield Horizontal(
                        Input("", classes="key", id="new-key"),
                        Input("", classes="value", id="new-value"),
                    )

            with Horizontal(id="footer"):
                yield Button("Cancel", id="cancel", variant="error")
                yield Button("Save", id="save", variant="success")

    def _set_new_item(self, container: DOMNode):
        self.create_new_item = False

        key: str = ""
        value: str = ""

        for child in container.children:
            if not isinstance(child, Input):
                continue
            if child.id == "new-key":
                key = child.value
            if child.id == "new-value":
                value = child.value

        self.data[key] = value

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        _ = self.app.pop_screen()
        self.data.clear()
        self.data.update(self.original_data)

    @on(Button.Pressed, "#save")
    def save(self) -> None:
        _ = self.app.pop_screen()

    @on(Button.Pressed, "#create")
    async def create(self) -> None:
        self.create_new_item = True
        _ = await self.recompose()

    @on(Input.Blurred, "#new-key")
    async def new_key_changed(self, event: Input.Blurred) -> None:
        if event.input.parent is None:
            return

        self._set_new_item(event.input.parent)

    @on(Input.Blurred, "#new-value")
    async def new_value_changed(self, event: Input.Blurred) -> None:
        if event.input.parent is None:
            return

        self._set_new_item(event.input.parent)
