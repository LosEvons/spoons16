"""Overview view component for displaying basic executable information."""

from textual.widgets import Static
from rich.table import Table

from caspoon.core.models import ExecutableReport


class OverviewView(Static):
    """Display overview information about the analyzed executable.
    
    Shows basic metadata including path, architecture, bit width,
    stripped status, and file type in a formatted table.
    """
    
    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.
        
        Args:
            report: ExecutableReport containing analysis results
        """
        table = Table(title="Executable Overview")
        table.add_column("Field", style="bold")
        table.add_column("Value")

        table.add_row("Path", report.path)
        table.add_row("Architecture", report.arch or "unknown")
        table.add_row("Bits", str(report.bits or "unknown"))
        table.add_row("Stripped", "Yes" if report.stripped else "No")

        short_ft = report.file_type.split(",")[0] if report.file_type else "unknown"
        table.add_row("File Type", short_ft)

        self.update(table)
