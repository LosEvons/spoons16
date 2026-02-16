"""Architecture detection for binary analysis reports.

This module provides functionality to detect and normalize architecture
information from ExecutableReport objects.
"""

from caspoon.core.models import ExecutableReport

# Architecture normalization mappings
_X86_64_VARIANTS = frozenset(['x86_64', 'x86-64', 'x64', 'amd64', 'x86-64-little'])
_X86_VARIANTS = frozenset(['x86', 'i386', 'i486', 'i586', 'i686', 'x86-32', 'ia32'])
_ARM64_VARIANTS = frozenset(['aarch64', 'arm64', 'armv8', 'arm64-little'])
_ARM_VARIANTS = frozenset(['arm', 'armv7', 'armv6', 'armv5', 'arm-little', 'armhf', 'armel'])
_MIPS64_VARIANTS = frozenset(['mips64', 'mips64el', 'mips64-little', 'mips64le'])
_MIPS_VARIANTS = frozenset(['mips', 'mipsel', 'mips-little', 'mipsle', 'mips32'])


def detect_architecture(report: ExecutableReport) -> str:
    """Detect and normalize the architecture from an ExecutableReport.

    Maps various architecture strings to normalized values for
    consistent architecture-specific processing.

    Args:
        report: The ExecutableReport to detect architecture from.

    Returns:
        Normalized architecture string: 'x86_64', 'x86', 'arm', 'arm64',
        'mips', 'mips64', or 'unknown'.
    """
    if not report or not report.arch:
        return 'unknown'

    arch = report.arch.lower().strip()

    # Check exact matches first
    if arch in _X86_64_VARIANTS:
        return 'x86_64'
    if arch in _X86_VARIANTS:
        return 'x86'
    if arch in _ARM64_VARIANTS:
        return 'arm64'
    if arch in _ARM_VARIANTS:
        return 'arm'
    if arch in _MIPS64_VARIANTS:
        return 'mips64'
    if arch in _MIPS_VARIANTS:
        return 'mips'

    # Fallback: check for common substrings
    if 'x86' in arch or 'amd64' in arch:
        return 'x86_64'  # Assume 64-bit if we're not sure

    if 'arm' in arch:
        return 'arm64' if ('64' in arch or 'aarch64' in arch) else 'arm'

    if 'mips' in arch:
        return 'mips64' if '64' in arch else 'mips'

    return 'unknown'


def get_architecture_display_name(arch: str) -> str:
    """Get a human-readable display name for an architecture.

    Args:
        arch: The normalized architecture string.

    Returns:
        Human-readable architecture name.
    """
    display_names = {
        'x86_64': 'x86-64 (64-bit)',
        'x86': 'x86 (32-bit)',
        'arm64': 'ARM64 (AArch64)',
        'arm': 'ARM (32-bit)',
        'mips64': 'MIPS64',
        'mips': 'MIPS (32-bit)',
        'unknown': 'Unknown Architecture',
    }

    return display_names.get(arch, arch)


def is_64bit_architecture(arch: str) -> bool:
    """Check if an architecture is 64-bit.

    Args:
        arch: The normalized architecture string.

    Returns:
        True if the architecture is 64-bit, False otherwise.
    """
    return arch in ('x86_64', 'arm64', 'mips64')


def is_little_endian_architecture(arch: str) -> bool:
    """Check if an architecture is typically little-endian.

    Note: This is a heuristic based on common configurations.
    Actual endianness may vary depending on the specific system.

    Args:
        arch: The normalized architecture string.

    Returns:
        True if the architecture is typically little-endian.
    """
    # x86/x64 are always little-endian
    if arch in ('x86', 'x86_64'):
        return True

    # ARM can be either, but most modern systems use little-endian
    # This is a simplification; actual endianness should be checked elsewhere
    if arch in ('arm', 'arm64'):
        return True  # Common case

    # MIPS can be either (mipsel/mipseb)
    # This returns True as a default; actual endianness should be checked
    if arch in ('mips', 'mips64'):
        return True  # Assuming little-endian variant

    return False  # Unknown, default to False
