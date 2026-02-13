"""Syntax highlighting for assembly code."""

from .highlighter import AsmHighlighter, InstructionType
from .schemes import ColorScheme, get_default_scheme

__all__ = [
    "AsmHighlighter",
    "InstructionType",
    "ColorScheme",
    "get_default_scheme",
]
