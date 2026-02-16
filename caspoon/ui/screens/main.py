"""Main screen with multi-panel layout."""

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from caspoon.ui.widgets.console import Console
from caspoon.ui.widgets.details_panel import DetailsPanel
from caspoon.ui.widgets.sidebar import Sidebar


class MainScreen(Container):
    """Main screen with multi-panel docking layout.

    Provides an IDE-like experience with:
    - Left sidebar: Function tree navigation
    - Center content: Tabbed views (Overview, Strings, etc.)
    - Right details panel: Context-sensitive information
    - Bottom console: Logs and messages

    All panels are collapsible via keyboard shortcuts.

    Keyboard Bindings:
        - Ctrl+B: Toggle sidebar visibility
        - Ctrl+D: Toggle details panel visibility
        - Ctrl+J: Toggle console visibility

    Example:
        >>> screen = MainScreen()
        >>> yield screen
    """

    BINDINGS = [
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar", show=False),
        Binding("ctrl+d", "toggle_details", "Toggle Details", show=False),
        Binding("ctrl+j", "toggle_console", "Toggle Console", show=False),
    ]

    DEFAULT_CSS = """
    MainScreen {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 2fr 1fr;
        grid-rows: 1fr auto;
    }

    #sidebar {
        column-span: 1;
        row-span: 2;
    }

    #content {
        column-span: 1;
        row-span: 1;
    }

    #details {
        column-span: 1;
        row-span: 2;
    }

    #console {
        column-span: 1;
        row-span: 1;
    }

    .hidden {
        display: none;
    }

    /* Adjust grid when panels are hidden */
    MainScreen.sidebar-hidden {
        grid-columns: 0 3fr 1fr;
    }

    MainScreen.details-hidden {
        grid-columns: 1fr 2fr 0;
    }

    MainScreen.sidebar-hidden.details-hidden {
        grid-columns: 0 1fr 0;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the main screen.

        Args:
            **kwargs: Additional keyword arguments for Screen
        """
        super().__init__(**kwargs)

    def compose(self):
        """Compose the multi-panel layout.

        Yields:
            Header, Sidebar, Content area with tabs, DetailsPanel, Console, Footer
        """
        from textual.widgets import Input, TabbedContent, TabPane
        from textual.containers import ScrollableContainer
        from caspoon.ui.views.imports_exports import ImportsExportsView
        from caspoon.ui.views.overview import OverviewView
        from caspoon.ui.views.protections import ProtectionsView
        from caspoon.ui.views.r2_view import R2View
        from caspoon.ui.views.strings_view import StringsView

        yield Header()
        yield Sidebar(id="sidebar")
        
        # Content area with input and tabs
        with Container(id="content"):
            yield Input(placeholder="Enter path to binary and press Enter...", id="path_input")
            
            with TabbedContent(id="tabs"):
                with TabPane("Overview", id="overview-tab"):
                    yield ScrollableContainer(OverviewView(id="overview"))
                
                with TabPane("Protections", id="protections-tab"):
                    yield ScrollableContainer(ProtectionsView(id="protections"))
                
                with TabPane("Strings", id="strings-tab"):
                    yield ScrollableContainer(StringsView(id="strings_view"))
                
                with TabPane("Imports / Exports", id="imports-tab"):
                    yield ScrollableContainer(ImportsExportsView(id="imp_exp"))
                
                with TabPane("R2 Analysis", id="r2-tab"):
                    yield ScrollableContainer(R2View(id="r2_view"))
        
        yield DetailsPanel(id="details")
        yield Console(id="console")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when mounted.

        Initializes panel visibility based on AppState.
        """
        try:
            # Sync initial visibility with AppState
            if hasattr(self.app, "state"):
                state = self.app.state.ui_state

                # Set initial visibility
                if not state.sidebar_visible:
                    self.query_one("#sidebar").add_class("hidden")
                    self.add_class("sidebar-hidden")

                if not state.details_visible:
                    self.query_one("#details").add_class("hidden")
                    self.add_class("details-hidden")

                if not state.console_visible:
                    self.query_one("#console").add_class("hidden")

        except Exception:
            # Continue with defaults if state not available
            pass

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility.

        Bound to: Ctrl+B

        Updates both the widget visibility and AppState.
        """
        try:
            sidebar = self.query_one("#sidebar")
            sidebar.toggle_class("hidden")

            # Update screen layout class
            self.toggle_class("sidebar-hidden")

            # Update AppState
            if hasattr(self.app, "state"):
                is_visible = not sidebar.has_class("hidden")
                self.app.state.ui_state.sidebar_visible = is_visible

                # Log to console
                console = self.query_one("#console", Console)
                status = "shown" if is_visible else "hidden"
                console.log(f"Sidebar {status}", level="info")

        except Exception:
            # Silently fail if widgets not found
            pass

    def action_toggle_details(self) -> None:
        """Toggle details panel visibility.

        Bound to: Ctrl+D

        Updates both the widget visibility and AppState.
        """
        try:
            details = self.query_one("#details")
            details.toggle_class("hidden")

            # Update screen layout class
            self.toggle_class("details-hidden")

            # Update AppState
            if hasattr(self.app, "state"):
                is_visible = not details.has_class("hidden")
                self.app.state.ui_state.details_visible = is_visible

                # Log to console
                console = self.query_one("#console", Console)
                status = "shown" if is_visible else "hidden"
                console.log(f"Details panel {status}", level="info")

        except Exception:
            # Silently fail if widgets not found
            pass

    def action_toggle_console(self) -> None:
        """Toggle console visibility.

        Bound to: Ctrl+J

        Updates both the widget visibility and AppState.
        """
        try:
            console = self.query_one("#console")
            console.toggle_class("hidden")

            # Update AppState
            if hasattr(self.app, "state"):
                is_visible = not console.has_class("hidden")
                self.app.state.ui_state.console_visible = is_visible

                # Only log if console is being shown (not hidden)
                if is_visible and isinstance(console, Console):
                    console.log("Console shown", level="info")

        except Exception:
            # Silently fail if widgets not found
            pass

    def get_console(self) -> Console | None:
        """Get the console widget.

        Returns:
            Console widget or None if not found
        """
        try:
            return self.query_one("#console", Console)
        except Exception:
            return None

    def get_details_panel(self) -> DetailsPanel | None:
        """Get the details panel widget.

        Returns:
            DetailsPanel widget or None if not found
        """
        try:
            return self.query_one("#details", DetailsPanel)
        except Exception:
            return None

    def get_sidebar(self) -> Sidebar | None:
        """Get the sidebar widget.

        Returns:
            Sidebar widget or None if not found
        """
        try:
            return self.query_one("#sidebar", Sidebar)
        except Exception:
            return None
