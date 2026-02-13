"""Unit tests for core data models.

Tests the core dataclasses and models used throughout the analysis pipeline,
including ExecutableReport, ProtectionInfo, and FunctionInfo.
"""

import pytest

from caspoon.core.models import (
    ExecutableReport,
    FunctionInfo,
    ProtectionInfo,
)


class TestProtectionInfo:
    """Test ProtectionInfo dataclass."""

    def test_default_protections(self) -> None:
        """Test default protection values are all disabled/unknown."""
        pi = ProtectionInfo()

        assert pi.pie is False, "PIE should default to False"
        assert pi.nx is False, "NX should default to False"
        assert pi.canary is False, "Canary should default to False"
        assert pi.relro == "Unknown", "RELRO should default to 'Unknown'"

    def test_full_protections(self) -> None:
        """Test fully protected binary with all mitigations enabled."""
        pi = ProtectionInfo(pie=True, nx=True, canary=True, relro="full")

        assert pi.pie is True, "PIE should be enabled"
        assert pi.nx is True, "NX should be enabled"
        assert pi.canary is True, "Canary should be enabled"
        assert pi.relro == "full", "RELRO should be full"

    def test_partial_relro(self) -> None:
        """Test partial RELRO configuration."""
        pi = ProtectionInfo(relro="partial")
        assert pi.relro == "partial", "RELRO should be partial"


class TestFunctionInfo:
    """Test FunctionInfo dataclass."""

    def test_create_function(self) -> None:
        """Test creating function info with basic fields."""
        func = FunctionInfo(name="main", address=0x400000)

        assert func.name == "main", "Function name should match"
        assert func.address == 0x400000, "Function address should match"
        assert func.imported is False, "Function should not be imported by default"

    def test_imported_function(self) -> None:
        """Test imported function flag is properly set."""
        func = FunctionInfo(name="printf", address=0x0, imported=True)

        assert func.imported is True, "Function should be marked as imported"


class TestExecutableReport:
    """Test ExecutableReport dataclass."""

    def test_create_empty_report(self) -> None:
        """Test creating empty report with only path specified."""
        report = ExecutableReport(path="/test/binary")

        assert report.path == "/test/binary", "Path should match"
        assert report.arch == "", "Architecture should be empty by default"
        assert report.bits is None, "Bits should be None by default"
        assert report.file_type == "", "File type should be empty by default"
        assert report.stripped is False, "Stripped should be False by default"
        assert report.protections is None, "Protections should be None by default"
        assert len(report.strings) == 0, "Strings list should be empty"
        assert len(report.imports) == 0, "Imports list should be empty"
        assert len(report.exports) == 0, "Exports list should be empty"
        assert len(report.raw_backend_data) == 0, "Raw backend data should be empty"

    def test_create_full_report(self) -> None:
        """Test creating report with all fields populated."""
        protections = ProtectionInfo(pie=True, nx=True, canary=True, relro="full")

        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            file_type="ELF 64-bit LSB executable",
            stripped=False,
            protections=protections,
            strings=["hello", "world"],
            imports=["printf", "exit"],
            exports=["main"],
            raw_backend_data={"test": "data"},
        )

        assert report.arch == "x86-64", "Architecture should match"
        assert report.bits == 64, "Bit width should be 64"
        assert report.file_type == "ELF 64-bit LSB executable", "File type should match"
        assert report.stripped is False, "Binary should not be stripped"
        assert report.protections is not None, "Protections should be set"
        assert report.protections.pie is True, "PIE should be enabled"
        assert len(report.strings) == 2, "Should have 2 strings"
        assert "hello" in report.strings, "'hello' should be in strings"
        assert len(report.imports) == 2, "Should have 2 imports"
        assert "printf" in report.imports, "'printf' should be in imports"
        assert len(report.exports) == 1, "Should have 1 export"
        assert "main" in report.exports, "'main' should be in exports"

    def test_pretty_output(self) -> None:
        """Test pretty() method returns properly formatted dict."""
        protections = ProtectionInfo(pie=True)
        report = ExecutableReport(
            path="/test/binary", arch="x86-64", bits=64, protections=protections, strings=["test"]
        )

        pretty = report.pretty()

        assert isinstance(pretty, dict), "pretty() should return a dictionary"
        assert pretty["path"] == "/test/binary", "Path should be in output"
        assert pretty["arch"] == "x86-64", "Architecture should be in output"
        assert pretty["bits"] == 64, "Bit width should be in output"
        assert "protections" in pretty, "Protections should be in output"
        assert pretty["strings_count"] == 1, "String count should match"

    def test_pretty_unknown_bits(self) -> None:
        """Test pretty() with None bits shows 'unknown'."""
        report = ExecutableReport(path="/test")
        pretty = report.pretty()

        assert pretty["bits"] == "unknown", "None bits should show as 'unknown'"
