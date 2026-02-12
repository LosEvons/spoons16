from textual.widgets import Static
from rich.table import Table
from rich.console import Group
from rich.text import Text

class ImportsExportsView(Static):
    def update_data(self, report):
        imports_table = Table(title="Imports")
        imports_table.add_column("Name")

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