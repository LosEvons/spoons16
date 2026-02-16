"""Overview view component for displaying basic executable information."""

import logging

from rich.panel import Panel
from rich.table import Table

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import BinaryInfo

logger = logging.getLogger(__name__)


class OverviewView(BaseView[BinaryInfo]):
    """Display overview information about the analyzed executable.

    Shows basic metadata including path, architecture, bit width,
    stripped status, and file type in a formatted table.

    Automatically updates when AppState.binary_info changes.
    """

    def on_mount(self) -> None:
        """Subscribe to binary info updates from AppState.

        This is called when the view is added to the app. It sets up
        the reactive subscription to binary_info state changes.
        """
        try:
            app = self.app
            if hasattr(app, "state"):
                # Subscribe to binary_info changes via callback
                app.state.subscribe("binary_info", self._on_binary_info_changed)
                logger.debug("OverviewView subscribed to binary_info updates")
        except Exception as e:
            # Handle case where app is not available (e.g., in tests)
            logger.debug(f"Could not subscribe to state in on_mount: {e}")

    def _on_binary_info_changed(self, new_value: BinaryInfo | None) -> None:
        """Handle binary info state changes.

        Args:
            new_value: New binary info data (or None if cleared)
        """
        # Setting self.data triggers render_content() via BaseView's watch_data()
        self.data = new_value

    def render_content(self, data: BinaryInfo) -> None:
        """Render binary information as a formatted table.

        Args:
            data: Binary info data to display
        """
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", justify="right")
        table.add_column(style="white")

        # File information
        table.add_row("Path:", data.path)
        table.add_row("Architecture:", data.architecture)
        table.add_row("Bits:", f"{data.bits}-bit" if data.bits else "unknown")

        # File type (truncate if too long)
        file_type_display = data.file_type.split(",")[0] if data.file_type else "unknown"
        table.add_row("File Type:", file_type_display)

        # File size with formatting
        if data.file_size:
            table.add_row("Size:", f"{data.file_size:,} bytes")

        # Entry point (if available)
        if data.entry_point:
            table.add_row("Entry Point:", data.entry_point)

        # Stripped status with color coding
        stripped_status = "[red]Yes[/red]" if data.stripped else "[green]No[/green]"
        table.add_row("Stripped:", stripped_status)

        # Wrap in a panel for visual separation
        panel = Panel(
            table, title="[bold]Executable Overview[/bold]", border_style="blue", padding=(1, 2)
        )

        self.update(panel)

    def update_data(self, report: ExecutableReport) -> None:
        """Legacy compatibility shim for old-style view updates.

        This method maintains backward compatibility with the old update pattern.
        New code should update AppState instead, which will trigger reactive updates.

        Args:
            report: ExecutableReport containing analysis results
        """
        logger.warning(
            "OverviewView.update_data() is deprecated. "
            "Use app.state.binary_info = ... for reactive updates."
        )

        # Still works - extract binary info and update manually
        # This path is used for non-migrated views until full migration
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
