from textual.widgets import Static
from rich.pretty import Pretty

class OverviewView(Static):
    def update_data(self, report):
        data = {
            "path": report.path,
            "arch": report.arch,
            "bits": report.bits,
            "file_type": report.file_type,
            "stripped": report.stripped,
        }
        self.update(Pretty(data, expand_all=True))
