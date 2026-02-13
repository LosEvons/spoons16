"""Integration tests for architecture-aware syntax highlighting."""

from unittest.mock import Mock

import pytest
from rich.text import Text

from caspoon.core.models import ExecutableReport
from caspoon.ui.syntax import AsmHighlighter, ColorScheme, InstructionType
from caspoon.ui.syntax.arch_detector import detect_architecture
from caspoon.ui.syntax.arch_manager import get_instruction_classifier


class TestHighlighterWithARMArchitecture:
    """Integration tests for highlighter with ARM architecture."""

    def test_highlighter_with_arm_classifier(self):
        """Test highlighter uses ARM classifier when provided."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # ARM-specific instruction should be classified correctly
        result = highlighter.highlight_instruction("ldr r0, [r1]")
        assert isinstance(result, Text)
        assert "ldr r0, [r1]" in result.plain

    def test_highlighter_classifies_arm_instructions(self):
        """Test highlighter correctly classifies ARM instructions."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # Test ARM-specific classifications
        assert highlighter.classify_instruction("ldr r0, [r1]") == InstructionType.MOVE
        assert highlighter.classify_instruction("str r0, [r1]") == InstructionType.MOVE
        assert highlighter.classify_instruction("bl func") == InstructionType.CALL
        assert highlighter.classify_instruction("b label") == InstructionType.JUMP
        assert highlighter.classify_instruction("cmp r0, r1") == InstructionType.COMPARE

    def test_highlighter_with_arm64_classifier(self):
        """Test highlighter uses ARM64 classifier when provided."""
        report = Mock(spec=ExecutableReport)
        report.arch = "aarch64"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # ARM64-specific instruction
        result = highlighter.highlight_instruction("adrp x0, #0x1000")
        assert isinstance(result, Text)
        assert "adrp x0, #0x1000" in result.plain
        
        # Classification check
        assert highlighter.classify_instruction("adrp x0, #0x1000") == InstructionType.MOVE
        assert highlighter.classify_instruction("blr x0") == InstructionType.CALL
        assert highlighter.classify_instruction("br x0") == InstructionType.JUMP
        assert highlighter.classify_instruction("ret") == InstructionType.RETURN

    def test_highlighter_arm_with_address(self):
        """Test ARM instruction highlighting with address."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        result = highlighter.highlight_instruction("ldr r0, [r1]", address="0x8000")
        assert "0x8000" in result.plain
        assert "ldr r0, [r1]" in result.plain

    def test_arm_instructions_get_correct_colors(self):
        """Test that ARM instructions get correct colors."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        
        scheme = ColorScheme()
        highlighter = AsmHighlighter(instruction_classifier=classifier, color_scheme=scheme)
        
        # Test different instruction types have styling
        jump_result = highlighter.highlight_instruction("b label")
        call_result = highlighter.highlight_instruction("bl func")
        move_result = highlighter.highlight_instruction("ldr r0, [r1]")
        
        assert len(jump_result.spans) > 0
        assert len(call_result.spans) > 0
        assert len(move_result.spans) > 0


class TestHighlighterWithMIPSArchitecture:
    """Integration tests for highlighter with MIPS architecture."""

    def test_highlighter_with_mips_classifier(self):
        """Test highlighter uses MIPS classifier when provided."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # MIPS-specific instruction
        result = highlighter.highlight_instruction("lw $t0, 0($sp)")
        assert isinstance(result, Text)
        assert "lw $t0, 0($sp)" in result.plain

    def test_highlighter_classifies_mips_instructions(self):
        """Test highlighter correctly classifies MIPS instructions."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # Test MIPS-specific classifications
        assert highlighter.classify_instruction("lw $t0, 0($sp)") == InstructionType.MOVE
        assert highlighter.classify_instruction("sw $t0, 0($sp)") == InstructionType.MOVE
        assert highlighter.classify_instruction("jal func") == InstructionType.CALL
        assert highlighter.classify_instruction("j label") == InstructionType.JUMP
        assert highlighter.classify_instruction("beq $t0, $t1, label") == InstructionType.JUMP
        assert highlighter.classify_instruction("slt $t0, $t1, $t2") == InstructionType.COMPARE

    def test_highlighter_with_mips64_classifier(self):
        """Test highlighter uses MIPS64 classifier when provided."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips64"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # MIPS64-specific instruction
        result = highlighter.highlight_instruction("ld $t0, 0($sp)")
        assert isinstance(result, Text)
        assert "ld $t0, 0($sp)" in result.plain
        
        # Classification check
        assert highlighter.classify_instruction("ld $t0, 0($sp)") == InstructionType.MOVE
        assert highlighter.classify_instruction("dadd $t0, $t1, $t2") == InstructionType.ARITHMETIC

    def test_highlighter_mips_with_address(self):
        """Test MIPS instruction highlighting with address."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        result = highlighter.highlight_instruction("lw $t0, 0($sp)", address="0x400000")
        assert "0x400000" in result.plain
        assert "lw $t0, 0($sp)" in result.plain

    def test_mips_instructions_get_correct_colors(self):
        """Test that MIPS instructions get correct colors."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        
        scheme = ColorScheme()
        highlighter = AsmHighlighter(instruction_classifier=classifier, color_scheme=scheme)
        
        # Test different instruction types have styling
        jump_result = highlighter.highlight_instruction("j label")
        call_result = highlighter.highlight_instruction("jal func")
        move_result = highlighter.highlight_instruction("lw $t0, 0($sp)")
        
        assert len(jump_result.spans) > 0
        assert len(call_result.spans) > 0
        assert len(move_result.spans) > 0


class TestHighlighterWithX86Architecture:
    """Integration tests for highlighter with x86 architecture (backward compatibility)."""

    def test_highlighter_with_x86_64_classifier(self):
        """Test highlighter works correctly with x86-64."""
        report = Mock(spec=ExecutableReport)
        report.arch = "x86_64"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # x86 instruction
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)
        assert "mov rax, rbx" in result.plain

    def test_highlighter_classifies_x86_instructions(self):
        """Test highlighter correctly classifies x86 instructions."""
        report = Mock(spec=ExecutableReport)
        report.arch = "x86_64"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # Test x86 classifications
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE
        assert highlighter.classify_instruction("jmp target") == InstructionType.JUMP
        assert highlighter.classify_instruction("call func") == InstructionType.CALL
        assert highlighter.classify_instruction("ret") == InstructionType.RETURN
        assert highlighter.classify_instruction("push rax") == InstructionType.STACK

    def test_highlighter_without_classifier_defaults_to_x86(self):
        """Test highlighter defaults to x86 when no classifier is provided."""
        highlighter = AsmHighlighter()
        
        # Should use x86 classifier by default
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE
        assert highlighter.classify_instruction("push rax") == InstructionType.STACK


class TestHighlighterArchitectureDetection:
    """Tests for architecture detection integration with highlighter."""

    def test_highlighter_detects_arm_from_report(self):
        """Test highlighter with ARM architecture detected from report."""
        report = ExecutableReport(
            path="/usr/bin/app",
            arch="armv7",
            bits=32
        )
        
        # Should detect and use ARM classifier
        detected_arch = detect_architecture(report)
        assert detected_arch == "arm"
        
        classifier = get_instruction_classifier(detected_arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # ARM instruction should be classified correctly
        assert highlighter.classify_instruction("ldr r0, [r1]") == InstructionType.MOVE

    def test_highlighter_detects_arm64_from_report(self):
        """Test highlighter with ARM64 architecture detected from report."""
        report = ExecutableReport(
            path="/usr/bin/app",
            arch="aarch64",
            bits=64
        )
        
        # Should detect and use ARM64 classifier
        detected_arch = detect_architecture(report)
        assert detected_arch == "arm64"
        
        classifier = get_instruction_classifier(detected_arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # ARM64 instruction should be classified correctly
        assert highlighter.classify_instruction("adrp x0, #0x1000") == InstructionType.MOVE

    def test_highlighter_detects_mips_from_report(self):
        """Test highlighter with MIPS architecture detected from report."""
        report = ExecutableReport(
            path="/usr/bin/app",
            arch="mipsel",
            bits=32
        )
        
        # Should detect and use MIPS classifier
        detected_arch = detect_architecture(report)
        assert detected_arch == "mips"
        
        classifier = get_instruction_classifier(detected_arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # MIPS instruction should be classified correctly
        assert highlighter.classify_instruction("lw $t0, 0($sp)") == InstructionType.MOVE


class TestHighlighterCompleteDisassembly:
    """Integration tests with complete disassembly snippets for different architectures."""

    def test_highlight_arm_disassembly_snippet(self):
        """Test highlighting a complete ARM disassembly snippet."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        instructions = [
            ("0x8000", "push {r4, r5, r6, lr}"),
            ("0x8004", "mov r4, r0"),
            ("0x8008", "ldr r5, [r0, #4]"),
            ("0x800c", "add r0, r4, #8"),
            ("0x8010", "bl 0x8100"),
            ("0x8014", "cmp r0, #0"),
            ("0x8018", "bne 0x8024"),
            ("0x801c", "mov r0, r4"),
            ("0x8020", "pop {r4, r5, r6, pc}"),
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

    def test_highlight_mips_disassembly_snippet(self):
        """Test highlighting a complete MIPS disassembly snippet."""
        report = Mock(spec=ExecutableReport)
        report.arch = "mips"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        instructions = [
            ("0x400000", "addiu $sp, $sp, -32"),
            ("0x400004", "sw $ra, 28($sp)"),
            ("0x400008", "sw $s0, 24($sp)"),
            ("0x40000c", "move $s0, $a0"),
            ("0x400010", "lw $t0, 0($s0)"),
            ("0x400014", "jal 0x400100"),
            ("0x400018", "nop"),
            ("0x40001c", "beq $v0, $zero, 0x400030"),
            ("0x400020", "nop"),
            ("0x400024", "lw $ra, 28($sp)"),
            ("0x400028", "lw $s0, 24($sp)"),
            ("0x40002c", "jr $ra"),
            ("0x400030", "addiu $sp, $sp, 32"),
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

    def test_highlight_arm64_disassembly_snippet(self):
        """Test highlighting a complete ARM64 disassembly snippet."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm64"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        instructions = [
            ("0x400000", "stp x29, x30, [sp, #-16]!"),
            ("0x400004", "mov x29, sp"),
            ("0x400008", "adrp x0, #0x411000"),
            ("0x40000c", "add x0, x0, #0x10"),
            ("0x400010", "bl 0x400100"),
            ("0x400014", "cbz x0, 0x400024"),
            ("0x400018", "ldr x0, [x0]"),
            ("0x40001c", "ldp x29, x30, [sp], #16"),
            ("0x400020", "ret"),
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


class TestHighlighterArchitectureSwitching:
    """Tests for switching architectures with different highlighter instances."""

    def test_create_separate_highlighter_per_architecture(self):
        """Test creating separate highlighter instances for different architectures."""
        # Create highlighter for x86
        report_x86 = Mock(spec=ExecutableReport)
        report_x86.arch = "x86_64"
        arch_x86 = detect_architecture(report_x86)
        classifier_x86 = get_instruction_classifier(arch_x86)
        highlighter_x86 = AsmHighlighter(instruction_classifier=classifier_x86)
        
        # Create highlighter for ARM
        report_arm = Mock(spec=ExecutableReport)
        report_arm.arch = "arm"
        arch_arm = detect_architecture(report_arm)
        classifier_arm = get_instruction_classifier(arch_arm)
        highlighter_arm = AsmHighlighter(instruction_classifier=classifier_arm)
        
        # Create highlighter for MIPS
        report_mips = Mock(spec=ExecutableReport)
        report_mips.arch = "mips"
        arch_mips = detect_architecture(report_mips)
        classifier_mips = get_instruction_classifier(arch_mips)
        highlighter_mips = AsmHighlighter(instruction_classifier=classifier_mips)
        
        # Each should classify instructions correctly for their architecture
        assert highlighter_x86.classify_instruction("push rax") == InstructionType.STACK
        assert highlighter_arm.classify_instruction("ldr r0, [r1]") == InstructionType.MOVE
        assert highlighter_mips.classify_instruction("lw $t0, 0($sp)") == InstructionType.MOVE
        
        # ARM also has push instruction (it's not x86-specific), so test with a truly x86-specific instruction
        # Test that x86-specific instructions aren't recognized by MIPS
        assert highlighter_mips.classify_instruction("movzx eax, byte ptr [rsi]") == InstructionType.OTHER


class TestHighlighterEdgeCases:
    """Edge case tests for architecture-aware highlighting."""

    def test_highlighter_with_unknown_architecture(self):
        """Test highlighter with unknown architecture defaults gracefully."""
        report = Mock(spec=ExecutableReport)
        report.arch = "riscv64"
        
        # Detect architecture (will return 'unknown')
        arch = detect_architecture(report)
        assert arch == "unknown"
        
        # Get classifier (will default to x86)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # Should default to x86 classifier
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE

    def test_highlighter_without_classifier(self):
        """Test highlighter without explicit classifier."""
        highlighter = AsmHighlighter()
        
        # Should default to x86 classifier
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE

    def test_highlighter_with_empty_arch(self):
        """Test highlighter with empty architecture string."""
        report = Mock(spec=ExecutableReport)
        report.arch = ""
        
        # Detect architecture (will return 'unknown')
        arch = detect_architecture(report)
        assert arch == "unknown"
        
        # Get classifier (will default to x86)
        classifier = get_instruction_classifier(arch)
        highlighter = AsmHighlighter(instruction_classifier=classifier)
        
        # Should default to x86 classifier
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)

    def test_highlighter_preserves_custom_color_scheme(self):
        """Test that custom color scheme is preserved with architecture detection."""
        report = Mock(spec=ExecutableReport)
        report.arch = "arm"
        
        # Detect architecture and get appropriate classifier
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        
        custom_scheme = ColorScheme(
            jump="red",
            call="blue",
            move="yellow"
        )
        
        highlighter = AsmHighlighter(instruction_classifier=classifier, color_scheme=custom_scheme)
        
        # Should still use ARM classifier
        assert highlighter.classify_instruction("ldr r0, [r1]") == InstructionType.MOVE
        
        # And use custom colors
        result = highlighter.highlight_instruction("ldr r0, [r1]")
        assert isinstance(result, Text)


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing code."""

    def test_highlighter_without_parameters_still_works(self):
        """Test that highlighter without parameters still works (backward compat)."""
        highlighter = AsmHighlighter()
        
        # Should work with x86 instructions
        result = highlighter.highlight_instruction("mov rax, rbx")
        assert isinstance(result, Text)
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE

    def test_highlighter_with_only_color_scheme(self):
        """Test highlighter with only color scheme (no classifier)."""
        custom_scheme = ColorScheme(jump="red")
        highlighter = AsmHighlighter(color_scheme=custom_scheme)
        
        # Should work with default x86 classifier
        result = highlighter.highlight_instruction("jmp target")
        assert isinstance(result, Text)
        assert highlighter.classify_instruction("jmp target") == InstructionType.JUMP

    def test_existing_x86_tests_still_pass(self):
        """Test that existing x86-focused tests still pass."""
        highlighter = AsmHighlighter()
        
        # All these should still work as before
        assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE
        assert highlighter.classify_instruction("jmp target") == InstructionType.JUMP
        assert highlighter.classify_instruction("call func") == InstructionType.CALL
        assert highlighter.classify_instruction("ret") == InstructionType.RETURN
        assert highlighter.classify_instruction("push rax") == InstructionType.STACK
        assert highlighter.classify_instruction("add rax, 5") == InstructionType.ARITHMETIC
        assert highlighter.classify_instruction("and rax, 0xff") == InstructionType.LOGIC
        assert highlighter.classify_instruction("cmp rax, rbx") == InstructionType.COMPARE
