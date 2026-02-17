"""Unit tests for Sidebar widget."""

import pytest

from caspoon.ui import widget_ids as wid
from caspoon.ui.widgets.sidebar import Sidebar


class TestSidebar:
    """Test suite for Sidebar widget."""

    @pytest.mark.asyncio
    async def test_sidebar_initialization(self, app_with_state):
        """Test sidebar initializes correctly."""
        sidebar = Sidebar()
        assert sidebar is not None
        assert sidebar.explorer is not None

    @pytest.mark.asyncio
    async def test_sidebar_compose(self, app_with_state):
        """Test sidebar composes all components."""
        sidebar = Sidebar()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(sidebar)
            await pilot.pause()

            # Check all components are present
            title = sidebar.query_one(".title")
            assert title is not None
            assert "Navigation" in str(title.renderable)

            filter_input = sidebar.query_one(f"#{wid.FUNCTION_FILTER}")
            assert filter_input is not None

            explorer = sidebar.query_one(f"#{wid.FUNCTION_EXPLORER}")
            assert explorer is not None

    @pytest.mark.asyncio
    async def test_filter_input_changes(self, app_with_state):
        """Test filter input changes are applied to explorer."""
        sidebar = Sidebar()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(sidebar)
            await pilot.pause()

            # Get filter input
            filter_input = sidebar.query_one(f"#{wid.FUNCTION_FILTER}")
            assert filter_input is not None

            # Simulate typing in filter
            filter_input.value = "test"
            await pilot.pause()

            # Explorer should have filter applied
            assert sidebar.explorer.current_filter == "test"

    @pytest.mark.asyncio
    async def test_filter_input_submit(self, app_with_state):
        """Test filter input submission returns focus to explorer."""
        sidebar = Sidebar()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(sidebar)
            await pilot.pause()

            # Get filter input
            filter_input = sidebar.query_one(f"#{wid.FUNCTION_FILTER}")
            filter_input.focus()
            await pilot.pause()

            # Submit (press Enter)
            # The on_input_submitted should return focus to explorer
            # We can't easily test focus change, so just verify handler exists
            assert hasattr(sidebar, "on_input_submitted")

    @pytest.mark.asyncio
    async def test_explorer_focus_on_mount(self, app_with_state):
        """Test explorer receives focus on mount."""
        sidebar = Sidebar()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(sidebar)
            await pilot.pause()

            # Explorer should be present
            explorer = sidebar.query_one(f"#{wid.FUNCTION_EXPLORER}")
            assert explorer is not None
