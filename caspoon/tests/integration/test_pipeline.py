"""Integration tests for full analysis pipeline.

Tests the complete end-to-end analysis workflow, including all recon modules
working together to produce comprehensive binary analysis reports.
"""

from pathlib import Path

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.core.runner import ReconRunner


@pytest.mark.integration
class TestFullPipeline:
    """Test complete analysis pipeline."""

    @pytest.fixture
    def runner(self) -> ReconRunner:
        """Create ReconRunner instance for testing.

        Returns:
            Fresh ReconRunner instance.
        """
        return ReconRunner()

    def test_runner_has_steps(self, runner: ReconRunner) -> None:
        """Test runner is properly configured with recon steps."""
        assert len(runner.steps) > 0, "Runner should have steps configured"
        assert hasattr(runner.steps[0], "run"), "Steps should have run method"

    def test_analyze_system_binary(self, runner: ReconRunner, sample_binary: str) -> None:
        """Test full analysis pipeline on system binary."""
        report = runner.run(sample_binary)

        # Verify basic analysis completed successfully
        assert report is not None, "Should return a report"
        assert report.path == sample_binary, "Report path should match input"

        # Should have some data from recon modules
        # (exact data depends on which modules succeed)
        assert isinstance(report, ExecutableReport), "Should return ExecutableReport"

    def test_report_structure(self, runner: ReconRunner, sample_binary: str) -> None:
        """Test that report has all expected fields and structure."""
        report = runner.run(sample_binary)

        # Verify report structure matches ExecutableReport
        assert hasattr(report, "path"), "Report should have path field"
        assert hasattr(report, "arch"), "Report should have arch field"
        assert hasattr(report, "bits"), "Report should have bits field"
        assert hasattr(report, "protections"), "Report should have protections field"
        assert hasattr(report, "strings"), "Report should have strings field"
        assert hasattr(report, "imports"), "Report should have imports field"
        assert hasattr(report, "exports"), "Report should have exports field"
        assert hasattr(report, "raw_backend_data"), "Report should have raw_backend_data field"

    @pytest.mark.parametrize(
        "binary_name,expected_stripped,expected_pie",
        [
            ("test_hello_x64", False, False),
            ("test_stripped", True, False),
            ("test_with_pie", False, True),
        ],
    )
    def test_binary_characteristics(
        self,
        runner: ReconRunner,
        test_binaries_dir: Path,
        binary_name: str,
        expected_stripped: bool,
        expected_pie: bool,
    ) -> None:
        """Test analysis correctly identifies binary characteristics."""
        binary_path = test_binaries_dir / binary_name
        if not binary_path.exists():
            pytest.skip(f"{binary_name} binary not available")

        report = runner.run(str(binary_path))

        # Verify basic info
        assert report.arch in ["x86_64", "x86"], f"Should detect architecture for {binary_name}"
        assert report.bits in [32, 64], f"Should detect bit width for {binary_name}"
        assert "ELF" in report.file_type, f"Should detect ELF file type for {binary_name}"

        # Verify stripped status
        assert (
            report.stripped == expected_stripped
        ), f"Stripped status should be {expected_stripped} for {binary_name}"

        # Verify PIE (if protections were detected and checksec is available)
        if report.protections and report.protections.relro != "checksec_not_found":
            assert (
                report.protections.pie == expected_pie
            ), f"PIE should be {expected_pie} for {binary_name}"

    def test_pipeline_produces_complete_report(
        self, runner: ReconRunner, test_binaries_dir: Path
    ) -> None:
        """Test that pipeline produces comprehensive analysis report."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = runner.run(str(binary_path))

        # Should have file info populated
        assert report.arch != "", "Should populate architecture"
        assert report.bits is not None, "Should populate bit width"
        assert report.file_type != "", "Should populate file type"

        # Should have protections info
        assert report.protections is not None, "Should populate protections"

        # Should have strings (our test binary has "Hello" etc)
        assert len(report.strings) > 0, "Should extract strings"

        # Should have imports (at least printf)
        assert len(report.imports) > 0, "Should extract imports"

        # Should have exports (our functions)
        assert len(report.exports) > 0, "Should extract exports"

    def test_pretty_output_format(self, runner: ReconRunner, sample_binary: str) -> None:
        """Test that pretty() produces correctly formatted output."""
        report = runner.run(sample_binary)
        pretty = report.pretty()

        # Verify structure
        assert isinstance(pretty, dict), "pretty() should return dict"
        assert "path" in pretty, "Should include path"
        assert "arch" in pretty, "Should include architecture"
        assert "bits" in pretty, "Should include bit width"
        assert "file_type" in pretty, "Should include file type"
        assert "stripped" in pretty, "Should include stripped status"
        assert "protections" in pretty, "Should include protections"
        assert "imports" in pretty, "Should include imports"
        assert "exports" in pretty, "Should include exports"
        assert "strings_count" in pretty, "Should include strings count"

    def test_multiple_runs_same_binary(self, runner: ReconRunner, sample_binary: str) -> None:
        """Test that running analysis twice produces consistent results."""
        report1 = runner.run(sample_binary)
        report2 = runner.run(sample_binary)

        # Results should be consistent (deterministic)
        assert report1.arch == report2.arch, "Architecture should be consistent"
        assert report1.bits == report2.bits, "Bit width should be consistent"
        assert report1.stripped == report2.stripped, "Stripped status should be consistent"

    def test_pipeline_error_recovery(self, runner: ReconRunner, test_binaries_dir: Path) -> None:
        """Test that pipeline handles errors gracefully and continues."""
        # Use a non-existent file
        report = runner.run("/nonexistent/path")

        # Should still return a report (with errors noted)
        assert isinstance(report, ExecutableReport), "Should return report even with errors"
        assert report.path == "/nonexistent/path", "Path should be preserved even with errors"
