"""Syntax highlighting for assembly code."""

from .arch_detector import detect_architecture, get_architecture_display_name
from .arch_manager import (
    ArchitectureManager,
    get_instruction_classifier,
    get_supported_architectures,
    supports_architecture,
)
from .highlighter import AsmHighlighter
from .instructions import (
    X86_64_INSTRUCTIONS,
    get_instruction_type,
    is_fpu_instruction,
    is_simd_instruction,
    is_string_instruction,
    is_system_instruction,
)
from .operand_parser import OperandInfo, OperandParser, OperandType
from .schemes import ColorScheme, InstructionType, get_default_scheme

__all__ = [
    # Highlighter
    "AsmHighlighter",
    # Schemes and types
    "InstructionType",
    "ColorScheme",
    "get_default_scheme",
    # Operand parsing
    "OperandParser",
    "OperandType",
    "OperandInfo",
    # x86/x64 instructions
    "X86_64_INSTRUCTIONS",
    "get_instruction_type",
    "is_string_instruction",
    "is_system_instruction",
    "is_simd_instruction",
    "is_fpu_instruction",
    # Architecture detection and management
    "detect_architecture",
    "get_architecture_display_name",
    "ArchitectureManager",
    "get_instruction_classifier",
    "supports_architecture",
    "get_supported_architectures",
]
