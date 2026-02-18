"""QApplication entry point for the Caspoon GUI."""

import sys

from PySide6.QtWidgets import QApplication

from caspoon.gui.main_window import CaspoonMainWindow
from caspoon.gui.theme import DARK_STYLESHEET
from caspoon.ui.core.state import AppState


def run_gui() -> None:
    """Create the QApplication, apply dark theme, and start the event loop."""
    app = QApplication(sys.argv)
    app.setApplicationName("Caspoon")
    app.setOrganizationName("Caspoon")
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLESHEET)

    state = AppState()
    window = CaspoonMainWindow(state)
    window.show()

    sys.exit(app.exec())
