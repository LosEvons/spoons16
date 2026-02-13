"""Imports and exports view component."""

from rich.console import Group
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from caspoon.core.models import ExecutableReport


class ImportsExportsView(Static):
    """Display imported and exported functions.

    Shows two tables listing the imported and exported functions
    found in the executable's symbol tables.
    """

    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.

        Args:
            report: ExecutableReport containing analysis results
        """
        imports_table = Table(title="Imports")
        imports_table.add_column("Name")

        # Use sorted set to remove duplicates and sort
        for imp in sorted(set(report.imports)):
            imports_table.add_row(imp or "<unnamed>")

        exports_table = Table(title="Exports")
        exports_table.add_column("Name")

        for exp in sorted(set(report.exports)):
            exports_table.add_row(exp or "<unnamed>")

        group = Group(
            Text("Imports", style="bold yellow"),
            imports_table,
            Text("\nExports", style="bold yellow"),
            exports_table,
        )

        self.update(group)
