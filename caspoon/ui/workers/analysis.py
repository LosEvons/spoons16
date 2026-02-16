"""Analysis worker for binary analysis operations.

This module provides the AnalysisWorker class that runs ReconRunner
in a background thread to avoid blocking the TUI event loop.
"""

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from caspoon.core.runner import ReconRunner
from caspoon.ui.workers.base import Worker

if TYPE_CHECKING:
    from caspoon.core.models import ExecutableReport
    from caspoon.ui.app import CaspoonApp

logger = logging.getLogger(__name__)


class AnalysisWorker(Worker):
    """Worker for binary analysis using ReconRunner.

    Runs binary analysis in a background thread to keep the UI responsive,
    reporting progress at key stages and updating AppState on completion.

    Progress stages:
    - 10%: File loaded and validated
    - 30%: Binary info extracted
    - 50%: Functions analyzed
    - 70%: Strings extracted
    - 90%: Finalizing report
    - 100%: Analysis complete

    Example:
        ```python
        worker = AnalysisWorker(app, "/path/to/binary")
        await worker.start()
        # Worker runs in background, posts AnalysisComplete when done
        ```
    """

    def __init__(self, app: "CaspoonApp", file_path: str) -> None:
        """Initialize analysis worker.

        Args:
            app: The Textual app instance
            file_path: Path to binary file to analyze
        """
        super().__init__(app)
        self.file_path = file_path
        self.runner: ReconRunner | None = None

    async def run(self) -> Optional["ExecutableReport"]:
        """Run binary analysis.

        Returns:
            ExecutableReport with analysis results, or None if cancelled

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path is not a file
            Exception: Any error during analysis
        """
        # Validate file exists
        path = Path(self.file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {self.file_path}")

        self.report_progress(10, "Loading binary...")

        # Check if cancelled early
        if self._cancelled:
            return None

        # Initialize ReconRunner (quick operation, but yield to event loop)
        await asyncio.sleep(0.01)
        self.runner = ReconRunner()

        if self._cancelled:
            return None

        self.report_progress(30, "Extracting binary info...")

        # Run analysis in background thread (blocking operation)
        # This is the key to keeping the UI responsive
        report = await asyncio.to_thread(self._run_analysis_blocking)

        if self._cancelled or report is None:
            return None

        self.report_progress(100, "Analysis complete")
        return report

    def _run_analysis_blocking(self) -> Optional["ExecutableReport"]:
        """Run analysis (blocking). Called in background thread.

        This method runs in a separate thread to avoid blocking the
        asyncio event loop. It performs the actual binary analysis.

        Returns:
            ExecutableReport with results, or None if cancelled
        """
        try:
            # Check cancellation flag before starting
            if self._cancelled:
                self.logger.info("Analysis cancelled before starting")
                return None

            # Run the actual analysis (blocking operation)
            self.logger.info(f"Starting analysis of {self.file_path}")
            report = self.runner.run(self.file_path)

            # Note: We can't easily report progress from within ReconRunner
            # without modifying it to support callbacks. For now, progress
            # is reported at the async level.

            self.logger.info(f"Analysis completed for {self.file_path}")
            return report

        except Exception as e:
            self.logger.error(f"Error during analysis: {e}", exc_info=True)
            raise

    def on_complete(self, result: Optional["ExecutableReport"]) -> None:
        """Update app state with analysis results.

        Args:
            result: ExecutableReport with analysis data
        """
        if result is None:
            self.logger.warning("Analysis completed with None result")
            return

        # Update centralized app state
        self.app.state.update_from_report(result)
        self.logger.info(f"AppState updated from analysis of {self.file_path}")

        # Post completion message
        from caspoon.ui.core.messages import AnalysisComplete

        self.app.post_message(AnalysisComplete(result))

    def on_error(self, error: Exception) -> None:
        """Post error message on analysis failure.

        Args:
            error: The exception that occurred
        """
        from caspoon.ui.core.messages import AnalysisError

        error_msg = str(error)
        self.app.post_message(AnalysisError(error_msg))
        self.logger.error(f"Analysis failed for {self.file_path}: {error_msg}")

    def on_cancel(self) -> None:
        """Cleanup on cancellation."""
        # Close runner resources if needed
        if self.runner:
            # ReconRunner doesn't currently have cleanup methods
            # but we can add them here when available
            pass

        # Post cancellation message
        from caspoon.ui.core.messages import AnalysisCancelled

        self.app.post_message(AnalysisCancelled())
        self.logger.info(f"Analysis cancelled for {self.file_path}")
