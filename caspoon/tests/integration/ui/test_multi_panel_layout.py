"""Integration tests for multi-panel layout."""

import pytest
from textual.containers import Container

from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.screens import MainScreen
from caspoon.ui.widgets import Console, DetailsPanel, Sidebar


class TestMultiPanelLayout:
    """Integration test suite for multi-panel layout."""

    @pytest.mark.asyncio
    async def test_main_screen_layout(self, app_with_state):
        """Test MainScreen composes correctly with all panels."""
        # Create content area
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Check all panels are present
            sidebar = screen.query_one("#sidebar", Sidebar)
            assert sidebar is not None

            details = screen.query_one("#details", DetailsPanel)
            assert details is not None

            console = screen.query_one("#console", Console)
            assert console is not None

            content_area = screen.query_one("#content")
            assert content_area is not None

    @pytest.mark.asyncio
    async def test_toggle_sidebar(self, app_with_state):
        """Test sidebar visibility toggle (Ctrl+B)."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            sidebar = screen.query_one("#sidebar")

            # Initially visible
            assert not sidebar.has_class("hidden")

            # Toggle to hide
            screen.action_toggle_sidebar()
            await pilot.pause()

            assert sidebar.has_class("hidden")
            assert not app_with_state.state.ui_state.sidebar_visible

            # Toggle to show
            screen.action_toggle_sidebar()
            await pilot.pause()

            assert not sidebar.has_class("hidden")
            assert app_with_state.state.ui_state.sidebar_visible

    @pytest.mark.asyncio
    async def test_toggle_details(self, app_with_state):
        """Test details panel visibility toggle (Ctrl+D)."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            details = screen.query_one("#details")

            # Initially visible
            assert not details.has_class("hidden")

            # Toggle to hide
            screen.action_toggle_details()
            await pilot.pause()

            assert details.has_class("hidden")
            assert not app_with_state.state.ui_state.details_visible

            # Toggle to show
            screen.action_toggle_details()
            await pilot.pause()

            assert not details.has_class("hidden")
            assert app_with_state.state.ui_state.details_visible

    @pytest.mark.asyncio
    async def test_toggle_console(self, app_with_state):
        """Test console visibility toggle (Ctrl+J)."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            console = screen.query_one("#console")

            # Initially visible
            assert not console.has_class("hidden")

            # Toggle to hide
            screen.action_toggle_console()
            await pilot.pause()

            assert console.has_class("hidden")
            assert not app_with_state.state.ui_state.console_visible

            # Toggle to show
            screen.action_toggle_console()
            await pilot.pause()

            assert not console.has_class("hidden")
            assert app_with_state.state.ui_state.console_visible

    @pytest.mark.asyncio
    async def test_function_explorer_navigation(self, app_with_state):
        """Test function explorer tree navigation works."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Get function explorer from sidebar
            sidebar = screen.query_one("#sidebar", Sidebar)
            explorer = sidebar._explorer

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
    async def test_details_panel_updates(self, app_with_state):
        """Test details panel updates on selection."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Get details panel
            details = screen.query_one("#details", DetailsPanel)

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
    async def test_console_logging(self, app_with_state):
        """Test console receives and displays logs."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Get console
            console = screen.get_console()
            assert console is not None

            # Log messages
            console.log("Test info message", level="info")
            console.log("Test error message", level="error")
            await pilot.pause()

            # Verify messages were logged
            rich_log = console.query_one("#console_log")
            assert len(rich_log.lines) >= 2

    @pytest.mark.asyncio
    async def test_panel_state_persistence(self, app_with_state):
        """Test AppState tracks panel visibility."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Initial state
            assert app_with_state.state.ui_state.sidebar_visible is True
            assert app_with_state.state.ui_state.details_visible is True
            assert app_with_state.state.ui_state.console_visible is True

            # Toggle sidebar
            screen.action_toggle_sidebar()
            await pilot.pause()
            assert app_with_state.state.ui_state.sidebar_visible is False

            # Toggle details
            screen.action_toggle_details()
            await pilot.pause()
            assert app_with_state.state.ui_state.details_visible is False

            # Toggle console
            screen.action_toggle_console()
            await pilot.pause()
            assert app_with_state.state.ui_state.console_visible is False

    @pytest.mark.asyncio
    async def test_helper_methods(self, app_with_state):
        """Test MainScreen helper methods for getting panels."""
        content = Container(id="content")
        screen = MainScreen(content)

        async with app_with_state.run_test() as pilot:
            pilot.app.install_screen(screen, name="test_screen")
            pilot.app.push_screen("test_screen")
            await pilot.pause()

            # Test helper methods
            console = screen.get_console()
            assert console is not None
            assert isinstance(console, Console)

            details = screen.get_details_panel()
            assert details is not None
            assert isinstance(details, DetailsPanel)

            sidebar = screen.get_sidebar()
            assert sidebar is not None
            assert isinstance(sidebar, Sidebar)
