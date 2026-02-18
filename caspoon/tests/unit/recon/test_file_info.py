"""Unit tests for FileInfoRecon module.

Tests the FileInfoRecon recon module which extracts basic file information
including architecture, bit width, file type, and stripped status.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.recon.file_info import FileInfoRecon


class TestFileInfoRecon:
    """Test FileInfoRecon module."""

    @pytest.fixture
    def recon(self) -> FileInfoRecon:
        """Create FileInfoRecon instance for testing."""
        return FileInfoRecon()

    # ------------------------------------------------------------------
    # Basic / contract tests
    # ------------------------------------------------------------------

    def test_module_name(self, recon: FileInfoRecon) -> None:
        """Test module has correct identifying name."""
        assert recon.name == "file_info", "Module name should be 'file_info'"

    def test_analyze_system_binary(self, recon: FileInfoRecon, sample_binary: str) -> None:
        """Test analysis of real system binary."""
        report = ExecutableReport(path=sample_binary)
        result = recon.run(sample_binary, report)

        assert result is not None, "Should return a report"
        assert (
            result.arch != "" or result.file_type != ""
        ), "Should populate at least arch or file_type"

    def test_nonexistent_file(self, recon: FileInfoRecon) -> None:
        """Test graceful handling of nonexistent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)

        assert result is not None, "Should return report even for missing file"
        assert result.path == "/nonexistent/file", "Path should be preserved"
        assert "Error: File not found" in result.file_type, "Should note file not found error"

    def test_directory_not_file(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """Test handling of directory instead of file."""
        report = ExecutableReport(path=str(tmp_path))
        result = recon.run(str(tmp_path), report)

        assert result is not None, "Should return report"
        assert "Error: Not a file" in result.file_type, "Should note that path is not a file"

    def test_report_enrichment(self, recon: FileInfoRecon, sample_binary: str) -> None:
        """Test that module enriches report with file information."""
        report = ExecutableReport(path=sample_binary)

        assert report.arch == "", "Architecture should start empty"
        assert report.file_type == "", "File type should start empty"

        result = recon.run(sample_binary, report)

        assert result.arch != "" or result.file_type != "", "Should populate at least one field"

    # ------------------------------------------------------------------
    # Dispatch tests — mock _read_magic to control format detection
    # ------------------------------------------------------------------

    def test_elf_binary_dispatched(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """ELF magic bytes cause _analyze_elf to be called."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF\x00\x00\x00\x00")

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"\x7fELF") as mock_magic,
            patch("caspoon.recon.file_info._analyze_elf") as mock_analyze,
        ):
            mock_analyze.side_effect = lambda path, report: report
            report = ExecutableReport(path=str(test_file))
            recon.run(str(test_file), report)

        mock_magic.assert_called_once_with(str(test_file))
        mock_analyze.assert_called_once()

    def test_pe_binary_dispatched(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """PE magic bytes (MZ) cause _analyze_pe to be called."""
        test_file = tmp_path / "binary.exe"
        test_file.write_bytes(b"MZ\x00\x00")

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"MZ\x00\x00"),
            patch("caspoon.recon.file_info._analyze_pe") as mock_analyze,
        ):
            mock_analyze.side_effect = lambda path, report: report
            report = ExecutableReport(path=str(test_file))
            recon.run(str(test_file), report)

        mock_analyze.assert_called_once()

    def test_macho_binary_dispatched(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """Mach-O magic bytes cause _analyze_macho to be called."""
        macho_magic = b"\xfe\xed\xfa\xce"
        test_file = tmp_path / "binary"
        test_file.write_bytes(macho_magic)

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=macho_magic),
            patch("caspoon.recon.file_info._analyze_macho") as mock_analyze,
        ):
            mock_analyze.side_effect = lambda path, report: report
            report = ExecutableReport(path=str(test_file))
            recon.run(str(test_file), report)

        mock_analyze.assert_called_once()

    def test_unknown_format(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """Unrecognized magic bytes produce an 'Unknown format' file_type."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\xde\xad\xbe\xef")

        with patch("caspoon.recon.file_info._read_magic", return_value=b"\xde\xad\xbe\xef"):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert "Unknown format" in result.file_type

    # ------------------------------------------------------------------
    # Content tests — mock _analyze_elf to inject report fields
    # ------------------------------------------------------------------

    def test_elf_64bit_arch_populated(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """64-bit arch fields are set when _analyze_elf reports them."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        def fake_analyze(path, report):
            report.bits = 64
            report.arch = "x86_64"
            report.file_type = "ELF 64-bit LSB executable, x64"
            return report

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"\x7fELF"),
            patch("caspoon.recon.file_info._analyze_elf", side_effect=fake_analyze),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.bits == 64
        assert result.arch == "x86_64"

    def test_elf_32bit_arch_populated(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """32-bit arch fields are set when _analyze_elf reports them."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        def fake_analyze(path, report):
            report.bits = 32
            report.arch = "x86"
            report.file_type = "ELF 32-bit LSB executable, x86"
            return report

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"\x7fELF"),
            patch("caspoon.recon.file_info._analyze_elf", side_effect=fake_analyze),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.bits == 32
        assert result.arch == "x86"

    def test_elf_stripped_populated(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """stripped=True is propagated when _analyze_elf sets it."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        def fake_analyze(path, report):
            report.stripped = True
            report.file_type = "ELF 64-bit LSB executable, x64"
            return report

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"\x7fELF"),
            patch("caspoon.recon.file_info._analyze_elf", side_effect=fake_analyze),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.stripped is True

    # ------------------------------------------------------------------
    # Error handling tests
    # ------------------------------------------------------------------

    def test_read_error(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """OSError from _read_magic produces an 'Error:' file_type."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"data")

        with patch(
            "caspoon.recon.file_info._read_magic",
            side_effect=OSError("permission denied"),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert "Error:" in result.file_type

    def test_analysis_exception_caught(self, recon: FileInfoRecon, tmp_path: Path) -> None:
        """Exception from _analyze_elf is caught and produces an 'Error:' file_type."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        with (
            patch("caspoon.recon.file_info._read_magic", return_value=b"\x7fELF"),
            patch(
                "caspoon.recon.file_info._analyze_elf",
                side_effect=RuntimeError("crash"),
            ),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert "Error:" in result.file_type

    # ------------------------------------------------------------------
    # Integration tests — exercise real pyelftools parsing
    # ------------------------------------------------------------------

    @pytest.mark.integration
    def test_real_test_binary_x64(self, recon, test_binaries_dir):
        """Test with real test_hello_x64 binary."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        assert result.arch in ["x86_64", "x86"]
        assert result.bits in [32, 64]
        assert "ELF" in result.file_type

    @pytest.mark.integration
    def test_real_stripped_binary(self, recon, test_binaries_dir):
        """Test with real stripped binary."""
        binary_path = test_binaries_dir / "test_stripped"
        if not binary_path.exists():
            pytest.skip("test_stripped binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        assert result.stripped is True

    @pytest.mark.integration
    def test_real_not_stripped_binary(self, recon, test_binaries_dir):
        """Test with real non-stripped binary."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        assert result.stripped is False
