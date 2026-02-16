"""Textual-based terminal UI for Caspoon."""

import logging
import os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Input, TabbedContent, TabPane

from .core.actions import ActionRegistry
from .core.messages import (
    AnalysisCancelled,
    AnalysisComplete,
    AnalysisError,
    ProgressUpdate,
    SelectFunction,
    StartAnalysis,
)
from .core.state import AppState
from .screens import MainScreen
from .views.imports_exports import ImportsExportsView
from .views.overview import OverviewView
from .views.protections import ProtectionsView
from .views.r2_view import R2View
from .views.strings_view import StringsView
from .widgets import CommandPalette
from .workers import AnalysisWorker, Worker

logger = logging.getLogger(__name__)


class CaspoonApp(App):
    """Main Textual application for interactive binary analysis.

    Provides a tabbed interface for viewing different aspects of
    executable analysis results.
    """

    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"

    BINDINGS = [
        Binding("ctrl+p", "show_command_palette", "Commands", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("f1", "show_help", "Help", show=True),
        Binding("1", "switch_tab('overview-tab')", "Overview", show=False),
        Binding("2", "switch_tab('protections-tab')", "Protections", show=False),
        Binding("3", "switch_tab('strings-tab')", "Strings", show=False),
        Binding("4", "switch_tab('imports-tab')", "Imports/Exports", show=False),
        Binding("5", "switch_tab('r2-tab')", "R2 Analysis", show=False),
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar", show=False),
        Binding("ctrl+d", "toggle_details", "Toggle Details", show=False),
        Binding("ctrl+j", "toggle_console", "Toggle Console", show=False),
    ]

    def __init__(self, **kwargs):
        """Initialize the application with centralized state management."""
        super().__init__(**kwargs)

        # Centralized state management
        self.state = AppState()

        # Action registry for command palette
        self.action_registry = ActionRegistry()

        # Current worker for analysis (None if no analysis in progress)
        self._current_worker: Worker | None = None

        # Register all commands
        self._register_commands()

        logger.info("CaspoonApp initialized with AppState and ActionRegistry")

    def compose(self) -> ComposeResult:
        """Compose the UI layout with multi-panel MainScreen.

        Yields:
            UI components for the application
        """
        # Yield the MainScreen - it will compose its own content
        yield MainScreen()

        # Command palette (overlays on top)
        yield CommandPalette(self.action_registry, id="command_palette")

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle input submission when user enters a file path.

        Args:
            message: Input submission event
        """
        path = message.value.strip()
        if not path:
            self.notify("Please enter a path", severity="warning")
            return

        # Validate file path
        if not os.path.exists(path):
            self.notify(f"File not found: {path}", severity="error")
            return

        if not os.path.isfile(path):
            self.notify(f"Not a file: {path}", severity="error")
            return

        if not os.access(path, os.R_OK):
            self.notify(f"File not readable: {path}", severity="error")
            return

        # Start async analysis
        self.run_worker(self.start_analysis(path), exclusive=True)

    async def start_analysis(self, path: str) -> None:
        """Start binary analysis in background worker.

        Args:
            path: Path to binary file to analyze
        """
        # Cancel any existing analysis
        if self._current_worker:
            await self._current_worker.cancel()
            self._current_worker = None

        # Create and start new worker
        logger.info(f"Starting analysis of {path}")
        self._current_worker = AnalysisWorker(self, path)

        # Update UI state to show analysis in progress
        self.state.ui_state.is_analyzing = True
        self.state.ui_state.analysis_progress = 0
        self.state.ui_state.analysis_message = "Starting analysis..."
        self.update_status()

        # Start worker (non-blocking)
        await self._current_worker.start()

    async def cancel_analysis(self) -> None:
        """Cancel current analysis."""
        if self._current_worker:
            logger.info("Cancelling analysis...")
            await self._current_worker.cancel()
            self._current_worker = None

            # Reset UI state
            self.state.ui_state.is_analyzing = False
            self.state.ui_state.analysis_progress = 0
            self.state.ui_state.analysis_message = ""
            self.update_status()

    def on_progress_update(self, message: ProgressUpdate) -> None:
        """Handle progress update from worker.

        Args:
            message: ProgressUpdate message with percent and status
        """
        self.state.ui_state.analysis_progress = message.percent
        self.state.ui_state.analysis_message = message.message
        self.update_status()
        self._log_to_console(f"Progress: {message.percent}% - {message.message}", "debug")
        logger.debug(f"Progress: {message.percent}% - {message.message}")

    def on_analysis_complete(self, message: AnalysisComplete) -> None:
        """Handle analysis completion.

        Args:
            message: AnalysisComplete message with report
        """
        # Update views using old interface (backward compatibility)
        self.display_report(message.report)

        # Reset worker and UI state
        self._current_worker = None
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_progress = 100
        self.state.ui_state.analysis_message = "Analysis complete"
        self.update_status()

        self.notify("Analysis complete", severity="information")
        self._log_to_console("Analysis completed successfully", "success")
        logger.info("Analysis completed successfully")

    def on_analysis_error(self, message: AnalysisError) -> None:
        """Handle analysis error.

        Args:
            message: AnalysisError message with error details
        """
        # Reset worker and UI state
        self._current_worker = None
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_progress = 0
        self.state.ui_state.analysis_message = ""
        self.update_status()

        self.notify(f"Analysis failed: {message.error}", severity="error")
        self._log_to_console(f"Analysis failed: {message.error}", "error")
        logger.error(f"Analysis error: {message.error}")

    def on_analysis_cancelled(self, message: AnalysisCancelled) -> None:
        """Handle analysis cancellation.

        Args:
            message: AnalysisCancelled message
        """
        # Reset worker and UI state
        self._current_worker = None
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_progress = 0
        self.state.ui_state.analysis_message = ""
        self.update_status()

        self.notify("Analysis cancelled", severity="warning")
        self._log_to_console("Analysis cancelled by user", "warning")
        logger.info("Analysis cancelled by user")

    def on_start_analysis(self, message: StartAnalysis) -> None:
        """Handle StartAnalysis message.

        Args:
            message: StartAnalysis message with file path
        """
        self.run_worker(self.start_analysis(message.path), exclusive=True)

    def update_status(self) -> None:
        """Update footer status message based on current state."""
        if self.state.ui_state.is_analyzing:
            progress = self.state.ui_state.analysis_progress
            msg = self.state.ui_state.analysis_message
            status = f"[Analyzing... {progress:.0f}%] {msg}"
        else:
            status = "Ready"

        self.set_status(status)

    def display_report(self, report) -> None:
        """Display analysis report across all views.

        Args:
            report: ExecutableReport to display
        """
        try:
            self.query_one("#overview", OverviewView).update_data(report)
            self.query_one("#protections", ProtectionsView).update_data(report)
            self.query_one("#strings_view", StringsView).update_data(report)
            self.query_one("#imp_exp", ImportsExportsView).update_data(report)
            self.query_one("#r2_view", R2View).update_data(report)
        except Exception as e:
            logger.error(f"Error updating views: {e}")
            self.set_status(f"Error displaying report: {str(e)}")

    def set_status(self, text: str) -> None:
        """Update the footer status message.

        Args:
            text: Status message to display
        """
        try:
            footer = self.query_one(Footer)
            footer.renderable = text  # type: ignore[attr-defined]
        except Exception as e:
            logger.error(f"Error setting status: {e}")

    def _register_commands(self) -> None:
        """Register all application commands with the action registry."""
        reg = self.action_registry

        # File commands
        reg.register(
            "file.quit",
            "Quit Application",
            self.action_quit,
            "Exit the application",
            "ctrl+q",
            "File",
        )
        reg.register(
            "file.reload",
            "Reload Binary",
            self.action_reload_analysis,
            "Reload current binary analysis",
            "ctrl+r",
            "File",
        )

        # View commands
        reg.register(
            "view.overview",
            "Show Overview",
            lambda: self.action_switch_tab("overview-tab"),
            "Switch to Overview tab",
            "1",
            "View",
        )
        reg.register(
            "view.protections",
            "Show Protections",
            lambda: self.action_switch_tab("protections-tab"),
            "Switch to Protections tab",
            "2",
            "View",
        )
        reg.register(
            "view.strings",
            "Show Strings",
            lambda: self.action_switch_tab("strings-tab"),
            "Switch to Strings tab",
            "3",
            "View",
        )
        reg.register(
            "view.imports_exports",
            "Show Imports/Exports",
            lambda: self.action_switch_tab("imports-tab"),
            "Switch to Imports/Exports tab",
            "4",
            "View",
        )
        reg.register(
            "view.disassembly",
            "Show R2 Analysis",
            lambda: self.action_switch_tab("r2-tab"),
            "Switch to R2 Analysis tab",
            "5",
            "View",
        )
        reg.register(
            "view.next_tab",
            "Next Tab",
            self.action_next_tab,
            "Switch to next tab",
            "tab",
            "View",
        )
        reg.register(
            "view.prev_tab",
            "Previous Tab",
            self.action_prev_tab,
            "Switch to previous tab",
            "shift+tab",
            "View",
        )

        # Analysis commands
        reg.register(
            "analysis.start",
            "Start Analysis",
            self.action_start_analysis_prompt,
            "Start binary analysis",
            "f5",
            "Analysis",
        )
        reg.register(
            "analysis.cancel",
            "Cancel Analysis",
            lambda: self.run_worker(self.cancel_analysis(), exclusive=False),
            "Cancel ongoing analysis",
            "escape",
            "Analysis",
        )

        # Navigation commands
        reg.register(
            "nav.filter",
            "Focus Filter",
            self.action_focus_filter,
            "Focus the filter input in current view",
            "/",
            "Navigation",
        )
        reg.register(
            "nav.clear_filter",
            "Clear Filter",
            self.action_clear_filter,
            "Clear filter in current view",
            "ctrl+shift+f",
            "Navigation",
        )

        # Help commands
        reg.register(
            "help.show",
            "Show Help",
            self.action_show_help,
            "Show help documentation",
            "f1",
            "Help",
        )
        reg.register(
            "help.command_palette",
            "Show Command Palette",
            self.action_show_command_palette,
            "Open command palette",
            "ctrl+p",
            "Help",
        )

        logger.info(f"Registered {len(reg.get_all_actions())} commands")

    # Action Handlers

    def action_show_command_palette(self) -> None:
        """Show the command palette."""
        palette = self.query_one("#command_palette", CommandPalette)
        palette.show()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_reload_analysis(self) -> None:
        """Reload current binary analysis."""
        # Get current file path from input
        path_input = self.query_one("#path_input", Input)
        path = path_input.value.strip()

        if path and os.path.exists(path):
            self.run_worker(self.start_analysis(path), exclusive=True)
        else:
            self.notify("No binary loaded to reload", severity="warning")

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to specified tab.

        Args:
            tab_id: ID of the tab to switch to
        """
        try:
            tabs = self.query_one("#tabs", TabbedContent)
            tabs.active = tab_id
        except Exception as e:
            logger.error(f"Error switching tab: {e}")

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        try:
            tabs = self.query_one("#tabs", TabbedContent)
            # Get current tab index and cycle to next
            tab_panes = list(tabs.query(TabPane))
            if tab_panes:
                current_idx = next(
                    (i for i, pane in enumerate(tab_panes) if pane.id == tabs.active),
                    0,
                )
                next_idx = (current_idx + 1) % len(tab_panes)
                tabs.active = tab_panes[next_idx].id or "overview-tab"
        except Exception as e:
            logger.error(f"Error switching to next tab: {e}")

    def action_prev_tab(self) -> None:
        """Switch to previous tab."""
        try:
            tabs = self.query_one("#tabs", TabbedContent)
            # Get current tab index and cycle to previous
            tab_panes = list(tabs.query(TabPane))
            if tab_panes:
                current_idx = next(
                    (i for i, pane in enumerate(tab_panes) if pane.id == tabs.active),
                    0,
                )
                prev_idx = (current_idx - 1) % len(tab_panes)
                tabs.active = tab_panes[prev_idx].id or "overview-tab"
        except Exception as e:
            logger.error(f"Error switching to previous tab: {e}")

    def action_start_analysis_prompt(self) -> None:
        """Focus the path input to start analysis."""
        try:
            path_input = self.query_one("#path_input", Input)
            path_input.focus()
        except Exception as e:
            logger.error(f"Error focusing path input: {e}")

    def action_focus_filter(self) -> None:
        """Focus filter input in current view (if available)."""
        # This is a stub - will be implemented when views support filtering
        self.notify("Filter not yet implemented in current view", severity="information")

    def action_clear_filter(self) -> None:
        """Clear filter in current view (if available)."""
        # This is a stub - will be implemented when views support filtering
        self.notify("Filter not yet implemented in current view", severity="information")

    def action_show_help(self) -> None:
        """Show help documentation."""
        help_text = """
Caspoon Reverse Engineering Toolkit - Help

Keyboard Shortcuts:
  Ctrl+P    - Open Command Palette
  Ctrl+Q    - Quit Application
  Ctrl+B    - Toggle Sidebar
  Ctrl+D    - Toggle Details Panel
  Ctrl+J    - Toggle Console
  F1        - Show this help
  1-5       - Switch between tabs
  Tab       - Next tab
  Shift+Tab - Previous tab
  F5        - Start Analysis (focus path input)
  Escape    - Cancel Analysis (if running)

Command Palette:
  Type to search commands, use Up/Down to navigate,
  and press Enter to execute.

For more information, visit the documentation.
        """
        self.notify(help_text.strip(), severity="information", timeout=10)

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility.

        Delegates to MainScreen's action_toggle_sidebar method.
        """
        try:
            from .screens.main import MainScreen
            main_screen = self.query_one(MainScreen)
            main_screen.action_toggle_sidebar()
        except Exception as e:
            logger.error(f"Error toggling sidebar: {e}")

    def action_toggle_details(self) -> None:
        """Toggle details panel visibility.

        Delegates to MainScreen's action_toggle_details method.
        """
        try:
            from .screens.main import MainScreen
            main_screen = self.query_one(MainScreen)
            main_screen.action_toggle_details()
        except Exception as e:
            logger.error(f"Error toggling details: {e}")

    def action_toggle_console(self) -> None:
        """Toggle console visibility.

        Delegates to MainScreen's action_toggle_console method.
        """
        try:
            from .screens.main import MainScreen
            main_screen = self.query_one(MainScreen)
            main_screen.action_toggle_console()
        except Exception as e:
            logger.error(f"Error toggling console: {e}")

    def on_select_function(self, message: SelectFunction) -> None:
        """Handle function selection from sidebar.

        Args:
            message: SelectFunction message with function name and address
        """
        # Update UI state
        self.state.ui_state.selected_function = message.function_name
        self.state.ui_state.selected_address = message.address

        # Log to console
        self._log_to_console(
            f"Selected function: {message.function_name} at {message.address}",
            "info",
        )

        logger.info(f"Function selected: {message.function_name} at {message.address}")

    def _log_to_console(self, message: str, level: str = "info") -> None:
        """Write a message to the console panel.

        Args:
            message: Message text to log
            level: Severity level (info, warning, error, success, debug)
        """
        try:
            # Try to get console from MainScreen
            main_screen = self.query_one(MainScreen)
            console = main_screen.get_console()
            if console:
                console.log(message, level)
        except Exception:
            # Console not available - silently skip
            pass
