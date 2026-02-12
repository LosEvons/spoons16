"""Strings view component for displaying extracted strings."""

from textual.widgets import Static
from rich.console import Group
from rich.text import Text

from caspoon.core.models import ExecutableReport

# Maximum strings to display to prevent UI slowdown
MAX_DISPLAY_STRINGS = 1000


class StringsView(Static):
    """Display extracted strings from the executable.
    
    Shows a list of printable strings found in the binary,
    limited to prevent performance issues.
    """
    
    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.
        
        Args:
            report: ExecutableReport containing analysis results
        """
        if not report.strings:
            self.update("No interesting strings found.")
            return

        # Limit the number of displayed strings to prevent UI slowdown
        strings_to_show = report.strings[:MAX_DISPLAY_STRINGS]
        text_elements = [Text(s) for s in strings_to_show]
        
        # Add truncation notice if needed
        if len(report.strings) > MAX_DISPLAY_STRINGS:
            truncated_count = len(report.strings) - MAX_DISPLAY_STRINGS
            text_elements.append(Text(f"... {truncated_count} more strings (truncated for display)", style="italic yellow"))

        group = Group(*text_elements)
        self.update(group)