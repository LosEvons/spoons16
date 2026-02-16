"""Unit tests for FunctionExplorer widget."""

import pytest

from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.widgets.function_explorer import FunctionExplorer


class TestFunctionExplorer:
    """Test suite for FunctionExplorer widget."""

    @pytest.mark.asyncio
    async def test_function_explorer_initialization(self, app_with_state):
        """Test function explorer initializes correctly."""
        explorer = FunctionExplorer()
        assert explorer is not None
        assert explorer._functions == []
        assert explorer._sections == {}

    @pytest.mark.asyncio
    async def test_render_with_no_data(self, app_with_state):
        """Test rendering with no analysis data."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Render with empty data
            empty_results = AnalysisResults()
            explorer.render_content(empty_results)
            await pilot.pause()

            # Should not crash
            assert explorer._functions == []

    @pytest.mark.asyncio
    async def test_render_with_functions(self, app_with_state):
        """Test rendering with function data."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Create test data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "printf", "address": 0x402000, "section": ".plt"},
                    {"name": "malloc", "address": 0x403000, "section": ".plt"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Verify functions are organized
            assert len(explorer._functions) == 3
            assert len(explorer._sections) == 2
            assert ".text" in explorer._sections
            assert ".plt" in explorer._sections

    @pytest.mark.asyncio
    async def test_get_root_nodes(self, app_with_state):
        """Test getting root section nodes."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "sub_401100", "address": 0x401100, "section": ".text"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Get root nodes
            roots = explorer.get_root_nodes()
            assert len(roots) == 1
            assert roots[0].node_id == ".text"
            assert roots[0].has_children is True
            assert "2 functions" in roots[0].label

    @pytest.mark.asyncio
    async def test_get_child_nodes(self, app_with_state):
        """Test getting child function nodes."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "sub_401100", "address": 0x401100, "section": ".text"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Get child nodes
            children = explorer.get_child_nodes(".text")
            assert len(children) == 2
            assert children[0].has_children is False
            assert "main" in children[0].label
            assert "0x00401000" in children[0].label

    @pytest.mark.asyncio
    async def test_get_item_count(self, app_with_state):
        """Test getting total item count."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Initially collapsed - only section node visible
            count = explorer.get_item_count()
            assert count == 1

            # Expand section
            explorer.expanded_nodes = {".text"}
            count = explorer.get_item_count()
            assert count == 2  # Section + 1 function

    @pytest.mark.asyncio
    async def test_apply_filter(self, app_with_state):
        """Test filtering functions by name."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "test_func", "address": 0x401100, "section": ".text"},
                    {"name": "printf", "address": 0x402000, "section": ".plt"},
                ]
            )
            explorer.data = results
            explorer.render_content(results)
            await pilot.pause()

            # Apply filter
            explorer.apply_filter("test")
            await pilot.pause()

            # Should only show functions matching "test"
            assert len(explorer._functions) == 1
            assert explorer._functions[0]["name"] == "test_func"

    @pytest.mark.asyncio
    async def test_section_organization(self, app_with_state):
        """Test functions are correctly organized by section."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data with multiple sections
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                    {"name": "sub_401100", "address": 0x401100, "section": ".text"},
                    {"name": "printf", "address": 0x402000, "section": ".plt"},
                    {"name": "_start", "address": 0x400000, "section": ".init"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Check section organization
            assert len(explorer._sections) == 3
            assert len(explorer._sections[".text"]) == 2
            assert len(explorer._sections[".plt"]) == 1
            assert len(explorer._sections[".init"]) == 1

    @pytest.mark.asyncio
    async def test_format_function_label(self, app_with_state):
        """Test function label formatting."""
        explorer = FunctionExplorer()

        # Test normal function
        func1 = {"name": "main", "address": 0x401000}
        label1 = explorer._format_function_label(func1)
        assert "main" in label1
        assert "0x00401000" in label1

        # Test long function name (should truncate)
        long_name = "a" * 50
        func2 = {"name": long_name, "address": 0x402000}
        label2 = explorer._format_function_label(func2)
        assert "..." in label2
        assert len(label2) < len(long_name) + 20

    @pytest.mark.asyncio
    async def test_function_selection_toggle(self, app_with_state):
        """Test selecting a section toggles expansion."""
        explorer = FunctionExplorer()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(explorer)
            await pilot.pause()

            # Set up data
            results = AnalysisResults(
                functions=[
                    {"name": "main", "address": 0x401000, "section": ".text"},
                ]
            )
            explorer.render_content(results)
            await pilot.pause()

            # Select section (index 0)
            explorer.selected_index = 0
            explorer.on_item_selected(0)
            await pilot.pause()

            # Section should be expanded
            assert ".text" in explorer.expanded_nodes
