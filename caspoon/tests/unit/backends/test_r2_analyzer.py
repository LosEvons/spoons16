"""Unit tests for backends/r2_analyzer.py module."""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from caspoon.backends.r2_analyzer import (
    MAX_MAIN_INSTRUCTIONS,
    analyze_with_r2,
)


class TestAnalyzeWithR2:
    """Tests for the analyze_with_r2 function."""

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_successful_analysis_with_all_data(self, mock_r2pipe):
        """Test successful analysis with all data present."""
        # Setup mock r2pipe instance
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # Mock command responses
        functions_data = [
            {"name": "main", "offset": 0x1000, "size": 100},
            {"name": "helper", "offset": 0x2000, "size": 50},
        ]
        imports_data = [
            {"name": "printf", "type": "FUNC"},
            {"name": "malloc", "type": "FUNC"},
        ]
        strings_data = [
            {"string": "Hello World", "vaddr": 0x3000},
            {"string": "Error", "vaddr": 0x3010},
        ]
        main_ops_data = [
            {"offset": 0x1000, "opcode": "push rbp"},
            {"offset": 0x1001, "opcode": "mov rbp, rsp"},
        ]

        mock_r2.cmd.side_effect = [
            None,  # aa command
            json.dumps(functions_data),  # aflj
            json.dumps(imports_data),  # isj
            json.dumps(strings_data),  # izj
            None,  # s main
            json.dumps(main_ops_data),  # pdj
        ]

        # Execute
        result = analyze_with_r2("/path/to/binary")

        # Verify
        assert result["functions"] == functions_data
        assert result["imports"] == imports_data
        assert result["strings"] == strings_data
        assert result["main_ops"] == main_ops_data

        # Verify r2pipe was called correctly
        mock_r2pipe.open.assert_called_once_with("/path/to/binary", flags=["-2"])
        mock_r2.cmd.assert_any_call("aa")
        mock_r2.cmd.assert_any_call("aflj")
        mock_r2.cmd.assert_any_call("isj")
        mock_r2.cmd.assert_any_call("izj")
        mock_r2.cmd.assert_any_call("s main")
        mock_r2.cmd.assert_any_call(f"pdj {MAX_MAIN_INSTRUCTIONS}")
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_analysis_with_empty_results(self, mock_r2pipe):
        """Test analysis when r2 returns empty results."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # Mock empty responses
        mock_r2.cmd.side_effect = [
            None,  # aa
            "",  # aflj (empty)
            "   ",  # isj (whitespace only)
            "",  # izj
            None,  # s main
            "",  # pdj
        ]

        result = analyze_with_r2("/path/to/binary")

        # Verify empty lists are returned
        assert result["functions"] == []
        assert result["imports"] == []
        assert result["strings"] == []
        assert result["main_ops"] == []

        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_json_decode_error_functions(self, mock_r2pipe, caplog):
        """Test handling of JSON decode error for functions."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # Mock invalid JSON for functions
        mock_r2.cmd.side_effect = [
            None,  # aa
            "invalid json{",  # aflj (invalid JSON)
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        # Verify empty list returned and warning logged
        assert result["functions"] == []
        assert "Failed to parse functions JSON" in caplog.text
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_json_decode_error_imports(self, mock_r2pipe, caplog):
        """Test handling of JSON decode error for imports."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [
            None,  # aa
            "[]",  # aflj
            "not valid json",  # isj (invalid JSON)
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        assert result["imports"] == []
        assert "Failed to parse imports JSON" in caplog.text
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_json_decode_error_strings(self, mock_r2pipe, caplog):
        """Test handling of JSON decode error for strings."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [
            None,  # aa
            "[]",  # aflj
            "[]",  # isj
            "{broken",  # izj (invalid JSON)
            None,  # s main
            "[]",  # pdj
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        assert result["strings"] == []
        assert "Failed to parse strings JSON" in caplog.text
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_json_decode_error_main_ops(self, mock_r2pipe, caplog):
        """Test handling of JSON decode error for main disassembly."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [
            None,  # aa
            "[]",  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "}{invalid",  # pdj (invalid JSON)
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        assert result["main_ops"] == []
        assert "Failed to parse main disassembly JSON" in caplog.text
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_all_json_decode_errors(self, mock_r2pipe, caplog):
        """Test handling when all JSON responses are invalid."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # All invalid JSON
        mock_r2.cmd.side_effect = [
            None,  # aa
            "bad",  # aflj
            "bad",  # isj
            "bad",  # izj
            None,  # s main
            "bad",  # pdj
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        # All should be empty lists
        assert result["functions"] == []
        assert result["imports"] == []
        assert result["strings"] == []
        assert result["main_ops"] == []

        # All four warnings should be logged
        assert "Failed to parse functions JSON" in caplog.text
        assert "Failed to parse imports JSON" in caplog.text
        assert "Failed to parse strings JSON" in caplog.text
        assert "Failed to parse main disassembly JSON" in caplog.text

        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_r2_quit_called_on_success(self, mock_r2pipe):
        """Test that r2.quit() is always called even on success."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        analyze_with_r2("/path/to/binary")

        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_r2_quit_called_on_exception(self, mock_r2pipe):
        """Test that r2.quit() is called even when an exception occurs."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # Simulate an exception during analysis
        mock_r2.cmd.side_effect = RuntimeError("r2 command failed")

        with pytest.raises(RuntimeError, match="r2 command failed"):
            analyze_with_r2("/path/to/binary")

        # quit() should still be called
        mock_r2.quit.assert_called_once()

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_max_instructions_constant_used(self, mock_r2pipe):
        """Test that MAX_MAIN_INSTRUCTIONS constant is used in pdj command."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        analyze_with_r2("/path/to/binary")

        # Verify the pdj command uses MAX_MAIN_INSTRUCTIONS
        mock_r2.cmd.assert_any_call(f"pdj {MAX_MAIN_INSTRUCTIONS}")

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_debug_logging(self, mock_r2pipe, caplog):
        """Test that debug logging messages are produced."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "func1"}]
        imports_data = [{"name": "import1"}]
        strings_data = [{"string": "str1"}]

        mock_r2.cmd.side_effect = [
            None,
            json.dumps(functions_data),
            json.dumps(imports_data),
            json.dumps(strings_data),
            None,
            "[]",
        ]

        with caplog.at_level(logging.DEBUG):
            analyze_with_r2("/test/binary")

        assert "Starting radare2 analysis on /test/binary" in caplog.text
        assert "Radare2 analysis complete: 1 functions, 1 imports, 1 strings" in caplog.text

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_flags_parameter_passed_to_r2pipe(self, mock_r2pipe):
        """Test that the correct flags are passed to r2pipe.open()."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        analyze_with_r2("/binary/path")

        # Verify flags are passed
        mock_r2pipe.open.assert_called_once_with("/binary/path", flags=["-2"])

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_r2_commands_executed_in_correct_order(self, mock_r2pipe):
        """Test that r2 commands are executed in the correct sequence."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        analyze_with_r2("/path")

        # Check the order of commands
        calls = [call[0][0] for call in mock_r2.cmd.call_args_list]
        assert calls == ["aa", "aflj", "isj", "izj", "s main", f"pdj {MAX_MAIN_INSTRUCTIONS}"]

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_return_structure(self, mock_r2pipe):
        """Test that the return dictionary has the correct structure."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        result = analyze_with_r2("/path")

        # Verify all expected keys are present
        assert "functions" in result
        assert "imports" in result
        assert "strings" in result
        assert "main_ops" in result

        # Verify they're all lists
        assert isinstance(result["functions"], list)
        assert isinstance(result["imports"], list)
        assert isinstance(result["strings"], list)
        assert isinstance(result["main_ops"], list)

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_r2pipe_open_exception(self, mock_r2pipe):
        """Test handling when r2pipe.open() raises an exception."""
        mock_r2pipe.open.side_effect = Exception("Failed to open binary")

        with pytest.raises(Exception, match="Failed to open binary"):
            analyze_with_r2("/nonexistent/binary")

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_seek_main_command(self, mock_r2pipe):
        """Test that 's main' command is executed to seek to main function."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        analyze_with_r2("/binary")

        # Verify 's main' was called before pdj
        mock_r2.cmd.assert_any_call("s main")

        # Verify order: 's main' before 'pdj'
        calls = [call[0][0] for call in mock_r2.cmd.call_args_list]
        s_main_idx = calls.index("s main")
        pdj_idx = calls.index(f"pdj {MAX_MAIN_INSTRUCTIONS}")
        assert s_main_idx < pdj_idx
