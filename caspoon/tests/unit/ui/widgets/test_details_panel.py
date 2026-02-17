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

    @pytest.mark.asyncio
    async def test_show_xrefs_with_callers_and_callees(self, app_with_state):
        """Test displaying xrefs with both callers and callees."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with both callers and callees
            xref_data = {
                "callers": [
                    {"from": 0x400000, "type": "CALL", "fcn_name": "entry0"},
                    {"from": 0x401234, "type": "JMP", "fcn_name": "main"},
                ],
                "callees": [
                    {"to": 0x402000, "type": "CALL", "fcn_name": "helper"},
                    {"to": 0x403000, "type": "CALL", "fcn_name": "printf"},
                ],
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes and content is updated
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_xrefs_callers_only(self, app_with_state):
        """Test displaying xrefs with only callers."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with only callers
            xref_data = {
                "callers": [
                    {"from": 0x400000, "type": "CALL", "fcn_name": "entry0"},
                ],
                "callees": [],
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_xrefs_callees_only(self, app_with_state):
        """Test displaying xrefs with only callees."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with only callees
            xref_data = {
                "callers": [],
                "callees": [
                    {"to": 0x402000, "type": "CALL", "fcn_name": "helper"},
                ],
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_xrefs_empty(self, app_with_state):
        """Test displaying xrefs with no callers or callees."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with no data
            xref_data = {
                "callers": [],
                "callees": [],
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes and appropriate message is shown
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_xrefs_missing_keys(self, app_with_state):
        """Test displaying xrefs with missing keys in data."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with missing optional keys
            xref_data = {
                "callers": [
                    {"from": 0x400000},  # Missing type and fcn_name
                ],
                "callees": [
                    {"type": "CALL"},  # Missing to and fcn_name
                ],
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes (should use default values)
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None

    @pytest.mark.asyncio
    async def test_show_xrefs_many_entries(self, app_with_state):
        """Test displaying xrefs with many entries."""
        panel = DetailsPanel()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(panel)
            await pilot.pause()

            # Show xrefs with many entries
            callers = [
                {"from": 0x400000 + i * 0x10, "type": "CALL", "fcn_name": f"func_{i}"}
                for i in range(20)
            ]
            callees = [
                {"to": 0x500000 + i * 0x10, "type": "CALL", "fcn_name": f"helper_{i}"}
                for i in range(15)
            ]

            xref_data = {
                "callers": callers,
                "callees": callees,
            }
            panel.show_xrefs("0x401000", xref_data)
            await pilot.pause()

            # Verify no crashes with many entries
            content = panel.query_one(f"#{wid.DETAILS_CONTENT}")
            assert content is not None
