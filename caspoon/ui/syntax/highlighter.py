"""Assembly instruction syntax highlighter."""


from rich.text import Text

from .schemes import ColorScheme, InstructionType, get_default_scheme


class AsmHighlighter:
    """Syntax highlighter for assembly code.

    Classifies instructions by type and applies color highlighting
    using Rich's Text API.
    """

    def __init__(self, color_scheme: ColorScheme | None = None):
        """Initialize the highlighter.

        Args:
            color_scheme: Optional color scheme. If None, uses the default scheme.
        """
        self.scheme = color_scheme or get_default_scheme()

        # Instruction classification mappings for x86/x64
        self._jump_instructions = {
            'jmp', 'je', 'jne', 'jz', 'jnz', 'jg', 'jge', 'jl', 'jle',
            'ja', 'jae', 'jb', 'jbe', 'jo', 'jno', 'js', 'jns',
            'jp', 'jnp', 'jc', 'jnc', 'jecxz', 'jrcxz',
        }

        self._call_instructions = {
            'call', 'callq',
        }

        self._move_instructions = {
            'mov', 'movq', 'movl', 'movw', 'movb',
            'movzx', 'movzb', 'movzw', 'movzl', 'movzq',
            'movsx', 'movsb', 'movsw', 'movsl', 'movsq',
            'lea', 'leaq', 'leal',
            'xchg', 'xchgq', 'xchgl',
        }

        self._arithmetic_instructions = {
            'add', 'addq', 'addl', 'addw', 'addb',
            'sub', 'subq', 'subl', 'subw', 'subb',
            'mul', 'mulq', 'mull', 'mulw', 'mulb',
            'imul', 'imulq', 'imull',
            'div', 'divq', 'divl', 'divw', 'divb',
            'idiv', 'idivq', 'idivl',
            'inc', 'incq', 'incl', 'incw', 'incb',
            'dec', 'decq', 'decl', 'decw', 'decb',
            'neg', 'negq', 'negl',
            'adc', 'adcq', 'adcl',
            'sbb', 'sbbq', 'sbbl',
        }

        self._logic_instructions = {
            'and', 'andq', 'andl', 'andw', 'andb',
            'or', 'orq', 'orl', 'orw', 'orb',
            'xor', 'xorq', 'xorl', 'xorw', 'xorb',
            'not', 'notq', 'notl',
            'shl', 'shlq', 'shll', 'sal', 'salq', 'sall',
            'shr', 'shrq', 'shrl', 'sar', 'sarq', 'sarl',
            'rol', 'rolq', 'roll',
            'ror', 'rorq', 'rorl',
            'rcl', 'rclq', 'rcll',
            'rcr', 'rcrq', 'rcrl',
        }

        self._stack_instructions = {
            'push', 'pushq', 'pushl', 'pushw', 'pushb',
            'pop', 'popq', 'popl', 'popw', 'popb',
            'pusha', 'pushad', 'popa', 'popad',
            'pushf', 'pushfq', 'popf', 'popfq',
        }

        self._compare_instructions = {
            'cmp', 'cmpq', 'cmpl', 'cmpw', 'cmpb',
            'test', 'testq', 'testl', 'testw', 'testb',
        }

        self._return_instructions = {
            'ret', 'retq', 'retn', 'retf',
        }

    def classify_instruction(self, opcode: str) -> InstructionType:
        """Classify an instruction by its opcode.

        Args:
            opcode: The instruction opcode (may include operands).

        Returns:
            The instruction type classification.
        """
        if not opcode or not isinstance(opcode, str):
            return InstructionType.OTHER

        # Extract the base opcode (first token, lowercase)
        opcode_lower = opcode.strip().lower().split()[0] if opcode.strip() else ""

        if not opcode_lower:
            return InstructionType.OTHER

        # Check each instruction category
        if opcode_lower in self._jump_instructions:
            return InstructionType.JUMP
        elif opcode_lower in self._call_instructions:
            return InstructionType.CALL
        elif opcode_lower in self._move_instructions:
            return InstructionType.MOVE
        elif opcode_lower in self._arithmetic_instructions:
            return InstructionType.ARITHMETIC
        elif opcode_lower in self._logic_instructions:
            return InstructionType.LOGIC
        elif opcode_lower in self._stack_instructions:
            return InstructionType.STACK
        elif opcode_lower in self._compare_instructions:
            return InstructionType.COMPARE
        elif opcode_lower in self._return_instructions:
            return InstructionType.RETURN
        else:
            return InstructionType.OTHER

    def highlight_instruction(self, opcode: str, address: str = "") -> Text:
        """Create a highlighted Text object for an assembly instruction.

        Args:
            opcode: The instruction opcode and operands.
            address: Optional address/offset to prepend.

        Returns:
            A Rich Text object with syntax highlighting applied.
        """
        try:
            # Classify the instruction
            instr_type = self.classify_instruction(opcode)

            # Get the appropriate color
            color = self.scheme.get_style(instr_type)

            # Build the highlighted text
            text = Text()

            # Add address if provided
            if address:
                text.append(f"{address}: ", style=self.scheme.address)

            # Add the instruction with appropriate color
            text.append(opcode, style=color)

            return text

        except Exception:
            # Graceful fallback: return plain text if highlighting fails
            text = Text()
            if address:
                text.append(f"{address}: ")
            text.append(opcode)
            return text
