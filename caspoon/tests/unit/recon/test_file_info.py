"""Unit tests for FileInfoRecon module.

Tests the FileInfoRecon recon module which extracts basic file information
including architecture, bit width, file type, and stripped status.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.recon.file_info import ARCH_MAP, FileInfoRecon


class TestFileInfoRecon:
    """Test FileInfoRecon module."""

    @pytest.fixture
    def recon(self) -> FileInfoRecon:
        """Create FileInfoRecon instance for testing.

        Returns:
            Fresh FileInfoRecon instance.
        """
        return FileInfoRecon()

    def test_module_name(self, recon: FileInfoRecon) -> None:
        """Test module has correct identifying name."""
        assert recon.name == "file_info", "Module name should be 'file_info'"

    def test_analyze_system_binary(self, recon: FileInfoRecon, sample_binary: str) -> None:
        """Test analysis of real system binary."""
        report = ExecutableReport(path=sample_binary)
        result = recon.run(sample_binary, report)

        # Should have some arch info populated
        assert (
            result.arch != "" or result.file_type != ""
        ), "Should populate at least arch or file_type"
        assert result is not None, "Should return a report"

    def test_nonexistent_file(self, recon: FileInfoRecon) -> None:
        """Test graceful handling of nonexistent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)

        # Should handle gracefully without raising exception
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

        # Before: empty fields
        assert report.arch == "", "Architecture should start empty"
        assert report.file_type == "", "File type should start empty"

        # After: enriched with data
        result = recon.run(sample_binary, report)

        # Should have at least one field populated
        # (arch or file_type, depending on file command output)
        assert result.arch != "" or result.file_type != "", "Should populate at least one field"

    def test_64bit_detection(self, recon, tmp_path):
        """Test detection of 64-bit binary."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": 0x3E, "e_type": "ET_EXEC"}  # x86_64, executable
        mock_elffile.elfclass = 64
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = Mock()  # not stripped

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.bits == 64
                assert result.arch == "x86_64"

    def test_32bit_detection(self, recon, tmp_path):
        """Test detection of 32-bit binary."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": 0x03, "e_type": "ET_EXEC"}  # x86, executable
        mock_elffile.elfclass = 32
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = Mock()  # not stripped

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.bits == 32
                assert result.arch == "x86"

    def test_unknown_bit_width(self, recon, tmp_path):
        """Test handling of unknown bit width."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": 0x3E, "e_type": "ET_EXEC"}
        mock_elffile.elfclass = 0  # Unknown
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = None

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.bits is None

    def test_stripped_detection(self, recon, tmp_path):
        """Test detection of stripped binary."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": 0x3E, "e_type": "ET_EXEC"}
        mock_elffile.elfclass = 64
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = None  # No .symtab = stripped

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.stripped is True

    def test_not_stripped_detection(self, recon, tmp_path):
        """Test detection of non-stripped binary."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": 0x3E, "e_type": "ET_EXEC"}
        mock_elffile.elfclass = 64
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = Mock()  # .symtab exists = not stripped

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.stripped is False

    def test_non_elf_file(self, recon, tmp_path):
        """Test handling when file is not an ELF file."""
        test_file = tmp_path / "test_binary"
        test_file.write_text("not an elf file")

        with patch("builtins.open", mock_open(read_data=b"not elf")):
            with patch("caspoon.recon.file_info.ELFFile", side_effect=Exception("Not ELF")):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert "Not an ELF file" in result.file_type

    def test_unexpected_error(self, recon, tmp_path):
        """Test handling of unexpected exception."""
        test_file = tmp_path / "test_binary"
        test_file.write_text("test")

        with patch("builtins.open", side_effect=RuntimeError("Unexpected")):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

            assert "Error:" in result.file_type

    @pytest.mark.parametrize(
        "e_machine,expected_arch",
        [
            (0x3E, "x86_64"),      # EM_X86_64
            (0x03, "x86"),         # EM_386
            (0x28, "ARM"),         # EM_ARM
            (0xB7, "ARM64"),       # EM_AARCH64
            (0x08, "MIPS"),        # EM_MIPS
            (0x14, "PowerPC"),     # EM_PPC
            (0x15, "PowerPC64"),   # EM_PPC64
            (0xF3, "RISC-V"),      # EM_RISCV
            (0x9999, "Unknown"),   # Unknown architecture
        ],
    )
    def test_architecture_detection(self, recon, tmp_path, e_machine, expected_arch):
        """Test architecture detection for various architectures."""
        test_file = tmp_path / "test_binary"
        test_file.write_bytes(b"test")

        mock_elffile = MagicMock()
        mock_elffile.header = {"e_machine": e_machine, "e_type": "ET_EXEC"}
        mock_elffile.elfclass = 64
        mock_elffile.little_endian = True
        mock_elffile.get_section_by_name.return_value = None

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.file_info.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert result.arch == expected_arch

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
