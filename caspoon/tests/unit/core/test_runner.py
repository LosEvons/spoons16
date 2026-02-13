"""Unit tests for ReconRunner."""
import pytest
from caspoon.core.runner import ReconRunner
from caspoon.core.models import ExecutableReport


class TestReconRunner:
    """Test ReconRunner class."""

    def test_runner_initialization(self):
        """Test that runner initializes with steps."""
        runner = ReconRunner()
        
        assert runner.steps is not None
        assert len(runner.steps) > 0
        assert all(hasattr(step, 'run') for step in runner.steps)
        assert all(hasattr(step, 'name') for step in runner.steps)

    def test_runner_run_creates_report(self, sample_binary):
        """Test that runner creates ExecutableReport."""
        runner = ReconRunner()
        report = runner.run(sample_binary)
        
        assert isinstance(report, ExecutableReport)
        assert report.path == sample_binary

    def test_runner_executes_all_steps(self, sample_binary):
        """Test that runner executes all configured steps."""
        runner = ReconRunner()
        report = runner.run(sample_binary)
        
        # Each step should have added some data
        # At minimum, file_info should have populated file_type or arch
        assert report.file_type != "" or report.arch != ""
