"""Console widget for displaying logs and messages."""

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import RichLog


class Console(Container):
    """Bottom console for logs and messages.

    Displays color-coded log messages with auto-scroll functionality.
    Provides methods to write messages at different severity levels.

    Keyboard Bindings:
        - Ctrl+L: Clear console

    Example:
        >>> console = Console()
        >>> console.log("Analysis started", level="info")
        >>> console.log("Warning: missing symbols", level="warning")
        >>> console.log("Error: failed to load", level="error")
    """

    BINDINGS = [
        Binding("ctrl+l", "clear_console", "Clear Console", show=False),
    ]

    DEFAULT_CSS = """
    Console {
        height: 10;
        border: solid yellow;
    }

    Console RichLog {
        scrollbar-gutter: stable;
        background: $surface;
    }
    """

    def compose(self):
        """Compose the console with RichLog widget.

        Yields:
            RichLog widget for displaying log messages
        """
        yield RichLog(id="console_log", wrap=True, highlight=True, markup=True)

    def log(self, message: str, level: str = "info") -> None:
        """Write a log message to the console.

        Args:
            message: Message text to display
            level: Severity level (info, warning, error, success, debug)

        The message is color-coded based on the level:
        - error: red
        - warning: yellow
        - success: green
        - debug: dim
        - info: default (white)
        """
        try:
            log_widget = self.query_one("#console_log", RichLog)

            if level == "error":
                log_widget.write(f"[red]ERROR:[/red] {message}")
            elif level == "warning":
                log_widget.write(f"[yellow]WARNING:[/yellow] {message}")
            elif level == "success":
                log_widget.write(f"[green]✓[/green] {message}")
            elif level == "debug":
                log_widget.write(f"[dim]DEBUG: {message}[/dim]")
            else:  # info
                log_widget.write(message)

        except Exception:
            # Silently fail if widget not found
            pass

    def clear(self) -> None:
        """Clear all messages from the console."""
        try:
            log_widget = self.query_one("#console_log", RichLog)
            log_widget.clear()
        except Exception:
            pass

    def action_clear_console(self) -> None:
        """Action handler to clear the console.

        Bound to: Ctrl+L
        """
        self.clear()
