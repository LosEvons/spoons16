"""Reusable widget library.

This package contains reusable widgets for the TUI:
- Base widget classes (BaseView, InteractiveView)
- Specialized widgets (TreeView, TableView, CodeView)
- Common UI components (SearchBar, StatusBar, ProgressBar)
- Command Palette (CommandPalette)
- Multi-panel widgets (Sidebar, Console, DetailsPanel, FunctionExplorer)
- Custom Header/Footer (AppHeader, AppFooter)
"""

from .app_footer import AppFooter
from .app_header import AppHeader
from .command_palette import CommandPalette
from .console import Console
from .details_panel import DetailsPanel
from .function_explorer import FunctionExplorer
from .sidebar import Sidebar

__all__: list[str] = [
    "AppFooter",
    "AppHeader",
    "CommandPalette",
    "Console",
    "DetailsPanel",
    "FunctionExplorer",
    "Sidebar",
]
