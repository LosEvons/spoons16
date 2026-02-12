from textual.widgets import Static
from rich.pretty import Pretty

class ImportsExportsView(Static):
    def update_data(self, report):
        data = {
            "imports": report.imports,
            "exports": report.exports,
        }
        self.update(Pretty(data, expand_all=True))