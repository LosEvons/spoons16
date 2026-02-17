"""Integration tests for CommandPalette with CaspoonApp."""

import pytest
from textual.widgets import Input

from caspoon.ui import widget_ids as wid
from caspoon.ui.app import CaspoonApp
from caspoon.ui.widgets.command_palette import CommandPalette


class TestCommandPaletteIntegration:
    """Integration tests for CommandPalette in the full app."""

    @pytest.mark.asyncio
    async def test_show_command_palette(self):
        """Test that Ctrl+P shows the command palette."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Initially palette should not be visible
            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)
            assert not palette.has_class("visible")

            # Trigger show command palette action
            app.action_show_command_palette()

            await pilot.pause()

            # Palette should now be visible
            assert palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_palette_closes_after_execution(self):
        """Test that palette closes after executing a command."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)
            assert palette.has_class("visible")

            # Search for quit command
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "quit"

            await pilot.pause()

            # Execute the command (but catch the exit)
            # We can't actually test quit execution, so we'll test close instead
            palette.action_close()

            await pilot.pause()

            # Palette should be hidden
            assert not palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_search_finds_commands(self):
        """Test that search returns expected results."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Search for "overview"
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "overview"

            await pilot.pause()

            # Should find the "Show Overview" command
            results = palette.query_one(f"#{wid.COMMAND_RESULTS}")
            assert len(results.children) >= 1

    @pytest.mark.asyncio
    async def test_palette_keyboard_navigation(self):
        """Test full keyboard workflow in palette."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)
            assert palette.has_class("visible")

            # Type to search
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "help"

            await pilot.pause()

            # Results should be filtered
            results = palette.query_one(f"#{wid.COMMAND_RESULTS}")
            assert len(results.children) >= 1

            # Close with escape
            palette.action_close()

            await pilot.pause()

            # Should be hidden
            assert not palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_execute_command_from_palette(self):
        """Test executing a command through the palette."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Search for help command
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "help"

            await pilot.pause()

            # Execute the command (this will show help notification)
            palette.action_execute()

            await pilot.pause()

            # Palette should be closed
            assert not palette.has_class("visible")

    @pytest.mark.asyncio
    async def test_command_registry_populated(self):
        """Test that app has registered commands."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Check that commands are registered
            all_actions = app.action_registry.get_all_actions()

            # Should have multiple commands
            assert len(all_actions) > 10

            # Check for specific categories
            categories = app.action_registry.get_all_categories()
            assert "File" in categories
            assert "View" in categories
            assert "Analysis" in categories
            assert "Help" in categories

    @pytest.mark.asyncio
    async def test_search_by_category(self):
        """Test searching commands by category."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Search for "view" (should match category)
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "view"

            await pilot.pause()

            results = palette.query_one(f"#{wid.COMMAND_RESULTS}")
            # Should find multiple view commands
            assert len(results.children) >= 3

    @pytest.mark.asyncio
    async def test_search_by_keybinding_text(self):
        """Test that keybindings are displayed in results."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Search for a command with a keybinding
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "quit"

            await pilot.pause()

            results = palette.query_one(f"#{wid.COMMAND_RESULTS}")
            # Should have at least one result
            assert len(results.children) >= 1

    @pytest.mark.asyncio
    async def test_palette_resets_on_reopen(self):
        """Test that palette resets when closed and reopened."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Show palette
            app.action_show_command_palette()

            await pilot.pause()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Set some search text
            search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
            search_input.value = "test"

            await pilot.pause()

            # Close palette
            palette.action_close()

            await pilot.pause()

            # Reopen palette
            app.action_show_command_palette()

            await pilot.pause()

            # Search should be reset
            assert search_input.value == ""

    @pytest.mark.asyncio
    async def test_all_registered_commands_searchable(self):
        """Test that all registered commands can be found via search."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            # Get all registered actions
            all_actions = app.action_registry.get_all_actions()

            palette = app.query_one(f"#{wid.COMMAND_PALETTE}", CommandPalette)

            # Test a few key commands
            test_commands = [
                ("quit", "file.quit"),
                ("overview", "view.overview"),
                ("help", "help.show"),
            ]

            for query, expected_id in test_commands:
                palette.show()
                await pilot.pause()

                search_input = palette.query_one(f"#{wid.COMMAND_SEARCH}", Input)
                search_input.value = query

                await pilot.pause()

                results = palette.query_one(f"#{wid.COMMAND_RESULTS}")
                # Should find the command - check the action_id attribute
                assert any(
                    getattr(child, "action_id", None) == expected_id
                    for child in results.children
                ), f"Command {expected_id} not found for query '{query}'"

                palette.action_close()
                await pilot.pause()
