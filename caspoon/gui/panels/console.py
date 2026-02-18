"""Console dock panel for log output."""

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QDockWidget, QPlainTextEdit

LEVEL_COLORS = {
    "debug":   "#808080",
    "info":    "#d4d4d4",
    "success": "#4ec9b0",
    "warning": "#dcdcaa",
    "error":   "#f44747",
}


class ConsolePanel(QDockWidget):
    """Scrollable log panel with colored level text."""

    def __init__(self, parent=None) -> None:
        super().__init__("Console", parent)
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(2000)
        self.setWidget(self._text)

    def log(self, message: str, level: str = "info") -> None:
        """Append a colored log line.

        Args:
            message: Text to display.
            level: One of debug / info / success / warning / error.
        """
        color = LEVEL_COLORS.get(level, LEVEL_COLORS["info"])
        # Escape HTML special characters
        safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self._text.appendHtml(f'<span style="color:{color}">{safe}</span>')
        self._text.moveCursor(QTextCursor.MoveOperation.End)

    def clear(self) -> None:
        """Clear all log output."""
        self._text.clear()
