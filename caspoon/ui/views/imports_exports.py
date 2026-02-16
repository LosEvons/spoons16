"""Imports and exports view component."""

import logging

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import AnalysisResults

logger = logging.getLogger(__name__)


class ImportsExportsView(BaseView[AnalysisResults]):
    """Display imported and exported functions.

    Shows two tables listing the imported and exported functions
    found in the executable's symbol tables side-by-side.

    Automatically updates when AppState.analysis_results changes.
    """

    def on_mount(self) -> None:
        """Subscribe to analysis results updates from AppState.

        This is called when the view is added to the app. It sets up
        the reactive subscription to analysis_results state changes.
        """
        try:
            app = self.app
            if hasattr(app, "state"):
                # Subscribe to analysis_results changes via callback
                app.state.subscribe("analysis_results", self._on_results_changed)
                logger.debug("ImportsExportsView subscribed to analysis_results updates")
        except Exception as e:
            # Handle case where app is not available (e.g., in tests)
            logger.debug(f"Could not subscribe to state in on_mount: {e}")

    def _on_results_changed(self, new_value: AnalysisResults | None) -> None:
        """Handle analysis results state changes.

        Args:
            new_value: New analysis results (or None if cleared)
        """
        # Setting self.data triggers render_content() via BaseView's watch_data()
        self.data = new_value

    def render_content(self, data: AnalysisResults) -> None:
        """Render imports and exports tables side-by-side.

        Args:
            data: Analysis results containing imports and exports
        """
        imports_panel = self._build_imports_table(data.imports or [])
        exports_panel = self._build_exports_table(data.exports or [])

        # Display side-by-side using Columns
        layout = Columns([imports_panel, exports_panel], equal=True, expand=True)
        self.update(layout)

    def _build_imports_table(self, imports: list[str]) -> Panel:
        """Build imports table.

        Args:
            imports: List of imported function names

        Returns:
            Panel containing imports table
        """
        table = Table(show_header=True, show_edge=False, expand=True, box=None)
        table.add_column("Name", style="cyan", overflow="ellipsis")

        if not imports:
            table.add_row("[dim]No imports found[/]")
        else:
            # Use sorted set to remove duplicates and sort
            # Filter out None values before sorting to avoid comparison errors
            unique_imports = sorted(set(imp or "" for imp in imports))
            for imp in unique_imports[:500]:  # Limit for performance
                table.add_row(imp or "<unnamed>")

        count = len(set(imports)) if imports else 0
        title = f"[bold]Imports ({count})[/]"
        return Panel(table, title=title, border_style="cyan", padding=(1, 2))

    def _build_exports_table(self, exports: list[str]) -> Panel:
        """Build exports table.

        Args:
            exports: List of exported function names

        Returns:
            Panel containing exports table
        """
        table = Table(show_header=True, show_edge=False, expand=True, box=None)
        table.add_column("Name", style="green", overflow="ellipsis")

        if not exports:
            table.add_row("[dim]No exports found[/]")
        else:
            # Use sorted set to remove duplicates and sort
            # Filter out None values before sorting to avoid comparison errors
            unique_exports = sorted(set(exp or "" for exp in exports))
            for exp in unique_exports[:500]:  # Limit for performance
                table.add_row(exp or "<unnamed>")

        count = len(set(exports)) if exports else 0
        title = f"[bold]Exports ({count})[/]"
        return Panel(table, title=title, border_style="green", padding=(1, 2))

    def update_data(self, report: ExecutableReport) -> None:
        """Legacy compatibility shim for old-style view updates.

        This method maintains backward compatibility with the old update pattern.
        New code should update AppState instead, which will trigger reactive updates.

        Args:
            report: ExecutableReport containing analysis results
        """
        logger.warning(
            "ImportsExportsView.update_data() is deprecated. "
            "Use app.state.analysis_results = ... for reactive updates."
        )

        # Still works - use old rendering path
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
