"""Unit tests for message types."""

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.messages import (
    AnalysisComplete,
    AnalysisError,
    AnalysisProgress,
    CloseBinary,
    ExecuteCommand,
    JumpToAddress,
    OpenBinary,
    SelectFunction,
    ShowCommandPalette,
    StartAnalysis,
    SwitchTab,
    TogglePanel,
)


class TestAnalysisMessages:
    """Tests for analysis-related messages."""

    def test_start_analysis_message(self):
        """Test StartAnalysis message creation."""
        msg = StartAnalysis(path="/path/to/binary")

        assert msg.path == "/path/to/binary"

    def test_analysis_progress_message(self):
        """Test AnalysisProgress message creation."""
        msg = AnalysisProgress(percent=45.5, message="Analyzing imports...")

        assert msg.percent == 45.5
        assert msg.message == "Analyzing imports..."

    def test_analysis_complete_message(self):
        """Test AnalysisComplete message creation."""
        report = ExecutableReport(path="/test")
        msg = AnalysisComplete(report=report)

        assert msg.report == report
        assert msg.report.path == "/test"

    def test_analysis_error_message(self):
        """Test AnalysisError message creation."""
        msg = AnalysisError(error="Failed to load binary")

        assert msg.error == "Failed to load binary"


class TestNavigationMessages:
    """Tests for navigation-related messages."""

    def test_select_function_message(self):
        """Test SelectFunction message creation."""
        msg = SelectFunction(function_name="main", address="0x401000")

        assert msg.function_name == "main"
        assert msg.address == "0x401000"

    def test_select_function_message_no_address(self):
        """Test SelectFunction message without address."""
        msg = SelectFunction(function_name="foo")

        assert msg.function_name == "foo"
        assert msg.address is None

    def test_jump_to_address_message_hex(self):
        """Test JumpToAddress message with hex string."""
        msg = JumpToAddress(address="0x401000")

        assert msg.address == "0x401000"

    def test_jump_to_address_message_int(self):
        """Test JumpToAddress message with integer."""
        msg = JumpToAddress(address=4198400)

        assert msg.address == 4198400

    def test_switch_tab_message(self):
        """Test SwitchTab message creation."""
        msg = SwitchTab(tab_id="strings")

        assert msg.tab_id == "strings"


class TestUIMessages:
    """Tests for UI-related messages."""

    def test_toggle_panel_message(self):
        """Test TogglePanel message creation."""
        msg = TogglePanel(panel_id="sidebar")

        assert msg.panel_id == "sidebar"

    def test_show_command_palette_message(self):
        """Test ShowCommandPalette message creation."""
        msg = ShowCommandPalette()

        # Message has no attributes, just verify it can be created
        assert msg is not None

    def test_execute_command_message_no_args(self):
        """Test ExecuteCommand message without arguments."""
        msg = ExecuteCommand(command_id="file.open")

        assert msg.command_id == "file.open"
        assert msg.args == ()
        assert msg.kwargs == {}

    def test_execute_command_message_with_args(self):
        """Test ExecuteCommand message with positional arguments."""
        msg = ExecuteCommand("file.open", "/path/to/file")

        assert msg.command_id == "file.open"
        assert msg.args == ("/path/to/file",)
        assert msg.kwargs == {}

    def test_execute_command_message_with_kwargs(self):
        """Test ExecuteCommand message with keyword arguments."""
        msg = ExecuteCommand("view.filter", pattern="main", case_sensitive=True)

        assert msg.command_id == "view.filter"
        assert msg.args == ()
        assert msg.kwargs == {"pattern": "main", "case_sensitive": True}

    def test_execute_command_message_with_both(self):
        """Test ExecuteCommand message with both args and kwargs."""
        msg = ExecuteCommand("analysis.jump", "0x401000", highlight=True)

        assert msg.command_id == "analysis.jump"
        assert msg.args == ("0x401000",)
        assert msg.kwargs == {"highlight": True}


class TestFileMessages:
    """Tests for file-related messages."""

    def test_open_binary_message(self):
        """Test OpenBinary message creation."""
        msg = OpenBinary(path="/path/to/binary")

        assert msg.path == "/path/to/binary"

    def test_close_binary_message(self):
        """Test CloseBinary message creation."""
        msg = CloseBinary()

        # Message has no attributes, just verify it can be created
        assert msg is not None


class TestMessageInheritance:
    """Tests for message inheritance and Textual integration."""

    def test_messages_inherit_from_textual_message(self):
        """Test that all messages inherit from Textual's Message."""
        from textual.message import Message

        # Test a few representative messages
        assert isinstance(StartAnalysis("/test"), Message)
        assert isinstance(AnalysisProgress(50.0, "test"), Message)
        assert isinstance(SelectFunction("main"), Message)
        assert isinstance(TogglePanel("sidebar"), Message)

    def test_messages_can_be_instantiated(self):
        """Test that all message types can be instantiated."""
        # Analysis messages
        StartAnalysis("/test")
        AnalysisProgress(50.0, "test")
        AnalysisComplete(ExecutableReport(path="/test"))
        AnalysisError("error")

        # Navigation messages
        SelectFunction("main")
        JumpToAddress("0x401000")
        SwitchTab("strings")

        # UI messages
        TogglePanel("sidebar")
        ShowCommandPalette()
        ExecuteCommand("test.cmd")

        # File messages
        OpenBinary("/test")
        CloseBinary()

        # If we get here, all messages instantiated successfully
        assert True


class TestMessageAttributes:
    """Tests for message attribute access patterns."""

    def test_message_attributes_accessible(self):
        """Test that message attributes are accessible."""
        msg = StartAnalysis(path="/test/binary")

        # Should be able to access path attribute
        assert hasattr(msg, "path")
        assert msg.path == "/test/binary"

    def test_multiple_attributes(self):
        """Test messages with multiple attributes."""
        msg = AnalysisProgress(percent=75.0, message="Processing...")

        assert msg.percent == 75.0
        assert msg.message == "Processing..."

    def test_optional_attributes(self):
        """Test messages with optional attributes."""
        # With optional attribute
        msg1 = SelectFunction(function_name="main", address="0x401000")
        assert msg1.address == "0x401000"

        # Without optional attribute
        msg2 = SelectFunction(function_name="foo")
        assert msg2.address is None
