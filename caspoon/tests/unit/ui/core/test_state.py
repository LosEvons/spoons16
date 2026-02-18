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
        """Test update_from_report extracts disassembly from raw_backend_data["r2"]."""
        state = AppState()

        r2_data = {"functions": [{"name": "main", "offset": 0x1000}], "imports": ["printf"]}
        report = ExecutableReport(
            path="/test",
            raw_backend_data={
                "r2": r2_data,
                "other_data": "ignored",
            },
        )

        state.update_from_report(report)

        assert state.analysis_results is not None
        assert state.analysis_results.disassembly == r2_data

    def test_update_from_report_wrong_key_yields_no_disassembly(self):
        """Test that data stored under wrong key does not populate disassembly."""
        state = AppState()

        report = ExecutableReport(
            path="/test",
            raw_backend_data={"disassembly": {"main": "0x401000: push rbp"}},
        )

        state.update_from_report(report)

        # "disassembly" is not the key r2_recon.py uses; result should be None
        assert state.analysis_results is not None
        assert state.analysis_results.disassembly is None

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
