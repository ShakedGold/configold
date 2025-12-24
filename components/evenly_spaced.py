import textual.widget


class EvenlySpaced(textual.widget.Widget):

    class _Spacer(textual.widget.Widget):
        def __init__(self, character: str = " "):
            super().__init__()
            self.character: str = character

        def render(self) -> str:
            return "\n".join(
                (
                    self.character * self.content_size.width
                    for _ in range(self.content_size.height)
                )
            )

    class _HorizontalSpacer(_Spacer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.styles.width = "1fr"

    class _VerticalSpacer(_Spacer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def __init__(self, *children, layout, **kwargs):
        def generate_children():
            # Tell children to not expand if they have no width/height set.
            if layout == "horizontal":
                for child in children:
                    if child.styles.width is None:
                        child.styles.width = "auto"
            else:
                for child in children:
                    if child.styles.height is None:
                        child.styles.height = "auto"

            # Insert one spacer between two adjacent children.
            def intersperse_spacers(children):
                for child in children[:-1]:
                    yield child
                    if layout == "horizontal":
                        yield self._HorizontalSpacer()
                    else:
                        yield self._VerticalSpacer()
                yield children[-1]

            return intersperse_spacers(children)

        super().__init__(*generate_children(), **kwargs)

        self.styles.layout = layout
        self.styles.height = "auto"
        self.styles.width = "1fr"
