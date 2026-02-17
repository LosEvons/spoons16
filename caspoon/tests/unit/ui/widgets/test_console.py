"""Unit tests for Console widget."""

import pytest
from textual.widgets import RichLog

from caspoon.ui import widget_ids as wid
from caspoon.ui.widgets.console import Console


class TestConsole:
    """Test suite for Console widget."""

    @pytest.mark.asyncio
    async def test_console_initialization(self, app_with_state):
        """Test console initializes correctly."""
        console = Console()
        assert console is not None
        assert console.id is None  # No ID set by default

    @pytest.mark.asyncio
    async def test_console_compose(self, app_with_state):
        """Test console composes with RichLog widget."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)

            # Check RichLog widget is present
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert rich_log is not None

    @pytest.mark.asyncio
    async def test_log_info_message(self, app_with_state):
        """Test logging info level message."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log an info message
            console.log("Test info message", level="info")
            await pilot.pause()

            # Verify message was logged (RichLog should contain it)
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

    @pytest.mark.asyncio
    async def test_log_error_message(self, app_with_state):
        """Test logging error level message."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log an error message
            console.log("Test error message", level="error")
            await pilot.pause()

            # Verify message was logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

    @pytest.mark.asyncio
    async def test_log_warning_message(self, app_with_state):
        """Test logging warning level message."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log a warning message
            console.log("Test warning message", level="warning")
            await pilot.pause()

            # Verify message was logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

    @pytest.mark.asyncio
    async def test_log_success_message(self, app_with_state):
        """Test logging success level message."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log a success message
            console.log("Test success message", level="success")
            await pilot.pause()

            # Verify message was logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

    @pytest.mark.asyncio
    async def test_log_debug_message(self, app_with_state):
        """Test logging debug level message."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log a debug message
            console.log("Test debug message", level="debug")
            await pilot.pause()

            # Verify message was logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

    @pytest.mark.asyncio
    async def test_clear_console(self, app_with_state):
        """Test clearing console messages."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log some messages
            console.log("Message 1")
            console.log("Message 2")
            console.log("Message 3")
            await pilot.pause()

            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) > 0

            # Clear console
            console.clear()
            await pilot.pause()

            # Verify console is empty
            assert len(rich_log.lines) == 0

    @pytest.mark.asyncio
    async def test_action_clear_console(self, app_with_state):
        """Test clear console action (Ctrl+L)."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log some messages
            console.log("Message 1")
            await pilot.pause()

            # Trigger clear action
            console.action_clear_console()
            await pilot.pause()

            # Verify console is empty
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) == 0

    @pytest.mark.asyncio
    async def test_multiple_log_messages(self, app_with_state):
        """Test logging multiple messages in sequence."""
        console = Console()

        async with app_with_state.run_test() as pilot:
            await pilot.app.mount(console)
            await pilot.pause()

            # Log multiple messages
            console.log("Message 1", level="info")
            console.log("Message 2", level="warning")
            console.log("Message 3", level="error")
            await pilot.pause()

            # Verify all messages were logged
            rich_log = console.query_one(f"#{wid.CONSOLE_LOG}", RichLog)
            assert len(rich_log.lines) >= 3
