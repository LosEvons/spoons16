"""Sidebar widget containing navigation components."""

from textual.containers import Vertical
from textual.widgets import Input, Static

from caspoon.ui import widget_ids as wid
from .function_explorer import FunctionExplorer


class Sidebar(Vertical):
    """Navigation sidebar with function tree.

    Contains a title, filter input, and FunctionExplorer widget for
    navigating through functions in the binary.

    Keyboard Bindings:
        - /: Focus filter input (when not already focused)
        - Escape: Clear filter and return focus to tree

    Example:
        >>> sidebar = Sidebar()
        >>> # Filter automatically applies to FunctionExplorer
    """

    DEFAULT_CSS = """
    Sidebar {
        border: solid green;
        background: $surface;
    }

    Sidebar Static.title {
        dock: top;
        height: 1;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Sidebar Input {
        dock: top;
        height: 3;
        border: solid $primary;
        margin: 1 1;
    }

    Sidebar FunctionExplorer {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the sidebar.

        Args:
            **kwargs: Additional keyword arguments for Vertical
        """
        super().__init__(**kwargs)
        self._explorer = FunctionExplorer(id=wid.FUNCTION_EXPLORER)

    @property
    def explorer(self) -> FunctionExplorer:
        """Return the function explorer widget."""
        return self._explorer

    def compose(self):
        """Compose the sidebar components.

        Yields:
            Title, filter input, and FunctionExplorer widgets
        """
        yield Static("Navigation", classes="title")
        yield Input(placeholder="Filter functions...", id=wid.FUNCTION_FILTER)
        yield self._explorer

    def on_mount(self) -> None:
        """Set up the sidebar when mounted."""
        # Focus the function explorer by default
        try:
            self._explorer.focus()
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes.

        Args:
            event: Input changed event
        """
        # Only handle the filter input
        if event.input.id == wid.FUNCTION_FILTER:
            filter_text = event.value
            self._explorer.apply_filter(filter_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle filter input submission (Enter key).

        Returns focus to the function explorer.

        Args:
            event: Input submitted event
        """
        if event.input.id == wid.FUNCTION_FILTER:
            # Return focus to explorer
            self._explorer.focus()
