"""Screen management.

This package contains screen classes for the TUI:
- Main application screen (multi-panel layout)
- File picker screen
- Help/documentation screens
- Settings screen
"""

from .main import MainScreen

__all__: list[str] = ["MainScreen"]
