"""Unit tests for MIPS instruction classification."""

import pytest

from caspoon.ui.syntax import InstructionType
from caspoon.ui.syntax.instructions_mips import (
    get_instruction_type,
    is_branch_likely,
    is_coprocessor_instruction,
    is_fp_instruction,
    is_pseudo_instruction,
)


class TestMIPSInstructionClassification:
    """Tests for MIPS instruction type classification."""

    def test_classify_mips_jump_instructions(self):
        """Test classification of MIPS jump/branch instructions."""
        # Unconditional jumps
        assert get_instruction_type("j") == InstructionType.JUMP
        assert get_instruction_type("jr") == InstructionType.JUMP

        # Conditional branches
        assert get_instruction_type("beq") == InstructionType.JUMP
        assert get_instruction_type("bne") == InstructionType.JUMP
        assert get_instruction_type("bgtz") == InstructionType.JUMP
        assert get_instruction_type("blez") == InstructionType.JUMP
        assert get_instruction_type("bltz") == InstructionType.JUMP
        assert get_instruction_type("bgez") == InstructionType.JUMP

        # Branch and link
        assert get_instruction_type("bltzal") == InstructionType.JUMP
        assert get_instruction_type("bgezal") == InstructionType.JUMP

        # Branch likely (deprecated but still used)
        assert get_instruction_type("beql") == InstructionType.JUMP
        assert get_instruction_type("bnel") == InstructionType.JUMP
        assert get_instruction_type("bgtzl") == InstructionType.JUMP
        assert get_instruction_type("blezl") == InstructionType.JUMP

        # FP branches
        assert get_instruction_type("bc1f") == InstructionType.JUMP
        assert get_instruction_type("bc1t") == InstructionType.JUMP
        assert get_instruction_type("bc1fl") == InstructionType.JUMP
        assert get_instruction_type("bc1tl") == InstructionType.JUMP

    def test_classify_mips_r6_branches(self):
        """Test classification of MIPS R6 compact branch instructions."""
        assert get_instruction_type("beqc") == InstructionType.JUMP
        assert get_instruction_type("bnec") == InstructionType.JUMP
        assert get_instruction_type("bltc") == InstructionType.JUMP
        assert get_instruction_type("bgec") == InstructionType.JUMP
        assert get_instruction_type("bltuc") == InstructionType.JUMP
        assert get_instruction_type("bgeuc") == InstructionType.JUMP
        assert get_instruction_type("beqzc") == InstructionType.JUMP
        assert get_instruction_type("bnezc") == InstructionType.JUMP

    def test_classify_mips_pseudo_branches(self):
        """Test classification of MIPS pseudo-instruction branches."""
        # b and bal are pseudo-instructions that map to beq/bgezal
        assert get_instruction_type("b") == InstructionType.JUMP
        assert get_instruction_type("bal") == InstructionType.JUMP

    def test_classify_mips_call_instructions(self):
        """Test classification of MIPS call instructions."""
        # Jump and link (function calls)
        assert get_instruction_type("jal") == InstructionType.CALL
        assert get_instruction_type("jalr") == InstructionType.CALL
        assert get_instruction_type("jalx") == InstructionType.CALL

        # MIPS R6
        assert get_instruction_type("jialc") == InstructionType.CALL
        assert get_instruction_type("jic") == InstructionType.CALL
        assert get_instruction_type("balc") == InstructionType.CALL

    def test_classify_mips_move_instructions(self):
        """Test classification of MIPS move/load/store instructions."""
        # Load operations
        assert get_instruction_type("lw") == InstructionType.MOVE
        assert get_instruction_type("lh") == InstructionType.MOVE
        assert get_instruction_type("lb") == InstructionType.MOVE
        assert get_instruction_type("lhu") == InstructionType.MOVE
        assert get_instruction_type("lbu") == InstructionType.MOVE
        assert get_instruction_type("lwl") == InstructionType.MOVE
        assert get_instruction_type("lwr") == InstructionType.MOVE
        assert get_instruction_type("ll") == InstructionType.MOVE

        # MIPS64 loads
        assert get_instruction_type("ld") == InstructionType.MOVE
        assert get_instruction_type("ldl") == InstructionType.MOVE
        assert get_instruction_type("ldr") == InstructionType.MOVE
        assert get_instruction_type("lld") == InstructionType.MOVE

        # Store operations
        assert get_instruction_type("sw") == InstructionType.MOVE
        assert get_instruction_type("sh") == InstructionType.MOVE
        assert get_instruction_type("sb") == InstructionType.MOVE
        assert get_instruction_type("swl") == InstructionType.MOVE
        assert get_instruction_type("swr") == InstructionType.MOVE
        assert get_instruction_type("sc") == InstructionType.MOVE

        # MIPS64 stores
        assert get_instruction_type("sd") == InstructionType.MOVE
        assert get_instruction_type("sdl") == InstructionType.MOVE
        assert get_instruction_type("sdr") == InstructionType.MOVE
        assert get_instruction_type("scd") == InstructionType.MOVE

    def test_classify_mips_move_operations(self):
        """Test classification of MIPS move operations."""
        # Move operations
        assert get_instruction_type("move") == InstructionType.MOVE
        assert get_instruction_type("mfhi") == InstructionType.MOVE
        assert get_instruction_type("mflo") == InstructionType.MOVE
        assert get_instruction_type("mthi") == InstructionType.MOVE
        assert get_instruction_type("mtlo") == InstructionType.MOVE

        # Coprocessor moves
        assert get_instruction_type("mfc0") == InstructionType.MOVE
        assert get_instruction_type("mtc0") == InstructionType.MOVE
        assert get_instruction_type("mfc1") == InstructionType.MOVE
        assert get_instruction_type("mtc1") == InstructionType.MOVE
        assert get_instruction_type("mfc2") == InstructionType.MOVE
        assert get_instruction_type("mtc2") == InstructionType.MOVE

        # Load immediate/address
        assert get_instruction_type("li") == InstructionType.MOVE
        assert get_instruction_type("la") == InstructionType.MOVE
        assert get_instruction_type("lui") == InstructionType.MOVE

        # Conditional move
        assert get_instruction_type("movn") == InstructionType.MOVE
        assert get_instruction_type("movz") == InstructionType.MOVE
        assert get_instruction_type("movf") == InstructionType.MOVE
        assert get_instruction_type("movt") == InstructionType.MOVE

    def test_classify_mips_arithmetic_instructions(self):
        """Test classification of MIPS arithmetic instructions."""
        # Addition
        assert get_instruction_type("add") == InstructionType.ARITHMETIC
        assert get_instruction_type("addu") == InstructionType.ARITHMETIC
        assert get_instruction_type("addi") == InstructionType.ARITHMETIC
        assert get_instruction_type("addiu") == InstructionType.ARITHMETIC

        # MIPS64 doubleword addition
        assert get_instruction_type("dadd") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddu") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddi") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddiu") == InstructionType.ARITHMETIC

        # Subtraction
        assert get_instruction_type("sub") == InstructionType.ARITHMETIC
        assert get_instruction_type("subu") == InstructionType.ARITHMETIC

        # MIPS64 doubleword subtraction
        assert get_instruction_type("dsub") == InstructionType.ARITHMETIC
        assert get_instruction_type("dsubu") == InstructionType.ARITHMETIC

        # Multiplication
        assert get_instruction_type("mult") == InstructionType.ARITHMETIC
        assert get_instruction_type("multu") == InstructionType.ARITHMETIC
        assert get_instruction_type("mul") == InstructionType.ARITHMETIC
        assert get_instruction_type("muh") == InstructionType.ARITHMETIC
        assert get_instruction_type("mulu") == InstructionType.ARITHMETIC
        assert get_instruction_type("muhu") == InstructionType.ARITHMETIC

        # MIPS64 doubleword multiplication
        assert get_instruction_type("dmult") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmultu") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmul") == InstructionType.ARITHMETIC

        # Multiply-add/sub
        assert get_instruction_type("madd") == InstructionType.ARITHMETIC
        assert get_instruction_type("maddu") == InstructionType.ARITHMETIC
        assert get_instruction_type("msub") == InstructionType.ARITHMETIC
        assert get_instruction_type("msubu") == InstructionType.ARITHMETIC

        # Division
        assert get_instruction_type("div") == InstructionType.ARITHMETIC
        assert get_instruction_type("divu") == InstructionType.ARITHMETIC

        # MIPS64 doubleword division
        assert get_instruction_type("ddiv") == InstructionType.ARITHMETIC
        assert get_instruction_type("ddivu") == InstructionType.ARITHMETIC

        # Modulo (MIPS32 R6)
        assert get_instruction_type("mod") == InstructionType.ARITHMETIC
        assert get_instruction_type("modu") == InstructionType.ARITHMETIC

        # Negate/Absolute
        assert get_instruction_type("neg") == InstructionType.ARITHMETIC
        assert get_instruction_type("negu") == InstructionType.ARITHMETIC
        assert get_instruction_type("abs") == InstructionType.ARITHMETIC

    def test_classify_mips_logic_instructions(self):
        """Test classification of MIPS logical instructions."""
        # Logical operations
        assert get_instruction_type("and") == InstructionType.LOGIC
        assert get_instruction_type("or") == InstructionType.LOGIC
        assert get_instruction_type("xor") == InstructionType.LOGIC
        assert get_instruction_type("nor") == InstructionType.LOGIC
        assert get_instruction_type("andi") == InstructionType.LOGIC
        assert get_instruction_type("ori") == InstructionType.LOGIC
        assert get_instruction_type("xori") == InstructionType.LOGIC
        assert get_instruction_type("not") == InstructionType.LOGIC

        # Shift operations
        assert get_instruction_type("sll") == InstructionType.LOGIC
        assert get_instruction_type("srl") == InstructionType.LOGIC
        assert get_instruction_type("sra") == InstructionType.LOGIC
        assert get_instruction_type("sllv") == InstructionType.LOGIC
        assert get_instruction_type("srlv") == InstructionType.LOGIC
        assert get_instruction_type("srav") == InstructionType.LOGIC

        # MIPS64 doubleword shifts
        assert get_instruction_type("dsll") == InstructionType.LOGIC
        assert get_instruction_type("dsrl") == InstructionType.LOGIC
        assert get_instruction_type("dsra") == InstructionType.LOGIC
        assert get_instruction_type("dsllv") == InstructionType.LOGIC
        assert get_instruction_type("dsrlv") == InstructionType.LOGIC
        assert get_instruction_type("dsrav") == InstructionType.LOGIC
        assert get_instruction_type("dsll32") == InstructionType.LOGIC
        assert get_instruction_type("dsrl32") == InstructionType.LOGIC
        assert get_instruction_type("dsra32") == InstructionType.LOGIC

        # Rotate (MIPS32 Release 2)
        assert get_instruction_type("rotr") == InstructionType.LOGIC
        assert get_instruction_type("rotrv") == InstructionType.LOGIC

        # Bit manipulation
        assert get_instruction_type("ext") == InstructionType.LOGIC
        assert get_instruction_type("ins") == InstructionType.LOGIC
        assert get_instruction_type("wsbh") == InstructionType.LOGIC
        assert get_instruction_type("seb") == InstructionType.LOGIC
        assert get_instruction_type("seh") == InstructionType.LOGIC

        # Count bits
        assert get_instruction_type("clz") == InstructionType.LOGIC
        assert get_instruction_type("clo") == InstructionType.LOGIC

    def test_classify_mips_compare_instructions(self):
        """Test classification of MIPS compare instructions."""
        # Set on less than
        assert get_instruction_type("slt") == InstructionType.COMPARE
        assert get_instruction_type("sltu") == InstructionType.COMPARE
        assert get_instruction_type("slti") == InstructionType.COMPARE
        assert get_instruction_type("sltiu") == InstructionType.COMPARE

        # Set equal/not equal (pseudo-instructions)
        assert get_instruction_type("seq") == InstructionType.COMPARE
        assert get_instruction_type("sne") == InstructionType.COMPARE
        assert get_instruction_type("sgt") == InstructionType.COMPARE
        assert get_instruction_type("sgtu") == InstructionType.COMPARE
        assert get_instruction_type("sge") == InstructionType.COMPARE
        assert get_instruction_type("sgeu") == InstructionType.COMPARE
        assert get_instruction_type("sle") == InstructionType.COMPARE
        assert get_instruction_type("sleu") == InstructionType.COMPARE

    def test_classify_mips_other_instructions(self):
        """Test classification of MIPS other/system instructions."""
        # No operation
        assert get_instruction_type("nop") == InstructionType.OTHER
        assert get_instruction_type("ssnop") == InstructionType.OTHER

        # Breakpoint and trap
        assert get_instruction_type("break") == InstructionType.OTHER
        assert get_instruction_type("syscall") == InstructionType.OTHER

        # Trap on condition
        assert get_instruction_type("teq") == InstructionType.OTHER
        assert get_instruction_type("tne") == InstructionType.OTHER
        assert get_instruction_type("tge") == InstructionType.OTHER
        assert get_instruction_type("tgeu") == InstructionType.OTHER
        assert get_instruction_type("tlt") == InstructionType.OTHER
        assert get_instruction_type("tltu") == InstructionType.OTHER

        # Sync
        assert get_instruction_type("sync") == InstructionType.OTHER
        assert get_instruction_type("synci") == InstructionType.OTHER

        # Cache
        assert get_instruction_type("cache") == InstructionType.OTHER
        assert get_instruction_type("pref") == InstructionType.OTHER

        # Exception and interrupt
        assert get_instruction_type("eret") == InstructionType.OTHER
        assert get_instruction_type("deret") == InstructionType.OTHER
        assert get_instruction_type("wait") == InstructionType.OTHER


class TestMIPSEdgeCases:
    """Tests for MIPS instruction classification edge cases."""

    def test_classify_empty_mnemonic(self):
        """Test classification of empty mnemonic."""
        assert get_instruction_type("") == InstructionType.OTHER
        assert get_instruction_type("   ") == InstructionType.OTHER

    def test_classify_unknown_instruction(self):
        """Test classification of unknown MIPS instruction."""
        assert get_instruction_type("notarealmipsinstruction") == InstructionType.OTHER
        assert get_instruction_type("xyz123") == InstructionType.OTHER

    def test_classify_case_insensitive(self):
        """Test that classification is case-insensitive."""
        assert get_instruction_type("LW") == InstructionType.MOVE
        assert get_instruction_type("JAL") == InstructionType.CALL
        assert get_instruction_type("ADD") == InstructionType.ARITHMETIC
        assert get_instruction_type("SLT") == InstructionType.COMPARE

    def test_classify_with_whitespace(self):
        """Test classification with leading/trailing whitespace."""
        assert get_instruction_type("  lw  ") == InstructionType.MOVE
        assert get_instruction_type("\tjal\t") == InstructionType.CALL
        assert get_instruction_type("\nadd\n") == InstructionType.ARITHMETIC


class TestMIPSHelperFunctions:
    """Tests for MIPS helper functions."""

    def test_is_branch_likely(self):
        """Test detection of branch likely instructions."""
        # Branch likely instructions (deprecated but still used)
        assert is_branch_likely("beql")
        assert is_branch_likely("bnel")
        assert is_branch_likely("bgtzl")
        assert is_branch_likely("blezl")
        assert is_branch_likely("bltzl")
        assert is_branch_likely("bgezl")
        assert is_branch_likely("bc1fl")
        assert is_branch_likely("bc1tl")

        # Non-likely branches
        assert not is_branch_likely("beq")
        assert not is_branch_likely("bne")
        assert not is_branch_likely("j")
        assert not is_branch_likely("jal")

    def test_is_branch_likely_edge_cases(self):
        """Test is_branch_likely with edge cases."""
        # Empty string
        assert not is_branch_likely("")

        # Case insensitive
        assert is_branch_likely("BEQL")
        assert is_branch_likely("BeqL")

        # With whitespace
        assert is_branch_likely("  beql  ")

    def test_is_pseudo_instruction(self):
        """Test detection of MIPS pseudo-instructions."""
        # Common pseudo-instructions
        assert is_pseudo_instruction("move")
        assert is_pseudo_instruction("li")
        assert is_pseudo_instruction("la")
        assert is_pseudo_instruction("b")
        assert is_pseudo_instruction("bal")
        assert is_pseudo_instruction("not")
        assert is_pseudo_instruction("neg")
        assert is_pseudo_instruction("negu")
        assert is_pseudo_instruction("abs")

        # Set pseudo-instructions
        assert is_pseudo_instruction("seq")
        assert is_pseudo_instruction("sne")
        assert is_pseudo_instruction("sgt")
        assert is_pseudo_instruction("sgtu")
        assert is_pseudo_instruction("sge")
        assert is_pseudo_instruction("sgeu")
        assert is_pseudo_instruction("sle")
        assert is_pseudo_instruction("sleu")

        # Non-pseudo instructions
        assert not is_pseudo_instruction("add")
        assert not is_pseudo_instruction("lw")
        assert not is_pseudo_instruction("jal")
        assert not is_pseudo_instruction("slt")

    def test_is_pseudo_instruction_edge_cases(self):
        """Test is_pseudo_instruction with edge cases."""
        # Empty string
        assert not is_pseudo_instruction("")

        # Case insensitive
        assert is_pseudo_instruction("MOVE")
        assert is_pseudo_instruction("Li")

        # With whitespace
        assert is_pseudo_instruction("  move  ")

    def test_is_fp_instruction(self):
        """Test detection of floating-point instructions."""
        # FP arithmetic
        assert is_fp_instruction("add.s")
        assert is_fp_instruction("add.d")
        assert is_fp_instruction("add.ps")
        assert is_fp_instruction("sub.s")
        assert is_fp_instruction("sub.d")
        assert is_fp_instruction("mul.s")
        assert is_fp_instruction("mul.d")
        assert is_fp_instruction("div.s")
        assert is_fp_instruction("div.d")
        assert is_fp_instruction("sqrt.s")
        assert is_fp_instruction("sqrt.d")

        # FP move
        assert is_fp_instruction("mov.s")
        assert is_fp_instruction("mov.d")

        # FP compare
        assert is_fp_instruction("c.f.s")
        assert is_fp_instruction("c.f.d")
        assert is_fp_instruction("c.eq.s")
        assert is_fp_instruction("c.eq.d")
        assert is_fp_instruction("c.lt.s")
        assert is_fp_instruction("c.le.d")

        # Non-FP instructions
        assert not is_fp_instruction("add")
        assert not is_fp_instruction("lw")
        assert not is_fp_instruction("jal")

    def test_is_fp_instruction_edge_cases(self):
        """Test is_fp_instruction with edge cases."""
        # Empty string
        assert not is_fp_instruction("")

        # Case insensitive
        assert is_fp_instruction("ADD.S")
        assert is_fp_instruction("Add.D")

    def test_is_coprocessor_instruction(self):
        """Test detection of coprocessor instructions."""
        # Move to/from coprocessor
        assert is_coprocessor_instruction("mfc0")
        assert is_coprocessor_instruction("mtc0")
        assert is_coprocessor_instruction("mfc1")
        assert is_coprocessor_instruction("mtc1")
        assert is_coprocessor_instruction("mfc2")
        assert is_coprocessor_instruction("mtc2")

        # Coprocessor control
        assert is_coprocessor_instruction("cfc0")
        assert is_coprocessor_instruction("ctc0")
        assert is_coprocessor_instruction("cfc1")
        assert is_coprocessor_instruction("ctc1")

        # Load/store coprocessor
        assert is_coprocessor_instruction("lwc0")
        assert is_coprocessor_instruction("swc0")
        assert is_coprocessor_instruction("lwc1")
        assert is_coprocessor_instruction("swc1")
        assert is_coprocessor_instruction("ldc1")
        assert is_coprocessor_instruction("sdc1")

        # Coprocessor operations
        assert is_coprocessor_instruction("cop0")
        assert is_coprocessor_instruction("cop1")
        assert is_coprocessor_instruction("cop2")

        # Non-coprocessor instructions
        assert not is_coprocessor_instruction("add")
        assert not is_coprocessor_instruction("lw")
        assert not is_coprocessor_instruction("jal")

    def test_is_coprocessor_instruction_edge_cases(self):
        """Test is_coprocessor_instruction with edge cases."""
        # Empty string
        assert not is_coprocessor_instruction("")

        # Case insensitive
        assert is_coprocessor_instruction("MFC0")
        assert is_coprocessor_instruction("Lwc1")


class TestMIPS64SpecificFeatures:
    """Tests for MIPS64-specific instruction features."""

    def test_mips64_load_store(self):
        """Test MIPS64 doubleword load/store instructions."""
        assert get_instruction_type("ld") == InstructionType.MOVE
        assert get_instruction_type("ldl") == InstructionType.MOVE
        assert get_instruction_type("ldr") == InstructionType.MOVE
        assert get_instruction_type("lld") == InstructionType.MOVE
        assert get_instruction_type("sd") == InstructionType.MOVE
        assert get_instruction_type("sdl") == InstructionType.MOVE
        assert get_instruction_type("sdr") == InstructionType.MOVE
        assert get_instruction_type("scd") == InstructionType.MOVE

    def test_mips64_arithmetic(self):
        """Test MIPS64 doubleword arithmetic instructions."""
        assert get_instruction_type("dadd") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddu") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddi") == InstructionType.ARITHMETIC
        assert get_instruction_type("daddiu") == InstructionType.ARITHMETIC
        assert get_instruction_type("dsub") == InstructionType.ARITHMETIC
        assert get_instruction_type("dsubu") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmult") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmultu") == InstructionType.ARITHMETIC
        assert get_instruction_type("ddiv") == InstructionType.ARITHMETIC
        assert get_instruction_type("ddivu") == InstructionType.ARITHMETIC

    def test_mips64_shifts(self):
        """Test MIPS64 doubleword shift instructions."""
        assert get_instruction_type("dsll") == InstructionType.LOGIC
        assert get_instruction_type("dsrl") == InstructionType.LOGIC
        assert get_instruction_type("dsra") == InstructionType.LOGIC
        assert get_instruction_type("dsllv") == InstructionType.LOGIC
        assert get_instruction_type("dsrlv") == InstructionType.LOGIC
        assert get_instruction_type("dsrav") == InstructionType.LOGIC
        assert get_instruction_type("dsll32") == InstructionType.LOGIC
        assert get_instruction_type("dsrl32") == InstructionType.LOGIC
        assert get_instruction_type("dsra32") == InstructionType.LOGIC

    def test_mips64_bit_manipulation(self):
        """Test MIPS64 doubleword bit manipulation."""
        assert get_instruction_type("dext") == InstructionType.LOGIC
        assert get_instruction_type("dextu") == InstructionType.LOGIC
        assert get_instruction_type("dextm") == InstructionType.LOGIC
        assert get_instruction_type("dins") == InstructionType.LOGIC
        assert get_instruction_type("dinsu") == InstructionType.LOGIC
        assert get_instruction_type("dinsm") == InstructionType.LOGIC
        assert get_instruction_type("dclz") == InstructionType.LOGIC
        assert get_instruction_type("dclo") == InstructionType.LOGIC


class TestMIPSR6Features:
    """Tests for MIPS Release 6 specific features."""

    def test_mips_r6_compact_branches(self):
        """Test MIPS R6 compact branch instructions."""
        assert get_instruction_type("beqc") == InstructionType.JUMP
        assert get_instruction_type("bnec") == InstructionType.JUMP
        assert get_instruction_type("bltc") == InstructionType.JUMP
        assert get_instruction_type("bgec") == InstructionType.JUMP
        assert get_instruction_type("bltuc") == InstructionType.JUMP
        assert get_instruction_type("bgeuc") == InstructionType.JUMP
        assert get_instruction_type("beqzc") == InstructionType.JUMP
        assert get_instruction_type("bnezc") == InstructionType.JUMP
        assert get_instruction_type("bltzc") == InstructionType.JUMP
        assert get_instruction_type("bgezc") == InstructionType.JUMP
        assert get_instruction_type("blezc") == InstructionType.JUMP
        assert get_instruction_type("bgtzc") == InstructionType.JUMP

    def test_mips_r6_multiply(self):
        """Test MIPS R6 multiply instructions."""
        assert get_instruction_type("mul") == InstructionType.ARITHMETIC
        assert get_instruction_type("muh") == InstructionType.ARITHMETIC
        assert get_instruction_type("mulu") == InstructionType.ARITHMETIC
        assert get_instruction_type("muhu") == InstructionType.ARITHMETIC

    def test_mips_r6_modulo(self):
        """Test MIPS R6 modulo instructions."""
        assert get_instruction_type("mod") == InstructionType.ARITHMETIC
        assert get_instruction_type("modu") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmod") == InstructionType.ARITHMETIC
        assert get_instruction_type("dmodu") == InstructionType.ARITHMETIC

    def test_mips_r6_bit_manipulation(self):
        """Test MIPS R6 bit manipulation instructions."""
        assert get_instruction_type("bitswap") == InstructionType.LOGIC
        assert get_instruction_type("dbitswap") == InstructionType.LOGIC
