"""Assembly syntax highlighting and instruction classification."""

from .instructions import get_instruction_type
from .schemes import InstructionType

__all__ = ["get_instruction_type", "InstructionType"]
