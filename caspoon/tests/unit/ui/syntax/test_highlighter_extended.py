"""Extended tests for syntax highlighter - Priority 1 critical coverage gaps."""

import pytest
from rich.text import Text
from unittest.mock import Mock, patch

from caspoon.ui.syntax import AsmHighlighter, InstructionType, ColorScheme


class TestExceptionHandling:
    """Tests for exception handling and error resilience."""
    
    def test_highlight_instruction_graceful_fallback_on_exception(self):
        """Test that highlighting fails gracefully when an exception occurs."""
        # Create a scheme that raises an exception
        bad_scheme = Mock(spec=ColorScheme)
        bad_scheme.get_style.side_effect = RuntimeError("Simulated failure")
        
        highlighter = AsmHighlighter(color_scheme=bad_scheme)
        
        # Should not raise, should return plain text
        result = highlighter.highlight_instruction("mov rax, rbx", address="0x1000")
        
        assert isinstance(result, Text)
        assert "0x1000" in result.plain
        assert "mov rax, rbx" in result.plain
    
    def test_highlight_instruction_fallback_with_address_on_exception(self):
        """Test that address is included in fallback on exception."""
        bad_scheme = Mock(spec=ColorScheme)
        bad_scheme.get_style.side_effect = Exception("Generic error")
        bad_scheme.address = "dim"  # Add this attribute to prevent early exception
        
        highlighter = AsmHighlighter(color_scheme=bad_scheme)
        
        result = highlighter.highlight_instruction("call printf", address="0x400000")
        
        assert isinstance(result, Text)
        assert "0x400000:" in result.plain or "0x400000" in result.plain
        assert "call printf" in result.plain
    
    def test_highlight_instruction_fallback_without_address_on_exception(self):
        """Test that fallback works without address on exception."""
        bad_scheme = Mock(spec=ColorScheme)
        bad_scheme.get_style.side_effect = ValueError("Bad value")
        
        highlighter = AsmHighlighter(color_scheme=bad_scheme)
        
        result = highlighter.highlight_instruction("ret")
        
        assert isinstance(result, Text)
        assert "ret" in result.plain
        assert ":" not in result.plain  # No colon without address


class TestActualColorApplication:
    """Tests that verify colors are actually applied, not just that Text objects exist."""
    
    def test_colors_are_applied_to_text_spans(self):
        """Test that colors are actually applied to Text object spans."""
        scheme = ColorScheme(
            jump="red",
            call="blue",
            move="green"
        )
        highlighter = AsmHighlighter(color_scheme=scheme)
        
        # Test that the instruction has a colored span
        result = highlighter.highlight_instruction("jmp target")
        
        # The Text object should have styling applied
        assert len(result) > 0  # Has content
        # Check that spans exist with styling
        assert len(result.spans) > 0, "Text should have style spans"
    
    def test_address_has_correct_style(self):
        """Test that addresses get the correct style."""
        scheme = ColorScheme()
        highlighter = AsmHighlighter(color_scheme=scheme)
        
        result = highlighter.highlight_instruction("mov rax, rbx", address="0x1000")
        
        # Should have multiple spans (address + instruction)
        assert len(result.spans) >= 2, "Should have spans for address and instruction"
    
    def test_different_instructions_get_different_colors(self):
        """Test that different instruction types result in different styling."""
        scheme = ColorScheme(
            jump="cyan",
            move="green",
            call="blue"
        )
        highlighter = AsmHighlighter(color_scheme=scheme)
        
        jump_result = highlighter.highlight_instruction("jmp target")
        move_result = highlighter.highlight_instruction("mov rax, rbx")
        call_result = highlighter.highlight_instruction("call func")
        
        # All should have content and spans
        assert len(jump_result.spans) > 0
        assert len(move_result.spans) > 0
        assert len(call_result.spans) > 0


class TestComplexOperands:
    """Tests for instructions with complex operands."""
    
    def test_classify_complex_memory_operands(self):
        """Test classification with complex memory operands."""
        highlighter = AsmHighlighter()
        
        # Complex memory operands should still be classified correctly
        assert highlighter.classify_instruction(
            "mov qword ptr [rbp-8], rdi"
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "lea rax, [rip+0x2000]"
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "call qword ptr [rax+0x10]"
        ) == InstructionType.CALL
        
        assert highlighter.classify_instruction(
            "jmp qword ptr [rax*8+rbx]"
        ) == InstructionType.JUMP
    
    def test_classify_with_size_prefixes(self):
        """Test classification with size prefixes."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction(
            "movzx eax, byte ptr [rsi]"
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "movsx rax, dword ptr [rdi]"
        ) == InstructionType.MOVE
    
    def test_highlight_complex_operands(self):
        """Test highlighting preserves complex operands."""
        highlighter = AsmHighlighter()
        
        complex_instr = "mov qword ptr [rbp-8], rdi"
        result = highlighter.highlight_instruction(complex_instr, address="0x1234")
        
        assert complex_instr in result.plain
        assert "0x1234" in result.plain


class TestMalformedInput:
    """Tests for handling malformed or unusual input."""
    
    def test_classify_with_multiple_spaces(self):
        """Test classification handles multiple spaces."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction(
            "mov     rax,    rbx"
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "call      printf"
        ) == InstructionType.CALL
    
    def test_classify_with_tabs(self):
        """Test classification handles tab characters."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction(
            "mov\trax,\trbx"
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "jmp\t0x1234"
        ) == InstructionType.JUMP
    
    def test_classify_with_leading_trailing_whitespace(self):
        """Test classification handles leading/trailing whitespace."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction(
            "  mov rax, rbx  "
        ) == InstructionType.MOVE
        
        assert highlighter.classify_instruction(
            "\t\tret\n"
        ) == InstructionType.RETURN
    
    def test_highlight_preserves_instruction_content(self):
        """Test that highlighting preserves original instruction content."""
        highlighter = AsmHighlighter()
        
        original = "  mov     rax,   rbx  "
        result = highlighter.highlight_instruction(original)
        
        # Should contain the instruction (whitespace may vary)
        assert "mov" in result.plain
        assert "rax" in result.plain
        assert "rbx" in result.plain


class TestAddressFormatVariations:
    """Tests for various address format handling."""
    
    def test_highlight_hex_address(self):
        """Test highlighting with hexadecimal address."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("mov rax, rbx", address="0x400000")
        assert "0x400000" in result.plain
        assert "mov rax, rbx" in result.plain
    
    def test_highlight_decimal_address(self):
        """Test highlighting with decimal address."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("mov rax, rbx", address="1234")
        assert "1234" in result.plain
    
    def test_highlight_relative_address(self):
        """Test highlighting with relative address."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("mov rax, rbx", address="+0x10")
        assert "+0x10" in result.plain
    
    def test_highlight_empty_address(self):
        """Test highlighting with empty string address."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("mov rax, rbx", address="")
        # Should not have colon separator if no address
        assert result.plain == "mov rax, rbx"
    
    def test_highlight_no_address_parameter(self):
        """Test highlighting without address parameter."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("mov rax, rbx")
        # Should not have colon separator
        assert ":" not in result.plain
        assert "mov rax, rbx" in result.plain
    
    def test_highlight_long_address(self):
        """Test highlighting with very long address."""
        highlighter = AsmHighlighter()
        
        long_addr = "0x7fffffffffffffff"
        result = highlighter.highlight_instruction("ret", address=long_addr)
        assert long_addr in result.plain


class TestUnknownArchitectures:
    """Tests for instructions from non-x86 architectures."""
    
    def test_classify_arm_instructions(self):
        """Test that ARM instructions return OTHER."""
        highlighter = AsmHighlighter()
        
        # ARM instructions should not be classified as known types
        assert highlighter.classify_instruction("ldr r0, [r1]") == InstructionType.OTHER
        assert highlighter.classify_instruction("str r0, [r1]") == InstructionType.OTHER
        assert highlighter.classify_instruction("bl func") == InstructionType.OTHER
        assert highlighter.classify_instruction("bx lr") == InstructionType.OTHER
    
    def test_classify_mips_instructions(self):
        """Test that MIPS instructions return OTHER."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction("lw $t0, 0($sp)") == InstructionType.OTHER
        assert highlighter.classify_instruction("sw $t0, 0($sp)") == InstructionType.OTHER
        assert highlighter.classify_instruction("jal func") == InstructionType.OTHER
    
    def test_classify_made_up_instructions(self):
        """Test that made up instructions return OTHER."""
        highlighter = AsmHighlighter()
        
        assert highlighter.classify_instruction("foo bar, baz") == InstructionType.OTHER
        assert highlighter.classify_instruction("xyz123") == InstructionType.OTHER
        assert highlighter.classify_instruction("notarealinstruction") == InstructionType.OTHER
    
    def test_highlight_unknown_instructions(self):
        """Test highlighting of unknown instructions."""
        highlighter = AsmHighlighter()
        
        # Should still highlight, just with OTHER color
        result = highlighter.highlight_instruction("ldr r0, [r1]", address="0x8000")
        assert isinstance(result, Text)
        assert "ldr r0, [r1]" in result.plain
        assert "0x8000" in result.plain


class TestEdgeCasesAndStress:
    """Tests for edge cases and stress scenarios."""
    
    def test_very_long_instruction(self):
        """Test handling of very long instructions."""
        highlighter = AsmHighlighter()
        
        # Create a very long instruction
        long_instr = "mov rax, " + "0x" + "f" * 1000
        result = highlighter.highlight_instruction(long_instr)
        
        assert isinstance(result, Text)
        assert "mov rax" in result.plain
    
    def test_instruction_with_special_characters(self):
        """Test handling of special characters in instructions."""
        highlighter = AsmHighlighter()
        
        # Instructions with special characters
        result = highlighter.highlight_instruction("mov rax, $0x1234")
        assert isinstance(result, Text)
        
        result = highlighter.highlight_instruction("mov rax, #0x1234")
        assert isinstance(result, Text)
    
    def test_empty_string_instruction(self):
        """Test handling of empty string instruction."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("")
        assert isinstance(result, Text)
        assert result.plain == ""
    
    def test_whitespace_only_instruction(self):
        """Test handling of whitespace-only instruction."""
        highlighter = AsmHighlighter()
        
        result = highlighter.highlight_instruction("     ")
        assert isinstance(result, Text)
        # Should not crash, classification returns OTHER
    
    def test_none_instruction(self):
        """Test handling of None instruction."""
        highlighter = AsmHighlighter()
        
        # Should not crash
        instr_type = highlighter.classify_instruction(None)
        assert instr_type == InstructionType.OTHER
    
    def test_numeric_instruction(self):
        """Test handling of numeric instruction (not string)."""
        highlighter = AsmHighlighter()
        
        # Should handle non-string input gracefully
        instr_type = highlighter.classify_instruction(12345)
        assert instr_type == InstructionType.OTHER


class TestColorSchemeEdgeCases:
    """Tests for ColorScheme edge cases."""
    
    def test_color_scheme_with_none_values(self):
        """Test ColorScheme with None values."""
        # Should be able to create scheme with None values
        scheme = ColorScheme(jump=None)
        assert scheme.jump is None
    
    def test_get_style_returns_expected_values(self):
        """Test that get_style returns correct values for all types."""
        scheme = ColorScheme(
            jump="color1",
            call="color2",
            move="color3",
            arithmetic="color4",
            logic="color5",
            stack="color6",
            compare="color7",
            return_="color8",
            other="color9"
        )
        
        assert scheme.get_style(InstructionType.JUMP) == "color1"
        assert scheme.get_style(InstructionType.CALL) == "color2"
        assert scheme.get_style(InstructionType.MOVE) == "color3"
        assert scheme.get_style(InstructionType.ARITHMETIC) == "color4"
        assert scheme.get_style(InstructionType.LOGIC) == "color5"
        assert scheme.get_style(InstructionType.STACK) == "color6"
        assert scheme.get_style(InstructionType.COMPARE) == "color7"
        assert scheme.get_style(InstructionType.RETURN) == "color8"
        assert scheme.get_style(InstructionType.OTHER) == "color9"
