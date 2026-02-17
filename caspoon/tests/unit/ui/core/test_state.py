"""Unit tests for AppState."""

from unittest.mock import Mock

import pytest

from caspoon.core.models import ExecutableReport, ProtectionInfo
from caspoon.ui.core.models import AnalysisResults, BinaryInfo, UIState, UserPreferences
from caspoon.ui.core.state import AppState


class TestAppState:
    """Tests for AppState class."""

    def test_state_initialization(self):
        """Test AppState initializes with default values."""
        state = AppState()

        assert state.binary_info is None
        assert state.analysis_results is None
        assert isinstance(state.ui_state, UIState)
        assert isinstance(state.user_prefs, UserPreferences)

    def test_state_reset(self):
        """Test reset clears binary and analysis data."""
        state = AppState()

        # Set some data
        state.binary_info = BinaryInfo(path="/test")
        state.analysis_results = AnalysisResults(strings=["test"])
        state.ui_state = UIState(is_analyzing=True, analysis_progress=50.0)

        # Reset
        state.reset()

        # Binary and analysis should be cleared
        assert state.binary_info is None
        assert state.analysis_results is None

        # UI state should be reset
        assert state.ui_state.is_analyzing is False
        assert state.ui_state.analysis_progress == 0.0

        # User preferences should NOT be reset (they're persistent)
        assert isinstance(state.user_prefs, UserPreferences)

    def test_binary_info_update(self):
        """Test setting binary info."""
        state = AppState()

        info = BinaryInfo(
            path="/path/to/binary",
            architecture="x86_64",
            bits=64,
            file_type="ELF",
        )

        state.binary_info = info

        assert state.binary_info == info
        assert state.binary_info.path == "/path/to/binary"
        assert state.binary_info.architecture == "x86_64"

    def test_analysis_results_update(self):
        """Test setting analysis results."""
        state = AppState()

        results = AnalysisResults(
            functions=["main", "foo"],
            strings=["hello"],
            imports=["printf"],
        )

        state.analysis_results = results

        assert state.analysis_results == results
        assert state.analysis_results.functions == ["main", "foo"]
        assert state.analysis_results.strings == ["hello"]

    def test_ui_state_updates(self):
        """Test updating UI state."""
        state = AppState()

        # Update UI state
        new_ui_state = UIState(
            is_analyzing=True,
            analysis_progress=75.0,
            analysis_message="Analyzing...",
            selected_function="main",
        )

        state.ui_state = new_ui_state

        assert state.ui_state.is_analyzing is True
        assert state.ui_state.analysis_progress == 75.0
        assert state.ui_state.analysis_message == "Analyzing..."
        assert state.ui_state.selected_function == "main"

    def test_user_prefs_updates(self):
        """Test updating user preferences."""
        state = AppState()

        # Update preferences
        new_prefs = UserPreferences(
            theme="light",
            show_addresses=False,
            max_strings=500,
        )

        state.user_prefs = new_prefs

        assert state.user_prefs.theme == "light"
        assert state.user_prefs.show_addresses is False
        assert state.user_prefs.max_strings == 500

    def test_update_from_report_basic(self):
        """Test populating state from ExecutableReport."""
        state = AppState()

        # Create a mock report
        report = ExecutableReport(
            path="/path/to/binary",
            arch="x86_64",
            bits=64,
            file_type="ELF 64-bit LSB executable",
            stripped=True,
            protections=ProtectionInfo(pie=True, nx=True, canary=False, relro="Full"),
            strings=["hello", "world", "test"],
            imports=["printf", "malloc", "free"],
            exports=["main", "custom_func"],
        )

        state.update_from_report(report)

        # Check binary info
        assert state.binary_info is not None
        assert state.binary_info.path == "/path/to/binary"
        assert state.binary_info.architecture == "x86_64"
        assert state.binary_info.bits == 64
        assert state.binary_info.file_type == "ELF 64-bit LSB executable"
        assert state.binary_info.stripped is True

        # Check analysis results
        assert state.analysis_results is not None
        assert state.analysis_results.strings == ["hello", "world", "test"]
        assert state.analysis_results.imports == ["printf", "malloc", "free"]
        assert state.analysis_results.exports == ["main", "custom_func"]
        assert state.analysis_results.protections["pie"] is True
        assert state.analysis_results.protections["nx"] is True
        assert state.analysis_results.protections["canary"] is False
        assert state.analysis_results.protections["relro"] == "Full"

        # Check UI state updated
        assert state.ui_state.is_analyzing is False
        assert state.ui_state.analysis_progress == 100.0
        assert state.ui_state.analysis_message == "Analysis complete"

    def test_update_from_report_minimal(self):
        """Test update_from_report with minimal data."""
        state = AppState()

        # Create minimal report
        report = ExecutableReport(path="/test")

        state.update_from_report(report)

        # Should handle missing/None values gracefully
        assert state.binary_info is not None
        assert state.binary_info.path == "/test"
        assert state.binary_info.architecture == "unknown"
        assert state.binary_info.bits == 0
        assert state.binary_info.file_type == "unknown"

        assert state.analysis_results is not None
        assert state.analysis_results.strings == []
        assert state.analysis_results.imports == []
        assert state.analysis_results.exports == []
        assert state.analysis_results.protections == {}

    def test_update_from_report_no_protections(self):
        """Test update_from_report when protections is None."""
        state = AppState()

        report = ExecutableReport(
            path="/test",
            arch="arm",
            bits=32,
            protections=None,  # No protections data
        )

        state.update_from_report(report)

        assert state.binary_info is not None
        assert state.binary_info.architecture == "arm"
        assert state.binary_info.bits == 32

        assert state.analysis_results is not None
        assert state.analysis_results.protections == {}

    def test_update_from_report_with_raw_backend_data(self):
        """Test update_from_report extracts disassembly from raw_backend_data."""
        state = AppState()

        report = ExecutableReport(
            path="/test",
            raw_backend_data={
                "disassembly": {"main": "0x401000: push rbp"},
                "other_data": "ignored",
            },
        )

        state.update_from_report(report)

        assert state.analysis_results is not None
        assert state.analysis_results.disassembly == {"main": "0x401000: push rbp"}

    def test_state_preserves_ui_state_panels(self):
        """Test that update_from_report preserves panel visibility."""
        state = AppState()

        # Set custom panel visibility
        state.ui_state = UIState(panels_visible={"sidebar": False, "details": True, "bottom": True})

        # Update from report
        report = ExecutableReport(path="/test")
        state.update_from_report(report)

        # Panel visibility should be preserved
        assert state.ui_state.panels_visible["sidebar"] is False
        assert state.ui_state.panels_visible["details"] is True
        assert state.ui_state.panels_visible["bottom"] is True

    def test_state_preserves_active_tab(self):
        """Test that update_from_report preserves active tab."""
        state = AppState()

        # Set active tab
        state.ui_state = UIState(active_tab="strings")

        # Update from report
        report = ExecutableReport(path="/test")
        state.update_from_report(report)

        # Active tab should be preserved
        assert state.ui_state.active_tab == "strings"

    def test_subscribe_binary_info_fires_callback(self):
        """Test that subscribing to binary_info fires callback on change."""
        state = AppState()
        received = []

        state.subscribe("binary_info", lambda val: received.append(val))

        info = BinaryInfo(path="/test", architecture="x86_64")
        state.binary_info = info

        assert len(received) == 1
        assert received[0] is info

    def test_subscribe_analysis_results_fires_callback(self):
        """Test that subscribing to analysis_results fires callback on change."""
        state = AppState()
        received = []

        state.subscribe("analysis_results", lambda val: received.append(val))

        results = AnalysisResults(strings=["hello"])
        state.analysis_results = results

        assert len(received) == 1
        assert received[0] is results

    def test_subscribe_ui_state_fires_callback(self):
        """Test that subscribing to ui_state fires callback on change."""
        state = AppState()
        received = []

        state.subscribe("ui_state", lambda val: received.append(val))

        new_state = UIState(is_analyzing=True, analysis_progress=50.0)
        state.ui_state = new_state

        assert len(received) == 1
        assert received[0].is_analyzing is True
        assert received[0].analysis_progress == 50.0

    def test_subscribe_multiple_callbacks(self):
        """Test multiple subscribers all get notified."""
        state = AppState()
        received_a = []
        received_b = []

        state.subscribe("binary_info", lambda val: received_a.append(val))
        state.subscribe("binary_info", lambda val: received_b.append(val))

        state.binary_info = BinaryInfo(path="/test")

        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_subscribe_callback_error_does_not_block_others(self):
        """Test that a failing callback doesn't prevent other callbacks from firing."""
        state = AppState()
        received = []

        def bad_callback(val):
            raise ValueError("callback error")

        state.subscribe("binary_info", bad_callback)
        state.subscribe("binary_info", lambda val: received.append(val))

        state.binary_info = BinaryInfo(path="/test")

        assert len(received) == 1, "Second callback should still fire after first one fails"

    def test_reset_fires_callbacks(self):
        """Test that reset() fires callbacks for cleared properties."""
        state = AppState()
        binary_updates = []
        analysis_updates = []

        state.subscribe("binary_info", lambda val: binary_updates.append(val))
        state.subscribe("analysis_results", lambda val: analysis_updates.append(val))

        state.binary_info = BinaryInfo(path="/test")
        state.analysis_results = AnalysisResults(strings=["test"])

        state.reset()

        # Should have received set + reset notifications
        assert len(binary_updates) == 2
        assert binary_updates[1] is None
        assert len(analysis_updates) == 2
        assert analysis_updates[1] is None

    def test_update_from_report_fires_callbacks(self):
        """Test that update_from_report fires all relevant callbacks."""
        state = AppState()
        binary_updates = []
        analysis_updates = []
        ui_updates = []

        state.subscribe("binary_info", lambda val: binary_updates.append(val))
        state.subscribe("analysis_results", lambda val: analysis_updates.append(val))
        state.subscribe("ui_state", lambda val: ui_updates.append(val))

        report = ExecutableReport(path="/test", strings=["hello"])
        state.update_from_report(report)

        assert len(binary_updates) == 1
        assert binary_updates[0].path == "/test"
        assert len(analysis_updates) == 1
        assert analysis_updates[0].strings == ["hello"]
        assert len(ui_updates) == 1
        assert ui_updates[0].is_analyzing is False

    def test_multiple_updates(self):
        """Test multiple sequential updates to state."""
        state = AppState()

        # First update
        report1 = ExecutableReport(path="/first", strings=["test1"])
        state.update_from_report(report1)
        assert state.binary_info.path == "/first"
        assert state.analysis_results.strings == ["test1"]

        # Second update (should replace)
        report2 = ExecutableReport(path="/second", strings=["test2", "test3"])
        state.update_from_report(report2)
        assert state.binary_info.path == "/second"
        assert state.analysis_results.strings == ["test2", "test3"]

        # Third update with reset
        state.reset()
        assert state.binary_info is None
        assert state.analysis_results is None


class TestNavigationHistory:
    """Tests for navigation history functionality."""

    def test_navigation_history_initialization(self):
        """Test navigation history initializes empty."""
        state = AppState()

        assert state.navigation_history == []
        assert state.current_nav_index == -1
        assert not state.can_go_back()
        assert not state.can_go_forward()

    def test_navigate_to_first_address(self):
        """Test navigating to first address."""
        state = AppState()

        state.navigate_to("0x401000")

        assert state.navigation_history == ["0x401000"]
        assert state.current_nav_index == 0
        assert not state.can_go_back()
        assert not state.can_go_forward()

    def test_navigate_to_multiple_addresses(self):
        """Test navigating to multiple addresses in sequence."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")

        assert state.navigation_history == ["0x401000", "0x401010", "0x401020"]
        assert state.current_nav_index == 2
        assert state.can_go_back()
        assert not state.can_go_forward()

    def test_go_back_single_step(self):
        """Test going back one step."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        result = state.go_back()

        assert result == "0x401000"
        assert state.current_nav_index == 0
        assert not state.can_go_back()
        assert state.can_go_forward()

    def test_go_back_multiple_steps(self):
        """Test going back multiple steps."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")
        state.navigate_to("0x401030")

        result1 = state.go_back()
        result2 = state.go_back()
        result3 = state.go_back()

        assert result1 == "0x401020"
        assert result2 == "0x401010"
        assert result3 == "0x401000"
        assert state.current_nav_index == 0
        assert not state.can_go_back()
        assert state.can_go_forward()

    def test_go_back_at_beginning(self):
        """Test going back when already at beginning."""
        state = AppState()

        state.navigate_to("0x401000")

        # Already at beginning
        result = state.go_back()

        assert result is None
        assert state.current_nav_index == 0
        assert not state.can_go_back()

    def test_go_back_empty_history(self):
        """Test going back with empty history."""
        state = AppState()

        result = state.go_back()

        assert result is None
        assert state.current_nav_index == -1
        assert not state.can_go_back()

    def test_go_forward_single_step(self):
        """Test going forward one step."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.go_back()

        result = state.go_forward()

        assert result == "0x401010"
        assert state.current_nav_index == 1
        assert state.can_go_back()
        assert not state.can_go_forward()

    def test_go_forward_multiple_steps(self):
        """Test going forward multiple steps."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")
        state.go_back()
        state.go_back()

        result1 = state.go_forward()
        result2 = state.go_forward()

        assert result1 == "0x401010"
        assert result2 == "0x401020"
        assert state.current_nav_index == 2
        assert state.can_go_back()
        assert not state.can_go_forward()

    def test_go_forward_at_end(self):
        """Test going forward when already at end."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        # Already at end
        result = state.go_forward()

        assert result is None
        assert state.current_nav_index == 1
        assert not state.can_go_forward()

    def test_go_forward_empty_history(self):
        """Test going forward with empty history."""
        state = AppState()

        result = state.go_forward()

        assert result is None
        assert state.current_nav_index == -1
        assert not state.can_go_forward()

    def test_navigate_truncates_forward_history(self):
        """Test that navigating from middle of history truncates forward entries."""
        state = AppState()

        # Build history
        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")
        state.navigate_to("0x401030")

        # Go back to middle
        state.go_back()
        state.go_back()

        assert state.current_nav_index == 1
        assert state.navigation_history == ["0x401000", "0x401010", "0x401020", "0x401030"]

        # Navigate to new address - should truncate forward history
        state.navigate_to("0x402000")

        assert state.navigation_history == ["0x401000", "0x401010", "0x402000"]
        assert state.current_nav_index == 2
        assert state.can_go_back()
        assert not state.can_go_forward()

    def test_navigate_after_go_back_multiple_times(self):
        """Test navigation behavior after multiple back steps."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")

        # Go all the way back
        state.go_back()
        state.go_back()

        # Navigate to new address
        state.navigate_to("0x403000")

        # Forward history should be cleared
        assert state.navigation_history == ["0x401000", "0x403000"]
        assert state.current_nav_index == 1
        assert not state.can_go_forward()

    def test_can_go_back_after_navigation(self):
        """Test can_go_back() returns correct values."""
        state = AppState()

        assert not state.can_go_back()

        state.navigate_to("0x401000")
        assert not state.can_go_back()

        state.navigate_to("0x401010")
        assert state.can_go_back()

        state.go_back()
        assert not state.can_go_back()

    def test_can_go_forward_after_navigation(self):
        """Test can_go_forward() returns correct values."""
        state = AppState()

        assert not state.can_go_forward()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        assert not state.can_go_forward()

        state.go_back()
        assert state.can_go_forward()

        state.go_forward()
        assert not state.can_go_forward()

    def test_navigation_history_with_duplicates(self):
        """Test that duplicate addresses are still tracked separately."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401000")  # Navigate back to first address

        assert state.navigation_history == ["0x401000", "0x401010", "0x401000"]
        assert state.current_nav_index == 2

        # Can go back through history
        result = state.go_back()
        assert result == "0x401010"

        result = state.go_back()
        assert result == "0x401000"

    def test_reset_clears_navigation_history(self):
        """Test that reset() clears navigation history."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.navigate_to("0x401020")

        state.reset()

        assert state.navigation_history == []
        assert state.current_nav_index == -1
        assert not state.can_go_back()
        assert not state.can_go_forward()

    def test_navigation_fires_callbacks(self):
        """Test that navigation methods fire appropriate callbacks."""
        state = AppState()
        history_updates = []
        index_updates = []

        state.subscribe("navigation_history", lambda val: history_updates.append(val.copy()))
        state.subscribe("current_nav_index", lambda val: index_updates.append(val))

        state.navigate_to("0x401000")

        assert len(history_updates) == 1
        assert history_updates[0] == ["0x401000"]
        assert len(index_updates) == 1
        assert index_updates[0] == 0

    def test_go_back_fires_index_callback(self):
        """Test that go_back() fires callback for index change."""
        state = AppState()
        index_updates = []

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        state.subscribe("current_nav_index", lambda val: index_updates.append(val))

        state.go_back()

        assert len(index_updates) == 1
        assert index_updates[0] == 0

    def test_go_forward_fires_index_callback(self):
        """Test that go_forward() fires callback for index change."""
        state = AppState()
        index_updates = []

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")
        state.go_back()

        state.subscribe("current_nav_index", lambda val: index_updates.append(val))

        state.go_forward()

        assert len(index_updates) == 1
        assert index_updates[0] == 1

    def test_navigation_history_is_readonly_property(self):
        """Test that navigation_history property returns the list."""
        state = AppState()

        state.navigate_to("0x401000")
        state.navigate_to("0x401010")

        # Getting the property should work
        history = state.navigation_history
        assert history == ["0x401000", "0x401010"]

        # Note: The property returns the internal list, so modifications
        # would affect the state. This is acceptable for this implementation.

    def test_current_nav_index_is_readonly_property(self):
        """Test that current_nav_index property returns the index."""
        state = AppState()

        assert state.current_nav_index == -1

        state.navigate_to("0x401000")
        assert state.current_nav_index == 0

        state.navigate_to("0x401010")
        assert state.current_nav_index == 1

    def test_complex_navigation_scenario(self):
        """Test a complex navigation scenario combining all operations."""
        state = AppState()

        # Navigate forward through several addresses
        state.navigate_to("0x401000")  # history: [0x401000], index: 0
        state.navigate_to("0x401010")  # history: [0x401000, 0x401010], index: 1
        state.navigate_to("0x401020")  # history: [0x401000, 0x401010, 0x401020], index: 2

        assert state.current_nav_index == 2
        assert len(state.navigation_history) == 3

        # Go back twice
        addr1 = state.go_back()  # index: 1
        addr2 = state.go_back()  # index: 0

        assert addr1 == "0x401010"
        assert addr2 == "0x401000"
        assert state.current_nav_index == 0

        # Go forward once
        addr3 = state.go_forward()  # index: 1
        assert addr3 == "0x401010"
        assert state.current_nav_index == 1

        # Navigate to new address (truncates 0x401020)
        state.navigate_to("0x402000")  # history: [0x401000, 0x401010, 0x402000], index: 2

        assert state.navigation_history == ["0x401000", "0x401010", "0x402000"]
        assert state.current_nav_index == 2
        assert not state.can_go_forward()

        # Go back and verify
        addr4 = state.go_back()  # index: 1
        assert addr4 == "0x401010"
        assert state.can_go_back()
        assert state.can_go_forward()
