"""Architecture-specific instruction classifier manager.

This module provides a centralized way to get the appropriate instruction
classifier for different architectures.
"""

from typing import Callable

from . import instructions, instructions_arm, instructions_mips
from .schemes import InstructionType


class ArchitectureManager:
    """Manages architecture-specific instruction classifiers.

    This class provides a unified interface to get instruction classifiers
    for different architectures (x86/x64, ARM, MIPS, etc.).
    """

    def __init__(self):
        """Initialize the architecture manager."""
        # Map architecture names to their instruction classifier functions
        self._classifiers = {
            'x86': instructions.get_instruction_type,
            'x86_64': instructions.get_instruction_type,
            'arm': instructions_arm.get_instruction_type,
            'arm64': instructions_arm.get_instruction_type,
            'mips': instructions_mips.get_instruction_type,
            'mips64': instructions_mips.get_instruction_type,
        }

    def get_instruction_classifier(self, arch: str) -> Callable[[str], InstructionType]:
        """Get the instruction classifier function for a specific architecture.

        Args:
            arch: The normalized architecture string (e.g., 'x86_64', 'arm', 'mips').

        Returns:
            A function that takes a mnemonic string and returns an InstructionType.
            Defaults to x86_64 classifier for unknown architectures.
        """
        # Normalize architecture string
        arch_lower = arch.lower().strip()

        # Get the classifier, defaulting to x86_64 for unknown architectures
        classifier = self._classifiers.get(arch_lower, instructions.get_instruction_type)

        return classifier

    def supports_architecture(self, arch: str) -> bool:
        """Check if an architecture is supported.

        Args:
            arch: The architecture string to check.

        Returns:
            True if the architecture has a specific classifier, False otherwise.
        """
        arch_lower = arch.lower().strip()
        return arch_lower in self._classifiers

    def get_supported_architectures(self) -> list[str]:
        """Get a list of all supported architectures.

        Returns:
            List of supported architecture strings.
        """
        return list(self._classifiers.keys())


# Global singleton instance for convenience
_architecture_manager = ArchitectureManager()


def get_instruction_classifier(arch: str) -> Callable[[str], InstructionType]:
    """Get the instruction classifier function for a specific architecture.

    This is a convenience function that uses the global ArchitectureManager instance.

    Args:
        arch: The normalized architecture string (e.g., 'x86_64', 'arm', 'mips').

    Returns:
        A function that takes a mnemonic string and returns an InstructionType.
        Defaults to x86_64 classifier for unknown architectures.
    """
    return _architecture_manager.get_instruction_classifier(arch)


def supports_architecture(arch: str) -> bool:
    """Check if an architecture is supported.

    This is a convenience function that uses the global ArchitectureManager instance.

    Args:
        arch: The architecture string to check.

    Returns:
        True if the architecture has a specific classifier, False otherwise.
    """
    return _architecture_manager.supports_architecture(arch)


def get_supported_architectures() -> list[str]:
    """Get a list of all supported architectures.

    This is a convenience function that uses the global ArchitectureManager instance.

    Returns:
        List of supported architecture strings.
    """
    return _architecture_manager.get_supported_architectures()
