"""Textual-based terminal UI for Caspoon."""

import logging
import os

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header, Input, TabbedContent, TabPane

from .core.actions import ActionRegistry
from .core.messages import (
    AnalysisCancelled,
    AnalysisComplete,
    AnalysisError,
    ProgressUpdate,
    StartAnalysis,
)
from .core.state import AppState
from .views.imports_exports import ImportsExportsView
from .views.overview import OverviewView
from .views.protections import ProtectionsView
from .views.r2_view import R2View
from .views.strings_view import StringsView
from .workers import AnalysisWorker, Worker

logger = logging.getLogger(__name__)


class CaspoonApp(App):
    """Main Textual application for interactive binary analysis.

    Provides a tabbed interface for viewing different aspects of
    executable analysis results.
    """

    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"

    def __init__(self, **kwargs):
        """Initialize the application with centralized state management."""
        super().__init__(**kwargs)

        # Centralized state management
        self.state = AppState()

        # Action registry for command palette (future use)
        self.action_registry = ActionRegistry()

        # Current worker for analysis (None if no analysis in progress)
        self._current_worker: Worker | None = None

        logger.info("CaspoonApp initialized with AppState and ActionRegistry")

    def compose(self) -> ComposeResult:
        """Compose the UI layout.

        Yields:
            UI components for the application
        """
        yield Header()

        yield Input(placeholder="Enter path to binary and press Enter...", id="path_input")

        with TabbedContent():
            with TabPane("Overview"):
                with ScrollableContainer():
                    yield OverviewView(id="overview")
            with TabPane("Protections"):
                with ScrollableContainer():
                    yield ProtectionsView(id="protections")
            with TabPane("Strings"):
                with ScrollableContainer():
                    yield StringsView(id="strings_view")
            with TabPane("Imports / Exports"):
                with ScrollableContainer():
                    yield ImportsExportsView(id="imp_exp")
            with TabPane("R2 Analysis"):
                with ScrollableContainer():
                    yield R2View(id="r2_view")

        yield Footer()

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
