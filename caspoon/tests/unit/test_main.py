"""Unit tests for main.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from caspoon.main import main, validate_file_path


class TestValidateFilePath:
    """Tests for validate_file_path function."""

    def test_empty_path(self, caplog):
        """Test validation fails for empty path."""
        result = validate_file_path("")
        assert result is False
        assert "Empty path provided" in caplog.text

    def test_none_path(self, caplog):
        """Test validation fails for None path."""
        result = validate_file_path(None)
        assert result is False
        assert "Empty path provided" in caplog.text

    def test_nonexistent_file(self, caplog):
        """Test validation fails for nonexistent file."""
        result = validate_file_path("/nonexistent/file/path")
        assert result is False
        assert "File does not exist" in caplog.text

    def test_directory_not_file(self, tmp_path, caplog):
        """Test validation fails for directory."""
        directory = tmp_path / "test_dir"
        directory.mkdir()

        result = validate_file_path(str(directory))
        assert result is False
        assert "Path is not a file" in caplog.text

    def test_unreadable_file(self, tmp_path, caplog):
        """Test validation fails for unreadable file."""
        test_file = tmp_path / "unreadable.txt"
        test_file.write_text("test")

        # Mock os.access to simulate unreadable file
        with patch("os.access", return_value=False):
            result = validate_file_path(str(test_file))
            assert result is False
            assert "File is not readable" in caplog.text

    def test_valid_file(self, tmp_path):
        """Test validation succeeds for valid readable file."""
        test_file = tmp_path / "valid_file.txt"
        test_file.write_text("test content")

        result = validate_file_path(str(test_file))
        assert result is True

    def test_relative_path_validation(self, tmp_path):
        """Test validation works with relative paths."""
        # Create a file in temp directory
        test_file = tmp_path / "test.bin"
        test_file.write_text("binary content")

        # Change to temp directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = validate_file_path("test.bin")
            assert result is True
        finally:
            os.chdir(original_cwd)


class TestMain:
    """Tests for main function."""

    def test_main_no_arguments(self, capsys):
        """Test main with no arguments shows usage."""
        with patch.object(sys, "argv", ["caspoon"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Usage:" in captured.out
            assert "python -m caspoon <binary>" in captured.out

    def test_main_capabilities_flag(self):
        """Test main with --capabilities flag."""
        with patch.object(sys, "argv", ["caspoon", "--capabilities"]):
            mock_caps = MagicMock()
            with patch("caspoon.utils.capabilities.get_capabilities", return_value=mock_caps):
                main()
                mock_caps.print_summary.assert_called_once()

    def test_main_capabilities_flag_error(self, caplog):
        """Test main with --capabilities flag when error occurs."""
        with patch.object(sys, "argv", ["caspoon", "--capabilities"]):
            with patch("caspoon.utils.capabilities.get_capabilities", side_effect=RuntimeError("Test error")):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1
                assert "Error checking capabilities" in caplog.text

    def test_main_ui_flag(self):
        """Test main with --ui flag."""
        with patch.object(sys, "argv", ["caspoon", "--ui"]):
            mock_app = MagicMock()
            with patch("caspoon.ui.app.CaspoonApp", return_value=mock_app):
                main()
                mock_app.run.assert_called_once()

    def test_main_ui_flag_error(self, caplog):
        """Test main with --ui flag when error occurs."""
        with patch.object(sys, "argv", ["caspoon", "--ui"]):
            mock_app = MagicMock()
            mock_app.run.side_effect = RuntimeError("UI error")
            with patch("caspoon.ui.app.CaspoonApp", return_value=mock_app):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1
                assert "Error running UI" in caplog.text

    def test_main_invalid_file(self, caplog):
        """Test main with invalid file path."""
        with patch.object(sys, "argv", ["caspoon", "/nonexistent/file"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            assert "File does not exist" in caplog.text

    def test_main_valid_file(self, tmp_path, capsys):
        """Test main with valid file."""
        test_file = tmp_path / "test.bin"
        test_file.write_text("binary")

        mock_runner = MagicMock()
        mock_report = MagicMock()
        mock_report.raw_backend_data = {"r2": {"functions": [], "imports": []}}
        mock_runner.run.return_value = mock_report

        with patch.object(sys, "argv", ["caspoon", str(test_file)]):
            with patch("caspoon.core.runner.ReconRunner", return_value=mock_runner):
                main()

                mock_runner.run.assert_called_once()
                captured = capsys.readouterr()
                # Should output JSON
                assert "{" in captured.out

    def test_main_analysis_error(self, tmp_path, caplog):
        """Test main when analysis raises exception."""
        test_file = tmp_path / "test.bin"
        test_file.write_text("binary")

        mock_runner = MagicMock()
        mock_runner.run.side_effect = RuntimeError("Analysis failed")

        with patch.object(sys, "argv", ["caspoon", str(test_file)]):
            with patch("caspoon.core.runner.ReconRunner", return_value=mock_runner):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1
                assert "Error during analysis" in caplog.text

    def test_main_uses_absolute_path(self, tmp_path, caplog):
        """Test main converts relative path to absolute."""
        test_file = tmp_path / "test.bin"
        test_file.write_text("binary")

        mock_runner = MagicMock()
        mock_report = MagicMock()
        mock_report.raw_backend_data = {"r2": {}}
        mock_runner.run.return_value = mock_report

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch.object(sys, "argv", ["caspoon", "test.bin"]):
                with patch("caspoon.core.runner.ReconRunner", return_value=mock_runner):
                    main()

                    # Should have been called with absolute path
                    call_args = mock_runner.run.call_args[0][0]
                    assert os.path.isabs(call_args)
                    assert call_args.endswith("test.bin")
        finally:
            os.chdir(original_cwd)

    def test_main_outputs_json(self, tmp_path, capsys):
        """Test main outputs valid JSON."""
        test_file = tmp_path / "test.bin"
        test_file.write_text("binary")

        mock_runner = MagicMock()
        mock_report = MagicMock()
        test_data = {"functions": ["main"], "imports": ["printf"]}
        mock_report.raw_backend_data = {"r2": test_data}
        mock_runner.run.return_value = mock_report

        with patch.object(sys, "argv", ["caspoon", str(test_file)]):
            with patch("caspoon.core.runner.ReconRunner", return_value=mock_runner):
                main()

                captured = capsys.readouterr()
                # Verify JSON is valid and contains expected data
                import json

                output = json.loads(captured.out)
                assert output == test_data
