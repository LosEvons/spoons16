"""Unit tests for ImportExportRecon module."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.recon.imports_exports import MAX_FILE_SIZE, ImportExportRecon


class TestImportExportRecon:
    """Test ImportExportRecon module."""

    @pytest.fixture
    def recon(self):
        """Create ImportExportRecon instance."""
        return ImportExportRecon()

    def test_module_name(self, recon):
        """Test module has correct name."""
        assert recon.name == "imports_exports"

    def test_file_not_found(self, recon):
        """Test handling of non-existent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)

        assert result is not None
        assert "imports_exports_error" in result.raw_backend_data
        assert result.raw_backend_data["imports_exports_error"] == "File not found"

    def test_file_too_large(self, recon, tmp_path):
        """Test handling of file exceeding size limit."""
        # Create a file path but mock the size check
        test_file = tmp_path / "large_file"
        test_file.write_text("test")

        with patch("os.path.getsize", return_value=MAX_FILE_SIZE + 1):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

            assert "imports_exports_error" in result.raw_backend_data
            assert result.raw_backend_data["imports_exports_error"] == "File too large"

    def test_getsize_os_error(self, recon, tmp_path):
        """Test handling of OSError when checking file size."""
        test_file = tmp_path / "test_file"
        test_file.write_text("test")

        with patch("os.path.getsize", side_effect=OSError("Permission denied")):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

            assert "imports_exports_error" in result.raw_backend_data
            assert "Permission denied" in result.raw_backend_data["imports_exports_error"]

    def test_not_elf_file(self, recon, tmp_path):
        """Test handling of non-ELF file."""
        # Create a text file
        test_file = tmp_path / "not_elf.txt"
        test_file.write_text("This is not an ELF file")

        report = ExecutableReport(path=str(test_file))
        result = recon.run(str(test_file), report)

        assert "imports_exports_error" in result.raw_backend_data
        assert result.raw_backend_data["imports_exports_error"] == "Not an ELF file"

    def test_io_error_reading_file(self, recon, tmp_path):
        """Test handling of IO error when reading file."""
        test_file = tmp_path / "test_file"
        test_file.write_text("test")

        # Mock open to raise IOError
        with patch("builtins.open", side_effect=OSError("Read error")):
            report = ExecutableReport(path=str(test_file))
            result = recon.run(str(test_file), report)

            assert "imports_exports_error" in result.raw_backend_data
            assert "IO error" in result.raw_backend_data["imports_exports_error"]

    def test_empty_imports_exports(self, recon):
        """Test handling of ELF file with no symbols."""
        # This will be tested with real binary or mocked ELF
        # For now, test that empty lists are initialized
        report = ExecutableReport(path="/test/binary")
        assert len(report.imports) == 0
        assert len(report.exports) == 0

    @pytest.mark.integration
    def test_real_test_binary(self, recon, test_binaries_dir):
        """Test with real test_hello_x64 binary."""
        binary_path = test_binaries_dir / "test_hello_x64"
        if not binary_path.exists():
            pytest.skip("test_hello_x64 binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # Should extract some imports (at least libc functions)
        assert len(result.imports) > 0
        # Should find printf from our test program
        assert any("printf" in imp for imp in result.imports)

        # Should have some exports (functions defined in the binary)
        assert len(result.exports) > 0

    @pytest.mark.integration
    def test_stripped_binary_symbols(self, recon, test_binaries_dir):
        """Test with stripped binary."""
        binary_path = test_binaries_dir / "test_stripped"
        if not binary_path.exists():
            pytest.skip("test_stripped binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # Stripped binary won't have .symtab but should have .dynsym
        assert len(result.imports) > 0
        # Exports from .symtab won't be available in stripped binary
        # but .dynsym might have some

    @pytest.mark.integration
    def test_pie_binary_symbols(self, recon, test_binaries_dir):
        """Test with PIE-enabled binary."""
        binary_path = test_binaries_dir / "test_with_pie"
        if not binary_path.exists():
            pytest.skip("test_with_pie binary not available")

        report = ExecutableReport(path=str(binary_path))
        result = recon.run(str(binary_path), report)

        # PIE binaries should still have symbol tables
        assert len(result.imports) > 0

    def test_mock_elf_with_imports(self, recon, tmp_path):
        """Test ELF parsing with mocked symbols."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")  # Minimal file

        # Create mock ELF file structure
        mock_symbol = {"st_info": {"type": "STT_FUNC"}, "name": "mock_function"}
        mock_sym_obj = Mock()
        mock_sym_obj.__getitem__ = lambda self, key: mock_symbol[key]
        mock_sym_obj.name = "mock_function"

        mock_section = Mock()
        mock_section.iter_symbols.return_value = [mock_sym_obj]

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: (
            mock_section if name == ".dynsym" else None
        )

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert "mock_function" in result.imports

    def test_filter_empty_symbol_names(self, recon, tmp_path):
        """Test that empty symbol names are filtered out."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        # Create properly mocked symbols
        def create_mock_sym(name, func_type="STT_FUNC"):
            sym = Mock()
            sym.__getitem__ = lambda self, key: {"type": func_type}
            sym.name = name
            return sym

        mock_symbols = [
            create_mock_sym("valid_function"),
            create_mock_sym(""),  # Empty
            create_mock_sym("   "),  # Whitespace only
            create_mock_sym("another_function"),
        ]

        mock_section = Mock()
        mock_section.iter_symbols.return_value = mock_symbols

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: (
            mock_section if name == ".dynsym" else None
        )

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                # Should only include non-empty names
                assert "valid_function" in result.imports
                assert "another_function" in result.imports
                # Empty and whitespace-only names should be filtered
                assert "" not in result.imports
                assert "   " not in result.imports

    def test_only_function_symbols_extracted(self, recon, tmp_path):
        """Test that only STT_FUNC symbols are extracted."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        # Create properly mocked symbols
        def create_mock_sym(name, func_type):
            sym = Mock()
            sym.__getitem__ = lambda self, key: {"type": func_type}
            sym.name = name
            return sym

        mock_symbols = [
            create_mock_sym("function1", "STT_FUNC"),
            create_mock_sym("variable1", "STT_OBJECT"),
            create_mock_sym("function2", "STT_FUNC"),
            create_mock_sym("section1", "STT_SECTION"),
        ]

        mock_section = Mock()
        mock_section.iter_symbols.return_value = mock_symbols

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: (
            mock_section if name == ".dynsym" else None
        )

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                # Should only include STT_FUNC types
                assert "function1" in result.imports
                assert "function2" in result.imports
                assert "variable1" not in result.imports
                assert "section1" not in result.imports

    def test_symtab_exports_extraction(self, recon, tmp_path):
        """Test that exports are extracted from .symtab section."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        # Create mock symbols for both .dynsym and .symtab
        def create_mock_sym(name, func_type="STT_FUNC"):
            sym = Mock()
            sym.__getitem__ = lambda self, key: {"type": func_type}
            sym.name = name
            return sym

        # .dynsym has imports
        dynsym_symbols = [create_mock_sym("imported_func")]
        mock_dynsym = Mock()
        mock_dynsym.iter_symbols.return_value = dynsym_symbols

        # .symtab has exports (local functions)
        symtab_symbols = [
            create_mock_sym("exported_func1"),
            create_mock_sym("exported_func2"),
            create_mock_sym(""),  # Empty name should be filtered
        ]
        mock_symtab = Mock()
        mock_symtab.iter_symbols.return_value = symtab_symbols

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: {
            ".dynsym": mock_dynsym,
            ".symtab": mock_symtab,
        }.get(name)

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                # Check imports from .dynsym
                assert "imported_func" in result.imports

                # Check exports from .symtab
                assert "exported_func1" in result.exports
                assert "exported_func2" in result.exports
                # Empty name should be filtered
                assert "" not in result.exports

    def test_symtab_filters_non_function_symbols(self, recon, tmp_path):
        """Test that .symtab only extracts STT_FUNC symbols."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        def create_mock_sym(name, func_type):
            sym = Mock()
            sym.__getitem__ = lambda self, key: {"type": func_type}
            sym.name = name
            return sym

        # .symtab with mixed symbol types
        symtab_symbols = [
            create_mock_sym("func_export", "STT_FUNC"),
            create_mock_sym("data_var", "STT_OBJECT"),
            create_mock_sym("another_func", "STT_FUNC"),
        ]
        mock_symtab = Mock()
        mock_symtab.iter_symbols.return_value = symtab_symbols

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: (
            mock_symtab if name == ".symtab" else None
        )

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                # Should only include STT_FUNC from symtab
                assert "func_export" in result.exports
                assert "another_func" in result.exports
                assert "data_var" not in result.exports

    def test_symtab_filters_whitespace_names(self, recon, tmp_path):
        """Test that .symtab filters out whitespace-only names."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        def create_mock_sym(name):
            sym = Mock()
            sym.__getitem__ = lambda self, key: {"type": "STT_FUNC"}
            sym.name = name
            return sym

        symtab_symbols = [
            create_mock_sym("valid_export"),
            create_mock_sym(""),
            create_mock_sym("  "),
            create_mock_sym("\t"),
        ]
        mock_symtab = Mock()
        mock_symtab.iter_symbols.return_value = symtab_symbols

        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = lambda name: (
            mock_symtab if name == ".symtab" else None
        )

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert "valid_export" in result.exports
                assert len(result.exports) == 1

    def test_generic_exception_handling(self, recon, tmp_path):
        """Test handling of unexpected exceptions during ELF parsing."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        mock_elf = Mock()
        # Raise an unexpected exception
        mock_elf.get_section_by_name.side_effect = RuntimeError("Unexpected error")

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert "imports_exports_error" in result.raw_backend_data
                assert "Unexpected error" in result.raw_backend_data["imports_exports_error"]

    def test_generic_exception_with_different_error_types(self, recon, tmp_path):
        """Test handling of various exception types."""
        test_file = tmp_path / "test.elf"
        test_file.write_bytes(b"ELF")

        # Test with ValueError
        mock_elf = Mock()
        mock_elf.get_section_by_name.side_effect = ValueError("Invalid value")

        with patch("builtins.open", mock_open(read_data=b"ELF")):
            with patch("caspoon.recon.imports_exports.ELFFile", return_value=mock_elf):
                report = ExecutableReport(path=str(test_file))
                result = recon.run(str(test_file), report)

                assert "imports_exports_error" in result.raw_backend_data
                assert "Invalid value" in result.raw_backend_data["imports_exports_error"]
