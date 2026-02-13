"""Unit tests for ReconRunner.

Tests the main ReconRunner class which orchestrates the analysis pipeline
and executes all recon modules in sequence.
"""

from unittest.mock import Mock, patch

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.core.runner import ReconRunner


class TestReconRunner:
    """Test ReconRunner class."""

    def test_runner_initialization(self) -> None:
        """Test that runner initializes with configured analysis steps."""
        runner = ReconRunner()

        assert runner.steps is not None, "Runner should have steps"
        assert len(runner.steps) > 0, "Runner should have at least one step"
        assert all(
            hasattr(step, "run") for step in runner.steps
        ), "All steps should have run method"
        assert all(
            hasattr(step, "name") for step in runner.steps
        ), "All steps should have name attribute"

    def test_runner_run_creates_report(self, sample_binary: str) -> None:
        """Test that runner creates and returns ExecutableReport."""
        runner = ReconRunner()
        report = runner.run(sample_binary)

        assert isinstance(report, ExecutableReport), "Should return ExecutableReport instance"
        assert report.path == sample_binary, "Report path should match input"

    def test_runner_executes_all_steps(self, sample_binary: str) -> None:
        """Test that runner executes all configured recon steps."""
        runner = ReconRunner()
        report = runner.run(sample_binary)

        # Each step should have added some data
        # At minimum, file_info should have populated file_type or arch
        assert (
            report.file_type != "" or report.arch != ""
        ), "Runner should populate at least file_type or arch"

    def test_runner_continues_on_step_failure(self, sample_binary: str) -> None:
        """Test that runner gracefully handles step failures and continues."""
        runner = ReconRunner()

        # Mock one step to fail
        original_run = runner.steps[1].run
        runner.steps[1].run = Mock(side_effect=RuntimeError("Step failed"))

        # Should not raise, should continue with other steps
        report = runner.run(sample_binary)

        # Should still return a valid report
        assert isinstance(report, ExecutableReport), "Should return report even with failures"
        assert report.path == sample_binary, "Report path should be preserved"

        # Restore original for other tests
        runner.steps[1].run = original_run

    def test_runner_logs_step_execution(self, sample_binary: str, caplog) -> None:
        """Test that runner logs execution of each step for debugging."""
        runner = ReconRunner()

        with caplog.at_level("DEBUG"):
            runner.run(sample_binary)

        # Should log each step name
        for step in runner.steps:
            assert any(
                step.name in record.message for record in caplog.records
            ), f"Should log execution of step: {step.name}"

    def test_runner_logs_errors(self, sample_binary: str, caplog) -> None:
        """Test that runner logs errors from failing steps for debugging."""
        runner = ReconRunner()

        # Mock a step to fail
        runner.steps[1].run = Mock(side_effect=RuntimeError("Test error"))

        with caplog.at_level("ERROR"):
            runner.run(sample_binary)

        # Should log the error
        assert any(
            "Error in step" in record.message for record in caplog.records
        ), "Should log error message when step fails"

    def test_report_path_invariant(self, sample_binary: str) -> None:
        """Property test: Report path must always match input path exactly."""
        runner = ReconRunner()
        report = runner.run(sample_binary)

        assert report.path == sample_binary, "Report path must be invariant"

    def test_report_enrichment_only(self, sample_binary: str) -> None:
        """Property test: Steps only add data, never remove or modify existing data."""
        runner = ReconRunner()

        # Create initial report with some data
        initial_report = ExecutableReport(path=sample_binary)
        initial_report.strings = ["pre-existing"]

        # Run one step
        step = runner.steps[0]
        result = step.run(sample_binary, initial_report)

        # Pre-existing data should still be there (enrichment only)
        assert "pre-existing" in result.strings, "Pre-existing data should be preserved"

    @pytest.mark.integration
    def test_runner_with_multiple_binaries(self, test_binaries_dir) -> None:
        """Integration test: Runner should handle different binary types consistently."""
        binaries = [
            test_binaries_dir / "test_hello_x64",
            test_binaries_dir / "test_stripped",
            test_binaries_dir / "test_with_pie",
        ]

        runner = ReconRunner()

        for binary in binaries:
            if not binary.exists():
                continue

            report = runner.run(str(binary))

            # All should produce valid reports
            assert isinstance(report, ExecutableReport), f"Should produce report for {binary.name}"
            assert report.path == str(binary), f"Path should match for {binary.name}"
            # Should have some data populated
            assert report.file_type != "", f"Should populate file_type for {binary.name}"
