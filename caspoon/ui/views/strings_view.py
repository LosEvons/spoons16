from textual.widgets import Static
from rich.console import Group
from rich.text import Text

class StringsView(Static):
    def update_data(self, report):
        if not report.strings:
            self.update("No interesting strings found.")
            return

        group = Group(*[Text(s) for s in report.strings])
        self.update(group)