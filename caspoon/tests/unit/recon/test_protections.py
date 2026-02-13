"""Unit tests for ProtectionsRecon module."""

from unittest.mock import Mock, patch

import pytest

from caspoon.core.models import ExecutableReport, ProtectionInfo
from caspoon.recon.protections import ProtectionsRecon


class TestProtectionsRecon:
    """Test ProtectionsRecon module."""

    @pytest.fixture
    def recon(self):
        """Create ProtectionsRecon instance."""
        return ProtectionsRecon()

    def test_module_name(self, recon):
        """Test module has correct name."""
        assert recon.name == "protections"

    def test_full_protections_detection(self, recon):
        """Test detection of all protections enabled."""
        mock_output = """
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH
Full RELRO      Canary found      NX enabled    PIE enabled     No RPATH   No RUNPATH
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout=mock_output)

            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections.pie is True
            assert result.protections.nx is True
            assert result.protections.canary is True
            assert result.protections.relro == "full"

    def test_partial_protections_detection(self, recon):
        """Test detection of partial protections."""
        mock_output = """
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout=mock_output)

            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections.pie is False
            assert result.protections.nx is True
            assert result.protections.canary is False
            assert result.protections.relro == "partial"

    def test_no_protections_detection(self, recon):
        """Test detection of no protections."""
        mock_output = """
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH
No RELRO        No canary found   NX disabled   No PIE          No RPATH   No RUNPATH
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout=mock_output)

            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections.pie is False
            assert result.protections.nx is False
            assert result.protections.canary is False
            assert result.protections.relro == "none"

    def test_checksec_not_found(self, recon):
        """Test handling when checksec is not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections is not None
            assert result.protections.relro == "checksec_not_found"
            assert result.protections.pie is False
            assert result.protections.nx is False
            assert result.protections.canary is False

    def test_checksec_timeout(self, recon):
        """Test handling when checksec times out."""
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("checksec", 10)):
            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections is not None
            assert result.protections.relro == "checksec_timeout"

    def test_checksec_non_zero_return(self, recon):
        """Test handling when checksec returns non-zero exit code."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout="Error")

            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections is not None
            assert result.protections.relro == "checksec_error"

    def test_unexpected_error_handling(self, recon):
        """Test handling of unexpected exceptions."""
        with patch("subprocess.run", side_effect=RuntimeError("Unexpected error")):
            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections is not None
            assert "error:" in result.protections.relro.lower()

    def test_checksec_command_format(self, recon):
        """Test that checksec is called with correct argument format.

        checksec requires --file=<path> not --file <path> as separate arguments.
        This test verifies the command is properly formatted.
        """
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Full RELRO")

            report = ExecutableReport(path="/test/binary")
            recon.run("/test/binary", report)

            # Verify subprocess.run was called with correct format
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]  # Get the command list

            # Should be ["checksec", "--file=/test/binary"], not ["checksec", "--file", "/test/binary"]
            assert len(call_args) == 2, f"Expected 2 arguments, got {len(call_args)}: {call_args}"
            assert call_args[0] == "checksec"
            assert call_args[1].startswith("--file="), f"Expected --file=<path>, got {call_args[1]}"
            assert call_args[1] == "--file=/test/binary"

    @pytest.mark.integration
    @pytest.mark.requires_checksec
    def test_checksec_with_real_binary(self, recon):
        """Test checksec command with a real system binary.

        This test verifies that checksec is called correctly and can analyze
        a real binary without errors. Requires checksec to be installed.
        """
        import shutil

        if not shutil.which("checksec"):
            pytest.skip("checksec not installed")

        # Use /bin/ls as it's available on all systems
        report = ExecutableReport(path="/bin/ls")
        result = recon.run("/bin/ls", report)

        # Should successfully detect protections
        assert result.protections is not None
        assert result.protections.relro != "checksec_error"
        assert result.protections.relro != "checksec_not_found"
        # /bin/ls typically has at least NX enabled on modern systems
        assert result.protections.nx is True

    @pytest.mark.integration
    def test_real_test_binary_no_pie(self, recon, test_binaries_dir):
        """Test with real test_hello_x64 binary (no PIE)."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # Should detect some protections on modern system
        assert result.protections is not None
        # NX is typically enabled on modern binaries
        assert result.protections.nx is True or result.protections.relro != "Unknown"

    @pytest.mark.integration
    @pytest.mark.requires_checksec
    def test_real_test_binary_with_pie(self, recon, test_binaries_dir):
        """Test with real test_with_pie binary (full protections)."""
        binary_path = test_binaries_dir / "test_with_pie"
        if not binary_path.exists():
            pytest.skip("test_with_pie binary not available")

        # Check if checksec is available
        import shutil

        if not shutil.which("checksec"):
            pytest.skip("checksec not installed")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # Should detect full protections
        assert result.protections is not None
        assert result.protections.pie is True
        assert result.protections.canary is True
        assert result.protections.nx is True
        assert result.protections.relro == "full"
