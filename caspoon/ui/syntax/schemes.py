"""Color schemes for assembly syntax highlighting."""

from enum import Enum


class InstructionType(Enum):
    """Types of assembly instructions for syntax highlighting."""

    JUMP = "jump"
    CALL = "call"
    MOVE = "move"
    ARITHMETIC = "arithmetic"
    LOGIC = "logic"
    STACK = "stack"
    COMPARE = "compare"
    RETURN = "return"
    OTHER = "other"
