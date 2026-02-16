"""Integration tests for core TUI components.

Tests the interaction between AppState, messages, and ActionRegistry
to ensure they work together correctly.
"""

from unittest.mock import Mock

from caspoon.core.models import ExecutableReport, ProtectionInfo
from caspoon.ui.core import (
    ActionRegistry,
    AnalysisComplete,
    AppState,
    SelectFunction,
    StartAnalysis,
)
from caspoon.ui.core.models import UIState


class TestStateAndMessages:
    """Test AppState and messages working together."""

    def test_state_update_workflow(self):
        """Test complete workflow: message → state update."""
        state = AppState()

        # Simulate analysis workflow
        # 1. Start analysis (would trigger StartAnalysis message)
        start_msg = StartAnalysis(path="/path/to/binary")
        assert start_msg.path == "/path/to/binary"

        # Update UI state to analyzing
        state.ui_state = UIState(
            is_analyzing=True,
            analysis_progress=0.0,
            analysis_message="Starting analysis...",
        )
        assert state.ui_state.is_analyzing is True

        # 2. Analysis completes (would trigger AnalysisComplete message)
        report = ExecutableReport(
            path="/path/to/binary",
            arch="x86_64",
            bits=64,
            strings=["test1", "test2"],
        )
        complete_msg = AnalysisComplete(report=report)

        # Update state from report
        state.update_from_report(report)

        assert state.binary_info is not None
        assert state.binary_info.path == "/path/to/binary"
        assert state.analysis_results is not None
        assert len(state.analysis_results.strings) == 2
        assert state.ui_state.is_analyzing is False
        assert state.ui_state.analysis_progress == 100.0

    def test_navigation_workflow(self):
        """Test navigation message workflow."""
        state = AppState()

        # Load some data
        report = ExecutableReport(path="/test", imports=["main", "foo", "bar"])
        state.update_from_report(report)

        # Simulate function selection
        select_msg = SelectFunction(function_name="main", address="0x401000")

        # Update UI state
        state.ui_state = UIState(
            selected_function=select_msg.function_name,
            selected_address=select_msg.address,
        )

        assert state.ui_state.selected_function == "main"
        assert state.ui_state.selected_address == "0x401000"


class TestActionsAndState:
    """Test ActionRegistry and AppState integration."""

    def test_action_modifies_state(self):
        """Test action execution can modify state."""
        state = AppState()
        registry = ActionRegistry()

        # Define action that modifies state
        def reset_handler():
            state.reset()

        registry.register(
            action_id="app.reset",
            name="Reset",
            handler=reset_handler,
            category="App",
        )

        # Set some state
        report = ExecutableReport(path="/test", strings=["test"])
        state.update_from_report(report)
        assert state.binary_info is not None

        # Execute reset action
        result = registry.execute("app.reset")

        assert result is True
        assert state.binary_info is None
        assert state.analysis_results is None

    def test_action_with_state_query(self):
        """Test action that queries state."""
        state = AppState()
        registry = ActionRegistry()

        result_holder = {"count": 0}

        # Define action that reads state
        def count_strings():
            if state.analysis_results:
                result_holder["count"] = len(state.analysis_results.strings)

        registry.register(
            action_id="analysis.count_strings",
            name="Count Strings",
            handler=count_strings,
        )

        # Set state with strings
        report = ExecutableReport(path="/test", strings=["a", "b", "c"])
        state.update_from_report(report)

        # Execute action
        registry.execute("analysis.count_strings")

        assert result_holder["count"] == 3


class TestCompleteWorkflow:
    """Test complete application workflow."""

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow from start to finish."""
        # Initialize components
        state = AppState()
        registry = ActionRegistry()

        # Mock handlers
        analysis_started = Mock()
        analysis_completed = Mock()

        # Register actions
        registry.register(
            action_id="file.analyze",
            name="Analyze Binary",
            handler=analysis_started,
            keybinding="ctrl+a",
            category="File",
        )

        registry.register(
            action_id="analysis.complete",
            name="Complete Analysis",
            handler=analysis_completed,
            category="Internal",
        )

        # Workflow Step 1: User triggers analysis
        action = registry.get_by_keybinding("ctrl+a")
        assert action is not None
        assert action.action_id == "file.analyze"

        # Execute analyze action
        registry.execute("file.analyze", "/path/to/binary")
        analysis_started.assert_called_once_with("/path/to/binary")

        # Workflow Step 2: Update UI state to show progress
        state.ui_state = UIState(
            is_analyzing=True,
            analysis_progress=50.0,
            analysis_message="Analyzing...",
        )

        assert state.ui_state.is_analyzing is True
        assert state.ui_state.analysis_progress == 50.0

        # Workflow Step 3: Analysis completes, update state
        report = ExecutableReport(
            path="/path/to/binary",
            arch="x86_64",
            bits=64,
            stripped=False,
            protections=ProtectionInfo(pie=True, nx=True, canary=True, relro="Full"),
            strings=["hello", "world"],
            imports=["printf", "malloc"],
            exports=["main"],
        )

        state.update_from_report(report)

        # Verify state updated correctly
        assert state.binary_info is not None
        assert state.binary_info.architecture == "x86_64"
        assert state.analysis_results is not None
        assert len(state.analysis_results.strings) == 2
        assert state.ui_state.is_analyzing is False
        assert state.ui_state.analysis_progress == 100.0

        # Workflow Step 4: User searches for actions
        search_results = registry.search("analyze")
        assert len(search_results) >= 1
        assert any(a.action_id == "file.analyze" for a in search_results)

    def test_multi_action_workflow(self):
        """Test workflow with multiple actions and state changes."""
        state = AppState()
        registry = ActionRegistry()

        # Track execution order
        execution_order = []

        def open_handler(path):
            execution_order.append(("open", path))

        def analyze_handler():
            execution_order.append(("analyze",))
            # Simulate analysis result
            report = ExecutableReport(path="/test", strings=["test"])
            state.update_from_report(report)

        def view_handler(tab):
            execution_order.append(("view", tab))
            state.ui_state = UIState(active_tab=tab)

        # Register actions
        registry.register("file.open", "Open", open_handler, category="File")
        registry.register("file.analyze", "Analyze", analyze_handler, category="File")
        registry.register("view.switch", "Switch View", view_handler, category="View")

        # Execute workflow
        registry.execute("file.open", "/path/to/binary")
        registry.execute("file.analyze")
        registry.execute("view.switch", "strings")

        # Verify execution order
        assert execution_order == [
            ("open", "/path/to/binary"),
            ("analyze",),
            ("view", "strings"),
        ]

        # Verify final state
        assert state.analysis_results is not None
        assert state.ui_state.active_tab == "strings"

    def test_action_categories_organization(self):
        """Test actions organized by categories for UI display."""
        registry = ActionRegistry()

        # Register various actions in different categories
        registry.register("file.open", "Open", Mock(), category="File")
        registry.register("file.close", "Close", Mock(), category="File")
        registry.register("view.functions", "Functions", Mock(), category="View")
        registry.register("view.strings", "Strings", Mock(), category="View")
        registry.register("nav.jump", "Jump to Address", Mock(), category="Navigation")

        # Get categories for menu/palette display
        categories = registry.get_all_categories()
        assert len(categories) == 3
        assert set(categories) == {"File", "View", "Navigation"}

        # Get actions by category
        file_actions = registry.get_by_category("File")
        assert len(file_actions) == 2

        view_actions = registry.get_by_category("View")
        assert len(view_actions) == 2

        nav_actions = registry.get_by_category("Navigation")
        assert len(nav_actions) == 1
