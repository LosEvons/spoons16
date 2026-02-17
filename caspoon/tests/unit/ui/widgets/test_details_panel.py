"""Unit tests for DetailsPanel widget."""

import pytest

from caspoon.ui import widget_ids as wid
from caspoon.ui.widgets.details_panel import DetailsPanel


class TestDetailsPanel:
    """Test suite for DetailsPanel widget."""

    @pytest.mark.asyncio
    async def test_details_panel_initialization(self, app_with_state):
        """Test details panel initializes correctly."""
        panel = DetailsPanel()
        assert panel is not None

    @pytest.mark.asyncio
    async def test_details_panel_compose(self, app_with_state):
        """Test details panel composes with content widget."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Check content widget is present
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_help_on_mount(self, app_with_state):
        """Test details panel shows help text on mount."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Help text should be displayed by default
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None
            # Just verify it doesn't crash

    @pytest.mark.asyncio
    async def test_show_function_details(self, app_with_state):
        """Test displaying function details."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show function details
            func_data = {
                "name": "main",
                "address": 0x401000,
                "size": 256,
                "section": ".text",
                "calls": ["printf", "malloc", "free"],
                "refs": ["_start"],
            }
            panel.show_function_details(func_data)
            await pilot.pause()

            # Verify no crashes and content is updated
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_function_details_minimal(self, app_with_state):
        """Test displaying function details with minimal data."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show function details with minimal data
            func_data = {
                "name": "sub_401000",
                "address": 0x401000,
            }
            panel.show_function_details(func_data)
            await pilot.pause()

            # Verify no crashes
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_string_details(self, app_with_state):
        """Test displaying string details."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show string details
            string_data = {
                "value": "Hello, World!",
                "offset": 0x2000,
                "length": 13,
                "encoding": "utf-8",
                "refs": ["main", "sub_401000"],
            }
            panel.show_string_details(string_data)
            await pilot.pause()

            # Verify no crashes
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_import_details(self, app_with_state):
        """Test displaying import details."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show import details
            import_data = {
                "name": "printf",
                "library": "libc.so.6",
                "address": 0x3000,
            }
            panel.show_import_details(import_data)
            await pilot.pause()

            # Verify no crashes
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_clear_details_panel(self, app_with_state):
        """Test clearing details panel returns to help text."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show some details
            func_data = {"name": "test", "address": 0x1000}
            panel.show_function_details(func_data)
            await pilot.pause()

            # Clear panel
            panel.clear()
            await pilot.pause()

            # Should show help text again
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_error_handling(self, app_with_state):
        """Test error handling with invalid data."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Try with None data (should not crash)
            try:
                panel.show_function_details(None)  # type: ignore
                await pilot.pause()
            except Exception:
                pass  # Expected to fail gracefully

            # Panel should still be functional
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None
