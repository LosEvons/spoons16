"""Unit tests for architecture detection functionality."""

from unittest.mock import Mock

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.ui.syntax.arch_detector import (
    detect_architecture,
    get_architecture_display_name,
    is_64bit_architecture,
    is_little_endian_architecture,
)


class TestArchitectureDetection:
    """Tests for architecture detection from ExecutableReport."""

    def test_detect_x86_64_architectures(self):
        """Test detection of x86-64 architecture variants."""
        # Standard x86-64 names
        report = Mock(spec=ExecutableReport)
        report.arch = "x86_64"
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "x86-64"
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "x64"
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "amd64"
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "x86-64-little"
        assert detect_architecture(report) == "x86_64"

    def test_detect_x86_architectures(self):
        """Test detection of x86 32-bit architecture variants."""
        report = Mock(spec=ExecutableReport)
        report.arch = "x86"
        assert detect_architecture(report) == "x86"
        
        report.arch = "i386"
        assert detect_architecture(report) == "x86"
        
        report.arch = "i486"
        assert detect_architecture(report) == "x86"
        
        report.arch = "i586"
        assert detect_architecture(report) == "x86"
        
        report.arch = "i686"
        assert detect_architecture(report) == "x86"
        
        report.arch = "x86-32"
        assert detect_architecture(report) == "x86"
        
        report.arch = "ia32"
        assert detect_architecture(report) == "x86"

    def test_detect_arm64_architectures(self):
        """Test detection of ARM64 architecture variants."""
        report = Mock(spec=ExecutableReport)
        report.arch = "aarch64"
        assert detect_architecture(report) == "arm64"
        
        report.arch = "arm64"
        assert detect_architecture(report) == "arm64"
        
        report.arch = "armv8"
        assert detect_architecture(report) == "arm64"
        
        report.arch = "arm64-little"
        assert detect_architecture(report) == "arm64"

    def test_detect_arm_architectures(self):
        """Test detection of ARM 32-bit architecture variants."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        assert detect_architecture(report) == "arm"
        
        report.arch = "armv7"
        assert detect_architecture(report) == "arm"
        
        report.arch = "armv6"
        assert detect_architecture(report) == "arm"
        
        report.arch = "armv5"
        assert detect_architecture(report) == "arm"
        
        report.arch = "arm-little"
        assert detect_architecture(report) == "arm"
        
        report.arch = "armhf"
        assert detect_architecture(report) == "arm"
        
        report.arch = "armel"
        assert detect_architecture(report) == "arm"

    def test_detect_mips64_architectures(self):
        """Test detection of MIPS64 architecture variants."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips64"
        assert detect_architecture(report) == "mips64"
        
        report.arch = "mips64el"
        assert detect_architecture(report) == "mips64"
        
        report.arch = "mips64-little"
        assert detect_architecture(report) == "mips64"
        
        report.arch = "mips64le"
        assert detect_architecture(report) == "mips64"

    def test_detect_mips_architectures(self):
        """Test detection of MIPS 32-bit architecture variants."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        assert detect_architecture(report) == "mips"
        
        report.arch = "mipsel"
        assert detect_architecture(report) == "mips"
        
        report.arch = "mips-little"
        assert detect_architecture(report) == "mips"
        
        report.arch = "mipsle"
        assert detect_architecture(report) == "mips"
        
        report.arch = "mips32"
        assert detect_architecture(report) == "mips"

    def test_detect_unknown_architecture(self):
        """Test detection returns unknown for unrecognized architectures."""
        report = Mock(spec=ExecutableReport)
        report.arch = "riscv64"
        assert detect_architecture(report) == "unknown"
        
        report.arch = "powerpc"
        assert detect_architecture(report) == "unknown"
        
        report.arch = "sparc"
        assert detect_architecture(report) == "unknown"
        
        report.arch = "completely_made_up_arch"
        assert detect_architecture(report) == "unknown"

    def test_detect_architecture_case_insensitive(self):
        """Test that architecture detection is case-insensitive."""
        report = Mock(spec=ExecutableReport)
        
        report.arch = "X86_64"
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "ARM64"
        assert detect_architecture(report) == "arm64"
        
        report.arch = "MIPS"
        assert detect_architecture(report) == "mips"
        
        report.arch = "AArch64"
        assert detect_architecture(report) == "arm64"

    def test_detect_architecture_with_whitespace(self):
        """Test architecture detection handles whitespace."""
        report = Mock(spec=ExecutableReport)
        
        report.arch = "  x86_64  "
        assert detect_architecture(report) == "x86_64"
        
        report.arch = "\tarm64\t"
        assert detect_architecture(report) == "arm64"
        
        report.arch = " mips "
        assert detect_architecture(report) == "mips"

    def test_detect_architecture_substring_fallback(self):
        """Test substring-based fallback detection."""
        report = Mock(spec=ExecutableReport)
        
        # Should detect x86 from substring
        report.arch = "some_x86_variant"
        assert detect_architecture(report) == "x86_64"  # Defaults to 64-bit
        
        # Should detect ARM from substring
        report.arch = "custom_arm_system"
        assert detect_architecture(report) == "arm"
        
        # Should detect ARM64 from substring with 64
        report.arch = "arm_system_64"
        assert detect_architecture(report) == "arm64"
        
        # Should detect MIPS from substring
        report.arch = "custom_mips_cpu"
        assert detect_architecture(report) == "mips"
        
        # Should detect MIPS64 from substring
        report.arch = "mips_system_64"
        assert detect_architecture(report) == "mips64"


class TestArchitectureDetectionEdgeCases:
    """Tests for architecture detection edge cases."""

    def test_detect_architecture_none_report(self):
        """Test detection with None report."""
        assert detect_architecture(None) == "unknown"

    def test_detect_architecture_empty_arch(self):
        """Test detection with empty arch field."""
        report = Mock(spec=ExecutableReport)
        report.arch = ""
        assert detect_architecture(report) == "unknown"

    def test_detect_architecture_none_arch(self):
        """Test detection with None arch field."""
        report = Mock(spec=ExecutableReport)
        report.arch = None
        assert detect_architecture(report) == "unknown"

    def test_detect_architecture_whitespace_only(self):
        """Test detection with whitespace-only arch field."""
        report = Mock(spec=ExecutableReport)
        report.arch = "   "
        assert detect_architecture(report) == "unknown"


class TestArchitectureDisplayName:
    """Tests for architecture display name functionality."""

    def test_get_display_name_x86_64(self):
        """Test display name for x86-64."""
        assert get_architecture_display_name("x86_64") == "x86-64 (64-bit)"

    def test_get_display_name_x86(self):
        """Test display name for x86."""
        assert get_architecture_display_name("x86") == "x86 (32-bit)"

    def test_get_display_name_arm64(self):
        """Test display name for ARM64."""
        assert get_architecture_display_name("arm64") == "ARM64 (AArch64)"

    def test_get_display_name_arm(self):
        """Test display name for ARM."""
        assert get_architecture_display_name("arm") == "ARM (32-bit)"

    def test_get_display_name_mips64(self):
        """Test display name for MIPS64."""
        assert get_architecture_display_name("mips64") == "MIPS64"

    def test_get_display_name_mips(self):
        """Test display name for MIPS."""
        assert get_architecture_display_name("mips") == "MIPS (32-bit)"

    def test_get_display_name_unknown(self):
        """Test display name for unknown architecture."""
        assert get_architecture_display_name("unknown") == "Unknown Architecture"

    def test_get_display_name_unrecognized(self):
        """Test display name for unrecognized architecture returns as-is."""
        assert get_architecture_display_name("riscv64") == "riscv64"
        assert get_architecture_display_name("powerpc") == "powerpc"


class TestArchitecture64BitCheck:
    """Tests for 64-bit architecture checking."""

    def test_is_64bit_x86_64(self):
        """Test x86-64 is recognized as 64-bit."""
        assert is_64bit_architecture("x86_64") is True

    def test_is_64bit_arm64(self):
        """Test ARM64 is recognized as 64-bit."""
        assert is_64bit_architecture("arm64") is True

    def test_is_64bit_mips64(self):
        """Test MIPS64 is recognized as 64-bit."""
        assert is_64bit_architecture("mips64") is True

    def test_is_not_64bit_x86(self):
        """Test x86 is recognized as not 64-bit."""
        assert is_64bit_architecture("x86") is False

    def test_is_not_64bit_arm(self):
        """Test ARM is recognized as not 64-bit."""
        assert is_64bit_architecture("arm") is False

    def test_is_not_64bit_mips(self):
        """Test MIPS is recognized as not 64-bit."""
        assert is_64bit_architecture("mips") is False

    def test_is_not_64bit_unknown(self):
        """Test unknown architecture is not recognized as 64-bit."""
        assert is_64bit_architecture("unknown") is False

    def test_is_not_64bit_unrecognized(self):
        """Test unrecognized architecture is not recognized as 64-bit."""
        assert is_64bit_architecture("riscv64") is False
        assert is_64bit_architecture("powerpc") is False


class TestArchitectureEndianness:
    """Tests for architecture endianness checking."""

    def test_is_little_endian_x86_64(self):
        """Test x86-64 is little-endian."""
        assert is_little_endian_architecture("x86_64") is True

    def test_is_little_endian_x86(self):
        """Test x86 is little-endian."""
        assert is_little_endian_architecture("x86") is True

    def test_is_little_endian_arm64(self):
        """Test ARM64 is typically little-endian."""
        # Note: This is a heuristic; ARM can be bi-endian
        assert is_little_endian_architecture("arm64") is True

    def test_is_little_endian_arm(self):
        """Test ARM is typically little-endian."""
        # Note: This is a heuristic; ARM can be bi-endian
        assert is_little_endian_architecture("arm") is True

    def test_is_little_endian_mips64(self):
        """Test MIPS64 default is little-endian."""
        # Note: This is a heuristic; MIPS can be bi-endian
        # Function assumes little-endian variant (mipsel)
        assert is_little_endian_architecture("mips64") is True

    def test_is_little_endian_mips(self):
        """Test MIPS default is little-endian."""
        # Note: This is a heuristic; MIPS can be bi-endian
        # Function assumes little-endian variant (mipsel)
        assert is_little_endian_architecture("mips") is True

    def test_is_little_endian_unknown(self):
        """Test unknown architecture defaults to False."""
        assert is_little_endian_architecture("unknown") is False

    def test_is_little_endian_unrecognized(self):
        """Test unrecognized architecture defaults to False."""
        assert is_little_endian_architecture("riscv64") is False
        assert is_little_endian_architecture("powerpc") is False


class TestArchitectureDetectionIntegration:
    """Integration tests for architecture detection with real ExecutableReport objects."""

    def test_detect_from_real_report_x86_64(self):
        """Test detection from a real ExecutableReport object for x86-64."""
        report = ExecutableReport(
            path="/bin/ls",
            arch="x86_64",
            bits=64,
            file_type="ELF 64-bit LSB executable"
        )
        assert detect_architecture(report) == "x86_64"
        assert is_64bit_architecture(detect_architecture(report)) is True
        assert is_little_endian_architecture(detect_architecture(report)) is True

    def test_detect_from_real_report_arm64(self):
        """Test detection from a real ExecutableReport object for ARM64."""
        report = ExecutableReport(
            path="/usr/bin/app",
            arch="aarch64",
            bits=64,
            file_type="ELF 64-bit LSB executable, ARM aarch64"
        )
        assert detect_architecture(report) == "arm64"
        assert is_64bit_architecture(detect_architecture(report)) is True

    def test_detect_from_real_report_mips(self):
        """Test detection from a real ExecutableReport object for MIPS."""
        report = ExecutableReport(
            path="/usr/bin/app",
            arch="mipsel",
            bits=32,
            file_type="ELF 32-bit LSB executable, MIPS"
        )
        assert detect_architecture(report) == "mips"
        assert is_64bit_architecture(detect_architecture(report)) is False

    def test_get_full_display_info(self):
        """Test getting full display information for an architecture."""
        report = ExecutableReport(
            path="/bin/test",
            arch="x86_64",
            bits=64
        )
        
        detected_arch = detect_architecture(report)
        display_name = get_architecture_display_name(detected_arch)
        is_64bit = is_64bit_architecture(detected_arch)
        is_little_endian = is_little_endian_architecture(detected_arch)
        
        assert detected_arch == "x86_64"
        assert display_name == "x86-64 (64-bit)"
        assert is_64bit is True
        assert is_little_endian is True
