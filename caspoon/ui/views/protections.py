from textual.widgets import Static
from rich.pretty import Pretty

class ProtectionsView(Static):
    def update_data(self, report):
        self.update(Pretty(report.protections, expand_all=True))