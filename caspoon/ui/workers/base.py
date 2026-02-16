"""Base worker class for async background operations.

This module provides the foundation for all async operations in the TUI,
enabling non-blocking execution with progress reporting and cancellation support.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from caspoon.ui.app import CaspoonApp

logger = logging.getLogger(__name__)


class WorkerState(Enum):
    """Worker lifecycle states.

    Attributes:
        IDLE: Worker has not started
        RUNNING: Worker is currently executing
        COMPLETED: Worker finished successfully
        FAILED: Worker encountered an error
        CANCELLED: Worker was cancelled by user
    """

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Worker(ABC):
    """Base class for async background workers.

    Provides:
    - State management (idle, running, completed, failed, cancelled)
    - Progress reporting via messages
    - Cancellation support
    - Error handling with callbacks
    - Lifecycle callbacks for completion, errors, and cancellation

    Subclasses must implement:
    - async def run(self) -> Any: Main work method

    Example:
        ```python
        class MyWorker(Worker):
            async def run(self):
                self.report_progress(0, "Starting...")
                result = await asyncio.to_thread(blocking_work)
                self.report_progress(100, "Done")
                return result

            def on_complete(self, result):
                self.app.notify(f"Completed: {result}")
        ```
    """

    def __init__(self, app: "CaspoonApp") -> None:
        """Initialize worker.

        Args:
            app: The Textual app instance
        """
        self.app = app
        self.state = WorkerState.IDLE
        self._cancelled = False
        self._task: asyncio.Task | None = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def run(self) -> Any:
        """Execute the work. Must be implemented by subclass.

        This method should:
        - Perform the actual work
        - Call report_progress() periodically
        - Check self._cancelled flag for early termination
        - Return the result on success

        Returns:
            Result of the work (type depends on worker)

        Raises:
            Exception: Any error that occurs during execution
        """
        pass

    async def start(self) -> None:
        """Start the worker asynchronously.

        Creates an asyncio task to run the worker with error handling.
        This method is non-blocking and returns immediately.
        """
        if self.state != WorkerState.IDLE:
            self.logger.warning(f"Worker already {self.state.value}, cannot start")
            return

        self.state = WorkerState.RUNNING
        self._task = asyncio.create_task(self._run_with_error_handling())
        self.logger.info("Worker started")

    async def _run_with_error_handling(self) -> None:
        """Run with error handling wrapper.

        Catches exceptions, handles cancellation, and invokes lifecycle callbacks.
        """
        try:
            result = await self.run()

            # Only complete if not cancelled
            if not self._cancelled:
                self.state = WorkerState.COMPLETED
                self.on_complete(result)
                self.logger.info("Worker completed successfully")

        except asyncio.CancelledError:
            self.logger.info("Worker cancelled via asyncio")
            self.state = WorkerState.CANCELLED
            self.on_cancel()
            # Re-raise to properly handle task cancellation
            raise

        except Exception as e:
            self.logger.error(f"Worker error: {e}", exc_info=True)
            self.state = WorkerState.FAILED
            self.on_error(e)

    async def cancel(self) -> None:
        """Cancel the worker gracefully.

        Sets the cancelled flag and cancels the asyncio task if running.
        The on_cancel() callback will be invoked when cancellation completes.
        """
        if self.state != WorkerState.RUNNING:
            self.logger.debug(f"Cannot cancel worker in state {self.state.value}")
            return

        self.logger.info("Cancelling worker...")
        self._cancelled = True

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                # Wait for task to complete cancellation
                await self._task
            except asyncio.CancelledError:
                pass

        self.state = WorkerState.CANCELLED
        self.on_cancel()

    def report_progress(self, percent: int, message: str) -> None:
        """Report progress to app.

        Posts a ProgressUpdate message that the app can handle to update UI.

        Args:
            percent: Progress percentage (0-100)
            message: Human-readable progress message
        """
        from caspoon.ui.core.messages import ProgressUpdate

        self.app.post_message(ProgressUpdate(percent, message))
        self.logger.debug(f"Progress: {percent}% - {message}")

    def on_complete(self, result: Any) -> None:
        """Called on successful completion. Override to handle result.

        Args:
            result: The result returned by run()
        """
        self.logger.info("Worker completed (no custom handler)")

    def on_error(self, error: Exception) -> None:
        """Called on error. Override to handle error.

        Args:
            error: The exception that occurred
        """
        self.logger.error(f"Worker failed (no custom handler): {error}")

    def on_cancel(self) -> None:
        """Called on cancellation. Override for cleanup."""
        self.logger.info("Worker cancelled (no custom handler)")
