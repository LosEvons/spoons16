"""Message types for event-driven communication in the TUI.

This module defines custom message types that extend Textual's Message class.
Messages enable loose coupling between components and event-driven architecture.
"""

from typing import TYPE_CHECKING, Any

from textual.message import Message

if TYPE_CHECKING:
    from caspoon.core.models import ExecutableReport


# ============================================================================
# Analysis Messages
# ============================================================================


class StartAnalysis(Message):
    """Request to start binary analysis.

    Posted when the user requests analysis of a binary file.

    Attributes:
        path: Full path to the binary file to analyze
    """

    def __init__(self, path: str) -> None:
        """Initialize StartAnalysis message.

        Args:
            path: Path to binary file
        """
        self.path = path
        super().__init__()


class AnalysisProgress(Message):
    """Progress update during binary analysis.

    Posted periodically during analysis to update UI progress indicators.

    Attributes:
        percent: Progress percentage (0.0 to 100.0)
        message: Human-readable progress message
    """

    def __init__(self, percent: float, message: str) -> None:
        """Initialize AnalysisProgress message.

        Args:
            percent: Progress percentage (0.0 to 100.0)
            message: Status message describing current operation
        """
        self.percent = percent
        self.message = message
        super().__init__()


class AnalysisComplete(Message):
    """Analysis completed successfully.

    Posted when binary analysis finishes without errors.

    Attributes:
        report: Complete ExecutableReport with analysis results
    """

    def __init__(self, report: "ExecutableReport") -> None:
        """Initialize AnalysisComplete message.

        Args:
            report: ExecutableReport with analysis results
        """
        self.report = report
        super().__init__()


class AnalysisError(Message):
    """Analysis failed with an error.

    Posted when binary analysis encounters an unrecoverable error.

    Attributes:
        error: Error message describing what went wrong
    """

    def __init__(self, error: str) -> None:
        """Initialize AnalysisError message.

        Args:
            error: Error message
        """
        self.error = error
        super().__init__()


# ============================================================================
# Navigation Messages
# ============================================================================


class SelectFunction(Message):
    """Function selected by user.

    Posted when user selects a function from the function list or other view.

    Attributes:
        function_name: Name of the selected function
        address: Optional address of the function (hex string)
    """

    def __init__(self, function_name: str, address: str | None = None) -> None:
        """Initialize SelectFunction message.

        Args:
            function_name: Name of the function
            address: Optional function address (hex string)
        """
        self.function_name = function_name
        self.address = address
        super().__init__()


class JumpToAddress(Message):
    """Navigate to a specific memory address.

    Posted when user requests to jump to a specific address (e.g., from cross-reference).

    Attributes:
        address: Target memory address (hex string or integer)
    """

    def __init__(self, address: str | int) -> None:
        """Initialize JumpToAddress message.

        Args:
            address: Memory address as hex string or integer
        """
        self.address = address
        super().__init__()


class SwitchTab(Message):
    """Switch to a different content tab.

    Posted when user switches between main content tabs (Functions, Strings, etc.).

    Attributes:
        tab_id: Identifier of the tab to switch to
    """

    def __init__(self, tab_id: str) -> None:
        """Initialize SwitchTab message.

        Args:
            tab_id: Tab identifier (e.g., "functions", "strings", "imports")
        """
        self.tab_id = tab_id
        super().__init__()


# ============================================================================
# UI Messages
# ============================================================================


class TogglePanel(Message):
    """Show or hide a UI panel.

    Posted when user toggles sidebar, details panel, or bottom panel visibility.

    Attributes:
        panel_id: Identifier of the panel to toggle
    """

    def __init__(self, panel_id: str) -> None:
        """Initialize TogglePanel message.

        Args:
            panel_id: Panel identifier (e.g., "sidebar", "details", "bottom")
        """
        self.panel_id = panel_id
        super().__init__()


class ShowCommandPalette(Message):
    """Request to open the command palette.

    Posted when user invokes command palette (typically Ctrl+P or Ctrl+Shift+P).
    """

    def __init__(self) -> None:
        """Initialize ShowCommandPalette message."""
        super().__init__()


class ExecuteCommand(Message):
    """Execute a registered command by ID.

    Posted from command palette or keyboard shortcut to execute an action.

    Attributes:
        command_id: ID of the command to execute
        args: Positional arguments for the command
        kwargs: Keyword arguments for the command
    """

    def __init__(self, command_id: str, *args: Any, **kwargs: Any) -> None:
        """Initialize ExecuteCommand message.

        Args:
            command_id: Command identifier from ActionRegistry
            args: Positional arguments to pass to command handler
            kwargs: Keyword arguments to pass to command handler
        """
        self.command_id = command_id
        self.args = args
        self.kwargs = kwargs
        super().__init__()


# ============================================================================
# File Messages
# ============================================================================


class OpenBinary(Message):
    """Request to open a binary file.

    Posted when user selects a file to open via file picker or command.

    Attributes:
        path: Full path to the binary file to open
    """

    def __init__(self, path: str) -> None:
        """Initialize OpenBinary message.

        Args:
            path: Path to binary file
        """
        self.path = path
        super().__init__()


class CloseBinary(Message):
    """Request to close the current binary.

    Posted when user closes the current binary to return to empty state.
    """

    def __init__(self) -> None:
        """Initialize CloseBinary message."""
        super().__init__()
