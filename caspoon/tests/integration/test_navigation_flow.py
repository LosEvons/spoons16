"""Integration tests for interactive navigation features.

Tests the complete navigation flow including navigation state management,
message passing, cross-reference integration, and multi-component interactions.
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from caspoon.backends.r2_analyzer import analyze_with_r2
from caspoon.ui.core.messages import JumpToAddress, SelectFunction
from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.core.state import AppState


@pytest.mark.integration
class TestNavigationStateFlow:
    """Test navigation state management in AppState."""

    def test_navigate_to_adds_to_history(self):
        """Test that navigate_to adds address to history."""
        state = AppState()

        # Initially empty
        assert state.navigation_history == []
        assert state.current_nav_index == -1

        # Add first address
        state.navigate_to("0x401000")
        assert state.navigation_history == ["0x401000"]
        assert state.current_nav_index == 0

        # Add second address
        state.navigate_to("0x401100")
        assert state.navigation_history == ["0x401000", "0x401100"]
        assert state.current_nav_index == 1

        # Add third address
        state.navigate_to("0x401200")
        assert state.navigation_history == ["0x401000", "0x401100", "0x401200"]
        assert state.current_nav_index == 2

    def test_navigate_truncates_forward_history(self):
        """Test that navigating from middle truncates forward history."""
        state = AppState()

        # Build history
        state.navigate_to("0x401000")
        state.navigate_to("0x401100")
        state.navigate_to("0x401200")
        state.navigate_to("0x401300")

        # Go back twice
        state.go_back()
        state.go_back()
        assert state.current_nav_index == 1
        assert state.navigation_history == ["0x401000", "0x401100", "0x401200", "0x401300"]

        # Navigate to new address - should truncate forward history
        state.navigate_to("0x402000")
        assert state.navigation_history == ["0x401000", "0x401100", "0x402000"]
        assert state.current_nav_index == 2

    def test_go_back_navigation(self):
        """Test backward navigation through history."""
        state = AppState()

        # Build history
        state.navigate_to("0x401000")
        state.navigate_to("0x401100")
        state.navigate_to("0x401200")

        # Test going back
        assert state.can_go_back()
        addr = state.go_back()
        assert addr == "0x401100"
        assert state.current_nav_index == 1

        assert state.can_go_back()
        addr = state.go_back()
        assert addr == "0x401000"
        assert state.current_nav_index == 0

        # Can't go back further
        assert not state.can_go_back()
        addr = state.go_back()
        assert addr is None
        assert state.current_nav_index == 0

    def test_go_forward_navigation(self):
        """Test forward navigation through history."""
        state = AppState()

        # Build history and go back
        state.navigate_to("0x401000")
        state.navigate_to("0x401100")
        state.navigate_to("0x401200")
        state.go_back()
        state.go_back()

        # Test going forward
        assert state.can_go_forward()
        addr = state.go_forward()
        assert addr == "0x401100"
        assert state.current_nav_index == 1

        assert state.can_go_forward()
        addr = state.go_forward()
        assert addr == "0x401200"
        assert state.current_nav_index == 2

        # Can't go forward further
        assert not state.can_go_forward()
        addr = state.go_forward()
        assert addr is None
        assert state.current_nav_index == 2

    def test_can_go_back_and_forward(self):
        """Test can_go_back and can_go_forward methods."""
        state = AppState()

        # Empty history
        assert not state.can_go_back()
        assert not state.can_go_forward()

        # One item
        state.navigate_to("0x401000")
        assert not state.can_go_back()
        assert not state.can_go_forward()

        # Two items
        state.navigate_to("0x401100")
        assert state.can_go_back()
        assert not state.can_go_forward()

        # After going back
        state.go_back()
        assert not state.can_go_back()
        assert state.can_go_forward()

        # In middle of history
        state.navigate_to("0x401100")
        state.navigate_to("0x401200")
        state.go_back()
        assert state.can_go_back()
        assert state.can_go_forward()

    def test_navigation_history_subscription(self):
        """Test that navigation changes trigger callbacks."""
        state = AppState()
        history_updates = []
        index_updates = []

        # Subscribe to changes
        state.subscribe("navigation_history", lambda v: history_updates.append(v))
        state.subscribe("current_nav_index", lambda v: index_updates.append(v))

        # Navigate
        state.navigate_to("0x401000")
        assert len(history_updates) == 1
        assert len(index_updates) == 1
        assert history_updates[0] == ["0x401000"]
        assert index_updates[0] == 0

        # Navigate again
        state.navigate_to("0x401100")
        assert len(history_updates) == 2
        assert len(index_updates) == 2
        assert history_updates[1] == ["0x401000", "0x401100"]
        assert index_updates[1] == 1

        # Go back
        state.go_back()
        assert len(history_updates) == 2  # History list doesn't change
        assert len(index_updates) == 3  # Index changes
        assert index_updates[2] == 0

    def test_reset_clears_navigation_history(self):
        """Test that reset() clears navigation history."""
        state = AppState()

        # Build history
        state.navigate_to("0x401000")
        state.navigate_to("0x401100")
        state.navigate_to("0x401200")

        # Reset
        state.reset()

        # History should be cleared
        assert state.navigation_history == []
        assert state.current_nav_index == -1
        assert not state.can_go_back()
        assert not state.can_go_forward()


@pytest.mark.integration
class TestJumpToAddressMessageFlow:
    """Test JumpToAddress message flow and handling."""

    @pytest.mark.asyncio
    async def test_jump_to_address_message_creation(self):
        """Test creating JumpToAddress messages with different address formats."""
        # String address
        msg1 = JumpToAddress("0x401000")
        assert msg1.address == "0x401000"

        # Integer address
        msg2 = JumpToAddress(0x401000)
        assert msg2.address == 0x401000

        # Verify messages are different instances
        assert msg1 is not msg2

    @pytest.mark.asyncio
    async def test_select_function_message_creation(self):
        """Test creating SelectFunction messages."""
        # With address
        msg1 = SelectFunction("main", address="0x401000")
        assert msg1.function_name == "main"
        assert msg1.address == "0x401000"

        # Without address
        msg2 = SelectFunction("printf")
        assert msg2.function_name == "printf"
        assert msg2.address is None


@pytest.mark.integration
@pytest.mark.requires_r2
class TestCrossReferenceIntegration:
    """Test cross-reference extraction and integration."""

    def test_xref_extraction_structure(self, sample_binary):
        """Test that xrefs are extracted with correct structure."""
        result = analyze_with_r2(sample_binary)

        assert "xrefs" in result
        assert isinstance(result["xrefs"], dict)

        # Verify structure of xref data
        for hex_addr, xref_data in result["xrefs"].items():
            # Check address format
            assert hex_addr.startswith("0x")
            assert isinstance(hex_addr, str)

            # Check xref data structure
            assert "callers" in xref_data
            assert "callees" in xref_data
            assert isinstance(xref_data["callers"], list)
            assert isinstance(xref_data["callees"], list)

            # At least one should be non-empty
            assert xref_data["callers"] or xref_data["callees"]

    def test_xref_addresses_are_valid_hex(self, sample_binary):
        """Test that all xref addresses are valid hex strings."""
        result = analyze_with_r2(sample_binary)

        for hex_addr in result["xrefs"].keys():
            # Should parse as hex
            try:
                int(hex_addr, 16)
            except ValueError:
                pytest.fail(f"Invalid hex address: {hex_addr}")

    def test_caller_callee_structure(self, sample_binary):
        """Test that callers and callees have correct structure."""
        result = analyze_with_r2(sample_binary)

        for hex_addr, xref_data in result["xrefs"].items():
            # Check callers
            for caller in xref_data["callers"]:
                # Should have address field (from or addr)
                assert "from" in caller or "addr" in caller
                # May have optional fields
                if "from" in caller:
                    assert isinstance(caller["from"], (str, int))

            # Check callees
            for callee in xref_data["callees"]:
                # Should have address field (to or addr)
                assert "to" in callee or "addr" in callee
                # May have optional fields
                if "to" in callee:
                    assert isinstance(callee["to"], (str, int))

    def test_xrefs_correspond_to_functions(self, sample_binary):
        """Test that xref addresses correspond to analyzed functions."""
        result = analyze_with_r2(sample_binary)

        if not result["xrefs"]:
            pytest.skip("No xrefs found in binary")

        # Get function addresses
        func_addrs = {f"0x{func['offset']:x}" for func in result["functions"] if "offset" in func}

        # All xref keys should correspond to function addresses
        for xref_addr in result["xrefs"].keys():
            assert xref_addr in func_addrs, f"Xref address {xref_addr} not in function list"

    def test_xrefs_with_navigation_addresses(self, sample_binary):
        """Test that xref addresses can be used for navigation."""
        result = analyze_with_r2(sample_binary)

        if not result["xrefs"]:
            pytest.skip("No xrefs found in binary")

        # Get first xref
        first_addr = next(iter(result["xrefs"]))
        xref_data = result["xrefs"][first_addr]

        # Test that we can navigate to callers
        for caller in xref_data["callers"]:
            caller_addr = caller.get("from") or caller.get("addr")
            if caller_addr:
                # Should be able to create navigation message
                msg = JumpToAddress(caller_addr)
                assert msg.address == caller_addr

        # Test that we can navigate to callees
        for callee in xref_data["callees"]:
            callee_addr = callee.get("to") or callee.get("addr")
            if callee_addr:
                # Should be able to create navigation message
                msg = JumpToAddress(callee_addr)
                assert msg.address == callee_addr


@pytest.mark.integration
class TestMultiComponentIntegration:
    """Test navigation across multiple UI components."""

    @pytest.mark.asyncio
    async def test_function_explorer_to_state_navigation(self, app_with_state, mock_analysis_results):
        """Test navigation from FunctionExplorer updates AppState."""
        app = app_with_state
        app.state.analysis_results = mock_analysis_results

        # Simulate function selection
        selected_function = mock_analysis_results.functions[0]
        function_address = f"0x{selected_function['address']:x}"

        # Navigate via state
        app.state.navigate_to(function_address)

        # Verify navigation history
        assert len(app.state.navigation_history) == 1
        assert app.state.navigation_history[0] == function_address
        assert app.state.current_nav_index == 0

    @pytest.mark.asyncio
    async def test_back_forward_navigation_preserves_state(self, app_with_state, mock_analysis_results):
        """Test that back/forward navigation preserves correct state."""
        app = app_with_state
        app.state.analysis_results = mock_analysis_results

        # Navigate to multiple addresses
        addresses = ["0x401000", "0x401100", "0x402000"]
        for addr in addresses:
            app.state.navigate_to(addr)

        # Go back twice
        back1 = app.state.go_back()
        assert back1 == "0x401100"

        back2 = app.state.go_back()
        assert back2 == "0x401000"

        # Go forward once
        forward1 = app.state.go_forward()
        assert forward1 == "0x401100"

        # Verify state is correct
        assert app.state.current_nav_index == 1
        assert app.state.navigation_history == addresses

    @pytest.mark.asyncio
    async def test_state_updates_trigger_callbacks(self, app_with_state):
        """Test that navigation state changes trigger registered callbacks."""
        app = app_with_state
        callback_invocations = []

        def nav_callback(value):
            callback_invocations.append(("history", value))

        def index_callback(value):
            callback_invocations.append(("index", value))

        # Subscribe callbacks
        app.state.subscribe("navigation_history", nav_callback)
        app.state.subscribe("current_nav_index", index_callback)

        # Navigate
        app.state.navigate_to("0x401000")

        # Verify callbacks were invoked
        assert len(callback_invocations) == 2
        assert any(t[0] == "history" for t in callback_invocations)
        assert any(t[0] == "index" for t in callback_invocations)

    @pytest.mark.asyncio
    async def test_multiple_navigation_sources(self, app_with_state, mock_analysis_results):
        """Test navigation from different sources (function list, xrefs, command palette)."""
        app = app_with_state
        app.state.analysis_results = mock_analysis_results

        # Navigate from function list
        app.state.navigate_to("0x401000")
        assert len(app.state.navigation_history) == 1

        # Navigate from xref (simulated)
        app.state.navigate_to("0x401100")
        assert len(app.state.navigation_history) == 2

        # Navigate from command palette (simulated)
        app.state.navigate_to("0x402000")
        assert len(app.state.navigation_history) == 3

        # All navigations should be in history
        assert app.state.navigation_history == ["0x401000", "0x401100", "0x402000"]


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end navigation workflows."""

    @pytest.mark.asyncio
    async def test_browse_select_navigate_back_forward(self, app_with_state, mock_analysis_results):
        """Test complete workflow: browse → select → navigate → back → forward.

        This simulates a typical user workflow:
        1. Browse functions
        2. Select a function
        3. Navigate to cross-reference
        4. Go back to previous function
        5. Go forward again
        """
        app = app_with_state
        app.state.analysis_results = mock_analysis_results

        # Step 1: Browse functions (select main)
        main_addr = "0x401000"
        app.state.navigate_to(main_addr)
        assert app.state.current_nav_index == 0
        assert app.state.navigation_history[-1] == main_addr

        # Step 2: Navigate to a called function
        called_addr = "0x401100"
        app.state.navigate_to(called_addr)
        assert app.state.current_nav_index == 1
        assert app.state.navigation_history[-1] == called_addr

        # Step 3: Navigate to another function
        plt_addr = "0x402000"
        app.state.navigate_to(plt_addr)
        assert app.state.current_nav_index == 2
        assert app.state.navigation_history[-1] == plt_addr

        # Step 4: Go back
        back_addr = app.state.go_back()
        assert back_addr == called_addr
        assert app.state.current_nav_index == 1

        # Step 5: Go back again
        back_addr2 = app.state.go_back()
        assert back_addr2 == main_addr
        assert app.state.current_nav_index == 0

        # Step 6: Go forward
        forward_addr = app.state.go_forward()
        assert forward_addr == called_addr
        assert app.state.current_nav_index == 1

        # Step 7: Go forward again
        forward_addr2 = app.state.go_forward()
        assert forward_addr2 == plt_addr
        assert app.state.current_nav_index == 2

    @pytest.mark.asyncio
    @pytest.mark.requires_r2
    async def test_xref_navigation_workflow(self, app_with_state, sample_binary):
        """Test workflow: view function → show xrefs → navigate to caller.

        This tests the cross-reference navigation workflow:
        1. Analyze binary and extract xrefs
        2. View a function
        3. Display its xrefs
        4. Navigate to a caller
        5. Navigate back
        """
        app = app_with_state

        # Analyze binary with xrefs
        result = analyze_with_r2(sample_binary)
        assert "xrefs" in result

        if not result["xrefs"]:
            pytest.skip("No xrefs found in binary")

        # Get first function with xrefs
        first_addr = next(iter(result["xrefs"]))
        xref_data = result["xrefs"][first_addr]

        # Step 1: Navigate to function
        app.state.navigate_to(first_addr)
        assert app.state.navigation_history[-1] == first_addr

        # Step 2: If function has callers, navigate to one
        if xref_data["callers"]:
            caller = xref_data["callers"][0]
            caller_addr = caller.get("from") or caller.get("addr")

            if caller_addr:
                # Normalize to hex string if needed
                if isinstance(caller_addr, int):
                    caller_addr = f"0x{caller_addr:x}"

                # Navigate to caller
                app.state.navigate_to(caller_addr)
                assert len(app.state.navigation_history) == 2
                assert app.state.navigation_history[-1] == caller_addr

                # Navigate back to original function
                back_addr = app.state.go_back()
                assert back_addr == first_addr
                assert app.state.current_nav_index == 0

    @pytest.mark.asyncio
    async def test_navigation_with_branching_history(self, app_with_state):
        """Test navigation with branching (creating new branch from history middle).

        Workflow:
        1. Navigate A → B → C
        2. Go back to B
        3. Navigate to D (creates new branch, truncates C)
        4. Verify forward to C is no longer possible
        """
        app = app_with_state

        # Build initial history
        app.state.navigate_to("0x401000")  # A
        app.state.navigate_to("0x401100")  # B
        app.state.navigate_to("0x401200")  # C

        # Go back to B
        app.state.go_back()
        assert app.state.current_nav_index == 1
        assert app.state.can_go_forward()  # C is still in future

        # Navigate to D - should truncate C
        app.state.navigate_to("0x402000")  # D

        # Verify C was truncated
        assert app.state.navigation_history == ["0x401000", "0x401100", "0x402000"]
        assert app.state.current_nav_index == 2
        assert not app.state.can_go_forward()  # No more forward history

        # Go back to verify history
        back1 = app.state.go_back()
        assert back1 == "0x401100"  # B

        back2 = app.state.go_back()
        assert back2 == "0x401000"  # A

    @pytest.mark.asyncio
    async def test_rapid_navigation_sequence(self, app_with_state, mock_analysis_results):
        """Test rapid navigation through many addresses.

        Ensures the navigation system handles many rapid state changes correctly.
        """
        app = app_with_state
        app.state.analysis_results = mock_analysis_results

        # Rapidly navigate through many addresses
        addresses = [f"0x{0x401000 + i * 0x100:x}" for i in range(20)]
        for addr in addresses:
            app.state.navigate_to(addr)

        # Verify all addresses in history
        assert len(app.state.navigation_history) == 20
        assert app.state.current_nav_index == 19

        # Go back 10 times
        for i in range(10):
            app.state.go_back()

        assert app.state.current_nav_index == 9

        # Go forward 5 times
        for i in range(5):
            app.state.go_forward()

        assert app.state.current_nav_index == 14

        # Navigate to new address - should truncate
        app.state.navigate_to("0x500000")
        assert len(app.state.navigation_history) == 16
        assert app.state.current_nav_index == 15

    @pytest.mark.asyncio
    async def test_navigation_error_handling(self, app_with_state):
        """Test error handling in navigation system.

        Ensures graceful handling of edge cases and invalid operations.
        """
        app = app_with_state

        # Test going back on empty history
        assert not app.state.can_go_back()
        result = app.state.go_back()
        assert result is None

        # Test going forward on empty history
        assert not app.state.can_go_forward()
        result = app.state.go_forward()
        assert result is None

        # Add one item
        app.state.navigate_to("0x401000")

        # Can't go back or forward with single item
        assert not app.state.can_go_back()
        assert not app.state.can_go_forward()

        result = app.state.go_back()
        assert result is None

        result = app.state.go_forward()
        assert result is None

    @pytest.mark.asyncio
    async def test_navigation_with_duplicate_addresses(self, app_with_state):
        """Test navigation behavior with duplicate addresses.

        Duplicate addresses should all be added to history.
        """
        app = app_with_state

        # Navigate to same address multiple times
        app.state.navigate_to("0x401000")
        app.state.navigate_to("0x401100")
        app.state.navigate_to("0x401000")  # Duplicate
        app.state.navigate_to("0x401200")
        app.state.navigate_to("0x401000")  # Another duplicate

        # All should be in history
        assert len(app.state.navigation_history) == 5
        assert app.state.navigation_history.count("0x401000") == 3

        # Back navigation should work correctly
        back1 = app.state.go_back()
        assert back1 == "0x401200"

        back2 = app.state.go_back()
        assert back2 == "0x401000"

        back3 = app.state.go_back()
        assert back3 == "0x401100"

        back4 = app.state.go_back()
        assert back4 == "0x401000"


@pytest.mark.integration
class TestNavigationPerformance:
    """Test navigation system performance and scalability."""

    @pytest.mark.asyncio
    async def test_large_navigation_history_performance(self, app_with_state):
        """Test performance with large navigation history.

        Ensures navigation remains responsive with many history entries.
        """
        import time

        app = app_with_state

        # Build large history (1000 entries)
        start = time.time()
        for i in range(1000):
            app.state.navigate_to(f"0x{0x401000 + i:x}")
        build_time = time.time() - start

        # Should complete quickly (< 1 second for 1000 entries)
        assert build_time < 1.0, f"Building history took {build_time:.3f}s, too slow"

        # Test navigation performance
        start = time.time()
        for _ in range(100):
            app.state.go_back()
        back_time = time.time() - start

        assert back_time < 0.5, f"100 back operations took {back_time:.3f}s, too slow"

        # Test forward navigation
        start = time.time()
        for _ in range(100):
            app.state.go_forward()
        forward_time = time.time() - start

        assert forward_time < 0.5, f"100 forward operations took {forward_time:.3f}s, too slow"

    @pytest.mark.asyncio
    async def test_callback_notification_performance(self, app_with_state):
        """Test performance of callback notifications.

        Ensures notifications don't become bottleneck with many subscribers.
        """
        import time

        app = app_with_state

        # Subscribe many callbacks
        callback_count = 100
        invocation_counts = []

        for i in range(callback_count):
            count = [0]
            invocation_counts.append(count)

            def make_callback(c):
                def callback(value):
                    c[0] += 1

                return callback

            app.state.subscribe("navigation_history", make_callback(count))

        # Navigate and measure time
        start = time.time()
        for i in range(10):
            app.state.navigate_to(f"0x{0x401000 + i:x}")
        elapsed = time.time() - start

        # Should complete quickly even with 100 subscribers
        assert elapsed < 1.0, f"10 navigations with 100 callbacks took {elapsed:.3f}s"

        # Verify all callbacks were invoked
        for count in invocation_counts:
            assert count[0] == 10, "Callback should be invoked for each navigation"
