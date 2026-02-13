"""Integration tests for full analysis pipeline."""
import pytest
from caspoon.core.runner import ReconRunner
from caspoon.core.models import ExecutableReport


@pytest.mark.integration
class TestFullPipeline:
    """Test complete analysis pipeline."""

    @pytest.fixture
    def runner(self):
        """Create ReconRunner instance."""
        return ReconRunner()

    def test_runner_has_steps(self, runner):
        """Test runner is configured with recon steps."""
        assert len(runner.steps) > 0
        assert hasattr(runner.steps[0], 'run')

    def test_analyze_system_binary(self, runner, sample_binary):
        """Test full analysis of system binary."""
        report = runner.run(sample_binary)
        
        # Verify basic analysis completed
        assert report is not None
        assert report.path == sample_binary
        
        # Should have some data from recon modules
        # (exact data depends on which modules succeed)
        assert isinstance(report, ExecutableReport)

    def test_report_structure(self, runner, sample_binary):
        """Test that report has expected structure."""
        report = runner.run(sample_binary)
        
        # Verify report structure
        assert hasattr(report, 'path')
        assert hasattr(report, 'arch')
        assert hasattr(report, 'bits')
        assert hasattr(report, 'protections')
        assert hasattr(report, 'strings')
        assert hasattr(report, 'imports')
        assert hasattr(report, 'exports')
        assert hasattr(report, 'raw_backend_data')
