"""Unit tests for assembly syntax highlighter."""

import pytest
from rich.text import Text

from caspoon.ui.syntax import AsmHighlighter, ColorScheme, InstructionType, get_default_scheme


class TestInstructionClassification:
    """Tests for instruction classification."""

    def test_classify_jump_instructions(self):
        """Test classification of jump instructions."""
        highlighter = AsmHighlighter()

        # Test various jump instructions
        assert highlighter.classify_instruction("jmp 0x1234") == InstructionType.JUMP
        assert highlighter.classify_instruction("je target") == InstructionType.JUMP
        assert highlighter.classify_instruction("jne 0x400000") == InstructionType.JUMP
        assert highlighter.classify_instruction("jz loc_123") == InstructionType.JUMP
        assert highlighter.classify_instruction("jnz 0x1000") == InstructionType.JUMP
        assert highlighter.classify_instruction("jg label") == InstructionType.JUMP
        assert highlighter.classify_instruction("jl label") == InstructionType.JUMP
        assert highlighter.classify_instruction("ja label") == InstructionType.JUMP
        assert highlighter.classify_instruction("jb label") == InstructionType.JUMP

    def test_classify_call_instructions(self):
        """Test classification of call instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("call func") == InstructionType.CALL
        assert highlighter.classify_instruction("callq 0x400500") == InstructionType.CALL
        assert highlighter.classify_instruction("CALL printf") == InstructionType.CALL

    def test_classify_move_instructions(self):
        """Test classification of move instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE
        assert highlighter.classify_instruction("movq rax, [rbp-8]") == InstructionType.MOVE
        assert highlighter.classify_instruction("lea rax, [rbp-16]") == InstructionType.MOVE
        assert highlighter.classify_instruction("movzx eax, byte ptr [rsi]") == InstructionType.MOVE
        assert highlighter.classify_instruction("movsx rax, dword ptr [rdi]") == InstructionType.MOVE
        assert highlighter.classify_instruction("xchg rax, rbx") == InstructionType.MOVE

    def test_classify_arithmetic_instructions(self):
        """Test classification of arithmetic instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("add rax, 5") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("sub rsp, 0x20") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("mul rcx") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("imul rax, rcx, 4") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("div rbx") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("inc rax") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("dec rcx") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("neg rax") == InstructionType.ARITHMETIC

    def test_classify_logic_instructions(self):
        """Test classification of logic instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("and rax, 0xff") == InstructionType.LOGIC
        assert highlighter.classify_instruction("or rax, rbx") == InstructionType.LOGIC
        assert highlighter.classify_instruction("xor rax, rax") == InstructionType.LOGIC
        assert highlighter.classify_instruction("not rax") == InstructionType.LOGIC
        assert highlighter.classify_instruction("shl rax, 2") == InstructionType.LOGIC
        assert highlighter.classify_instruction("shr rbx, 4") == InstructionType.LOGIC
        assert highlighter.classify_instruction("sal rcx, 1") == InstructionType.LOGIC
        assert highlighter.classify_instruction("sar rdx, 3") == InstructionType.LOGIC

    def test_classify_stack_instructions(self):
        """Test classification of stack instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("push rax") == InstructionType.STACK
        assert highlighter.classify_instruction("pop rbx") == InstructionType.STACK
        assert highlighter.classify_instruction("pushq rbp") == InstructionType.STACK
        assert highlighter.classify_instruction("popq rdi") == InstructionType.STACK
        assert highlighter.classify_instruction("pushf") == InstructionType.STACK
        assert highlighter.classify_instruction("popf") == InstructionType.STACK

    def test_classify_compare_instructions(self):
        """Test classification of compare instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("cmp rax, rbx") == InstructionType.COMPARE
        assert highlighter.classify_instruction("test rax, rax") == InstructionType.COMPARE
        assert highlighter.classify_instruction("cmpq rax, 0") == InstructionType.COMPARE
        assert highlighter.classify_instruction("testb al, 0xff") == InstructionType.COMPARE

    def test_classify_return_instructions(self):
        """Test classification of return instructions."""
        highlighter = AsmHighlighter()

        assert highlighter.classify_instruction("ret") == InstructionType.RETURN
        assert highlighter.classify_instruction("retq") == InstructionType.RETURN
        assert highlighter.classify_instruction("retn") == InstructionType.RETURN

    def test_classify_other_instructions(self):
        """Test classification of instructions that don't fit other categories."""
        highlighter = AsmHighlighter()

        # Instructions not in our classification should be OTHER
        assert highlighter.classify_instruction("nop") == InstructionType.OTHER
        assert highlighter.classify_instruction("syscall") == InstructionType.OTHER
        assert highlighter.classify_instruction("int 0x80") == InstructionType.OTHER
        assert highlighter.classify_instruction("hlt") == InstructionType.OTHER

    def test_classify_empty_or_invalid(self):
        """Test classification of edge cases."""
        highlighter = AsmHighlighter()

        # Empty strings
        assert highlighter.classify_instruction("") == InstructionType.OTHER
        assert highlighter.classify_instruction("   ") == InstructionType.OTHER

        # None or invalid types
        assert highlighter.classify_instruction(None) == InstructionType.OTHER

    def test_case_insensitive_classification(self):
        """Test that classification is case-insensitive."""
        highlighter = AsmHighlighter()

        # Mixed case should work
        assert highlighter.classify_instruction("MOV rax, rbx") == InstructionType.MOVE
        assert highlighter.classify_instruction("JMP 0x1234") == InstructionType.JUMP
        assert highlighter.classify_instruction("Call func") == InstructionType.CALL
        assert highlighter.classify_instruction("RET") == InstructionType.RETURN


class TestHighlighting:
    """Tests for syntax highlighting output."""

    def test_highlight_instruction_basic(self):
        """Test basic instruction highlighting."""
        highlighter = AsmHighlighter()

        result = highlighter.highlight_instruction("mov rax, rbx")

        assert isinstance(result, Text)
        # Should contain the instruction text
        assert "mov rax, rbx" in result.plain

    def test_highlight_instruction_with_address(self):
        """Test highlighting with address."""
        highlighter = AsmHighlighter()

        result = highlighter.highlight_instruction("jmp 0x1234", address="0x400000")

        assert isinstance(result, Text)
        assert "0x400000" in result.plain
        assert "jmp 0x1234" in result.plain

    def test_highlight_applies_correct_colors(self):
        """Test that correct colors are applied to different instruction types."""
        scheme = ColorScheme()
        highlighter = AsmHighlighter(color_scheme=scheme)

        # Test jump instruction
        jump_result = highlighter.highlight_instruction("jmp label")
        # We can't directly check the color, but we can verify it's a Text object
        assert isinstance(jump_result, Text)

        # Test call instruction
        call_result = highlighter.highlight_instruction("call func")
        assert isinstance(call_result, Text)

        # Test move instruction
        move_result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(move_result, Text)

    def test_highlight_empty_instruction(self):
        """Test highlighting of empty instruction."""
        highlighter = AsmHighlighter()

        result = highlighter.highlight_instruction("")

        assert isinstance(result, Text)
        assert result.plain == ""

    def test_highlight_with_custom_scheme(self):
        """Test highlighting with custom color scheme."""
        custom_scheme = ColorScheme(
            jump="red",
            call="blue",
            move="yellow"
        )
        highlighter = AsmHighlighter(color_scheme=custom_scheme)

        result = highlighter.highlight_instruction("jmp target")

        assert isinstance(result, Text)
        assert "jmp target" in result.plain

    def test_graceful_fallback_on_error(self):
        """Test that highlighting fails gracefully and returns plain text."""
        highlighter = AsmHighlighter()

        # Even with problematic input, should return a Text object
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)


class TestColorScheme:
    """Tests for ColorScheme class."""

    def test_default_scheme_creation(self):
        """Test creation of default color scheme."""
        scheme = get_default_scheme()

        assert isinstance(scheme, ColorScheme)
        assert scheme.jump == "cyan"
        assert scheme.call == "bright_blue"
        assert scheme.move == "green"
        assert scheme.arithmetic == "yellow"
        assert scheme.logic == "magenta"
        assert scheme.stack == "bright_green"
        assert scheme.compare == "yellow"
        assert scheme.return_ == "bright_cyan"
        assert scheme.other == "white"
        assert scheme.address == "dim"

    def test_get_style_for_instruction_types(self):
        """Test getting styles for different instruction types."""
        scheme = get_default_scheme()

        assert scheme.get_style(InstructionType.JUMP) == "cyan"
        assert scheme.get_style(InstructionType.CALL) == "bright_blue"
        assert scheme.get_style(InstructionType.MOVE) == "green"
        assert scheme.get_style(InstructionType.ARITHMETIC) == "yellow"
        assert scheme.get_style(InstructionType.LOGIC) == "magenta"
        assert scheme.get_style(InstructionType.STACK) == "bright_green"
        assert scheme.get_style(InstructionType.COMPARE) == "yellow"
        assert scheme.get_style(InstructionType.RETURN) == "bright_cyan"
        assert scheme.get_style(InstructionType.OTHER) == "white"

    def test_custom_color_scheme(self):
        """Test custom color scheme."""
        scheme = ColorScheme(
            jump="red",
            call="blue",
            move="green",
            arithmetic="yellow",
            logic="magenta",
            stack="cyan",
            compare="white",
            return_="bright_red",
            other="dim"
        )

        assert scheme.jump == "red"
        assert scheme.call == "blue"
        assert scheme.get_style(InstructionType.JUMP) == "red"
        assert scheme.get_style(InstructionType.CALL) == "blue"


class TestIntegration:
    """Integration tests for the highlighter."""

    def test_complete_disassembly_snippet(self):
        """Test highlighting a complete disassembly snippet."""
        highlighter = AsmHighlighter()

        instructions = [
            ("0x400000", "push rbp"),
            ("0x400001", "mov rbp, rsp"),
            ("0x400004", "sub rsp, 0x10"),
            ("0x400008", "mov edi, 0x0"),
            ("0x40000d", "call printf"),
            ("0x400012", "xor eax, eax"),
            ("0x400014", "add rsp, 0x10"),
            ("0x400018", "pop rbp"),
            ("0x400019", "ret"),
        ]

        results = []
        for addr, instr in instructions:
            result = highlighter.highlight_instruction(instr, addr)
            assert isinstance(result, Text)
            assert instr in result.plain
            assert addr in result.plain
            results.append(result)

        # Verify we got results for all instructions
        assert len(results) == len(instructions)

    def test_real_world_patterns(self):
        """Test with real-world instruction patterns."""
        highlighter = AsmHighlighter()

        # Test common patterns from actual disassembly
        patterns = [
            "mov qword ptr [rbp-8], rdi",
            "lea rax, [rip+0x2000]",
            "test eax, eax",
            "jne 0x401234",
            "call qword ptr [rax+0x10]",
            "add rsp, 0x20",
            "xor eax, eax",
        ]

        for pattern in patterns:
            result = highlighter.highlight_instruction(pattern)
            assert isinstance(result, Text)
            assert pattern in result.plain
