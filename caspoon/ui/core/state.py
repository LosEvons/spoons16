"""Centralized reactive state management for the TUI.

This module provides AppState, the single source of truth for all application state.
Views can subscribe to state changes and automatically update when values change.
"""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from .models import AnalysisResults, BinaryInfo, UIState, UserPreferences

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from caspoon.core.models import ExecutableReport


class AppState:
    """Centralized state store.

    Single source of truth for application state. Components can subscribe
    to state changes via callbacks to implement reactive behavior.

    Note: This is a standalone state container that doesn't require Textual's
    reactive system. When integrated into the TUI, the app will watch these
    properties and trigger updates accordingly.

    Attributes:
        binary_info: Current binary metadata (None if no binary loaded)
        analysis_results: Complete analysis data (None if not analyzed)
        ui_state: Current UI state (progress, selections, panel visibility)
        user_prefs: User preferences and settings
    """

    def __init__(self) -> None:
        """Initialize state with default values."""
        self._binary_info: BinaryInfo | None = None
        self._analysis_results: AnalysisResults | None = None
        self._ui_state: UIState = UIState()
        self._user_prefs: UserPreferences = UserPreferences()
        self._callbacks: dict[str, list[Callable]] = {}

    @property
    def binary_info(self) -> BinaryInfo | None:
        """Get binary metadata."""
        return self._binary_info

    @binary_info.setter
    def binary_info(self, value: BinaryInfo | None) -> None:
        """Set binary metadata and notify subscribers."""
        self._binary_info = value
        self._notify("binary_info", value)

    @property
    def analysis_results(self) -> AnalysisResults | None:
        """Get analysis results."""
        return self._analysis_results

    @analysis_results.setter
    def analysis_results(self, value: AnalysisResults | None) -> None:
        """Set analysis results and notify subscribers."""
        self._analysis_results = value
        self._notify("analysis_results", value)

    @property
    def ui_state(self) -> UIState:
        """Get UI state."""
        return self._ui_state

    @ui_state.setter
    def ui_state(self, value: UIState) -> None:
        """Set UI state and notify subscribers."""
        self._ui_state = value
        self._notify("ui_state", value)

    @property
    def user_prefs(self) -> UserPreferences:
        """Get user preferences."""
        return self._user_prefs

    @user_prefs.setter
    def user_prefs(self, value: UserPreferences) -> None:
        """Set user preferences and notify subscribers."""
        self._user_prefs = value
        self._notify("user_prefs", value)

    def subscribe(self, property_name: str, callback: Callable) -> None:
        """Subscribe to property changes.

        Args:
            property_name: Name of property to watch
            callback: Function to call when property changes
        """
        if property_name not in self._callbacks:
            self._callbacks[property_name] = []
        self._callbacks[property_name].append(callback)

    def _notify(self, property_name: str, value: object) -> None:
        """Notify subscribers of property change.

        Args:
            property_name: Name of changed property
            value: New value
        """
        if property_name in self._callbacks:
            for callback in self._callbacks[property_name]:
                try:
                    callback(value)
                except Exception:
                    logger.debug(
                        "Callback error in %s for property '%s'",
                        callback,
                        property_name,
                        exc_info=True,
                    )

    def reset(self) -> None:
        """Reset state to initial values.

        Clears all binary and analysis data. UI state is reset to defaults,
        but user preferences are preserved.
        """
        self._binary_info = None
        self._analysis_results = None
        self._ui_state = UIState()
        self._notify("binary_info", None)
        self._notify("analysis_results", None)
        self._notify("ui_state", self._ui_state)

    def update_from_report(self, report: "ExecutableReport") -> None:
        """Update state from ExecutableReport.

        Extracts relevant data from the ReconRunner's ExecutableReport and
        populates binary_info and analysis_results.

        Args:
            report: ExecutableReport from ReconRunner analysis
        """
        # Extract binary metadata
        self.binary_info = BinaryInfo(
            path=report.path,
            architecture=report.arch or "unknown",
            bits=report.bits or 0,
            file_type=report.file_type or "unknown",
            stripped=report.stripped,
            file_size=getattr(report, "file_size", 0),
            entry_point=None,  # Not currently in ExecutableReport
        )

        # Extract analysis results
        protections_dict = {}
        if report.protections:
            protections_dict = {
                "pie": report.protections.pie,
                "nx": report.protections.nx,
                "canary": report.protections.canary,
                "relro": report.protections.relro,
            }

        self.analysis_results = AnalysisResults(
            functions=[],  # Not currently available in ExecutableReport
            strings=report.strings or [],
            imports=report.imports or [],
            exports=report.exports or [],
            sections=[],  # Not currently available in ExecutableReport
            protections=protections_dict,
            disassembly=report.raw_backend_data.get("disassembly"),
        )

        # Update UI state to reflect analysis complete
        self.ui_state = UIState(
            is_analyzing=False,
            analysis_progress=100.0,
            analysis_message="Analysis complete",
            selected_function=None,
            selected_address=None,
            active_tab=self.ui_state.active_tab,
            panels_visible=self.ui_state.panels_visible,
        )
