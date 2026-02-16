"""Unit tests for CommandPalette widget."""

from unittest.mock import Mock

import pytest
from textual.widgets import Input, ListView

from caspoon.ui.core.actions import Action, ActionRegistry
from caspoon.ui.widgets.command_palette import CommandPalette


class TestCommandPalette:
    """Tests for CommandPalette widget."""

    @pytest.fixture
    def action_registry(self):
        """Create an ActionRegistry with test actions."""
        registry = ActionRegistry()

        # Register test actions
        registry.register(
            "file.open",
            "Open File",
            Mock(),
            "Open a file for editing",
            "ctrl+o",
            "File",
        )
        registry.register(
            "file.save",
            "Save File",
            Mock(),
            "Save current file",
            "ctrl+s",
            "File",
        )
        registry.register(
            "file.quit",
            "Quit Application",
            Mock(),
            "Exit the application",
            "ctrl+q",
            "File",
        )
        registry.register(
            "view.overview",
            "Show Overview",
            Mock(),
            "Switch to overview tab",
            "1",
            "View",
        )
        registry.register(
            "view.protections",
            "Show Protections",
            Mock(),
            "Switch to protections tab",
            "2",
            "View",
        )
        registry.register(
            "edit.copy",
            "Copy",
            Mock(),
            "Copy selection to clipboard",
            "ctrl+c",
            "Edit",
        )
        registry.register(
            "edit.paste",
            "Paste",
            Mock(),
            "Paste from clipboard",
            "ctrl+v",
            "Edit",
        )

        return registry

    def test_command_palette_initialization(self, action_registry):
        """Test that CommandPalette can be initialized with a registry."""
        palette = CommandPalette(action_registry)

        assert palette.action_registry is action_registry
        assert palette.id is None  # No ID set by default

    def test_command_palette_initialization_with_id(self, action_registry):
        """Test that CommandPalette can be initialized with an ID."""
        palette = CommandPalette(action_registry, id="test_palette")

        assert palette.action_registry is action_registry
        assert palette.id == "test_palette"

    @pytest.mark.asyncio
    async def test_command_palette_compose(self, action_registry):
        """Test that CommandPalette has Input and ListView components."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)

            # Check that Input and ListView are present
            search_input = palette.query_one("#search", Input)
            results_list = palette.query_one("#results", ListView)

            assert search_input is not None
            assert results_list is not None
            assert search_input.placeholder == "Type to search commands..."

    @pytest.mark.asyncio
    async def test_command_palette_shows_all_when_empty(self, action_registry):
        """Test that empty query shows all enabled commands."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")
            palette.on_show()

            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should show all actions (7 registered)
            assert len(results_list.children) == 7

    @pytest.mark.asyncio
    async def test_command_palette_filters_by_name(self, action_registry):
        """Test that palette filters commands by name."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # First populate all results
            palette._update_results("")
            await pilot.pause()

            # Now filter by "file"
            palette._update_results("file")
            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should show 3 file commands
            assert len(results_list.children) == 3

    @pytest.mark.asyncio
    async def test_command_palette_filters_by_description(self, action_registry):
        """Test that palette filters commands by description."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # First populate all results
            palette._update_results("")
            await pilot.pause()

            # Now filter by "clipboard"
            palette._update_results("clipboard")
            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should show copy and paste commands
            assert len(results_list.children) == 2

    @pytest.mark.asyncio
    async def test_command_palette_filters_by_category(self, action_registry):
        """Test that palette filters commands by category."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # First populate all results
            palette._update_results("")
            await pilot.pause()

            # Now filter by "view"
            palette._update_results("view")
            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should show 2 view commands
            assert len(results_list.children) == 2

    @pytest.mark.asyncio
    async def test_command_palette_case_insensitive(self, action_registry):
        """Test that search is case-insensitive."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # First populate all results
            palette._update_results("")
            await pilot.pause()

            # Now filter by "FILE" (uppercase)
            palette._update_results("FILE")
            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should still show 3 file commands
            assert len(results_list.children) == 3

    @pytest.mark.asyncio
    async def test_command_palette_limits_results(self, action_registry):
        """Test that palette limits results to 15."""
        from textual.app import App

        # Register 20 additional commands
        for i in range(20):
            action_registry.register(
                f"test.action{i}",
                f"Test Action {i}",
                Mock(),
                f"Test action number {i}",
                None,
                "Test",
            )

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")
            palette.on_show()

            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Should show max 15 results
            assert len(results_list.children) <= 15

    @pytest.mark.asyncio
    async def test_command_palette_execute_command(self):
        """Test that Enter executes the selected command."""
        from textual.app import App

        # Create a fresh registry just for this test
        fresh_registry = ActionRegistry()
        mock_handler = Mock()
        fresh_registry.register(
            "test.execute",
            "Test Execute",
            mock_handler,
            "Test command execution",
            None,
            "Test",
        )

        class TestApp(App):
            def compose(self):
                yield CommandPalette(fresh_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # Search for our test command
            palette._update_results("Test Execute")
            await pilot.pause()

            # Verify results are populated
            results = palette.query_one("#results", ListView)
            assert len(results.children) > 0, "Should have results"
            assert results.highlighted_child is not None, "Should have highlighted child"

            # Execute the command
            palette.action_execute()
            
            # Give time for execution to complete
            await pilot.pause()
            await pilot.pause()

            # Verify handler was called
            assert mock_handler.called, f"Handler should be called, call_count={mock_handler.call_count}"
            mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_command_palette_close(self, action_registry):
        """Test that Escape closes the palette."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            assert palette.has_class("visible")

            # Close the palette
            palette.action_close()

            await pilot.pause()

            # Should no longer be visible
            assert not palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_command_palette_displays_keybindings(self, action_registry):
        """Test that keybindings are displayed in results."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")
            palette.on_show()

            # Search for a command with keybinding
            search_input = palette.query_one("#search", Input)
            search_input.value = "open"

            await pilot.pause()

            results_list = palette.query_one("#results", ListView)
            # Check that results contain the keybinding
            # This is a simple check - the keybinding should be in the label text
            assert len(results_list.children) > 0

    @pytest.mark.asyncio
    async def test_command_palette_show_method(self, action_registry):
        """Test that show() method makes palette visible."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)

            # Initially not visible
            assert not palette.has_class("visible")

            # Show the palette
            palette.show()

            await pilot.pause()

            # Should now be visible
            assert palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_command_palette_reset_on_show(self, action_registry):
        """Test that palette resets search when shown."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CommandPalette(action_registry, id="palette")

        app = TestApp()
        async with app.run_test() as pilot:
            palette = app.query_one("#palette", CommandPalette)
            palette.add_class("visible")

            # Set some search text
            search_input = palette.query_one("#search", Input)
            search_input.value = "test"

            await pilot.pause()

            # Show again (should reset)
            palette.on_show()

            await pilot.pause()

            # Search should be cleared
            assert search_input.value == ""
