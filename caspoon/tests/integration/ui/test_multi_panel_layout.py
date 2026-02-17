"""Integration tests for multi-panel layout."""

import pytest
from textual.app import App

from caspoon.ui import widget_ids as wid
from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.core.state import AppState
from caspoon.ui.screens import MainScreen
from caspoon.ui.widgets import Console, DetailsPanel, Sidebar


@pytest.fixture
def test_app():
    """Create test app with MainScreen."""

    class TestApp(App):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.state = AppState()

        def compose(self):
            yield MainScreen()

    return TestApp()


class TestMultiPanelLayout:
    """Integration test suite for multi-panel layout."""

    @pytest.mark.asyncio
    async def test_main_screen_layout(self, test_app):
        """Test MainScreen composes correctly with all panels."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            # Check all panels are present
            main_screen = test_app.query_one(MainScreen)
            sidebar = main_screen.query_one(f"#{wid.SIDEBAR}", Sidebar)
            assert sidebar is not None

            details = main_screen.query_one(f"#{wid.DETAILS}", DetailsPanel)
            assert details is not None

            console = main_screen.query_one(f"#{wid.CONSOLE}", Console)
            assert console is not None

            content_area = main_screen.query_one(f"#{wid.CONTENT}")
            assert content_area is not None

    @pytest.mark.asyncio
    async def test_toggle_sidebar(self, test_app):
        """Test sidebar visibility toggle (Ctrl+B)."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            main_screen = test_app.query_one(MainScreen)

            # Initially visible
            assert "sidebar-hidden" not in main_screen.classes
            assert test_app.state.ui_state.sidebar_visible is True

            # Toggle to hide
            main_screen.action_toggle_sidebar()
            await pilot.pause()

            assert "sidebar-hidden" in main_screen.classes
            assert test_app.state.ui_state.sidebar_visible is False

            # Toggle to show
            main_screen.action_toggle_sidebar()
            await pilot.pause()

            assert "sidebar-hidden" not in main_screen.classes
            assert test_app.state.ui_state.sidebar_visible is True

    @pytest.mark.asyncio
    async def test_toggle_details(self, test_app):
        """Test details panel visibility toggle (Ctrl+D)."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            main_screen = test_app.query_one(MainScreen)

            # Initially visible
            assert "details-hidden" not in main_screen.classes
            assert test_app.state.ui_state.details_visible is True

            # Toggle to hide
            main_screen.action_toggle_details()
            await pilot.pause()

            assert "details-hidden" in main_screen.classes
            assert test_app.state.ui_state.details_visible is False

            # Toggle to show
            main_screen.action_toggle_details()
            await pilot.pause()

            assert "details-hidden" not in main_screen.classes
            assert test_app.state.ui_state.details_visible is True

    @pytest.mark.asyncio
    async def test_toggle_console(self, test_app):
        """Test console visibility toggle (Ctrl+J)."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            main_screen = test_app.query_one(MainScreen)

            # Initially visible
            assert "console-hidden" not in main_screen.classes
            assert test_app.state.ui_state.console_visible is True

            # Toggle to hide
            main_screen.action_toggle_console()
            await pilot.pause()

            assert "console-hidden" in main_screen.classes
            assert test_app.state.ui_state.console_visible is False

            # Toggle to show
            main_screen.action_toggle_console()
            await pilot.pause()

            assert "console-hidden" not in main_screen.classes
            assert test_app.state.ui_state.console_visible is True

    @pytest.mark.asyncio
    async def test_function_explorer_navigation(self, test_app):
        """Test function explorer tree navigation works."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            # Get function explorer from sidebar
            main_screen = test_app.query_one(MainScreen)
            sidebar = main_screen.query_one(f"#{wid.SIDEBAR}", Sidebar)
            explorer = sidebar.explorer

            # Set test data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "printf", "address": 0x402000, "section": ".plt"},
                ]
            )
            explorer.data = results
            explorer.render_content(results)
            await pilot.pause()

            # Verify tree has items
            assert explorer.get_item_count() > 0

            # Test navigation
            explorer.action_move_down()
            await pilot.pause()
            assert explorer.selected_index >= 0

    @pytest.mark.asyncio
    async def test_details_panel_updates(self, test_app):
        """Test details panel updates on selection."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            # Get details panel
            main_screen = test_app.query_one(MainScreen)
            details = main_screen.query_one(f"#{wid.DETAILS}", DetailsPanel)

            # Show function details
            func_data = {
                "name": "test_func",
                "address": 0x401000,
                "size": 100,
            }
            details.show_function_details(func_data)
            await pilot.pause()

            # Verify no crashes - content should be updated
            content_widget = details.query_one("#details_content")
            assert content_widget is not None

    @pytest.mark.asyncio
    async def test_console_logging(self, test_app):
        """Test console receives and displays logs."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            # Get console
            main_screen = test_app.query_one(MainScreen)
            console = main_screen.get_console()
            assert console is not None

            # Log messages
            console.log("Test info message", level="info")
            console.log("Test error message", level="error")
            await pilot.pause()

            # Verify messages were logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}")
            assert len(rich_log.lines) >= 2

    @pytest.mark.asyncio
    async def test_panel_state_persistence(self, test_app):
        """Test AppState tracks panel visibility."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            main_screen = test_app.query_one(MainScreen)

            # Initial state
            assert test_app.state.ui_state.sidebar_visible is True
            assert test_app.state.ui_state.details_visible is True
            assert test_app.state.ui_state.console_visible is True

            # Toggle sidebar
            main_screen.action_toggle_sidebar()
            await pilot.pause()
            assert test_app.state.ui_state.sidebar_visible is False

            # Toggle details
            main_screen.action_toggle_details()
            await pilot.pause()
            assert test_app.state.ui_state.details_visible is False

            # Toggle console
            main_screen.action_toggle_console()
            await pilot.pause()
            assert test_app.state.ui_state.console_visible is False

    @pytest.mark.asyncio
    async def test_helper_methods(self, test_app):
        """Test MainScreen helper methods for getting panels."""
        async with test_app.run_test() as pilot:
            await pilot.pause()

            main_screen = test_app.query_one(MainScreen)

            # Test helper methods
            console = main_screen.get_console()
            assert console is not None
            assert isinstance(console, Console)

            details = main_screen.get_details_panel()
            assert details is not None
            assert isinstance(details, DetailsPanel)

            sidebar = main_screen.get_sidebar()
            assert sidebar is not None
            assert isinstance(sidebar, Sidebar)
