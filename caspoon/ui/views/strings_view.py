"""Strings view component for displaying extracted strings."""

import logging

from rich.panel import Panel
from rich.table import Table
from textual.binding import Binding

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.models import AnalysisResults

logger = logging.getLogger(__name__)

# Maximum strings to display to prevent UI slowdown
MAX_DISPLAY_STRINGS = 1000


class StringsView(InteractiveView[list[str]]):
    """Display extracted strings from the executable.

    Shows a list of printable strings found in the binary with filtering
    capability and keyboard navigation. Automatically updates when
    AppState.analysis_results.strings changes.
    """

    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("enter", "select_item", "Select", show=True),
        Binding("c", "clear_filter", "Clear Filter", show=True),
    ]

    def __init__(self, **kwargs):
        """Initialize StringsView with empty string lists."""
        super().__init__(**kwargs)
        self._strings = []
        self._filtered = []

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
                logger.debug("StringsView subscribed to analysis_results updates")
        except Exception as e:
            # Handle case where app is not available (e.g., in tests)
            logger.debug(f"Could not subscribe to state in on_mount: {e}")

    def _on_results_changed(self, new_value: AnalysisResults | None) -> None:
        """Handle analysis results state changes.

        Extracts the strings list from analysis results.

        Args:
            new_value: New analysis results (or None if cleared)
        """
        if new_value and new_value.strings:
            # Setting self.data triggers render_content() via BaseView's watch_data()
            self.data = new_value.strings
        else:
            # Clear the view if no strings available
            self.data = []

    def render_content(self, data: list[str]) -> None:
        """Render strings list with current filter applied.

        Args:
            data: List of strings to display
        """
        self._strings = data
        # Apply current filter (will be empty string initially)
        self.apply_filter(self.filter_text)

    def apply_filter(self, text: str) -> None:
        """Apply filter to strings and re-render the view.

        Performs case-insensitive substring matching.

        Args:
            text: Filter string (empty for no filter)
        """
        if not text:
            self._filtered = self._strings
        else:
            text_lower = text.lower()
            self._filtered = [s for s in self._strings if text_lower in s.lower()]

        # Reset selection to top when filter changes
        if self.selected_index >= len(self._filtered):
            self.selected_index = 0

        self._render_strings()

    def _render_strings(self) -> None:
        """Render the filtered string list as a table."""
        if not self._filtered:
            self.update("[dim]No strings found.[/dim]")
            return

        table = Table(show_header=True, show_edge=False, expand=True)
        table.add_column("Index", style="dim", width=6)
        table.add_column("String", style="white", overflow="ellipsis")

        # Limit displayed strings to prevent UI slowdown
        display_count = min(len(self._filtered), MAX_DISPLAY_STRINGS)
        for i in range(display_count):
            string = self._filtered[i]

            # Truncate very long strings
            if len(string) > 100:
                string = string[:97] + "..."

            # Highlight selected row
            style = "reverse bold" if i == self.selected_index else ""
            table.add_row(str(i), string, style=style)

        # Show count with filter status
        total = len(self._strings)
        filtered = len(self._filtered)

        if filtered < total:
            title = f"[bold]Strings ({filtered} / {total})[/]"
        else:
            title = f"[bold]Strings ({total})[/]"

        if self.filter_text:
            title += f" [dim]- filter: '{self.filter_text}'[/]"

        if filtered > MAX_DISPLAY_STRINGS:
            title += f" [dim](showing first {MAX_DISPLAY_STRINGS})[/]"

        panel = Panel(table, title=title, border_style="green", padding=(1, 1))
        self.update(panel)

    def get_item_count(self) -> int:
        """Return number of filtered strings.

        Returns:
            Number of strings after filtering (up to MAX_DISPLAY_STRINGS)
        """
        return min(len(self._filtered), MAX_DISPLAY_STRINGS)

    def on_item_selected(self, index: int) -> None:
        """Handle string selection.

        Args:
            index: Index of selected string
        """
        if 0 <= index < len(self._filtered):
            selected_string = self._filtered[index]
            logger.debug(f"String selected: {selected_string[:50]}...")
            # Could post message for string details in future

    def action_clear_filter(self) -> None:
        """Clear current filter."""
        self.filter_text = ""

    def watch_selected_index(self, old_index: int, new_index: int) -> None:
        """Re-render when selection changes.

        Args:
            old_index: Previous selection index
            new_index: New selection index
        """
        self._render_strings()

    def update_data(self, report: ExecutableReport) -> None:
        """Legacy compatibility shim for old-style view updates.

        This method maintains backward compatibility with the old update pattern.
        New code should update AppState instead, which will trigger reactive updates.

        Args:
            report: ExecutableReport containing analysis results
        """
        logger.warning(
            "StringsView.update_data() is deprecated. "
            "Use app.state.analysis_results = ... for reactive updates."
        )

        # Still works - extract strings and render manually
        if not report.strings:
            self.update("No interesting strings found.")
            return

        # Use old rendering for backward compatibility
        from rich.console import Group
        from rich.text import Text

        strings_to_show = report.strings[:MAX_DISPLAY_STRINGS]
        text_elements = [Text(s) for s in strings_to_show]

        if len(report.strings) > MAX_DISPLAY_STRINGS:
            truncated_count = len(report.strings) - MAX_DISPLAY_STRINGS
            text_elements.append(
                Text(
                    f"... {truncated_count} more strings (truncated for display)",
                    style="italic yellow",
                )
            )

        group = Group(*text_elements)
        self.update(group)
