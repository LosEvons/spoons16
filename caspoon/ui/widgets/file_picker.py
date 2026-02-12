
from pathlib import Path
from textual.widgets import Static, ListView, ListItem
from textual.containers import Vertical
from textual.app import ComposeResult


class FilePicker(Static):
    DEFAULT_CSS = """
    FilePicker {
        background: $panel;
        padding: 1 2;
        border: solid green;
        width: 60%;
        height: 70%;
        layer: overlay;
    }
    """

    def __init__(self, start_path=".", on_select=None):
        super().__init__()
        self.start_path = Path(start_path).resolve()
        self.on_select = on_select

    def compose(self) -> ComposeResult:
        file_list = ListView(id="file_list")
        entries = sorted(self.start_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

        for path in entries:
            prefix = "[DIR] " if path.is_dir() else "[FILE]"
            file_list.append(ListItem(f"{prefix} {path.name}"))
        
        yield Vertical(
            Static(f"Select file in: {self.start_path}", classes="title"),
            file_list
        )

    def on_list_view_selected(self, message: ListView.Selected) -> None:
        text = message.item.text
        name = text.split(" ", 1)[1]
        chosen = self.start_path / name

        if chosen.is_file():
            if self.on_select:
                self.on_select(str(chosen))
            self.remove()
        else:
            self.start_path = chosen.resolve()
            self.clear()
            self.compose()
