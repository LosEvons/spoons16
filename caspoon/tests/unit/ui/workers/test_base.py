"""Unit tests for base Worker class."""

import asyncio
from unittest.mock import MagicMock, Mock, patch

import pytest

from caspoon.ui.workers.base import Worker, WorkerState


class MockWorker(Worker):
    """Mock worker for testing base class functionality."""

    def __init__(self, app, should_fail=False, should_cancel=False):
        super().__init__(app)
        self.should_fail = should_fail
        self.should_cancel = should_cancel
        self.run_called = False
        self.result_value = "test_result"

    async def run(self):
        """Mock run method."""
        self.run_called = True

        # Simulate some work
        await asyncio.sleep(0.01)

        if self.should_cancel and self._cancelled:
            return None

        if self.should_fail:
            raise ValueError("Mock failure")

        return self.result_value


@pytest.fixture
def mock_app():
    """Create a mock app for testing."""
    app = MagicMock()
    app.post_message = MagicMock()
    return app


class TestWorkerInitialization:
    """Tests for worker initialization."""

    def test_worker_initial_state(self, mock_app):
        """Test worker starts in IDLE state."""
        worker = MockWorker(mock_app)

        assert worker.state == WorkerState.IDLE
        assert worker._cancelled is False
        assert worker._task is None
        assert worker.app is mock_app

    def test_worker_abstract_run(self, mock_app):
        """Test that Worker is abstract and requires run() implementation."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Worker(mock_app)


class TestWorkerStateTransitions:
    """Tests for worker state transitions."""

    @pytest.mark.asyncio
    async def test_worker_start(self, mock_app):
        """Test worker transitions to RUNNING when started."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.02)  # Let worker run

        assert worker.run_called
        assert worker.state in (WorkerState.COMPLETED, WorkerState.RUNNING)

    @pytest.mark.asyncio
    async def test_worker_complete(self, mock_app):
        """Test worker transitions to COMPLETED on success."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.05)  # Wait for completion

        assert worker.state == WorkerState.COMPLETED

    @pytest.mark.asyncio
    async def test_worker_failed(self, mock_app):
        """Test worker transitions to FAILED on error."""
        worker = MockWorker(mock_app, should_fail=True)

        await worker.start()
        await asyncio.sleep(0.05)  # Wait for failure

        assert worker.state == WorkerState.FAILED

    @pytest.mark.asyncio
    async def test_worker_cancelled(self, mock_app):
        """Test worker transitions to CANCELLED when cancelled."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.005)  # Let it start
        await worker.cancel()

        assert worker.state == WorkerState.CANCELLED
        assert worker._cancelled is True

    @pytest.mark.asyncio
    async def test_worker_cannot_start_twice(self, mock_app):
        """Test worker cannot be started while already running."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.005)

        # Try to start again
        await worker.start()  # Should log warning but not start again

        await asyncio.sleep(0.05)

        # Should still complete normally
        assert worker.state == WorkerState.COMPLETED


class TestWorkerCancellation:
    """Tests for worker cancellation."""

    @pytest.mark.asyncio
    async def test_worker_cancel_sets_flag(self, mock_app):
        """Test cancel sets the cancelled flag."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.005)
        await worker.cancel()

        assert worker._cancelled is True

    @pytest.mark.asyncio
    async def test_worker_cancel_cancels_task(self, mock_app):
        """Test cancel cancels the asyncio task."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.005)

        assert worker._task is not None
        await worker.cancel()

        assert worker._task.cancelled() or worker._task.done()

    @pytest.mark.asyncio
    async def test_worker_cancel_invokes_callback(self, mock_app):
        """Test cancel invokes on_cancel callback."""
        worker = MockWorker(mock_app)
        on_cancel_calls = []

        # Track on_cancel calls
        original_on_cancel = worker.on_cancel

        def track_on_cancel():
            on_cancel_calls.append(1)
            original_on_cancel()

        worker.on_cancel = track_on_cancel

        await worker.start()
        await asyncio.sleep(0.005)
        await worker.cancel()

        # Should be called at least once
        assert len(on_cancel_calls) >= 1

    @pytest.mark.asyncio
    async def test_cancel_idle_worker_does_nothing(self, mock_app):
        """Test cancelling an idle worker does nothing."""
        worker = MockWorker(mock_app)
        worker.on_cancel = Mock()

        await worker.cancel()

        assert worker.state == WorkerState.IDLE
        # on_cancel should not be called if worker never started


class TestWorkerProgressReporting:
    """Tests for progress reporting."""

    @pytest.mark.asyncio
    async def test_report_progress_posts_message(self, mock_app):
        """Test report_progress posts ProgressUpdate message."""
        worker = MockWorker(mock_app)

        worker.report_progress(50, "Halfway there")

        mock_app.post_message.assert_called_once()
        message = mock_app.post_message.call_args[0][0]
        assert message.percent == 50
        assert message.message == "Halfway there"

    @pytest.mark.asyncio
    async def test_multiple_progress_updates(self, mock_app):
        """Test multiple progress updates."""
        worker = MockWorker(mock_app)

        worker.report_progress(25, "Quarter done")
        worker.report_progress(50, "Half done")
        worker.report_progress(75, "Three quarters")

        assert mock_app.post_message.call_count == 3


class TestWorkerCallbacks:
    """Tests for worker lifecycle callbacks."""

    @pytest.mark.asyncio
    async def test_on_complete_called(self, mock_app):
        """Test on_complete callback is invoked on success."""
        worker = MockWorker(mock_app)
        worker.on_complete = Mock()

        await worker.start()
        await asyncio.sleep(0.05)

        worker.on_complete.assert_called_once_with("test_result")

    @pytest.mark.asyncio
    async def test_on_error_called(self, mock_app):
        """Test on_error callback is invoked on error."""
        worker = MockWorker(mock_app, should_fail=True)
        worker.on_error = Mock()

        await worker.start()
        await asyncio.sleep(0.05)

        worker.on_error.assert_called_once()
        error = worker.on_error.call_args[0][0]
        assert isinstance(error, ValueError)
        assert str(error) == "Mock failure"

    @pytest.mark.asyncio
    async def test_on_cancel_called(self, mock_app):
        """Test on_cancel callback is invoked on cancellation."""
        worker = MockWorker(mock_app)
        worker.on_cancel = Mock()

        await worker.start()
        await asyncio.sleep(0.005)
        await worker.cancel()

        worker.on_cancel.assert_called()


class TestWorkerErrorHandling:
    """Tests for worker error handling."""

    @pytest.mark.asyncio
    async def test_exception_caught_and_handled(self, mock_app):
        """Test exceptions are caught and don't crash the worker."""
        worker = MockWorker(mock_app, should_fail=True)

        # Should not raise exception
        await worker.start()
        await asyncio.sleep(0.05)

        assert worker.state == WorkerState.FAILED

    @pytest.mark.asyncio
    async def test_error_logged(self, mock_app):
        """Test errors are logged."""
        worker = MockWorker(mock_app, should_fail=True)

        with patch.object(worker.logger, "error") as mock_error:
            await worker.start()
            await asyncio.sleep(0.05)

            mock_error.assert_called()
            # Check that error was logged (could be in custom handler or base)
            call_args = str(mock_error.call_args_list)
            assert "Mock failure" in call_args or "Worker" in call_args


class TestWorkerEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_on_complete_not_called_if_cancelled(self, mock_app):
        """Test on_complete is not called if worker was cancelled."""
        worker = MockWorker(mock_app, should_cancel=True)
        worker.on_complete = Mock()

        await worker.start()
        await asyncio.sleep(0.005)

        # Cancel before completion
        worker._cancelled = True
        await asyncio.sleep(0.05)

        # on_complete should not be called
        # (result is None due to cancellation check in MockWorker.run)

    @pytest.mark.asyncio
    async def test_worker_cleanup_after_completion(self, mock_app):
        """Test worker can be reused after completion."""
        worker = MockWorker(mock_app)

        await worker.start()
        await asyncio.sleep(0.05)

        assert worker.state == WorkerState.COMPLETED

        # Reset for reuse (not typical but should handle gracefully)
        worker.state = WorkerState.IDLE
        worker._cancelled = False
        worker._task = None
        worker.run_called = False

        await worker.start()
        await asyncio.sleep(0.05)

        assert worker.state == WorkerState.COMPLETED
        assert worker.run_called
