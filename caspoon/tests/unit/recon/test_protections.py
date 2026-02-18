"""Unit tests for ProtectionsRecon module."""

from unittest.mock import patch

import pytest

from caspoon.core.models import ExecutableReport, ProtectionInfo
from caspoon.recon.protections import ProtectionsRecon


class TestProtectionsRecon:
    """Test ProtectionsRecon module."""

    @pytest.fixture
    def recon(self):
        """Create ProtectionsRecon instance."""
        return ProtectionsRecon()

    # ------------------------------------------------------------------
    # Basic / contract tests
    # ------------------------------------------------------------------

    def test_module_name(self, recon):
        """Test module has correct name."""
        assert recon.name == "protections"

    # ------------------------------------------------------------------
    # Dispatch tests — mock _read_magic to control format detection
    # ------------------------------------------------------------------

    def test_elf_binary_dispatched(self, recon, tmp_path):
        """ELF magic bytes cause _detect_elf_protections to be called."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        with (
            patch(
                "caspoon.recon.protections._read_magic", return_value=b"\x7fELF"
            ),
            patch(
                "caspoon.recon.protections._detect_elf_protections",
                return_value=ProtectionInfo(),
            ) as mock_detect,
        ):
            report = ExecutableReport(path=str(test_file))
            recon.run(str(test_file), report)

        mock_detect.assert_called_once()

    def test_pe_binary_dispatched(self, recon, tmp_path):
        """PE magic bytes cause _detect_pe_protections to be called."""
        test_file = tmp_path / "binary.exe"
        test_file.write_bytes(b"MZ\x00\x00")

        with (
            patch(
                "caspoon.recon.protections._read_magic", return_value=b"MZ\x00\x00"
            ),
            patch(
                "caspoon.recon.protections._detect_pe_protections",
                return_value=ProtectionInfo(relro="N/A"),
            ) as mock_detect,
        ):
            report = ExecutableReport(path=str(test_file))
            recon.run(str(test_file), report)

        mock_detect.assert_called_once()

    def test_unsupported_format(self, recon, tmp_path):
        """Unrecognized magic bytes produce 'N/A (unsupported format)' relro."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\xde\xad\xbe\xef")

        with patch(
            "caspoon.recon.protections._read_magic", return_value=b"\xde\xad\xbe\xef"
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections.relro == "N/A (unsupported format)"

    # ------------------------------------------------------------------
    # Content tests — mock _detect_elf_protections return value
    # ------------------------------------------------------------------

    def test_full_protections_detection(self, recon, tmp_path):
        """All protections enabled are correctly propagated to report."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        full_pi = ProtectionInfo(pie=True, nx=True, canary=True, relro="full")

        with (
            patch("caspoon.recon.protections._read_magic", return_value=b"\x7fELF"),
            patch(
                "caspoon.recon.protections._detect_elf_protections",
                return_value=full_pi,
            ),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections.pie is True
        assert result.protections.nx is True
        assert result.protections.canary is True
        assert result.protections.relro == "full"

    def test_partial_protections_detection(self, recon, tmp_path):
        """Partial protections are correctly propagated to report."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        partial_pi = ProtectionInfo(pie=False, nx=True, canary=False, relro="partial")

        with (
            patch("caspoon.recon.protections._read_magic", return_value=b"\x7fELF"),
            patch(
                "caspoon.recon.protections._detect_elf_protections",
                return_value=partial_pi,
            ),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections.pie is False
        assert result.protections.nx is True
        assert result.protections.canary is False
        assert result.protections.relro == "partial"

    def test_no_protections_detection(self, recon, tmp_path):
        """No protections case is correctly propagated to report."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        none_pi = ProtectionInfo(pie=False, nx=False, canary=False, relro="none")

        with (
            patch("caspoon.recon.protections._read_magic", return_value=b"\x7fELF"),
            patch(
                "caspoon.recon.protections._detect_elf_protections",
                return_value=none_pi,
            ),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections.pie is False
        assert result.protections.nx is False
        assert result.protections.canary is False
        assert result.protections.relro == "none"

    # ------------------------------------------------------------------
    # Error handling tests
    # ------------------------------------------------------------------

    def test_file_not_readable(self, recon, tmp_path):
        """OSError from _read_magic produces 'Error:' in relro."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"data")

        with patch(
            "caspoon.recon.protections._read_magic",
            side_effect=OSError("permission denied"),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections is not None
        assert "Error:" in result.protections.relro

    def test_analysis_exception_caught(self, recon, tmp_path):
        """Exception from _detect_elf_protections is caught and produces 'Error:' in relro."""
        test_file = tmp_path / "binary"
        test_file.write_bytes(b"\x7fELF")

        with (
            patch("caspoon.recon.protections._read_magic", return_value=b"\x7fELF"),
            patch(
                "caspoon.recon.protections._detect_elf_protections",
                side_effect=RuntimeError("crash"),
            ),
        ):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

        assert result.protections is not None
        assert "Error:" in result.protections.relro

    # ------------------------------------------------------------------
    # Integration tests — exercise real pyelftools parsing
    # ------------------------------------------------------------------

    @pytest.mark.integration
    def test_real_test_binary_no_pie(self, recon, test_binaries_dir):
        """Test with real test_hello_x64 binary (no PIE)."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        assert result.protections is not None
        assert result.protections.nx is True or result.protections.relro != "Unknown"

    @pytest.mark.integration
    @pytest.mark.requires_checksec
    def test_checksec_with_real_binary(self, recon):
        """Test protections detection with a real system binary."""
        import shutil

        if not shutil.which("checksec"):
            pytest.skip("checksec not installed")

        report = ExecutableReport(path="/bin/ls")
        result = recon.run("/bin/ls", report)

        assert result.protections is not None
        assert "Error:" not in result.protections.relro
        assert result.protections.nx is True

    @pytest.mark.integration
    @pytest.mark.requires_checksec
    def test_real_test_binary_with_pie(self, recon, test_binaries_dir):
        """Test with real test_with_pie binary (full protections)."""
        binary_path = test_binaries_dir / "test_with_pie"
        if not binary_path.exists():
            pytest.skip("test_with_pie binary not available")

        import shutil

        if not shutil.which("checksec"):
            pytest.skip("checksec not installed")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        assert result.protections is not None
        assert result.protections.pie is True
        assert result.protections.canary is True
        assert result.protections.nx is True
        assert result.protections.relro == "full"
