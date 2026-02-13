"""Unit tests for architecture manager functionality."""

import pytest

from caspoon.ui.syntax import InstructionType
from caspoon.ui.syntax.arch_manager import (
    ArchitectureManager,
    get_instruction_classifier,
    get_supported_architectures,
    supports_architecture,
)


class TestArchitectureManagerClassifier:
    """Tests for ArchitectureManager classifier retrieval."""

    def test_get_x86_classifier(self):
        """Test getting x86 instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("x86")
        
        # Test that it classifies x86 instructions correctly
        assert classifier("mov") == InstructionType.MOVE
        assert classifier("jmp") == InstructionType.JUMP
        assert classifier("call") == InstructionType.CALL
        assert classifier("ret") == InstructionType.RETURN
        assert classifier("add") == InstructionType.ARITHMETIC

    def test_get_x86_64_classifier(self):
        """Test getting x86-64 instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("x86_64")
        
        # Test that it classifies x86 instructions correctly
        assert classifier("mov") == InstructionType.MOVE
        assert classifier("jmp") == InstructionType.JUMP
        assert classifier("call") == InstructionType.CALL
        assert classifier("ret") == InstructionType.RETURN
        assert classifier("push") == InstructionType.STACK

    def test_get_arm_classifier(self):
        """Test getting ARM instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("arm")
        
        # Test that it classifies ARM instructions correctly
        assert classifier("mov") == InstructionType.MOVE
        assert classifier("ldr") == InstructionType.MOVE
        assert classifier("str") == InstructionType.MOVE
        assert classifier("bl") == InstructionType.CALL
        assert classifier("b") == InstructionType.JUMP
        assert classifier("add") == InstructionType.ARITHMETIC
        assert classifier("cmp") == InstructionType.COMPARE

    def test_get_arm64_classifier(self):
        """Test getting ARM64 instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("arm64")
        
        # Test that it classifies ARM64 instructions correctly
        assert classifier("mov") == InstructionType.MOVE
        assert classifier("ldr") == InstructionType.MOVE
        assert classifier("str") == InstructionType.MOVE
        assert classifier("bl") == InstructionType.CALL
        assert classifier("blr") == InstructionType.CALL
        assert classifier("br") == InstructionType.JUMP
        assert classifier("ret") == InstructionType.RETURN
        assert classifier("adrp") == InstructionType.MOVE

    def test_get_mips_classifier(self):
        """Test getting MIPS instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("mips")
        
        # Test that it classifies MIPS instructions correctly
        assert classifier("lw") == InstructionType.MOVE
        assert classifier("sw") == InstructionType.MOVE
        assert classifier("jal") == InstructionType.CALL
        assert classifier("j") == InstructionType.JUMP
        assert classifier("beq") == InstructionType.JUMP
        assert classifier("add") == InstructionType.ARITHMETIC
        assert classifier("slt") == InstructionType.COMPARE

    def test_get_mips64_classifier(self):
        """Test getting MIPS64 instruction classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("mips64")
        
        # Test that it classifies MIPS64 instructions correctly
        assert classifier("ld") == InstructionType.MOVE
        assert classifier("sd") == InstructionType.MOVE
        assert classifier("jal") == InstructionType.CALL
        assert classifier("dadd") == InstructionType.ARITHMETIC


class TestArchitectureManagerFallback:
    """Tests for ArchitectureManager fallback behavior."""

    def test_unknown_architecture_defaults_to_x86(self):
        """Test that unknown architecture defaults to x86 classifier."""
        manager = ArchitectureManager()
        classifier = manager.get_instruction_classifier("unknown")
        
        # Should use x86 classifier as fallback
        assert classifier("mov") == InstructionType.MOVE
        assert classifier("jmp") == InstructionType.JUMP
        assert classifier("call") == InstructionType.CALL

    def test_unrecognized_architecture_defaults_to_x86(self):
        """Test that unrecognized architecture defaults to x86 classifier."""
        manager = ArchitectureManager()
        
        classifier = manager.get_instruction_classifier("riscv64")
        assert classifier("mov") == InstructionType.MOVE
        
        classifier = manager.get_instruction_classifier("powerpc")
        assert classifier("add") == InstructionType.ARITHMETIC
        
        classifier = manager.get_instruction_classifier("completely_made_up")
        assert classifier("ret") == InstructionType.RETURN


class TestArchitectureManagerCaseHandling:
    """Tests for ArchitectureManager case handling."""

    def test_classifier_case_insensitive(self):
        """Test that architecture names are case-insensitive."""
        manager = ArchitectureManager()
        
        # Test uppercase
        classifier = manager.get_instruction_classifier("X86_64")
        assert classifier("mov") == InstructionType.MOVE
        
        classifier = manager.get_instruction_classifier("ARM64")
        assert classifier("ldr") == InstructionType.MOVE
        
        classifier = manager.get_instruction_classifier("MIPS")
        assert classifier("lw") == InstructionType.MOVE

    def test_classifier_mixed_case(self):
        """Test that mixed case architecture names work."""
        manager = ArchitectureManager()
        
        classifier = manager.get_instruction_classifier("Arm64")
        assert classifier("bl") == InstructionType.CALL
        
        classifier = manager.get_instruction_classifier("MiPs64")
        assert classifier("jal") == InstructionType.CALL

    def test_classifier_with_whitespace(self):
        """Test that architecture names with whitespace work."""
        manager = ArchitectureManager()
        
        classifier = manager.get_instruction_classifier("  x86_64  ")
        assert classifier("mov") == InstructionType.MOVE
        
        classifier = manager.get_instruction_classifier("\tarm\t")
        assert classifier("ldr") == InstructionType.MOVE


class TestArchitectureSupport:
    """Tests for checking architecture support."""

    def test_supports_x86(self):
        """Test that x86 is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("x86") is True

    def test_supports_x86_64(self):
        """Test that x86-64 is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("x86_64") is True

    def test_supports_arm(self):
        """Test that ARM is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("arm") is True

    def test_supports_arm64(self):
        """Test that ARM64 is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("arm64") is True

    def test_supports_mips(self):
        """Test that MIPS is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("mips") is True

    def test_supports_mips64(self):
        """Test that MIPS64 is supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("mips64") is True

    def test_does_not_support_unknown(self):
        """Test that unknown architectures are not supported."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("unknown") is False
        assert manager.supports_architecture("riscv64") is False
        assert manager.supports_architecture("powerpc") is False

    def test_supports_case_insensitive(self):
        """Test that architecture support check is case-insensitive."""
        manager = ArchitectureManager()
        assert manager.supports_architecture("X86_64") is True
        assert manager.supports_architecture("ARM64") is True
        assert manager.supports_architecture("MIPS") is True


class TestArchitectureList:
    """Tests for getting list of supported architectures."""

    def test_get_supported_architectures(self):
        """Test getting list of supported architectures."""
        manager = ArchitectureManager()
        supported = manager.get_supported_architectures()
        
        # Check that all expected architectures are in the list
        assert "x86" in supported
        assert "x86_64" in supported
        assert "arm" in supported
        assert "arm64" in supported
        assert "mips" in supported
        assert "mips64" in supported

    def test_supported_architectures_count(self):
        """Test that we have the expected number of supported architectures."""
        manager = ArchitectureManager()
        supported = manager.get_supported_architectures()
        
        # Should have at least 6 architectures
        assert len(supported) >= 6

    def test_supported_architectures_is_list(self):
        """Test that supported architectures is a list."""
        manager = ArchitectureManager()
        supported = manager.get_supported_architectures()
        
        assert isinstance(supported, list)


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_convenience_get_instruction_classifier(self):
        """Test convenience function for getting instruction classifier."""
        classifier = get_instruction_classifier("x86_64")
        assert classifier("mov") == InstructionType.MOVE
        
        classifier = get_instruction_classifier("arm")
        assert classifier("ldr") == InstructionType.MOVE
        
        classifier = get_instruction_classifier("mips")
        assert classifier("lw") == InstructionType.MOVE

    def test_convenience_supports_architecture(self):
        """Test convenience function for checking architecture support."""
        assert supports_architecture("x86_64") is True
        assert supports_architecture("arm64") is True
        assert supports_architecture("mips") is True
        assert supports_architecture("riscv64") is False

    def test_convenience_get_supported_architectures(self):
        """Test convenience function for getting supported architectures."""
        supported = get_supported_architectures()
        
        assert "x86" in supported
        assert "x86_64" in supported
        assert "arm" in supported
        assert "arm64" in supported
        assert "mips" in supported
        assert "mips64" in supported


class TestArchitectureManagerSingleton:
    """Tests for ArchitectureManager singleton behavior."""

    def test_convenience_functions_use_same_instance(self):
        """Test that convenience functions use the same manager instance."""
        # Get classifiers multiple times
        classifier1 = get_instruction_classifier("x86_64")
        classifier2 = get_instruction_classifier("x86_64")
        
        # They should behave the same
        assert classifier1("mov") == classifier2("mov")
        assert classifier1("jmp") == classifier2("jmp")

    def test_multiple_calls_consistent(self):
        """Test that multiple calls return consistent results."""
        supported1 = get_supported_architectures()
        supported2 = get_supported_architectures()
        
        # Should return the same list
        assert set(supported1) == set(supported2)


class TestArchitectureManagerClassifierBehavior:
    """Tests for classifier function behavior."""

    def test_classifiers_are_callable(self):
        """Test that returned classifiers are callable."""
        manager = ArchitectureManager()
        
        for arch in ["x86", "x86_64", "arm", "arm64", "mips", "mips64"]:
            classifier = manager.get_instruction_classifier(arch)
            assert callable(classifier)

    def test_classifiers_return_instruction_type(self):
        """Test that classifiers return InstructionType enum values."""
        manager = ArchitectureManager()
        
        classifier = manager.get_instruction_classifier("x86_64")
        result = classifier("mov")
        assert isinstance(result, InstructionType)
        
        classifier = manager.get_instruction_classifier("arm")
        result = classifier("ldr")
        assert isinstance(result, InstructionType)
        
        classifier = manager.get_instruction_classifier("mips")
        result = classifier("lw")
        assert isinstance(result, InstructionType)

    def test_classifiers_handle_unknown_instructions(self):
        """Test that classifiers handle unknown instructions gracefully."""
        manager = ArchitectureManager()
        
        # Test with each architecture
        for arch in ["x86", "x86_64", "arm", "arm64", "mips", "mips64"]:
            classifier = manager.get_instruction_classifier(arch)
            # Unknown instruction should return OTHER type
            result = classifier("notarealinstruction")
            assert result == InstructionType.OTHER


class TestArchitectureManagerCorrectMapping:
    """Tests to verify correct architecture-to-classifier mapping."""

    def test_x86_and_x86_64_share_classifier(self):
        """Test that x86 and x86-64 use the same classifier."""
        manager = ArchitectureManager()
        
        classifier_x86 = manager.get_instruction_classifier("x86")
        classifier_x86_64 = manager.get_instruction_classifier("x86_64")
        
        # Should classify instructions the same way
        assert classifier_x86("mov") == classifier_x86_64("mov")
        assert classifier_x86("jmp") == classifier_x86_64("jmp")
        assert classifier_x86("push") == classifier_x86_64("push")

    def test_arm_and_arm64_share_classifier(self):
        """Test that ARM and ARM64 use the same classifier."""
        manager = ArchitectureManager()
        
        classifier_arm = manager.get_instruction_classifier("arm")
        classifier_arm64 = manager.get_instruction_classifier("arm64")
        
        # Should classify common instructions the same way
        assert classifier_arm("mov") == classifier_arm64("mov")
        assert classifier_arm("ldr") == classifier_arm64("ldr")
        assert classifier_arm("bl") == classifier_arm64("bl")

    def test_mips_and_mips64_share_classifier(self):
        """Test that MIPS and MIPS64 use the same classifier."""
        manager = ArchitectureManager()
        
        classifier_mips = manager.get_instruction_classifier("mips")
        classifier_mips64 = manager.get_instruction_classifier("mips64")
        
        # Should classify common instructions the same way
        assert classifier_mips("lw") == classifier_mips64("lw")
        assert classifier_mips("jal") == classifier_mips64("jal")
        assert classifier_mips("add") == classifier_mips64("add")

    def test_different_architectures_differ(self):
        """Test that different architectures classify differently."""
        manager = ArchitectureManager()
        
        classifier_x86 = manager.get_instruction_classifier("x86_64")
        classifier_arm = manager.get_instruction_classifier("arm")
        classifier_mips = manager.get_instruction_classifier("mips")
        
        # ldr is MOVE on ARM but OTHER on x86
        assert classifier_arm("ldr") == InstructionType.MOVE
        assert classifier_x86("ldr") == InstructionType.OTHER
        
        # lw is MOVE on MIPS but OTHER on x86 and ARM
        assert classifier_mips("lw") == InstructionType.MOVE
        assert classifier_x86("lw") == InstructionType.OTHER
        assert classifier_arm("lw") == InstructionType.OTHER
