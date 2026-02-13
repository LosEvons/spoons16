"""Syntax highlighting for assembly code."""

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
    "AsmHighlighter",
    "InstructionType",
    "ColorScheme",
    "get_default_scheme",
    "OperandParser",
    "OperandType",
    "OperandInfo",
    "X86_64_INSTRUCTIONS",
    "get_instruction_type",
    "is_string_instruction",
    "is_system_instruction",
    "is_simd_instruction",
    "is_fpu_instruction",
]
