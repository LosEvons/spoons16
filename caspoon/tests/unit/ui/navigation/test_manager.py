"""Tests for NavigationManager."""

import pytest

from caspoon.ui.navigation import NavigationManager


class TestNavigationManagerInitialization:
    """Tests for NavigationManager initialization."""

    def test_manager_initializes_empty(self):
        """Test that NavigationManager starts with empty state."""
        manager = NavigationManager()

        assert manager.history == []
        assert manager.current_index == -1
        assert manager.address_map == {}

    def test_manager_can_be_created(self):
        """Test that NavigationManager can be instantiated."""
        manager = NavigationManager()
        assert manager is not None


class TestBasicNavigation:
    """Tests for basic navigation operations."""

    def test_navigate_to_single_address(self):
        """Test navigating to a single address."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")

        assert len(manager.history) == 1
        assert manager.history[0] == "0x1000"
        assert manager.current_index == 0
        assert manager.current_address() == "0x1000"

    def test_navigate_to_multiple_addresses(self):
        """Test navigating to multiple addresses in sequence."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        assert len(manager.history) == 3
        assert manager.history == ["0x1000", "0x2000", "0x3000"]
        assert manager.current_index == 2
        assert manager.current_address() == "0x3000"

    def test_navigate_to_same_address_multiple_times(self):
        """Test that navigating to the same address adds it to history each time."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x1000")
        manager.navigate_to("0x1000")

        assert len(manager.history) == 3
        assert all(addr == "0x1000" for addr in manager.history)


class TestBackNavigation:
    """Tests for back navigation."""

    def test_go_back_from_end(self):
        """Test going back from the end of history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        result = manager.go_back()

        assert result == "0x2000"
        assert manager.current_index == 1
        assert manager.current_address() == "0x2000"

    def test_go_back_multiple_times(self):
        """Test going back multiple times through history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")
        manager.navigate_to("0x4000")

        assert manager.go_back() == "0x3000"
        assert manager.go_back() == "0x2000"
        assert manager.go_back() == "0x1000"

        assert manager.current_index == 0
        assert manager.current_address() == "0x1000"

    def test_go_back_at_start_returns_none(self):
        """Test that going back at the start of history returns None."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.go_back()  # Now at index 0 (first item)

        result = manager.go_back()

        assert result is None
        assert manager.current_index == 0
        assert manager.current_address() == "0x1000"

    def test_go_back_with_empty_history(self):
        """Test that going back with empty history returns None."""
        manager = NavigationManager()

        result = manager.go_back()

        assert result is None
        assert manager.current_index == -1
        assert manager.current_address() is None

    def test_can_go_back_with_history(self):
        """Test can_go_back returns True when history exists."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")

        assert manager.can_go_back() is True

    def test_can_go_back_at_start(self):
        """Test can_go_back returns False at start of history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")

        assert manager.can_go_back() is False

    def test_can_go_back_with_empty_history(self):
        """Test can_go_back returns False with empty history."""
        manager = NavigationManager()

        assert manager.can_go_back() is False


class TestForwardNavigation:
    """Tests for forward navigation."""

    def test_go_forward_after_going_back(self):
        """Test going forward after going back."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        manager.go_back()  # Now at 0x2000
        result = manager.go_forward()

        assert result == "0x3000"
        assert manager.current_index == 2
        assert manager.current_address() == "0x3000"

    def test_go_forward_multiple_times(self):
        """Test going forward multiple times through history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")
        manager.navigate_to("0x4000")

        manager.go_back()
        manager.go_back()
        manager.go_back()  # Now at 0x1000

        assert manager.go_forward() == "0x2000"
        assert manager.go_forward() == "0x3000"
        assert manager.go_forward() == "0x4000"

        assert manager.current_index == 3
        assert manager.current_address() == "0x4000"

    def test_go_forward_at_end_returns_none(self):
        """Test that going forward at the end of history returns None."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")

        result = manager.go_forward()

        assert result is None
        assert manager.current_index == 1
        assert manager.current_address() == "0x2000"

    def test_go_forward_with_empty_history(self):
        """Test that going forward with empty history returns None."""
        manager = NavigationManager()

        result = manager.go_forward()

        assert result is None
        assert manager.current_index == -1

    def test_can_go_forward_after_going_back(self):
        """Test can_go_forward returns True after going back."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.go_back()

        assert manager.can_go_forward() is True

    def test_can_go_forward_at_end(self):
        """Test can_go_forward returns False at end of history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")

        assert manager.can_go_forward() is False

    def test_can_go_forward_with_empty_history(self):
        """Test can_go_forward returns False with empty history."""
        manager = NavigationManager()

        assert manager.can_go_forward() is False


class TestHistoryTruncation:
    """Tests for history truncation when navigating from middle."""

    def test_navigate_from_middle_truncates_forward(self):
        """Test that navigating from middle of history truncates forward history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")
        manager.navigate_to("0x4000")

        manager.go_back()
        manager.go_back()  # Now at 0x2000

        manager.navigate_to("0x5000")  # Should truncate 0x3000 and 0x4000

        assert manager.history == ["0x1000", "0x2000", "0x5000"]
        assert manager.current_index == 2
        assert manager.current_address() == "0x5000"
        assert manager.can_go_forward() is False

    def test_navigate_from_start_truncates_all_forward(self):
        """Test that navigating from start truncates all forward history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        manager.go_back()
        manager.go_back()  # Now at 0x1000 (index 0)

        manager.navigate_to("0x9000")

        assert manager.history == ["0x1000", "0x9000"]
        assert manager.current_index == 1
        assert manager.current_address() == "0x9000"

    def test_navigate_from_middle_then_back_forward(self):
        """Test complex navigation pattern after truncation."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        manager.go_back()  # At 0x2000
        manager.navigate_to("0x4000")  # Truncates 0x3000

        # New history: ["0x1000", "0x2000", "0x4000"]

        manager.go_back()  # At 0x2000
        manager.go_back()  # At 0x1000

        assert manager.current_address() == "0x1000"
        assert manager.go_forward() == "0x2000"
        assert manager.go_forward() == "0x4000"
        assert manager.can_go_forward() is False


class TestCurrentAddress:
    """Tests for current_address method."""

    def test_current_address_with_empty_history(self):
        """Test current_address returns None with empty history."""
        manager = NavigationManager()

        assert manager.current_address() is None

    def test_current_address_after_navigation(self):
        """Test current_address returns correct address after navigation."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        assert manager.current_address() == "0x1000"

        manager.navigate_to("0x2000")
        assert manager.current_address() == "0x2000"

    def test_current_address_after_back_navigation(self):
        """Test current_address updates correctly with back navigation."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        manager.go_back()
        assert manager.current_address() == "0x2000"

        manager.go_back()
        assert manager.current_address() == "0x1000"


class TestClearHistory:
    """Tests for clear_history method."""

    def test_clear_empty_history(self):
        """Test clearing empty history doesn't cause errors."""
        manager = NavigationManager()

        manager.clear_history()

        assert manager.history == []
        assert manager.current_index == -1
        assert manager.address_map == {}

    def test_clear_history_with_data(self):
        """Test clearing history removes all data."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")
        manager.set_address_map({"0x1000": {"name": "main"}})

        manager.clear_history()

        assert manager.history == []
        assert manager.current_index == -1
        assert manager.address_map == {}
        assert manager.current_address() is None
        assert manager.can_go_back() is False
        assert manager.can_go_forward() is False

    def test_navigation_after_clear(self):
        """Test that navigation works correctly after clearing history."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.clear_history()

        manager.navigate_to("0x3000")
        manager.navigate_to("0x4000")

        assert manager.history == ["0x3000", "0x4000"]
        assert manager.current_index == 1
        assert manager.current_address() == "0x4000"


class TestAddressMap:
    """Tests for address_map functionality."""

    def test_set_address_map_empty(self):
        """Test setting an empty address map."""
        manager = NavigationManager()

        manager.set_address_map({})

        assert manager.address_map == {}

    def test_set_address_map_with_data(self):
        """Test setting address map with function data."""
        manager = NavigationManager()

        address_map = {
            "0x1000": {"name": "main", "size": 100},
            "0x2000": {"name": "helper", "size": 50},
        }

        manager.set_address_map(address_map)

        assert manager.address_map == address_map

    def test_set_address_map_replaces_existing(self):
        """Test that setting address map replaces existing data."""
        manager = NavigationManager()

        manager.set_address_map({"0x1000": {"name": "old"}})
        manager.set_address_map({"0x2000": {"name": "new"}})

        assert "0x1000" not in manager.address_map
        assert manager.address_map == {"0x2000": {"name": "new"}}

    def test_address_map_persists_through_navigation(self):
        """Test that address map persists during navigation."""
        manager = NavigationManager()

        address_map = {"0x1000": {"name": "main"}}
        manager.set_address_map(address_map)

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.go_back()

        assert manager.address_map == address_map

    def test_address_map_cleared_with_history(self):
        """Test that address map is cleared when clearing history."""
        manager = NavigationManager()

        manager.set_address_map({"0x1000": {"name": "main"}})
        manager.clear_history()

        assert manager.address_map == {}


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_history(self):
        """Test navigation with a very long history."""
        manager = NavigationManager()

        # Create long history
        for i in range(1000):
            manager.navigate_to(f"0x{i:04x}")

        assert len(manager.history) == 1000
        assert manager.current_index == 999

        # Test going back through long history
        for _ in range(100):
            manager.go_back()

        assert manager.current_index == 899
        assert manager.current_address() == "0x0383"

    def test_navigate_with_special_address_formats(self):
        """Test navigation with different address formats."""
        manager = NavigationManager()

        addresses = [
            "0x1000",
            "0x00001000",
            "0X1000",
            "1000",
            "func_main",
            "sym.main",
            "entry0",
        ]

        for addr in addresses:
            manager.navigate_to(addr)

        assert len(manager.history) == len(addresses)
        assert manager.history == addresses

    def test_navigate_with_empty_string(self):
        """Test navigation with empty string address."""
        manager = NavigationManager()

        manager.navigate_to("")
        manager.navigate_to("0x1000")
        manager.navigate_to("")

        assert len(manager.history) == 3
        assert manager.history[0] == ""
        assert manager.history[2] == ""

    def test_multiple_back_forward_cycles(self):
        """Test multiple back and forward navigation cycles."""
        manager = NavigationManager()

        manager.navigate_to("0x1000")
        manager.navigate_to("0x2000")
        manager.navigate_to("0x3000")

        # Cycle 1
        manager.go_back()
        manager.go_forward()

        assert manager.current_address() == "0x3000"

        # Cycle 2
        manager.go_back()
        manager.go_back()
        manager.go_forward()
        manager.go_forward()

        assert manager.current_address() == "0x3000"

    def test_navigation_boundary_conditions(self):
        """Test all boundary conditions in sequence."""
        manager = NavigationManager()

        # Empty state
        assert manager.go_back() is None
        assert manager.go_forward() is None
        assert manager.current_address() is None

        # Single item
        manager.navigate_to("0x1000")
        assert manager.go_back() is None  # Can't go back from first item
        assert manager.go_forward() is None  # No forward history
        assert manager.current_address() == "0x1000"

        # Two items
        manager.navigate_to("0x2000")
        assert manager.can_go_back() is True
        assert manager.can_go_forward() is False

        manager.go_back()
        assert manager.can_go_back() is False
        assert manager.can_go_forward() is True


class TestRealWorldScenarios:
    """Tests with realistic usage scenarios."""

    def test_typical_function_browsing(self):
        """Test typical navigation pattern when browsing functions."""
        manager = NavigationManager()

        # User starts at entry point
        manager.navigate_to("entry0")

        # Follows a call to main
        manager.navigate_to("sym.main")

        # Follows a call to printf
        manager.navigate_to("sym.imp.printf")

        # Goes back to main
        assert manager.go_back() == "sym.main"

        # Follows different call to malloc
        manager.navigate_to("sym.imp.malloc")

        # History should be: entry0, main, malloc
        # (printf was truncated)
        assert manager.history == ["entry0", "sym.main", "sym.imp.malloc"]

    def test_exploring_xrefs(self):
        """Test navigation when exploring cross-references."""
        manager = NavigationManager()

        # Set up address map with function info
        address_map = {
            "0x401000": {"name": "main", "xrefs": ["0x402000", "0x403000"]},
            "0x402000": {"name": "helper1"},
            "0x403000": {"name": "helper2"},
        }
        manager.set_address_map(address_map)

        # Start at main
        manager.navigate_to("0x401000")

        # Check first xref
        manager.navigate_to("0x402000")

        # Go back to main
        manager.go_back()
        assert manager.current_address() == "0x401000"

        # Check second xref
        manager.navigate_to("0x403000")

        # Verify history
        assert manager.history == ["0x401000", "0x403000"]

    def test_deep_call_chain_navigation(self):
        """Test navigating through a deep call chain."""
        manager = NavigationManager()

        call_chain = [
            "entry0",
            "__libc_start_main",
            "main",
            "process_input",
            "parse_args",
            "validate_arg",
            "strlen",
        ]

        # Navigate through call chain
        for func in call_chain:
            manager.navigate_to(func)

        # Navigate all the way back
        for i in range(len(call_chain) - 1, 0, -1):
            result = manager.go_back()
            assert result == call_chain[i - 1]

        # Navigate all the way forward
        for i in range(1, len(call_chain)):
            result = manager.go_forward()
            assert result == call_chain[i]
