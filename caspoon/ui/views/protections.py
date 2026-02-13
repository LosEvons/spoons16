"""Protections view component for displaying security features."""

from rich.table import Table
from textual.widgets import Static

from caspoon.core.models import ExecutableReport


class ProtectionsView(Static):
    """Display security protection features of the executable.

    Shows security hardening features including PIE, NX, stack canary,
    and RELRO with color-coded status indicators.
    """

    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.

        Args:
            report: ExecutableReport containing analysis results
        """
        pi = report.protections
        if not pi:
            self.update("No protection information available.")
            return

        table = Table(title="Binary Protections", show_header=False)
        table.add_column("Feature")
        table.add_column("Status")

        def yn(flag: bool) -> str:
            """Format boolean flag as colored YES/NO.

            Args:
                flag: Boolean value to format

            Returns:
                Formatted string with color markup
            """
            return "[green]YES[/green]" if flag else "[red]NO[/red]"

        table.add_row("PIE", yn(pi.pie))
        table.add_row("NX", yn(pi.nx))
        table.add_row("Canary", yn(pi.canary))

        relro_display = {
            "none": "[red]None[/red]",
            "partial": "[yellow]Partial[/yellow]",
            "full": "[green]Full[/green]",
        }.get(pi.relro, pi.relro)

        table.add_row("RELRO", relro_display)

        self.update(table)
