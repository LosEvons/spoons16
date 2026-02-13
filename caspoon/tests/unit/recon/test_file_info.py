"""Unit tests for FileInfoRecon module."""
import pytest
from caspoon.recon.file_info import FileInfoRecon
from caspoon.core.models import ExecutableReport


class TestFileInfoRecon:
    """Test FileInfoRecon module."""

    @pytest.fixture
    def recon(self):
        """Create FileInfoRecon instance."""
        return FileInfoRecon()

    def test_module_name(self, recon):
        """Test module has correct name."""
        assert recon.name == "file_info"

    def test_analyze_system_binary(self, recon, sample_binary):
        """Test analysis of system binary."""
        report = ExecutableReport(path=sample_binary)
        result = recon.run(sample_binary, report)
        
        # Should have some arch info
        assert result.arch != "" or result.file_type != ""
        assert result is not None

    def test_nonexistent_file(self, recon):
        """Test handling of nonexistent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)
        
        # Should handle gracefully, not crash
        assert result is not None
        assert result.path == "/nonexistent/file"

    def test_report_enrichment(self, recon, sample_binary):
        """Test that report is enriched with data."""
        report = ExecutableReport(path=sample_binary)
        
        # Before: empty
        assert report.arch == ""
        assert report.file_type == ""
        
        # After: enriched
        result = recon.run(sample_binary, report)
        
        # Should have at least one field populated
        # (arch or file_type, depending on file command output)
        assert result.arch != "" or result.file_type != ""
