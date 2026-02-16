"""Custom header widget to avoid Textual's Header coroutine warning."""

from textual.containers import Container
from textual.widgets import Static


class AppHeader(Container):
    """Application header without async mount issues.
    
    Replaces Textual's built-in Header widget to avoid RuntimeWarning
    about coroutine '_on_mount' not being awaited.
    """

    DEFAULT_CSS = """
    AppHeader {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    
    AppHeader Static {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self, title: str = "Caspoon Reverse Engineering Toolkit", **kwargs):
        """Initialize the header.
        
        Args:
            title: Title to display in header
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self._title = title

    def compose(self):
        """Compose the header with title.
        
        Yields:
            Static widget containing the title
        """
        yield Static(self._title)
