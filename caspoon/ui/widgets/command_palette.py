"""Command Palette widget for keyboard-driven command access.

Provides a Ctrl+P-style command palette with fuzzy search for quick
access to all application commands and actions.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Input, Label, ListItem, ListView

from ..core.actions import ActionRegistry


class CommandPalette(Container):
    """Fuzzy-search command palette (Ctrl+P style).

    Provides quick keyboard-driven access to all app commands with
    real-time search filtering and scoring.

    Attributes:
        action_registry: Registry of available actions
    """

    DEFAULT_CSS = """
    CommandPalette {
        display: none;
        layer: overlay;
        align: center middle;
        width: 70%;
        height: 60%;
        background: $surface;
        border: thick $primary;
    }

    CommandPalette.visible {
        display: block;
    }

    CommandPalette Input {
        margin: 1;
        border: solid $accent;
    }

    CommandPalette ListView {
        height: 1fr;
        margin: 0 1 1 1;
    }

    CommandPalette ListItem {
        padding: 0 1;
    }

    CommandPalette ListItem > Label {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "execute", "Execute", show=True),
    ]

    def __init__(self, action_registry: ActionRegistry, **kwargs) -> None:
        """Initialize command palette.

        Args:
            action_registry: Registry of available actions
            **kwargs: Additional Container arguments
        """
        super().__init__(**kwargs)
        self.action_registry = action_registry

    def compose(self) -> ComposeResult:
        """Compose the command palette UI.

        Yields:
            Input field for search query
            ListView for filtered command results
        """
        with Vertical():
            yield Input(placeholder="Type to search commands...", id="search")
            yield ListView(id="results")

    def on_mount(self) -> None:
        """Focus search input when mounted."""
        search_input = self.query_one("#search", Input)
        search_input.focus()

    def on_show(self) -> None:
        """Reset and show all commands when palette shown."""
        search_input = self.query_one("#search", Input)
        search_input.value = ""
        search_input.focus()
        self._update_results("")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types.

        Args:
            event: Input change event
        """
        if event.input.id == "search":
            self._update_results(event.value)

    def _update_results(self, query: str) -> None:
        """Update result list with filtered commands.

        Args:
            query: Search query string
        """
        # Search actions using registry
        filtered_actions = self.action_registry.search(query)

        # Update ListView
        results = self.query_one("#results", ListView)
        results.clear()

        # Show top 15 results
        for action in filtered_actions[:15]:
            # Format: "Command Name  (Keybinding)  Category"
            keybind = f"({action.keybinding})" if action.keybinding else ""
            label_text = (
                f"{action.name}  " f"[dim]{keybind}[/]  " f"[dim italic]{action.category}[/]"
            )

            # Create list item - don't set ID to avoid conflicts
            item = ListItem(Label(label_text))
            # Store the action_id for execution
            item.action_id = action.action_id  # type: ignore[attr-defined]
            results.append(item)

        # If we have results, highlight the first one
        if results.children:
            results.index = 0

    def action_execute(self) -> None:
        """Execute the currently selected command."""
        results = self.query_one("#results", ListView)

        # Get highlighted child
        if results.highlighted_child:
            # Get action_id from the custom attribute
            action_id = getattr(results.highlighted_child, "action_id", None)
            if action_id:
                # Execute the action
                self.action_registry.execute(action_id)
                # Close palette after execution
                self.action_close()

    def action_close(self) -> None:
        """Close the command palette."""
        self.remove_class("visible")

    def show(self) -> None:
        """Show the command palette."""
        self.add_class("visible")
        self.on_show()
