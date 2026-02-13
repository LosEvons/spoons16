"""Interactive UI widgets for Caspoon.

This package contains custom Textual widgets that provide rich,
interactive functionality for binary analysis visualization.
"""

from .goto_dialog import GotoDialog
from .interactive_disasm import InteractiveDisasmView

__all__ = [
    "InteractiveDisasmView",
    "GotoDialog",
]
