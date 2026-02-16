"""Textual-based terminal UI for Caspoon."""

import logging
import os

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header, Input, TabbedContent, TabPane

from caspoon.core.runner import ReconRunner

from .core.actions import ActionRegistry
from .core.state import AppState
from .views.imports_exports import ImportsExportsView
from .views.overview import OverviewView
from .views.protections import ProtectionsView
from .views.r2_view import R2View
from .views.strings_view import StringsView

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
            self.set_status("Error: Please enter a path")
            return

        # Validate file path
        if not os.path.exists(path):
            self.set_status(f"Error: File not found - {path}")
            return

        if not os.path.isfile(path):
            self.set_status(f"Error: Not a file - {path}")
            return

        if not os.access(path, os.R_OK):
            self.set_status(f"Error: File not readable - {path}")
            return

        try:
            self.set_status(f"Analyzing: {path}...")
            runner = ReconRunner()
            report = runner.run(path)

            # Update centralized state (new architecture)
            self.state.update_from_report(report)
            logger.info("AppState updated from analysis report")

            # Update views using old interface (backward compatibility)
            self.display_report(report)

            self.set_status(f"Loaded: {path}")
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            self.set_status(f"Error: {str(e)}")

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
