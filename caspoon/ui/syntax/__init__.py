"""Syntax highlighting for assembly code."""

from .highlighter import AsmHighlighter
from .schemes import ColorScheme, InstructionType, get_default_scheme

__all__ = [
    "AsmHighlighter",
    "InstructionType",
    "ColorScheme",
    "get_default_scheme",
]
