"""Unit tests for AnalysisWorker."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from caspoon.ui.workers.analysis import AnalysisWorker
from caspoon.ui.workers.base import WorkerState


@pytest.fixture
def mock_app():
    """Create a mock app for testing."""
    app = MagicMock()
    app.post_message = MagicMock()
    app.state = MagicMock()
    app.state.update_from_report = MagicMock()
    return app


@pytest.fixture
def mock_report():
    """Create a mock ExecutableReport."""
    report = MagicMock()
    report.path = "/test/binary"
    report.arch = "x86_64"
    report.bits = 64
    report.file_type = "ELF"
    report.stripped = False
    report.strings = ["string1", "string2"]
    report.imports = ["import1", "import2"]
    report.exports = ["export1", "export2"]
    report.protections = MagicMock()
    report.protections.pie = True
    report.protections.nx = True
    report.protections.canary = True
    report.protections.relro = "full"
    report.raw_backend_data = {}
    return report


@pytest.fixture
def temp_binary(tmp_path):
    """Create a temporary binary file for testing."""
    binary_path = tmp_path / "test_binary"
    binary_path.write_bytes(b"\x7fELF")
    return str(binary_path)


class TestAnalysisWorkerInitialization:
    """Tests for AnalysisWorker initialization."""

    def test_worker_initialization(self, mock_app):
        """Test AnalysisWorker can be initialized with file path."""
        worker = AnalysisWorker(mock_app, "/path/to/binary")

        assert worker.app is mock_app
        assert worker.file_path == "/path/to/binary"
        assert worker.runner is None
        assert worker.state == WorkerState.IDLE

    def test_worker_stores_file_path(self, mock_app):
        """Test file path is stored correctly."""
        worker = AnalysisWorker(mock_app, "/test/path")

        assert worker.file_path == "/test/path"


class TestAnalysisWorkerFileValidation:
    """Tests for file validation."""

    @pytest.mark.asyncio
    async def test_file_not_found_raises_error(self, mock_app):
        """Test FileNotFoundError raised for missing file."""
        worker = AnalysisWorker(mock_app, "/nonexistent/file")

        with pytest.raises(FileNotFoundError, match="File not found"):
            await worker.run()

    @pytest.mark.asyncio
    async def test_not_a_file_raises_error(self, mock_app, tmp_path):
        """Test ValueError raised for directory instead of file."""
        dir_path = tmp_path / "testdir"
        dir_path.mkdir()

        worker = AnalysisWorker(mock_app, str(dir_path))

        with pytest.raises(ValueError, match="Not a file"):
            await worker.run()

    @pytest.mark.asyncio
    async def test_valid_file_accepted(self, mock_app, temp_binary, mock_report):
        """Test valid file is accepted."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            result = await worker.run()

            assert result is not None


class TestAnalysisWorkerExecution:
    """Tests for analysis execution."""

    @pytest.mark.asyncio
    async def test_runner_initialized(self, mock_app, temp_binary, mock_report):
        """Test ReconRunner is initialized during run."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            await worker.run()

            mock_runner_class.assert_called_once()
            assert worker.runner is not None

    @pytest.mark.asyncio
    async def test_runner_run_called(self, mock_app, temp_binary, mock_report):
        """Test ReconRunner.run is called with correct path."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            result = await worker.run()

            mock_runner.run.assert_called_once_with(temp_binary)
            assert result is mock_report

    @pytest.mark.asyncio
    async def test_analysis_runs_in_thread(self, mock_app, temp_binary, mock_report):
        """Test analysis is run in background thread via asyncio.to_thread."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = mock_report

                result = await worker.run()

                # Verify asyncio.to_thread was used
                mock_to_thread.assert_called_once()
                assert result is mock_report


class TestAnalysisWorkerProgressReporting:
    """Tests for progress reporting."""

    @pytest.mark.asyncio
    async def test_progress_at_10_percent(self, mock_app, temp_binary, mock_report):
        """Test progress reported at 10%."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            await worker.run()

            # Check that progress was reported
            calls = mock_app.post_message.call_args_list
            progress_messages = [c[0][0] for c in calls if hasattr(c[0][0], "percent")]

            assert any(msg.percent == 10 for msg in progress_messages)

    @pytest.mark.asyncio
    async def test_progress_stages(self, mock_app, temp_binary, mock_report):
        """Test progress reported at key stages."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            await worker.run()

            # Check progress messages
            calls = mock_app.post_message.call_args_list
            progress_messages = [c[0][0] for c in calls if hasattr(c[0][0], "percent")]

            percents = [msg.percent for msg in progress_messages]
            assert 10 in percents  # Loading
            assert 30 in percents  # Extracting
            assert 100 in percents  # Complete

    @pytest.mark.asyncio
    async def test_progress_messages_descriptive(self, mock_app, temp_binary, mock_report):
        """Test progress messages are descriptive."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            await worker.run()

            calls = mock_app.post_message.call_args_list
            progress_messages = [c[0][0] for c in calls if hasattr(c[0][0], "message")]

            messages = [msg.message for msg in progress_messages]
            assert any("Loading" in msg or "binary" in msg for msg in messages)
            assert any("complete" in msg.lower() for msg in messages)


class TestAnalysisWorkerCompletion:
    """Tests for completion handling."""

    @pytest.mark.asyncio
    async def test_on_complete_updates_state(self, mock_app, mock_report):
        """Test on_complete updates AppState."""
        worker = AnalysisWorker(mock_app, "/test/path")

        worker.on_complete(mock_report)

        mock_app.state.update_from_report.assert_called_once_with(mock_report)

    @pytest.mark.asyncio
    async def test_on_complete_posts_message(self, mock_app, mock_report):
        """Test on_complete posts AnalysisComplete message."""
        worker = AnalysisWorker(mock_app, "/test/path")

        worker.on_complete(mock_report)

        mock_app.post_message.assert_called()
        message = mock_app.post_message.call_args[0][0]
        assert hasattr(message, "report")
        assert message.report is mock_report

    @pytest.mark.asyncio
    async def test_on_complete_with_none_result(self, mock_app):
        """Test on_complete handles None result gracefully."""
        worker = AnalysisWorker(mock_app, "/test/path")

        # Should not crash
        worker.on_complete(None)

        # Should not update state or post message
        mock_app.state.update_from_report.assert_not_called()


class TestAnalysisWorkerErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_on_error_posts_message(self, mock_app):
        """Test on_error posts AnalysisError message."""
        worker = AnalysisWorker(mock_app, "/test/path")

        error = ValueError("Test error")
        worker.on_error(error)

        mock_app.post_message.assert_called()
        message = mock_app.post_message.call_args[0][0]
        assert hasattr(message, "error")
        assert "Test error" in message.error

    @pytest.mark.asyncio
    async def test_analysis_error_propagated(self, mock_app, temp_binary):
        """Test analysis errors are propagated correctly."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.side_effect = RuntimeError("Analysis failed")
            mock_runner_class.return_value = mock_runner

            with pytest.raises(RuntimeError, match="Analysis failed"):
                await worker.run()


class TestAnalysisWorkerCancellation:
    """Tests for cancellation handling."""

    @pytest.mark.asyncio
    async def test_cancellation_before_runner_init(self, mock_app, temp_binary):
        """Test cancellation before runner initialization."""
        worker = AnalysisWorker(mock_app, temp_binary)

        # Set cancelled flag immediately
        worker._cancelled = True

        result = await worker.run()

        assert result is None
        assert worker.runner is None

    @pytest.mark.asyncio
    async def test_cancellation_after_runner_init(self, mock_app, temp_binary, mock_report):
        """Test cancellation after runner initialization."""
        worker = AnalysisWorker(mock_app, temp_binary)

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            # Let it initialize runner, then cancel
            async def delayed_cancel():
                await asyncio.sleep(0.01)
                worker._cancelled = True

            await asyncio.gather(worker.run(), delayed_cancel())

            # Runner should be initialized but result might be None due to cancellation

    @pytest.mark.asyncio
    async def test_on_cancel_posts_message(self, mock_app):
        """Test on_cancel posts AnalysisCancelled message."""
        worker = AnalysisWorker(mock_app, "/test/path")

        worker.on_cancel()

        mock_app.post_message.assert_called()
        message = mock_app.post_message.call_args[0][0]
        # Message should be AnalysisCancelled

    @pytest.mark.asyncio
    async def test_on_cancel_cleanup(self, mock_app):
        """Test on_cancel performs cleanup."""
        worker = AnalysisWorker(mock_app, "/test/path")
        worker.runner = MagicMock()

        worker.on_cancel()

        # Currently no cleanup needed, but test it doesn't crash
        assert worker.runner is not None  # Not cleared yet


class TestAnalysisWorkerIntegration:
    """Integration tests with worker lifecycle."""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, mock_app, temp_binary, mock_report):
        """Test complete analysis workflow from start to finish."""
        worker = AnalysisWorker(mock_app, temp_binary)
        worker.on_complete = Mock()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            await worker.start()
            await asyncio.sleep(0.1)  # Wait for completion

            # Check state
            assert worker.state == WorkerState.COMPLETED

            # Check callback was invoked
            worker.on_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_analysis_error_workflow(self, mock_app, temp_binary):
        """Test error workflow from start to finish."""
        worker = AnalysisWorker(mock_app, temp_binary)
        worker.on_error = Mock()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.side_effect = RuntimeError("Test error")
            mock_runner_class.return_value = mock_runner

            await worker.start()
            await asyncio.sleep(0.1)  # Wait for error

            # Check state
            assert worker.state == WorkerState.FAILED

            # Check callback was invoked
            worker.on_error.assert_called_once()
            error = worker.on_error.call_args[0][0]
            assert isinstance(error, RuntimeError)

    @pytest.mark.asyncio
    async def test_cancellation_workflow(self, mock_app, temp_binary, mock_report):
        """Test cancellation workflow."""
        worker = AnalysisWorker(mock_app, temp_binary)
        worker.on_cancel = Mock()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            # Make it slow so we can cancel
            async def slow_run(*args, **kwargs):
                await asyncio.sleep(1)
                return mock_report

            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            with patch("asyncio.to_thread", side_effect=slow_run):
                await worker.start()
                await asyncio.sleep(0.05)  # Let it start

                await worker.cancel()

                assert worker.state == WorkerState.CANCELLED
                assert worker._cancelled is True
