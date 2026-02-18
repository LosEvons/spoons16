"""Details dock panel — context-sensitive information."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class DetailsPanel(QDockWidget):
    """Right-dock panel that shows context-sensitive details.

    Displays information about the currently selected function or address.
    """

    def __init__(self, parent=None) -> None:
        super().__init__("Details", parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._label = QLabel("Select a function to see details.")
        self._label.setWordWrap(True)
        self._label.setTextFormat(Qt.TextFormat.RichText)
        self._label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._label)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        self.setWidget(scroll)

    def show_function(self, name: str, addr: int) -> None:
        """Display details for a selected function.

        Args:
            name: Function name.
            addr: Function address.
        """
        self._label.setText(
            f"<b>Function:</b> {name}<br>"
            f"<b>Address:</b> 0x{addr:x}"
        )

    def show_text(self, html: str) -> None:
        """Set arbitrary HTML content in the details panel."""
        self._label.setText(html)

    def clear(self) -> None:
        """Reset the panel to its default state."""
        self._label.setText("Select a function to see details.")
