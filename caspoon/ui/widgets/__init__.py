"""Reusable widget library.

This package will contain reusable widgets for the TUI:
- Base widget classes (BaseView, InteractiveView)
- Specialized widgets (TreeView, TableView, CodeView)
- Common UI components (SearchBar, StatusBar, ProgressBar)
- Command Palette (CommandPalette)

Currently empty - to be implemented in Subtask 2.
"""

from .command_palette import CommandPalette

__all__: list[str] = ["CommandPalette"]
