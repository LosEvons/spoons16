"""Operand parser for assembly instruction operands.

This module parses and classifies assembly operands into different types
(registers, immediates, memory references, symbols) for syntax highlighting.
"""

import re
from dataclasses import dataclass
from enum import Enum


class OperandType(Enum):
    """Types of assembly operands."""

    REGISTER = "register"
    IMMEDIATE = "immediate"
    MEMORY = "memory"
    SYMBOL = "symbol"
    UNKNOWN = "unknown"


@dataclass
class OperandInfo:
    """Information about a parsed operand.
    
    Attributes:
        operand_type: The type of the operand.
        value: The original operand string.
        components: Dictionary of parsed components (for memory references, etc.).
    """

    operand_type: OperandType
    value: str
    components: dict[str, str] | None = None


class OperandParser:
    """Parser for assembly instruction operands.
    
    Parses operands into types (register, immediate, memory, symbol)
    and extracts components for detailed syntax highlighting.
    """

    def __init__(self):
        """Initialize the operand parser with register and pattern definitions."""
        # x86/x64 register sets
        self._general_registers_64 = {
            'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp',
            'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15',
        }

        self._general_registers_32 = {
            'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp',
            'r8d', 'r9d', 'r10d', 'r11d', 'r12d', 'r13d', 'r14d', 'r15d',
        }

        self._general_registers_16 = {
            'ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp',
            'r8w', 'r9w', 'r10w', 'r11w', 'r12w', 'r13w', 'r14w', 'r15w',
        }

        self._general_registers_8 = {
            'al', 'bl', 'cl', 'dl', 'ah', 'bh', 'ch', 'dh',
            'sil', 'dil', 'bpl', 'spl',
            'r8b', 'r9b', 'r10b', 'r11b', 'r12b', 'r13b', 'r14b', 'r15b',
        }

        # Segment registers
        self._segment_registers = {
            'cs', 'ds', 'es', 'fs', 'gs', 'ss',
        }

        # Control registers
        self._control_registers = {
            'cr0', 'cr1', 'cr2', 'cr3', 'cr4', 'cr8',
        }

        # Debug registers
        self._debug_registers = {
            'dr0', 'dr1', 'dr2', 'dr3', 'dr4', 'dr5', 'dr6', 'dr7',
        }

        # FPU registers
        self._fpu_registers = {
            'st0', 'st1', 'st2', 'st3', 'st4', 'st5', 'st6', 'st7',
            'st',  # ST(0)
        }

        # MMX registers
        self._mmx_registers = {
            'mm0', 'mm1', 'mm2', 'mm3', 'mm4', 'mm5', 'mm6', 'mm7',
        }

        # SSE/AVX registers (XMM, YMM, ZMM)
        self._sse_registers = set()
        for i in range(32):  # AVX-512 has 32 registers
            self._sse_registers.add(f'xmm{i}')
            self._sse_registers.add(f'ymm{i}')
            self._sse_registers.add(f'zmm{i}')

        # AVX-512 mask registers
        self._mask_registers = {f'k{i}' for i in range(8)}

        # Instruction pointer
        self._ip_registers = {'rip', 'eip', 'ip'}

        # All registers combined
        self._all_registers = (
            self._general_registers_64 |
            self._general_registers_32 |
            self._general_registers_16 |
            self._general_registers_8 |
            self._segment_registers |
            self._control_registers |
            self._debug_registers |
            self._fpu_registers |
            self._mmx_registers |
            self._sse_registers |
            self._mask_registers |
            self._ip_registers
        )

        # Patterns for different operand types
        # Memory reference pattern: [base + index*scale + displacement]
        # Also handles: [base], [base+offset], qword ptr [address], etc.
        self._memory_pattern = re.compile(
            r'''
            (?:(?P<size>byte|word|dword|qword|xmmword|ymmword|zmmword)\s+ptr\s+)?
            \[
            (?P<contents>[^\]]+)
            \]
            ''',
            re.VERBOSE | re.IGNORECASE
        )

        # Immediate value patterns
        self._hex_immediate = re.compile(r'^-?0x[0-9a-f]+$', re.IGNORECASE)
        self._dec_immediate = re.compile(r'^-?\d+$')
        self._bin_immediate = re.compile(r'^0b[01]+$', re.IGNORECASE)
        self._oct_immediate = re.compile(r'^0o[0-7]+$', re.IGNORECASE)

        # Symbol pattern (labels, function names)
        # Typically alphanumeric with underscores, may have @ or . prefix
        self._symbol_pattern = re.compile(r'^[@._]?[a-z_][a-z0-9_]*[@._]?[a-z0-9_]*$', re.IGNORECASE)

    def parse_operand(self, operand: str) -> OperandInfo:
        """Parse an operand and determine its type.
        
        Args:
            operand: The operand string to parse.
        
        Returns:
            OperandInfo containing the operand type and parsed components.
        """
        if not operand or not isinstance(operand, str):
            return OperandInfo(OperandType.UNKNOWN, operand or "", None)

        # Clean up the operand
        operand = operand.strip()

        if not operand:
            return OperandInfo(OperandType.UNKNOWN, "", None)

        # Check for memory reference first (contains [...])
        if '[' in operand:
            return self._parse_memory_operand(operand)

        # Check for register
        if self._is_register(operand):
            return OperandInfo(OperandType.REGISTER, operand, None)

        # Check for immediate value
        if self._is_immediate(operand):
            return OperandInfo(OperandType.IMMEDIATE, operand, None)

        # Check for symbol
        if self._is_symbol(operand):
            return OperandInfo(OperandType.SYMBOL, operand, None)

        # Default to unknown
        return OperandInfo(OperandType.UNKNOWN, operand, None)

    def _is_register(self, operand: str) -> bool:
        """Check if an operand is a register.
        
        Args:
            operand: The operand to check.
        
        Returns:
            True if the operand is a register.
        """
        return operand.lower() in self._all_registers

    def _is_immediate(self, operand: str) -> bool:
        """Check if an operand is an immediate value.
        
        Args:
            operand: The operand to check.
        
        Returns:
            True if the operand is an immediate value.
        """
        # Remove any $ prefix (AT&T syntax)
        if operand.startswith('$'):
            operand = operand[1:]

        return bool(
            self._hex_immediate.match(operand) or
            self._dec_immediate.match(operand) or
            self._bin_immediate.match(operand) or
            self._oct_immediate.match(operand)
        )

    def _is_symbol(self, operand: str) -> bool:
        """Check if an operand is a symbol (label/function name).
        
        Args:
            operand: The operand to check.
        
        Returns:
            True if the operand is likely a symbol.
        """
        return bool(self._symbol_pattern.match(operand))

    def _parse_memory_operand(self, operand: str) -> OperandInfo:
        """Parse a memory reference operand.
        
        Args:
            operand: The memory operand to parse (contains [...]).
        
        Returns:
            OperandInfo with MEMORY type and parsed components.
        """
        match = self._memory_pattern.search(operand)

        if not match:
            # Malformed memory reference, return as unknown
            return OperandInfo(OperandType.UNKNOWN, operand, None)

        components = {
            'size': match.group('size'),
            'contents': match.group('contents'),
        }

        # Try to parse the contents of the memory reference
        contents = match.group('contents')
        if contents:
            components['parsed_contents'] = self._parse_memory_contents(contents)

        return OperandInfo(OperandType.MEMORY, operand, components)

    def _parse_memory_contents(self, contents: str) -> dict[str, str]:
        """Parse the contents of a memory reference.
        
        Handles expressions like:
        - rax
        - rax+0x10
        - rax+rbx*4
        - rax+rbx*4+0x10
        - rip+0x2000
        
        Args:
            contents: The contents string inside the brackets.
        
        Returns:
            Dictionary of parsed components.
        """
        parsed = {
            'base': None,
            'index': None,
            'scale': None,
            'displacement': None,
        }

        # Simple parsing: split by + and -
        # This is a simplified parser and doesn't handle all edge cases
        contents = contents.strip()

        # Look for registers, immediates, and scale factors
        tokens = re.split(r'([+\-])', contents)

        current_sign = '+'
        for token in tokens:
            token = token.strip()

            if not token:
                continue

            if token in ('+', '-'):
                current_sign = token
                continue

            # Check if it's a scaled index (e.g., rbx*4)
            if '*' in token:
                parts = token.split('*')
                if len(parts) == 2:
                    reg, scale = parts
                    if self._is_register(reg.strip()):
                        parsed['index'] = reg.strip()
                        parsed['scale'] = scale.strip()
                continue

            # Check if it's a register
            if self._is_register(token):
                if parsed['base'] is None:
                    parsed['base'] = token
                elif parsed['index'] is None:
                    parsed['index'] = token
                continue

            # Check if it's an immediate (displacement)
            if self._is_immediate(token):
                if current_sign == '-':
                    token = '-' + token
                parsed['displacement'] = token
                continue

        return parsed

    def parse_operands(self, operands_str: str) -> list[OperandInfo]:
        """Parse a comma-separated list of operands.
        
        Args:
            operands_str: String containing comma-separated operands.
        
        Returns:
            List of OperandInfo for each operand.
        """
        if not operands_str or not operands_str.strip():
            return []

        # Split by comma, but be careful with nested brackets
        operands = []
        current = []
        bracket_depth = 0

        for char in operands_str:
            if char == '[':
                bracket_depth += 1
                current.append(char)
            elif char == ']':
                bracket_depth -= 1
                current.append(char)
            elif char == ',' and bracket_depth == 0:
                operands.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        # Add the last operand
        if current:
            operands.append(''.join(current).strip())

        return [self.parse_operand(op) for op in operands]

    def is_register(self, operand: str) -> bool:
        """Public method to check if an operand is a register.
        
        Args:
            operand: The operand to check.
        
        Returns:
            True if the operand is a register.
        """
        return self._is_register(operand)

    def get_register_size(self, register: str) -> int | None:
        """Get the size of a register in bits.
        
        Args:
            register: The register name.
        
        Returns:
            Size in bits (8, 16, 32, 64) or None if not a register.
        """
        reg_lower = register.lower()

        if reg_lower in self._general_registers_64 or reg_lower in self._ip_registers:
            return 64
        elif reg_lower in self._general_registers_32:
            return 32
        elif reg_lower in self._general_registers_16 or reg_lower in self._segment_registers:
            return 16
        elif reg_lower in self._general_registers_8:
            return 8

        # SIMD registers
        if reg_lower.startswith('zmm'):
            return 512
        elif reg_lower.startswith('ymm'):
            return 256
        elif reg_lower.startswith('xmm') or reg_lower.startswith('mm'):
            return 128

        return None
