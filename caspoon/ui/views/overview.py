from textual.widgets import Static
from rich.table import Table

class OverviewView(Static):
    def update_data(self, report):
        table = Table(title="Executable Overview")
        table.add_column("Field", style="bold")
        table.add_column("Value")

        table.add_row("Path", report.path)
        table.add_row("Architecture", report.arch or "unknown")
        table.add_row("Bits", str(report.bits or "unknown"))
        table.add_row("Stripped", "Yes" if report.stripped else "No")

        # Show only the first part of file_type to avoid huge lines
        short_ft = report.file_type.split(",")[0] if report.file_type else "unknown"
        table.add_row("File Type", short_ft)

        self.update(table)
