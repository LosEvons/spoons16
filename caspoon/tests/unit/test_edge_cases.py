"""Edge case and robustness tests."""

from pathlib import Path

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.core.runner import ReconRunner


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_empty_file(self, tmp_path):
        """Test handling of empty file."""
        empty_file = tmp_path / "empty"
        empty_file.touch()

        runner = ReconRunner()
        report = runner.run(str(empty_file))

        # Should not crash
        assert isinstance(report, ExecutableReport)
        assert report.path == str(empty_file)

    def test_text_file_as_binary(self, tmp_path):
        """Test handling of non-binary file."""
        text_file = tmp_path / "text.txt"
        text_file.write_text("This is just a text file\nNot a binary\n")

        runner = ReconRunner()
        report = runner.run(str(text_file))

        # Should not crash, should detect it's not ELF
        assert isinstance(report, ExecutableReport)
        assert report.path == str(text_file)

    def test_nonexistent_file_path(self):
        """Test handling of completely nonexistent path."""
        runner = ReconRunner()
        report = runner.run("/totally/fake/path/to/nowhere")

        # Should not crash
        assert isinstance(report, ExecutableReport)

    def test_symlink_to_binary(self, sample_binary, tmp_path):
        """Test handling of symlink to binary."""
        import os

        symlink = tmp_path / "link_to_binary"
        os.symlink(sample_binary, symlink)

        runner = ReconRunner()
        report = runner.run(str(symlink))

        # Should follow symlink and analyze target
        assert isinstance(report, ExecutableReport)

    def test_special_characters_in_path(self, tmp_path):
        """Test handling of special characters in file path."""
        # Create file with special chars in name
        special_file = tmp_path / "test file with spaces & special.bin"
        special_file.write_bytes(b"\x7fELF")

        runner = ReconRunner()
        report = runner.run(str(special_file))

        # Should handle path correctly
        assert isinstance(report, ExecutableReport)

    def test_very_long_filename(self, tmp_path):
        """Test handling of very long filename."""
        long_name = "a" * 200 + ".bin"
        long_file = tmp_path / long_name
        long_file.write_bytes(b"test")

        runner = ReconRunner()
        report = runner.run(str(long_file))

        # Should handle long paths
        assert isinstance(report, ExecutableReport)

    @pytest.mark.slow
    def test_large_binary(self, tmp_path):
        """Test handling of large binary file (10MB)."""
        large_file = tmp_path / "large.bin"
        # Create 10MB file
        with open(large_file, "wb") as f:
            f.write(b"\x00" * (10 * 1024 * 1024))

        runner = ReconRunner()
        report = runner.run(str(large_file))

        # Should handle large files (though may be slow)
        assert isinstance(report, ExecutableReport)

    def test_corrupted_elf_header(self, tmp_path):
        """Test handling of file with corrupted ELF header."""
        corrupted = tmp_path / "corrupted.elf"
        # Start with ELF magic but corrupt the rest
        corrupted.write_bytes(b"\x7fELF\x00\x00\x00\x00" + b"\xff" * 100)

        runner = ReconRunner()
        report = runner.run(str(corrupted))

        # Should not crash, should handle gracefully
        assert isinstance(report, ExecutableReport)

    def test_binary_with_no_permissions(self, tmp_path):
        """Test handling of file with no read permissions."""
        import os

        no_perm = tmp_path / "no_read.bin"
        no_perm.write_bytes(b"test")
        os.chmod(no_perm, 0o000)

        try:
            runner = ReconRunner()
            report = runner.run(str(no_perm))

            # Should handle permission errors gracefully
            assert isinstance(report, ExecutableReport)
        finally:
            # Restore permissions for cleanup (owner read/write only)
            os.chmod(no_perm, 0o600)

    def test_unicode_in_path(self, tmp_path):
        """Test handling of unicode characters in path."""
        unicode_file = tmp_path / "test_日本語_файл.bin"
        unicode_file.write_bytes(b"test")

        runner = ReconRunner()
        report = runner.run(str(unicode_file))

        # Should handle unicode paths
        assert isinstance(report, ExecutableReport)

    def test_report_serialization(self, sample_binary):
        """Test that report can be serialized to dict."""
        runner = ReconRunner()
        report = runner.run(sample_binary)

        # Should be able to convert to dict
        pretty = report.pretty()
        assert isinstance(pretty, dict)
        assert "path" in pretty
        assert "arch" in pretty
        assert "bits" in pretty

    def test_concurrent_analysis(self, test_binaries_dir):
        """Test that multiple analyses can run in parallel (thread-safe)."""
        binaries = [
            test_binaries_dir / "test_hello_x64",
            test_binaries_dir / "test_stripped",
            test_binaries_dir / "test_with_pie",
        ]

        # Filter to existing binaries
        binaries = [b for b in binaries if b.exists()]

        if len(binaries) < 2:
            pytest.skip("Need at least 2 test binaries")

        import concurrent.futures

        def analyze(binary_path):
            runner = ReconRunner()
            return runner.run(str(binary_path))

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(analyze, b) for b in binaries]
            reports = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert len(reports) == len(binaries)
        assert all(isinstance(r, ExecutableReport) for r in reports)
