"""Unit tests for core data models."""
import pytest
from caspoon.core.models import (
    ExecutableReport,
    ProtectionInfo,
    FunctionInfo,
)


class TestProtectionInfo:
    """Test ProtectionInfo dataclass."""

    def test_default_protections(self):
        """Test default protection values."""
        pi = ProtectionInfo()
        
        assert pi.pie is False
        assert pi.nx is False
        assert pi.canary is False
        assert pi.relro == "Unknown"

    def test_full_protections(self):
        """Test fully protected binary."""
        pi = ProtectionInfo(
            pie=True,
            nx=True,
            canary=True,
            relro="full"
        )
        
        assert pi.pie is True
        assert pi.nx is True
        assert pi.canary is True
        assert pi.relro == "full"

    def test_partial_relro(self):
        """Test partial RELRO."""
        pi = ProtectionInfo(relro="partial")
        assert pi.relro == "partial"


class TestFunctionInfo:
    """Test FunctionInfo dataclass."""

    def test_create_function(self):
        """Test creating function info."""
        func = FunctionInfo(name="main", address=0x400000)
        
        assert func.name == "main"
        assert func.address == 0x400000
        assert func.imported is False

    def test_imported_function(self):
        """Test imported function flag."""
        func = FunctionInfo(
            name="printf",
            address=0x0,
            imported=True
        )
        
        assert func.imported is True


class TestExecutableReport:
    """Test ExecutableReport dataclass."""

    def test_create_empty_report(self):
        """Test creating empty report."""
        report = ExecutableReport(path="/test/binary")
        
        assert report.path == "/test/binary"
        assert report.arch == ""
        assert report.bits is None
        assert report.file_type == ""
        assert report.stripped is False
        assert report.protections is None
        assert len(report.strings) == 0
        assert len(report.imports) == 0
        assert len(report.exports) == 0
        assert len(report.raw_backend_data) == 0

    def test_create_full_report(self):
        """Test creating report with all fields."""
        protections = ProtectionInfo(
            pie=True,
            nx=True,
            canary=True,
            relro="full"
        )
        
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
            raw_backend_data={"test": "data"}
        )
        
        assert report.arch == "x86-64"
        assert report.bits == 64
        assert report.file_type == "ELF 64-bit LSB executable"
        assert report.stripped is False
        assert report.protections.pie is True
        assert len(report.strings) == 2
        assert "hello" in report.strings
        assert len(report.imports) == 2
        assert "printf" in report.imports
        assert len(report.exports) == 1
        assert "main" in report.exports

    def test_pretty_output(self):
        """Test pretty() method returns dict."""
        protections = ProtectionInfo(pie=True)
        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            protections=protections,
            strings=["test"]
        )
        
        pretty = report.pretty()
        
        assert isinstance(pretty, dict)
        assert pretty["path"] == "/test/binary"
        assert pretty["arch"] == "x86-64"
        assert pretty["bits"] == 64
        assert "protections" in pretty
        assert pretty["strings_count"] == 1

    def test_pretty_unknown_bits(self):
        """Test pretty() with None bits."""
        report = ExecutableReport(path="/test")
        pretty = report.pretty()
        
        assert pretty["bits"] == "unknown"
