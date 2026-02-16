"""Custom footer widget to avoid Textual's Footer coroutine warning."""

from textual.containers import Container
from textual.widgets import Static


class AppFooter(Container):
    """Application footer without async mount issues.
    
    Replaces Textual's built-in Footer widget to avoid RuntimeWarning
    about coroutine '_on_mount' not being awaited.
    """

    DEFAULT_CSS = """
    AppFooter {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }
    
    AppFooter Static {
        width: 100%;
        height: 1;
        padding: 0 1;
        text-style: dim;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the footer.
        
        Args:
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)

    def compose(self):
        """Compose the footer with keybindings hint.
        
        Yields:
            Static widget containing keybinding information
        """
        yield Static("↑↓ Navigate | 1-5 Tabs | Ctrl+P Commands | Ctrl+B/D/J Panels | F1 Help | Ctrl+Q Quit")
