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
        
        if len(report.strings) > MAX_DISPLAY_STRINGS:
            # Add a notice if strings were truncated
            strings_to_show.append(f"... {len(report.strings) - MAX_DISPLAY_STRINGS} more strings (truncated)")

        group = Group(*[Text(s) for s in strings_to_show])
        self.update(group)