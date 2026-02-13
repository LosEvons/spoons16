"""Color schemes for assembly syntax highlighting."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


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


@dataclass
class ColorScheme:
    """Color scheme for syntax highlighting.
    
    Maps instruction types to Rich style strings (color names or styles).
    """

    jump: str = "cyan"
    call: str = "bright_blue"
    move: str = "green"
    arithmetic: str = "yellow"
    logic: str = "magenta"
    stack: str = "bright_green"
    compare: str = "yellow"
    return_: str = "bright_cyan"  # Use return_ to avoid keyword conflict
    other: str = "white"
    address: str = "dim"
    
    def get_style(self, instr_type: InstructionType) -> str:
        """Get the style for a given instruction type.
        
        Args:
            instr_type: The instruction type to get the style for.
            
        Returns:
            The Rich style string for this instruction type.
        """
        mapping = {
            InstructionType.JUMP: self.jump,
            InstructionType.CALL: self.call,
            InstructionType.MOVE: self.move,
            InstructionType.ARITHMETIC: self.arithmetic,
            InstructionType.LOGIC: self.logic,
            InstructionType.STACK: self.stack,
            InstructionType.COMPARE: self.compare,
            InstructionType.RETURN: self.return_,
            InstructionType.OTHER: self.other,
        }
        return mapping.get(instr_type, self.other)


def get_default_scheme() -> ColorScheme:
    """Get the default color scheme.
    
    Returns:
        A ColorScheme with default colors optimized for readability.
    """
    return ColorScheme()
