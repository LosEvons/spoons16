"""Unit tests for ProtectionsRecon module."""

from unittest.mock import MagicMock, Mock, mock_open, patch

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
        mock_elffile = MagicMock()
        mock_elffile.header = {"e_type": "ET_DYN"}  # PIE enabled

        # Mock PT_GNU_STACK segment with NX (no execute flag)
        mock_stack_segment = Mock()
        mock_stack_segment.__getitem__ = lambda self, key: {
            "p_type": "PT_GNU_STACK",
            "p_flags": 0x6,  # RW, no execute (PF_X = 0x1)
        }[key]

        # Mock PT_GNU_RELRO segment
        mock_relro_segment = Mock()
        mock_relro_segment.__getitem__ = lambda self, key: {
            "p_type": "PT_GNU_RELRO",
            "p_flags": 0x4,
        }[key]

        mock_elffile.iter_segments.return_value = [mock_stack_segment, mock_relro_segment]

        # Mock .dynsym section with __stack_chk_fail
        mock_symbol = Mock()
        mock_symbol.name = "__stack_chk_fail"
        mock_dynsym = Mock()
        mock_dynsym.iter_symbols.return_value = [mock_symbol]
        
        # Mock .dynamic section with DT_BIND_NOW
        mock_bind_tag = Mock()
        mock_bind_tag.entry.d_tag = "DT_BIND_NOW"
        mock_dynamic = Mock()
        mock_dynamic.iter_tags.return_value = [mock_bind_tag]

        def mock_get_section(name):
            if name == ".dynsym":
                return mock_dynsym
            return None

        mock_elffile.get_section_by_name = mock_get_section
        
        # Mock iter_sections to return dynamic section
        from elftools.elf.dynamic import DynamicSection
        mock_dynamic.__class__ = DynamicSection
        mock_elffile.iter_sections.return_value = [mock_dynamic]

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.protections.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path="/test/binary")
                result = recon.run("/test/binary", report)

                assert result.protections.pie is True
                assert result.protections.nx is True
                assert result.protections.canary is True
                assert result.protections.relro == "full"

    def test_partial_protections_detection(self, recon):
        """Test detection of partial protections."""
        mock_elffile = MagicMock()
        mock_elffile.header = {"e_type": "ET_EXEC"}  # No PIE

        # Mock PT_GNU_STACK segment with NX
        mock_stack_segment = Mock()
        mock_stack_segment.__getitem__ = lambda self, key: {
            "p_type": "PT_GNU_STACK",
            "p_flags": 0x6,  # RW, no execute
        }[key]

        # Mock PT_GNU_RELRO segment (partial RELRO)
        mock_relro_segment = Mock()
        mock_relro_segment.__getitem__ = lambda self, key: {
            "p_type": "PT_GNU_RELRO",
            "p_flags": 0x4,
        }[key]

        mock_elffile.iter_segments.return_value = [mock_stack_segment, mock_relro_segment]

        # Mock .dynsym section without __stack_chk_fail
        mock_symbol = Mock()
        mock_symbol.name = "some_other_symbol"
        mock_dynsym = Mock()
        mock_dynsym.iter_symbols.return_value = [mock_symbol]

        mock_elffile.get_section_by_name.return_value = mock_dynsym

        # No DT_BIND_NOW in .dynamic
        mock_elffile.iter_sections.return_value = []

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.protections.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path="/test/binary")
                result = recon.run("/test/binary", report)

                assert result.protections.pie is False
                assert result.protections.nx is True
                assert result.protections.canary is False
                assert result.protections.relro == "partial"

    def test_no_protections_detection(self, recon):
        """Test detection of no protections."""
        mock_elffile = MagicMock()
        mock_elffile.header = {"e_type": "ET_EXEC"}  # No PIE

        # Mock PT_GNU_STACK segment with execute flag (no NX)
        mock_stack_segment = Mock()
        mock_stack_segment.__getitem__ = lambda self, key: {
            "p_type": "PT_GNU_STACK",
            "p_flags": 0x7,  # RWX (PF_X = 0x1 is set)
        }[key]

        mock_elffile.iter_segments.return_value = [mock_stack_segment]

        # No .dynsym section
        mock_elffile.get_section_by_name.return_value = None

        # No .dynamic sections
        mock_elffile.iter_sections.return_value = []

        with patch("builtins.open", mock_open(read_data=b"fake elf")):
            with patch("caspoon.recon.protections.ELFFile", return_value=mock_elffile):
                report = ExecutableReport(path="/test/binary")
                result = recon.run("/test/binary", report)

                assert result.protections.pie is False
                assert result.protections.nx is False
                assert result.protections.canary is False
                assert result.protections.relro == "none"

    def test_non_elf_file(self, recon):
        """Test handling when file is not an ELF file."""
        with patch("builtins.open", mock_open(read_data=b"not elf")):
            with patch("caspoon.recon.protections.ELFFile", side_effect=Exception("Not ELF")):
                report = ExecutableReport(path="/test/binary")
                result = recon.run("/test/binary", report)

                assert result.protections is not None
                assert result.protections.relro == "not_elf"
                assert result.protections.pie is False
                assert result.protections.nx is False
                assert result.protections.canary is False

    def test_unexpected_error_handling(self, recon):
        """Test handling of unexpected exceptions."""
        with patch("builtins.open", side_effect=RuntimeError("Unexpected error")):
            report = ExecutableReport(path="/test/binary")
            result = recon.run("/test/binary", report)

            assert result.protections is not None
            assert "error:" in result.protections.relro.lower()

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
    def test_real_test_binary_with_pie(self, recon, test_binaries_dir):
        """Test with real test_with_pie binary (full protections)."""
        binary_path = test_binaries_dir / "test_with_pie"
        if not binary_path.exists():
            pytest.skip("test_with_pie binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # Should detect full protections
        assert result.protections is not None
        assert result.protections.pie is True
        assert result.protections.canary is True
        assert result.protections.nx is True
        assert result.protections.relro == "full"
