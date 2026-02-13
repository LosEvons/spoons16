"""Unit tests for backends/r2_analyzer.py module."""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from caspoon.backends.r2_analyzer import (
    MAX_MAIN_INSTRUCTIONS,
    MAX_XREF_FUNCTIONS,
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
            # Xrefs for main (0x1000)
            "[]",  # axtj @ 0x1000
            "[]",  # axfj @ 0x1000
            # Xrefs for helper (0x2000)
            "[]",  # axtj @ 0x2000
            "[]",  # axfj @ 0x2000
        ]

        # Execute
        result = analyze_with_r2("/path/to/binary")

        # Verify
        assert result["functions"] == functions_data
        assert result["imports"] == imports_data
        assert result["strings"] == strings_data
        assert result["main_ops"] == main_ops_data
        assert "xrefs" in result
        assert "to" in result["xrefs"]
        assert "from" in result["xrefs"]

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


class TestXrefExtraction:
    """Tests for cross-reference extraction functionality."""

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xrefs_extracted_successfully(self, mock_r2pipe):
        """Test that xrefs are extracted and structured correctly."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [
            {"name": "main", "offset": 0x1000},
            {"name": "helper", "offset": 0x2000},
        ]

        # Xrefs TO main (who calls main)
        xrefs_to_main = [
            {"from": 0x100, "type": "CALL", "opcode": "call main"},
        ]

        # Xrefs FROM main (what main calls)
        xrefs_from_main = [
            {"to": 0x2000, "type": "CALL", "opcode": "call helper"},
        ]

        # Xrefs TO helper
        xrefs_to_helper = [
            {"from": 0x1000, "type": "CALL", "opcode": "call helper"},
        ]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            # Xrefs for main
            json.dumps(xrefs_to_main),  # axtj @ 0x1000
            json.dumps(xrefs_from_main),  # axfj @ 0x1000
            # Xrefs for helper
            json.dumps(xrefs_to_helper),  # axtj @ 0x2000
            "[]",  # axfj @ 0x2000 (no xrefs from helper)
        ]

        result = analyze_with_r2("/path/to/binary")

        # Verify xrefs structure exists
        assert "xrefs" in result
        assert "to" in result["xrefs"]
        assert "from" in result["xrefs"]

        # Verify xrefs for main
        assert "0x1000" in result["xrefs"]["to"]
        assert result["xrefs"]["to"]["0x1000"] == xrefs_to_main
        assert "0x1000" in result["xrefs"]["from"]
        assert result["xrefs"]["from"]["0x1000"] == xrefs_from_main

        # Verify xrefs for helper
        assert "0x2000" in result["xrefs"]["to"]
        assert result["xrefs"]["to"]["0x2000"] == xrefs_to_helper
        # helper has no xrefs from, so it shouldn't be in the dict
        assert "0x2000" not in result["xrefs"]["from"]

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xrefs_with_no_references(self, mock_r2pipe):
        """Test xref extraction when functions have no cross-references."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "isolated", "offset": 0x1000}]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            "",  # axtj @ 0x1000 (no xrefs to)
            "",  # axfj @ 0x1000 (no xrefs from)
        ]

        result = analyze_with_r2("/path/to/binary")

        # Verify xrefs structure exists but is empty
        assert "xrefs" in result
        assert result["xrefs"]["to"] == {}
        assert result["xrefs"]["from"] == {}

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_json_parse_error_to(self, mock_r2pipe, caplog):
        """Test handling of JSON parse error for xrefs-to."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "func", "offset": 0x1000}]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            "invalid json{",  # axtj @ 0x1000 (invalid JSON)
            "[]",  # axfj @ 0x1000
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        # Verify warning was logged
        assert "Failed to parse xrefs-to JSON for 0x1000" in caplog.text

        # Verify xrefs structure exists but doesn't include the failed parse
        assert "xrefs" in result
        assert "0x1000" not in result["xrefs"]["to"]

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_json_parse_error_from(self, mock_r2pipe, caplog):
        """Test handling of JSON parse error for xrefs-from."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "func", "offset": 0x1000}]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            "[]",  # axtj @ 0x1000
            "{bad json",  # axfj @ 0x1000 (invalid JSON)
        ]

        with caplog.at_level(logging.WARNING):
            result = analyze_with_r2("/path/to/binary")

        # Verify warning was logged
        assert "Failed to parse xrefs-from JSON for 0x1000" in caplog.text

        # Verify xrefs structure exists but doesn't include the failed parse
        assert "xrefs" in result
        assert "0x1000" not in result["xrefs"]["from"]

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_command_exception(self, mock_r2pipe, caplog):
        """Test handling of exception during xref command execution."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "func", "offset": 0x1000}]

        def cmd_side_effect(cmd):
            if "aflj" in cmd:
                return json.dumps(functions_data)
            elif "axtj" in cmd:
                raise RuntimeError("r2 command failed")
            elif cmd in ["aa", "s main"]:
                return None
            else:
                return "[]"

        mock_r2.cmd.side_effect = cmd_side_effect

        with caplog.at_level(logging.WARNING, logger="caspoon.backends.r2_analyzer"):
            result = analyze_with_r2("/path/to/binary")

        # Verify error was logged
        assert "Error extracting xrefs-to for 0x1000" in caplog.text

        # Analysis should still complete
        assert "xrefs" in result

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_max_functions_limit(self, mock_r2pipe):
        """Test that xref extraction respects MAX_XREF_FUNCTIONS limit."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        # Create more functions than MAX_XREF_FUNCTIONS
        num_functions = MAX_XREF_FUNCTIONS + 10
        functions_data = [
            {"name": f"func_{i}", "offset": 0x1000 + i * 0x100}
            for i in range(num_functions)
        ]

        # Track how many xref commands are executed
        xref_commands = []

        def cmd_side_effect(cmd):
            if "axtj" in cmd or "axfj" in cmd:
                xref_commands.append(cmd)
            if cmd == "aflj":
                return json.dumps(functions_data)
            return "[]" if cmd not in ["aa", "s main"] else None

        mock_r2.cmd.side_effect = cmd_side_effect

        analyze_with_r2("/path/to/binary")

        # Should only extract xrefs for MAX_XREF_FUNCTIONS
        # Each function gets 2 commands (axtj and axfj)
        assert len(xref_commands) == MAX_XREF_FUNCTIONS * 2

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_hex_address_format(self, mock_r2pipe):
        """Test that xref addresses are stored in hex format."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [
            {"name": "func", "offset": 4096},  # Decimal offset
        ]

        xrefs_to = [{"from": 0x100, "type": "CALL"}]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            json.dumps(xrefs_to),  # axtj @ 4096
            "[]",  # axfj @ 4096
        ]

        result = analyze_with_r2("/path/to/binary")

        # Verify address is stored as hex string
        assert "0x1000" in result["xrefs"]["to"]  # 4096 in decimal = 0x1000 in hex

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_with_missing_offset(self, mock_r2pipe):
        """Test that functions with missing offset are skipped in xref extraction."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [
            {"name": "valid", "offset": 0x1000},
            {"name": "no_offset"},  # Missing offset
            {"name": "valid2", "offset": 0x2000},
        ]

        mock_r2.cmd.side_effect = [
            None,  # aa
            json.dumps(functions_data),  # aflj
            "[]",  # isj
            "[]",  # izj
            None,  # s main
            "[]",  # pdj
            # Only 2 functions should have xrefs extracted
            "[]",  # axtj @ 0x1000
            "[]",  # axfj @ 0x1000
            "[]",  # axtj @ 0x2000
            "[]",  # axfj @ 0x2000
        ]

        result = analyze_with_r2("/path/to/binary")

        # Should complete successfully
        assert "xrefs" in result

        # Verify r2 commands - should only have xref commands for 2 functions
        xref_calls = [call for call in mock_r2.cmd.call_args_list if "axtj" in str(call) or "axfj" in str(call)]
        assert len(xref_calls) == 4  # 2 functions × 2 commands each

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_xref_logging(self, mock_r2pipe, caplog):
        """Test that xref extraction produces appropriate log messages."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        functions_data = [{"name": "func", "offset": 0x1000}]
        xrefs_to = [{"from": 0x100, "type": "CALL"}]

        mock_r2.cmd.side_effect = [
            None,
            json.dumps(functions_data),
            "[]",
            "[]",
            None,
            "[]",
            json.dumps(xrefs_to),
            "[]",
        ]

        with caplog.at_level(logging.DEBUG):
            analyze_with_r2("/path/to/binary")

        # Verify xref extraction is logged
        assert "Extracting cross-references for functions" in caplog.text
        assert "1 xrefs-to" in caplog.text
        assert "0 xrefs-from" in caplog.text

    @patch("caspoon.backends.r2_analyzer.r2pipe")
    def test_return_structure_includes_xrefs(self, mock_r2pipe):
        """Test that the return dictionary includes xrefs with correct structure."""
        mock_r2 = MagicMock()
        mock_r2pipe.open.return_value = mock_r2

        mock_r2.cmd.side_effect = [None, "[]", "[]", "[]", None, "[]"]

        result = analyze_with_r2("/path")

        # Verify xrefs key exists with correct structure
        assert "xrefs" in result
        assert isinstance(result["xrefs"], dict)
        assert "to" in result["xrefs"]
        assert "from" in result["xrefs"]
        assert isinstance(result["xrefs"]["to"], dict)
        assert isinstance(result["xrefs"]["from"], dict)

