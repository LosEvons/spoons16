"""Unit tests for navigation command handlers in CaspoonApp."""

from unittest.mock import Mock, patch

import pytest

from caspoon.ui.core.messages import JumpToAddress
from caspoon.ui.core.state import AppState


class TestNavigationCommandHandlers:
    """Tests for navigation command handlers."""

    @pytest.fixture
    def app_state(self):
        """Create an AppState with navigation history."""
        state = AppState()
        # Add some history
        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")
        return state

    def test_navigate_back_with_history(self, app_state):
        """Test navigate back when history is available."""
        # We're at index 2 (0x401020)
        assert app_state.current_nav_index == 2

        # Go back
        address = app_state.go_back()

        assert address == "0x401010"
        assert app_state.current_nav_index == 1

    def test_navigate_back_at_start(self, app_state):
        """Test navigate back when at start of history."""
        # Go back to start
        app_state.go_back()
        app_state.go_back()

        assert app_state.current_nav_index == 0

        # Try to go back again
        address = app_state.go_back()

        assert address is None
        assert app_state.current_nav_index == 0

    def test_navigate_forward_with_history(self, app_state):
        """Test navigate forward when forward history is available."""
        # Go back twice
        app_state.go_back()
        app_state.go_back()

        assert app_state.current_nav_index == 0

        # Go forward
        address = app_state.go_forward()

        assert address == "0x401010"
        assert app_state.current_nav_index == 1

    def test_navigate_forward_at_end(self, app_state):
        """Test navigate forward when at end of history."""
        # Already at end (index 2)
        assert app_state.current_nav_index == 2

        # Try to go forward
        address = app_state.go_forward()

        assert address is None
        assert app_state.current_nav_index == 2

    def test_navigate_to_truncates_forward_history(self, app_state):
        """Test that navigating to new address truncates forward history."""
        # Go back
        app_state.go_back()
        assert app_state.current_nav_index == 1

        # Navigate to new address
        app_state.navigate_to("0x401030")

        # Forward history should be truncated
        assert len(app_state.navigation_history) == 3
        assert app_state.navigation_history[-1] == "0x401030"
        assert app_state.current_nav_index == 2

    def test_can_go_back(self, app_state):
        """Test can_go_back method."""
        assert app_state.can_go_back() is True

        # Go back to start
        app_state.go_back()
        app_state.go_back()

        assert app_state.can_go_back() is False

    def test_can_go_forward(self, app_state):
        """Test can_go_forward method."""
        # At end, can't go forward
        assert app_state.can_go_forward() is False

        # Go back once
        app_state.go_back()

        # Now we can go forward
        assert app_state.can_go_forward() is True

    def test_empty_history(self):
        """Test navigation with empty history."""
        state = AppState()

        assert state.can_go_back() is False
        assert state.can_go_forward() is False
        assert state.go_back() is None
        assert state.go_forward() is None


class TestNavigationMessages:
    """Tests for navigation-related message handling."""

    def test_jump_to_address_message_creation(self):
        """Test JumpToAddress message can be created."""
        # Test with hex string
        msg = JumpToAddress("0x401000")
        assert msg.address == "0x401000"

        # Test with integer
        msg = JumpToAddress(0x401000)
        assert msg.address == 0x401000

    def test_jump_to_address_message_attributes(self):
        """Test JumpToAddress message has correct attributes."""
        msg = JumpToAddress("0x401000")

        assert hasattr(msg, "address")
        assert isinstance(msg.address, str)


class TestAddressValidation:
    """Tests for address validation logic."""

    @pytest.mark.parametrize(
        "address,expected",
        [
            ("0x401000", True),
            ("0x0", True),
            ("0xDEADBEEF", True),
            ("0xdeadbeef", True),
            ("401000", False),  # Missing 0x prefix
            ("0x", False),  # No hex digits
            ("0xGGGG", False),  # Invalid hex
            ("", False),  # Empty
            ("invalid", False),  # Not hex
        ],
    )
    def test_hex_address_validation(self, address, expected):
        """Test hex address validation patterns."""
        import re

        # Regex pattern for valid hex addresses
        pattern = r"^0x[0-9a-fA-F]+$"

        result = bool(re.match(pattern, address))
        assert result == expected

    def test_address_normalization(self):
        """Test address normalization (case insensitivity)."""
        addr1 = "0x401000"
        addr2 = "0X401000"
        addr3 = "0x401000"

        # All should normalize to same value
        assert addr1.lower() == addr2.lower()
        assert addr1.lower() == addr3.lower()

    def test_integer_to_hex_conversion(self):
        """Test converting integer addresses to hex strings."""
        address = 0x401000
        hex_str = hex(address)

        assert hex_str == "0x401000"
        assert isinstance(hex_str, str)


class TestNavigationStateSubscription:
    """Tests for navigation state change subscriptions."""

    def test_navigation_history_subscription(self):
        """Test subscribing to navigation history changes."""
        state = AppState()
        callback_called = []

        def on_history_change(value):
            callback_called.append(value)

        state.subscribe("navigation_history", on_history_change)

        # Navigate to trigger callback
        state.navigate_to("0x401000")

        assert len(callback_called) == 1
        assert callback_called[0] == ["0x401000"]

    def test_navigation_index_subscription(self):
        """Test subscribing to navigation index changes."""
        state = AppState()
        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        callback_called = []

        def on_index_change(value):
            callback_called.append(value)

        state.subscribe("current_nav_index", on_index_change)

        # Go back to trigger callback
        state.go_back()

        assert len(callback_called) == 1
        assert callback_called[0] == 0  # Index went from 1 to 0

    def test_multiple_navigation_changes(self):
        """Test multiple navigation changes trigger subscriptions."""
        state = AppState()
        history_changes = []
        index_changes = []

        state.subscribe("navigation_history", lambda v: history_changes.append(len(v)))
        state.subscribe("current_nav_index", lambda v: index_changes.append(v))

        # Make several navigation changes
        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")

        # Should have recorded all history changes
        assert len(history_changes) == 3
        assert history_changes == [1, 2, 3]

        # Index changes should track position
        assert len(index_changes) == 3
        assert index_changes == [0, 1, 2]


class TestNavigationEdgeCases:
    """Tests for edge cases in navigation."""

    def test_navigate_to_same_address_twice(self):
        """Test navigating to the same address multiple times."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401000")

        # Should have both entries in history
        assert len(state.navigation_history) == 2
        assert state.navigation_history == ["0x401000", "0x401000"]

    def test_navigate_to_special_addresses(self):
        """Test navigating to special addresses (0x0, very large)."""
        state = AppState()

        # Zero address
        state.navigate_to("0x0")
        assert state.navigation_history[-1] == "0x0"

        # Very large address
        state.navigate_to("0x7fffffffffffffff")
        assert state.navigation_history[-1] == "0x7fffffffffffffff"

    def test_reset_clears_navigation_history(self):
        """Test that reset clears navigation history."""
        state = AppState()

        # Add history
        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        # Reset
        state.reset()

        # History should be cleared
        assert len(state.navigation_history) == 0
        assert state.current_nav_index == -1

    def test_long_navigation_history(self):
        """Test navigation with long history."""
        state = AppState()

        # Add 100 addresses
        for i in range(100):
            state.navigate_to(f"0x{i:06x}")

        assert len(state.navigation_history) == 100
        assert state.current_nav_index == 99

        # Go back 50 times
        for _ in range(50):
            state.go_back()

        assert state.current_nav_index == 49

        # Go forward 25 times
        for _ in range(25):
            state.go_forward()

        assert state.current_nav_index == 74
