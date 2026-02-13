"""Unit tests for ARM/ARM64 instruction classification."""

import pytest

from caspoon.ui.syntax import InstructionType
from caspoon.ui.syntax.instructions_arm import (
    get_instruction_type,
    is_conditional_instruction,
    is_neon_instruction,
    is_thumb_instruction,
)


class TestARMInstructionClassification:
    """Tests for ARM instruction type classification."""

    def test_classify_arm_jump_instructions(self):
        """Test classification of ARM branch/jump instructions."""
        # Unconditional branches
        assert get_instruction_type("b") == InstructionType.JUMP
        assert get_instruction_type("bx") == InstructionType.JUMP

        # Conditional branches (ARM32)
        assert get_instruction_type("beq") == InstructionType.JUMP
        assert get_instruction_type("bne") == InstructionType.JUMP
        assert get_instruction_type("bcs") == InstructionType.JUMP
        assert get_instruction_type("bhs") == InstructionType.JUMP
        assert get_instruction_type("bcc") == InstructionType.JUMP
        assert get_instruction_type("blo") == InstructionType.JUMP
        assert get_instruction_type("bmi") == InstructionType.JUMP
        assert get_instruction_type("bpl") == InstructionType.JUMP
        assert get_instruction_type("bvs") == InstructionType.JUMP
        assert get_instruction_type("bvc") == InstructionType.JUMP
        assert get_instruction_type("bhi") == InstructionType.JUMP
        assert get_instruction_type("bls") == InstructionType.JUMP
        assert get_instruction_type("bge") == InstructionType.JUMP
        assert get_instruction_type("blt") == InstructionType.JUMP
        assert get_instruction_type("bgt") == InstructionType.JUMP
        assert get_instruction_type("ble") == InstructionType.JUMP
        assert get_instruction_type("bal") == InstructionType.JUMP

    def test_classify_arm64_jump_instructions(self):
        """Test classification of ARM64-specific branch/jump instructions."""
        # ARM64 branches
        assert get_instruction_type("br") == InstructionType.JUMP
        assert get_instruction_type("b.eq") == InstructionType.JUMP
        assert get_instruction_type("b.ne") == InstructionType.JUMP
        assert get_instruction_type("b.cs") == InstructionType.JUMP
        assert get_instruction_type("b.hs") == InstructionType.JUMP
        assert get_instruction_type("b.cc") == InstructionType.JUMP
        assert get_instruction_type("b.lo") == InstructionType.JUMP

        # Compare and branch (ARM64)
        assert get_instruction_type("cbz") == InstructionType.JUMP
        assert get_instruction_type("cbnz") == InstructionType.JUMP
        assert get_instruction_type("tbz") == InstructionType.JUMP
        assert get_instruction_type("tbnz") == InstructionType.JUMP

    def test_classify_arm_call_instructions(self):
        """Test classification of ARM call instructions."""
        # Branch with link (function calls)
        assert get_instruction_type("bl") == InstructionType.CALL
        assert get_instruction_type("blx") == InstructionType.CALL
        assert get_instruction_type("blr") == InstructionType.CALL

    def test_classify_arm_return_instructions(self):
        """Test classification of ARM return instructions."""
        # ARM64 return
        assert get_instruction_type("ret") == InstructionType.RETURN

    def test_classify_arm_move_instructions(self):
        """Test classification of ARM move/load/store instructions."""
        # Basic move operations
        assert get_instruction_type("mov") == InstructionType.MOVE
        assert get_instruction_type("movw") == InstructionType.MOVE
        assert get_instruction_type("movt") == InstructionType.MOVE
        assert get_instruction_type("mvn") == InstructionType.MOVE

        # ARM64 moves
        assert get_instruction_type("movz") == InstructionType.MOVE
        assert get_instruction_type("movk") == InstructionType.MOVE
        assert get_instruction_type("movn") == InstructionType.MOVE

        # Conditional moves
        assert get_instruction_type("moveq") == InstructionType.MOVE
        assert get_instruction_type("movne") == InstructionType.MOVE

        # Conditional select (ARM64)
        assert get_instruction_type("csel") == InstructionType.MOVE
        assert get_instruction_type("csinc") == InstructionType.MOVE
        assert get_instruction_type("csinv") == InstructionType.MOVE
        assert get_instruction_type("csneg") == InstructionType.MOVE

    def test_classify_arm_load_store_instructions(self):
        """Test classification of ARM load/store instructions."""
        # Single load/store
        assert get_instruction_type("ldr") == InstructionType.MOVE
        assert get_instruction_type("str") == InstructionType.MOVE
        assert get_instruction_type("ldrb") == InstructionType.MOVE
        assert get_instruction_type("strb") == InstructionType.MOVE
        assert get_instruction_type("ldrh") == InstructionType.MOVE
        assert get_instruction_type("strh") == InstructionType.MOVE
        assert get_instruction_type("ldrsb") == InstructionType.MOVE
        assert get_instruction_type("ldrsh") == InstructionType.MOVE
        assert get_instruction_type("ldrsw") == InstructionType.MOVE

        # ARM64 load/store
        assert get_instruction_type("ldar") == InstructionType.MOVE
        assert get_instruction_type("stlr") == InstructionType.MOVE
        assert get_instruction_type("ldarb") == InstructionType.MOVE
        assert get_instruction_type("stlrb") == InstructionType.MOVE

        # Exclusive
        assert get_instruction_type("ldaxr") == InstructionType.MOVE
        assert get_instruction_type("stlxr") == InstructionType.MOVE
        assert get_instruction_type("ldxr") == InstructionType.MOVE
        assert get_instruction_type("stxr") == InstructionType.MOVE

    def test_classify_arm_address_calculation(self):
        """Test classification of ARM address calculation instructions."""
        assert get_instruction_type("adr") == InstructionType.MOVE
        assert get_instruction_type("adrp") == InstructionType.MOVE
        assert get_instruction_type("adrl") == InstructionType.MOVE

    def test_classify_arm_arithmetic_instructions(self):
        """Test classification of ARM arithmetic instructions."""
        # Addition
        assert get_instruction_type("add") == InstructionType.ARITHMETIC
        assert get_instruction_type("adc") == InstructionType.ARITHMETIC
        assert get_instruction_type("addw") == InstructionType.ARITHMETIC
        assert get_instruction_type("adds") == InstructionType.ARITHMETIC

        # Subtraction
        assert get_instruction_type("sub") == InstructionType.ARITHMETIC
        assert get_instruction_type("sbc") == InstructionType.ARITHMETIC
        assert get_instruction_type("subs") == InstructionType.ARITHMETIC
        assert get_instruction_type("rsb") == InstructionType.ARITHMETIC
        assert get_instruction_type("rsc") == InstructionType.ARITHMETIC

        # Multiplication
        assert get_instruction_type("mul") == InstructionType.ARITHMETIC
        assert get_instruction_type("mla") == InstructionType.ARITHMETIC
        assert get_instruction_type("mls") == InstructionType.ARITHMETIC
        assert get_instruction_type("smull") == InstructionType.ARITHMETIC
        assert get_instruction_type("umull") == InstructionType.ARITHMETIC
        assert get_instruction_type("smulh") == InstructionType.ARITHMETIC
        assert get_instruction_type("umulh") == InstructionType.ARITHMETIC
        assert get_instruction_type("madd") == InstructionType.ARITHMETIC
        assert get_instruction_type("msub") == InstructionType.ARITHMETIC

        # Division
        assert get_instruction_type("sdiv") == InstructionType.ARITHMETIC
        assert get_instruction_type("udiv") == InstructionType.ARITHMETIC

        # Negate/Absolute
        assert get_instruction_type("neg") == InstructionType.ARITHMETIC
        assert get_instruction_type("negs") == InstructionType.ARITHMETIC
        assert get_instruction_type("abs") == InstructionType.ARITHMETIC

    def test_classify_arm_logic_instructions(self):
        """Test classification of ARM logical instructions."""
        # Logical operations
        assert get_instruction_type("and") == InstructionType.LOGIC
        assert get_instruction_type("orr") == InstructionType.LOGIC
        assert get_instruction_type("eor") == InstructionType.LOGIC
        assert get_instruction_type("bic") == InstructionType.LOGIC
        assert get_instruction_type("orn") == InstructionType.LOGIC
        assert get_instruction_type("eon") == InstructionType.LOGIC

        # Bitwise NOT
        assert get_instruction_type("mvn") == InstructionType.MOVE  # Note: mvn is in MOVE
        assert get_instruction_type("mvns") == InstructionType.LOGIC

        # Shift operations
        assert get_instruction_type("lsl") == InstructionType.LOGIC
        assert get_instruction_type("lsr") == InstructionType.LOGIC
        assert get_instruction_type("asr") == InstructionType.LOGIC
        assert get_instruction_type("ror") == InstructionType.LOGIC
        assert get_instruction_type("rrx") == InstructionType.LOGIC

        # Bit field operations
        assert get_instruction_type("bfi") == InstructionType.LOGIC
        assert get_instruction_type("bfc") == InstructionType.LOGIC
        assert get_instruction_type("bfm") == InstructionType.LOGIC

        # Bit manipulation
        assert get_instruction_type("rbit") == InstructionType.LOGIC
        assert get_instruction_type("rev") == InstructionType.LOGIC
        assert get_instruction_type("rev16") == InstructionType.LOGIC
        assert get_instruction_type("clz") == InstructionType.LOGIC
        assert get_instruction_type("cls") == InstructionType.LOGIC

    def test_classify_arm_stack_instructions(self):
        """Test classification of ARM stack instructions."""
        # Push and pop (ARM32)
        assert get_instruction_type("push") == InstructionType.STACK
        assert get_instruction_type("pop") == InstructionType.STACK

        # Load/Store multiple (used for stack operations)
        assert get_instruction_type("stm") == InstructionType.STACK
        assert get_instruction_type("stmia") == InstructionType.STACK
        assert get_instruction_type("stmib") == InstructionType.STACK
        assert get_instruction_type("stmda") == InstructionType.STACK
        assert get_instruction_type("stmdb") == InstructionType.STACK
        assert get_instruction_type("ldm") == InstructionType.STACK
        assert get_instruction_type("ldmia") == InstructionType.STACK
        assert get_instruction_type("ldmib") == InstructionType.STACK

        # ARM64 stack operations
        assert get_instruction_type("stp") == InstructionType.STACK
        assert get_instruction_type("ldp") == InstructionType.STACK

    def test_classify_arm_compare_instructions(self):
        """Test classification of ARM compare instructions."""
        assert get_instruction_type("cmp") == InstructionType.COMPARE
        assert get_instruction_type("cmn") == InstructionType.COMPARE
        assert get_instruction_type("tst") == InstructionType.COMPARE
        assert get_instruction_type("teq") == InstructionType.COMPARE

        # ARM64 conditional compare
        assert get_instruction_type("ccmn") == InstructionType.COMPARE
        assert get_instruction_type("ccmp") == InstructionType.COMPARE

    def test_classify_arm_other_instructions(self):
        """Test classification of ARM other/system instructions."""
        # No operation
        assert get_instruction_type("nop") == InstructionType.OTHER

        # Breakpoint
        assert get_instruction_type("bkpt") == InstructionType.OTHER
        assert get_instruction_type("brk") == InstructionType.OTHER

        # Hints
        assert get_instruction_type("yield") == InstructionType.OTHER
        assert get_instruction_type("wfe") == InstructionType.OTHER
        assert get_instruction_type("wfi") == InstructionType.OTHER
        assert get_instruction_type("sev") == InstructionType.OTHER

        # Barriers
        assert get_instruction_type("dsb") == InstructionType.OTHER
        assert get_instruction_type("dmb") == InstructionType.OTHER
        assert get_instruction_type("isb") == InstructionType.OTHER

        # System register access
        assert get_instruction_type("mrs") == InstructionType.OTHER
        assert get_instruction_type("msr") == InstructionType.OTHER

        # Supervisor call
        assert get_instruction_type("svc") == InstructionType.OTHER
        assert get_instruction_type("swi") == InstructionType.OTHER


class TestARMEdgeCases:
    """Tests for ARM instruction classification edge cases."""

    def test_classify_empty_mnemonic(self):
        """Test classification of empty mnemonic."""
        assert get_instruction_type("") == InstructionType.OTHER
        assert get_instruction_type("   ") == InstructionType.OTHER

    def test_classify_unknown_instruction(self):
        """Test classification of unknown ARM instruction."""
        assert get_instruction_type("notarealarminstruction") == InstructionType.OTHER
        assert get_instruction_type("xyz123") == InstructionType.OTHER

    def test_classify_case_insensitive(self):
        """Test that classification is case-insensitive."""
        assert get_instruction_type("MOV") == InstructionType.MOVE
        assert get_instruction_type("BL") == InstructionType.CALL
        assert get_instruction_type("RET") == InstructionType.RETURN
        assert get_instruction_type("CMP") == InstructionType.COMPARE

    def test_classify_with_whitespace(self):
        """Test classification with leading/trailing whitespace."""
        assert get_instruction_type("  mov  ") == InstructionType.MOVE
        assert get_instruction_type("\tbl\t") == InstructionType.CALL
        assert get_instruction_type("\nret\n") == InstructionType.RETURN


class TestARMHelperFunctions:
    """Tests for ARM helper functions."""

    def test_is_conditional_instruction(self):
        """Test detection of conditional ARM instructions."""
        # Conditional instructions should be detected
        assert is_conditional_instruction("moveq")
        assert is_conditional_instruction("addne")
        assert is_conditional_instruction("subcs")
        assert is_conditional_instruction("ldrhs")
        assert is_conditional_instruction("strcc")
        assert is_conditional_instruction("bge")
        assert is_conditional_instruction("blt")
        assert is_conditional_instruction("bgt")
        assert is_conditional_instruction("ble")

        # Non-conditional should return False
        assert not is_conditional_instruction("mov")
        assert not is_conditional_instruction("add")
        assert not is_conditional_instruction("ldr")
        assert not is_conditional_instruction("bl")

    def test_is_conditional_instruction_edge_cases(self):
        """Test is_conditional_instruction with edge cases."""
        # Empty string
        assert not is_conditional_instruction("")

        # Case insensitive
        assert is_conditional_instruction("MOVEQ")
        assert is_conditional_instruction("MoveQ")

        # With whitespace
        assert is_conditional_instruction("  moveq  ")

    def test_is_thumb_instruction(self):
        """Test detection of Thumb-specific instructions."""
        # IT (if-then) instructions are Thumb-specific
        assert is_thumb_instruction("it")
        assert is_thumb_instruction("ite")
        assert is_thumb_instruction("itt")
        assert is_thumb_instruction("ittt")
        assert is_thumb_instruction("itttt")
        assert is_thumb_instruction("itee")
        assert is_thumb_instruction("itte")

        # Non-Thumb instructions
        assert not is_thumb_instruction("mov")
        assert not is_thumb_instruction("add")
        assert not is_thumb_instruction("bl")

    def test_is_thumb_instruction_edge_cases(self):
        """Test is_thumb_instruction with edge cases."""
        # Empty string
        assert not is_thumb_instruction("")

        # Case insensitive
        assert is_thumb_instruction("IT")
        assert is_thumb_instruction("ITE")

    def test_is_neon_instruction(self):
        """Test detection of NEON/SIMD instructions."""
        # NEON vector operations
        assert is_neon_instruction("vadd")
        assert is_neon_instruction("vsub")
        assert is_neon_instruction("vmul")
        assert is_neon_instruction("vdiv")
        assert is_neon_instruction("vld1")
        assert is_neon_instruction("vld2")
        assert is_neon_instruction("vst1")
        assert is_neon_instruction("vst2")
        assert is_neon_instruction("vmov")
        assert is_neon_instruction("vdup")

        # Non-NEON instructions
        assert not is_neon_instruction("mov")
        assert not is_neon_instruction("add")
        assert not is_neon_instruction("ldr")

    def test_is_neon_instruction_edge_cases(self):
        """Test is_neon_instruction with edge cases."""
        # Empty string
        assert not is_neon_instruction("")

        # Case insensitive
        assert is_neon_instruction("VADD")
        assert is_neon_instruction("VAdd")


class TestARMConditionalInstructions:
    """Tests specifically for ARM conditional instruction variants."""

    def test_conditional_arithmetic(self):
        """Test conditional arithmetic instructions."""
        assert get_instruction_type("addeq") == InstructionType.ARITHMETIC
        assert get_instruction_type("addne") == InstructionType.ARITHMETIC
        assert get_instruction_type("subeq") == InstructionType.ARITHMETIC
        assert get_instruction_type("subne") == InstructionType.ARITHMETIC

    def test_conditional_logical(self):
        """Test conditional logical instructions."""
        assert get_instruction_type("andeq") == InstructionType.LOGIC
        assert get_instruction_type("andne") == InstructionType.LOGIC
        assert get_instruction_type("orreq") == InstructionType.LOGIC
        assert get_instruction_type("orrne") == InstructionType.LOGIC
        assert get_instruction_type("eoreq") == InstructionType.LOGIC
        assert get_instruction_type("eorne") == InstructionType.LOGIC

    def test_conditional_load_store(self):
        """Test conditional load/store instructions."""
        assert get_instruction_type("ldreq") == InstructionType.MOVE
        assert get_instruction_type("ldrne") == InstructionType.MOVE
        assert get_instruction_type("streq") == InstructionType.MOVE
        assert get_instruction_type("strne") == InstructionType.MOVE
        assert get_instruction_type("ldrcs") == InstructionType.MOVE
        assert get_instruction_type("strhs") == InstructionType.MOVE


class TestARM64SpecificFeatures:
    """Tests for ARM64-specific instruction features."""

    def test_arm64_wide_instructions(self):
        """Test ARM64 wide instruction variants."""
        assert get_instruction_type("movz") == InstructionType.MOVE
        assert get_instruction_type("movk") == InstructionType.MOVE
        assert get_instruction_type("movn") == InstructionType.MOVE

    def test_arm64_conditional_select(self):
        """Test ARM64 conditional select instructions."""
        assert get_instruction_type("csel") == InstructionType.MOVE
        assert get_instruction_type("csinc") == InstructionType.MOVE
        assert get_instruction_type("csinv") == InstructionType.MOVE
        assert get_instruction_type("csneg") == InstructionType.MOVE

    def test_arm64_compare_and_branch(self):
        """Test ARM64 compare and branch instructions."""
        assert get_instruction_type("cbz") == InstructionType.JUMP
        assert get_instruction_type("cbnz") == InstructionType.JUMP
        assert get_instruction_type("tbz") == InstructionType.JUMP
        assert get_instruction_type("tbnz") == InstructionType.JUMP

    def test_arm64_load_store_pair(self):
        """Test ARM64 load/store pair instructions."""
        assert get_instruction_type("stp") == InstructionType.STACK
        assert get_instruction_type("ldp") == InstructionType.STACK

    def test_arm64_pc_relative_addressing(self):
        """Test ARM64 PC-relative addressing."""
        assert get_instruction_type("adr") == InstructionType.MOVE
        assert get_instruction_type("adrp") == InstructionType.MOVE
