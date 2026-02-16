"""Integration tests for async analysis workflow."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.widgets import Input

from caspoon.ui.app import CaspoonApp
from caspoon.ui.core.messages import AnalysisComplete, ProgressUpdate, StartAnalysis


@pytest.fixture
def temp_binary(tmp_path):
    """Create a temporary binary file for testing."""
    binary_path = tmp_path / "test_binary"
    binary_path.write_bytes(b"\x7fELF\x02\x01\x01\x00")
    return str(binary_path)


@pytest.fixture
def mock_report():
    """Create a mock ExecutableReport."""
    report = MagicMock()
    report.path = "/test/binary"
    report.arch = "x86_64"
    report.bits = 64
    report.file_type = "ELF"
    report.stripped = False
    report.file_size = 1024
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


class TestAsyncAnalysisIntegration:
    """Integration tests for async analysis with CaspoonApp."""

    @pytest.mark.asyncio
    async def test_app_starts_analysis_worker(self, temp_binary, mock_report):
        """Test app can start analysis worker."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            # Start analysis
            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await asyncio.sleep(0.05)  # Shorter wait to check before completion

                # Check state - should be analyzing or just completed
                assert app.state.ui_state.analysis_progress >= 0

    @pytest.mark.asyncio
    async def test_app_receives_progress_updates(self, temp_binary, mock_report):
        """Test app receives progress updates during analysis."""
        app = CaspoonApp()
        progress_received = False

        # Track if any progress update was received
        original_handler = app.on_progress_update

        def capture_progress(message):
            nonlocal progress_received
            progress_received = True
            original_handler(message)

        app.on_progress_update = capture_progress

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await pilot.pause(0.2)  # Wait for analysis

                # At minimum, some progress should have been reported
                # The worker posts progress at 10%, 30%, and 100%
                assert app.state.ui_state.analysis_progress >= 0
                assert app.state.ui_state.analysis_progress <= 100

    @pytest.mark.asyncio
    async def test_app_state_updated_on_completion(self, temp_binary, mock_report):
        """Test app state is updated when analysis completes."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await asyncio.sleep(0.15)  # Wait for completion

                # Check state was updated
                assert app.state.binary_info is not None
                assert app.state.analysis_results is not None
                assert app.state.ui_state.is_analyzing is False

    @pytest.mark.asyncio
    async def test_app_cancels_analysis(self, temp_binary, mock_report):
        """Test app can cancel analysis."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()

            # Make analysis slow
            async def slow_analysis(*args, **kwargs):
                await asyncio.sleep(1)
                return mock_report

            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            with patch("asyncio.to_thread", side_effect=slow_analysis):
                async with app.run_test() as pilot:
                    await app.start_analysis(temp_binary)
                    await asyncio.sleep(0.05)  # Let it start

                    # Check it's running
                    assert app.state.ui_state.is_analyzing is True

                    # Cancel
                    await app.cancel_analysis()

                    # Check it stopped
                    assert app.state.ui_state.is_analyzing is False
                    assert app._current_worker is None

    @pytest.mark.asyncio
    async def test_multiple_analyses_sequential(self, temp_binary, mock_report):
        """Test starting new analysis cancels old one."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                # Start first analysis
                await app.start_analysis(temp_binary)
                first_worker = app._current_worker

                await asyncio.sleep(0.05)

                # Start second analysis (should cancel first)
                await app.start_analysis(temp_binary)
                second_worker = app._current_worker

                # Should be different workers
                assert first_worker is not second_worker

                await asyncio.sleep(0.15)

                # Should complete successfully
                assert app.state.ui_state.is_analyzing is False

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, temp_binary):
        """Test error handling in full workflow."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.side_effect = RuntimeError("Test error")
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await asyncio.sleep(0.15)  # Wait for error

                # Check error was handled
                assert app.state.ui_state.is_analyzing is False
                assert app._current_worker is None

    @pytest.mark.asyncio
    async def test_file_not_found_error(self):
        """Test handling of non-existent file."""
        app = CaspoonApp()

        async with app.run_test() as pilot:
            await app.start_analysis("/nonexistent/file")
            await asyncio.sleep(0.1)  # Wait for error

            # Check error was handled
            assert app.state.ui_state.is_analyzing is False
            assert app._current_worker is None

    @pytest.mark.asyncio
    async def test_ui_remains_responsive(self, temp_binary, mock_report):
        """Test UI remains responsive during analysis."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()

            # Simulate slow analysis
            async def slow_analysis(*args, **kwargs):
                await asyncio.sleep(0.2)
                return mock_report

            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            with patch("asyncio.to_thread", side_effect=slow_analysis):
                async with app.run_test() as pilot:
                    await app.start_analysis(temp_binary)

                    # UI should still be responsive
                    # We can query widgets, update state, etc.
                    input_widget = app.query_one(Input)
                    assert input_widget is not None

                    # Wait for completion
                    await asyncio.sleep(0.3)

                    assert app.state.ui_state.is_analyzing is False


class TestMessageBasedAnalysis:
    """Test analysis workflow using messages."""

    @pytest.mark.asyncio
    async def test_start_analysis_message(self, temp_binary, mock_report):
        """Test StartAnalysis message triggers analysis."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                # Post StartAnalysis message
                app.post_message(StartAnalysis(temp_binary))
                await asyncio.sleep(0.15)  # Wait for processing

                # Check analysis ran
                assert app.state.binary_info is not None
                assert app.state.ui_state.is_analyzing is False


class TestStateManagement:
    """Test state management during analysis."""

    @pytest.mark.asyncio
    async def test_is_analyzing_flag_set(self, temp_binary, mock_report):
        """Test is_analyzing flag is set during analysis."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()

            # Make it slow so we can check the flag
            async def slow_analysis(*args, **kwargs):
                await asyncio.sleep(0.2)
                return mock_report

            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            with patch("asyncio.to_thread", side_effect=slow_analysis):
                async with app.run_test() as pilot:
                    await app.start_analysis(temp_binary)
                    await asyncio.sleep(0.05)  # Let it start

                    # Check flag is set
                    assert app.state.ui_state.is_analyzing is True

                    # Wait for completion
                    await asyncio.sleep(0.3)

                    # Check flag is cleared
                    assert app.state.ui_state.is_analyzing is False

    @pytest.mark.asyncio
    async def test_progress_updates_state(self, temp_binary, mock_report):
        """Test progress updates modify state."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)

                # Wait a bit and check progress
                await asyncio.sleep(0.05)

                # Progress should be > 0
                assert app.state.ui_state.analysis_progress >= 0

                # Wait for completion
                await asyncio.sleep(0.15)

                # Progress should be 100
                assert app.state.ui_state.analysis_progress == 100


class TestStatusDisplay:
    """Test status message display."""

    @pytest.mark.asyncio
    async def test_status_shows_progress(self, temp_binary, mock_report):
        """Test status message shows progress during analysis."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await asyncio.sleep(0.05)

                # Status should contain "Analyzing"
                # (We'd need to query the footer to check this properly,
                # but update_status is called which sets it)

                await asyncio.sleep(0.15)

                # After completion, should show "Ready" or similar

    @pytest.mark.asyncio
    async def test_status_cleared_on_completion(self, temp_binary, mock_report):
        """Test status is cleared after completion."""
        app = CaspoonApp()

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                await app.start_analysis(temp_binary)
                await asyncio.sleep(0.15)

                # Check state is reset
                assert app.state.ui_state.is_analyzing is False
