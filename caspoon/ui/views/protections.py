from textual.widgets import Static
from rich.table import Table

class ProtectionsView(Static):
    def update_data(self, report):
        pi = report.protections
        if not pi:
            self.update("No protection information available.")
            return

        table = Table(title="Binary Protections", show_header=False)
        table.add_column("Feature")
        table.add_column("Status")

        def yn(flag: bool) -> str:
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
