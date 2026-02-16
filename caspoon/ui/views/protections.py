"""Protections view component for displaying security features."""

import logging

from rich.panel import Panel
from rich.table import Table

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import AnalysisResults

logger = logging.getLogger(__name__)


class ProtectionsView(BaseView[dict]):
    """Display security protection features of the executable.

    Shows security hardening features including PIE, NX, stack canary,
    and RELRO with color-coded status indicators.

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
                logger.debug("ProtectionsView subscribed to analysis_results updates")
        except Exception as e:
            # Handle case where app is not available (e.g., in tests)
            logger.debug(f"Could not subscribe to state in on_mount: {e}")

    def _on_results_changed(self, new_value: AnalysisResults | None) -> None:
        """Handle analysis results state changes.

        Extracts the protections dict from analysis results.

        Args:
            new_value: New analysis results (or None if cleared)
        """
        if new_value and new_value.protections:
            # Setting self.data triggers render_content() via BaseView's watch_data()
            self.data = new_value.protections
        else:
            # Clear the view if no protections available
            self.data = {}

    def render_content(self, data: dict) -> None:
        """Render protections status table.

        Args:
            data: Dictionary of protection name -> status
        """
        if not data:
            self.update("[dim]No protection information available.[/dim]")
            return

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold cyan", justify="right")
        table.add_column()

        # Display standard protections with color coding
        protection_names = {
            "pie": "PIE",
            "nx": "NX",
            "canary": "Canary",
            "relro": "RELRO",
        }

        for key, display_name in protection_names.items():
            status = data.get(key)
            status_str = self._format_status(key, status)
            table.add_row(f"{display_name}:", status_str)

        # Wrap in a panel for visual separation
        panel = Panel(
            table, title="[bold]Binary Protections[/bold]", border_style="yellow", padding=(1, 2)
        )

        self.update(panel)

    def _format_status(self, protection_name: str, status: bool | str | None) -> str:
        """Format protection status with color coding.

        Args:
            protection_name: Name of the protection (for special handling)
            status: Status value (bool, string, or None)

        Returns:
            Formatted string with color markup
        """
        # Handle RELRO special case (has "none", "partial", "full" values)
        if protection_name == "relro" and isinstance(status, str):
            relro_colors = {
                "none": "[red]None[/red]",
                "partial": "[yellow]Partial[/yellow]",
                "full": "[green]Full[/green]",
            }
            return relro_colors.get(status.lower(), f"[dim]{status}[/dim]")

        # Handle boolean values
        if isinstance(status, bool):
            return "[green]YES[/green]" if status else "[red]NO[/red]"

        # Handle string values
        if isinstance(status, str):
            status_lower = status.lower()
            if status_lower in ["enabled", "yes", "true"]:
                return "[green]YES[/green]"
            elif status_lower in ["disabled", "no", "false"]:
                return "[red]NO[/red]"

        # Unknown/None status
        return "[dim]Unknown[/dim]"

    def update_data(self, report: ExecutableReport) -> None:
        """Legacy compatibility shim for old-style view updates.

        This method maintains backward compatibility with the old update pattern.
        New code should update AppState instead, which will trigger reactive updates.

        Args:
            report: ExecutableReport containing analysis results
        """
        logger.warning(
            "ProtectionsView.update_data() is deprecated. "
            "Use app.state.analysis_results = ... for reactive updates."
        )

        # Still works - extract protections and update manually
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
