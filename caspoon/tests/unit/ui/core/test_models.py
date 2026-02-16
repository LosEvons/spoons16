"""Unit tests for data models."""

import pytest

from caspoon.ui.core.models import AnalysisResults, BinaryInfo, UIState, UserPreferences


class TestBinaryInfo:
    """Tests for BinaryInfo dataclass."""

    def test_binary_info_creation(self):
        """Test creating BinaryInfo with all fields."""
        info = BinaryInfo(
            path="/path/to/binary",
            architecture="x86_64",
            bits=64,
            file_type="ELF",
            stripped=True,
            file_size=12345,
            entry_point="0x401000",
        )

        assert info.path == "/path/to/binary"
        assert info.architecture == "x86_64"
        assert info.bits == 64
        assert info.file_type == "ELF"
        assert info.stripped is True
        assert info.file_size == 12345
        assert info.entry_point == "0x401000"

    def test_binary_info_defaults(self):
        """Test BinaryInfo with default values."""
        info = BinaryInfo(path="/test")

        assert info.path == "/test"
        assert info.architecture == "unknown"
        assert info.bits == 0
        assert info.file_type == "unknown"
        assert info.stripped is False
        assert info.file_size == 0
        assert info.entry_point is None

    def test_binary_info_immutable(self):
        """Test that BinaryInfo is immutable (frozen)."""
        info = BinaryInfo(path="/test")

        with pytest.raises(AttributeError):
            info.path = "/new/path"  # type: ignore


class TestAnalysisResults:
    """Tests for AnalysisResults dataclass."""

    def test_analysis_results_creation(self):
        """Test creating AnalysisResults with data."""
        results = AnalysisResults(
            functions=["main", "foo", "bar"],
            strings=["hello", "world"],
            imports=["printf", "malloc"],
            exports=["main"],
            sections=[".text", ".data"],
            protections={"pie": True, "nx": True},
            disassembly={"main": "0x401000: push rbp"},
        )

        assert results.functions == ["main", "foo", "bar"]
        assert results.strings == ["hello", "world"]
        assert results.imports == ["printf", "malloc"]
        assert results.exports == ["main"]
        assert results.sections == [".text", ".data"]
        assert results.protections == {"pie": True, "nx": True}
        assert results.disassembly == {"main": "0x401000: push rbp"}

    def test_analysis_results_defaults(self):
        """Test AnalysisResults with default empty values."""
        results = AnalysisResults()

        assert results.functions == []
        assert results.strings == []
        assert results.imports == []
        assert results.exports == []
        assert results.sections == []
        assert results.protections == {}
        assert results.disassembly is None

    def test_analysis_results_immutable(self):
        """Test that AnalysisResults is immutable (frozen)."""
        results = AnalysisResults(strings=["test"])

        with pytest.raises(AttributeError):
            results.strings = ["new"]  # type: ignore


class TestUIState:
    """Tests for UIState dataclass."""

    def test_ui_state_creation(self):
        """Test creating UIState with custom values."""
        state = UIState(
            is_analyzing=True,
            analysis_progress=50.0,
            analysis_message="Analyzing imports...",
            selected_function="main",
            selected_address="0x401000",
            active_tab="functions",
            panels_visible={"sidebar": True, "details": False},
        )

        assert state.is_analyzing is True
        assert state.analysis_progress == 50.0
        assert state.analysis_message == "Analyzing imports..."
        assert state.selected_function == "main"
        assert state.selected_address == "0x401000"
        assert state.active_tab == "functions"
        assert state.panels_visible == {"sidebar": True, "details": False}

    def test_ui_state_defaults(self):
        """Test UIState with default values."""
        state = UIState()

        assert state.is_analyzing is False
        assert state.analysis_progress == 0.0
        assert state.analysis_message == ""
        assert state.selected_function is None
        assert state.selected_address is None
        assert state.active_tab == "functions"
        assert state.panels_visible == {
            "sidebar": True,
            "details": True,
            "bottom": False,
        }

    def test_ui_state_mutable(self):
        """Test that UIState is mutable (not frozen)."""
        state = UIState()

        # Should be able to modify fields
        state.is_analyzing = True
        state.analysis_progress = 75.0
        state.selected_function = "foo"

        assert state.is_analyzing is True
        assert state.analysis_progress == 75.0
        assert state.selected_function == "foo"


class TestUserPreferences:
    """Tests for UserPreferences dataclass."""

    def test_user_preferences_creation(self):
        """Test creating UserPreferences with custom values."""
        prefs = UserPreferences(
            theme="monokai",
            show_addresses=False,
            auto_analyze=False,
            max_strings=500,
            show_line_numbers=False,
            font_size=14,
        )

        assert prefs.theme == "monokai"
        assert prefs.show_addresses is False
        assert prefs.auto_analyze is False
        assert prefs.max_strings == 500
        assert prefs.show_line_numbers is False
        assert prefs.font_size == 14

    def test_user_preferences_defaults(self):
        """Test UserPreferences with default values."""
        prefs = UserPreferences()

        assert prefs.theme == "dark"
        assert prefs.show_addresses is True
        assert prefs.auto_analyze is True
        assert prefs.max_strings == 1000
        assert prefs.show_line_numbers is True
        assert prefs.font_size == 12

    def test_user_preferences_mutable(self):
        """Test that UserPreferences is mutable."""
        prefs = UserPreferences()

        # Should be able to modify fields
        prefs.theme = "light"
        prefs.max_strings = 2000

        assert prefs.theme == "light"
        assert prefs.max_strings == 2000
