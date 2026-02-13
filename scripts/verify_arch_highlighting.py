#!/usr/bin/env python3
"""Verification script for architecture-specific syntax highlighting implementation.

This script verifies that:
1. All architecture instruction databases are properly structured
2. Architecture detection works correctly
3. Architecture manager provides correct classifiers
4. Highlighter accepts and uses architecture-specific classifiers
5. Backward compatibility is maintained
"""

import sys


def verify_instruction_databases():
    """Verify that all instruction databases are properly structured."""
    print("\n=== Verifying Instruction Databases ===")
    
    from caspoon.ui.syntax.schemes import InstructionType
    from caspoon.ui.syntax import instructions
    from caspoon.ui.syntax import instructions_arm
    from caspoon.ui.syntax import instructions_mips
    
    databases = [
        ("x86/x64", instructions.X86_64_INSTRUCTIONS),
        ("ARM", instructions_arm.ARM_INSTRUCTIONS),
        ("MIPS", instructions_mips.MIPS_INSTRUCTIONS),
    ]
    
    all_ok = True
    
    for name, db in databases:
        # Check that all keys are InstructionType enums
        for key in db.keys():
            if not isinstance(key, InstructionType):
                print(f"  ✗ {name}: Invalid key type: {type(key)}")
                all_ok = False
                continue
        
        # Check that all values are sets
        for key, value in db.items():
            if not isinstance(value, set):
                print(f"  ✗ {name}: Value for {key} is not a set: {type(value)}")
                all_ok = False
                continue
        
        # Count instructions
        total_instructions = sum(len(v) for v in db.values())
        print(f"  ✓ {name}: {len(db)} categories, {total_instructions} instructions")
    
    return all_ok


def verify_architecture_detection():
    """Verify architecture detection works correctly."""
    print("\n=== Verifying Architecture Detection ===")
    
    from caspoon.core.models import ExecutableReport
    from caspoon.ui.syntax.arch_detector import detect_architecture
    
    test_cases = [
        ("x86_64", "x86_64"),
        ("amd64", "x86_64"),
        ("i386", "x86"),
        ("arm", "arm"),
        ("aarch64", "arm64"),
        ("mips", "mips"),
        ("mips64", "mips64"),
        ("unknown", "unknown"),
    ]
    
    all_ok = True
    
    for input_arch, expected in test_cases:
        report = ExecutableReport(path="/test", arch=input_arch)
        detected = detect_architecture(report)
        
        if detected == expected:
            print(f"  ✓ {input_arch:15} -> {detected}")
        else:
            print(f"  ✗ {input_arch:15} -> {detected} (expected: {expected})")
            all_ok = False
    
    return all_ok


def verify_architecture_manager():
    """Verify architecture manager provides correct classifiers."""
    print("\n=== Verifying Architecture Manager ===")
    
    from caspoon.ui.syntax.arch_manager import (
        get_instruction_classifier,
        supports_architecture,
        get_supported_architectures,
    )
    from caspoon.ui.syntax.schemes import InstructionType
    
    # Check supported architectures
    supported = get_supported_architectures()
    print(f"  Supported: {', '.join(supported)}")
    
    # Test getting classifiers
    all_ok = True
    
    for arch in supported:
        classifier = get_instruction_classifier(arch)
        
        # Test that classifier returns InstructionType
        result = classifier("mov")
        
        if isinstance(result, InstructionType):
            print(f"  ✓ {arch:10} classifier works")
        else:
            print(f"  ✗ {arch:10} classifier returned {type(result)}")
            all_ok = False
    
    # Test unknown architecture (should fallback to x86_64)
    unknown_classifier = get_instruction_classifier("unknown")
    result = unknown_classifier("mov")
    
    if isinstance(result, InstructionType):
        print(f"  ✓ unknown    classifier falls back correctly")
    else:
        print(f"  ✗ unknown    classifier fallback failed")
        all_ok = False
    
    return all_ok


def verify_highlighter():
    """Verify highlighter accepts and uses architecture-specific classifiers."""
    print("\n=== Verifying Highlighter ===")
    
    from caspoon.ui.syntax import AsmHighlighter
    from caspoon.ui.syntax.arch_manager import get_instruction_classifier
    
    all_ok = True
    
    # Test default behavior (backward compatibility)
    try:
        highlighter = AsmHighlighter()
        result = highlighter.highlight_instruction("mov rax, rbx")
        print("  ✓ Default highlighter (x86_64) works")
    except Exception as e:
        print(f"  ✗ Default highlighter failed: {e}")
        all_ok = False
    
    # Test with explicit classifier
    for arch in ["x86_64", "arm", "mips"]:
        try:
            classifier = get_instruction_classifier(arch)
            highlighter = AsmHighlighter(instruction_classifier=classifier)
            result = highlighter.highlight_instruction("mov r0, r1")
            print(f"  ✓ {arch:10} highlighter works")
        except Exception as e:
            print(f"  ✗ {arch:10} highlighter failed: {e}")
            all_ok = False
    
    return all_ok


def verify_backward_compatibility():
    """Verify backward compatibility with existing code."""
    print("\n=== Verifying Backward Compatibility ===")
    
    from caspoon.ui.syntax import (
        AsmHighlighter,
        InstructionType,
        get_instruction_type,
    )
    
    all_ok = True
    
    # Test that old code still works
    try:
        # Creating highlighter without any parameters
        highlighter = AsmHighlighter()
        
        # Using get_instruction_type directly (old way)
        instr_type = get_instruction_type("mov")
        
        # Highlighting instruction (old way)
        result = highlighter.highlight_instruction("mov rax, rbx", "0x1000")
        
        print("  ✓ Old API still works")
    except Exception as e:
        print(f"  ✗ Old API failed: {e}")
        all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("Architecture-Specific Syntax Highlighting Verification")
    print("="*60)
    
    results = []
    
    results.append(("Instruction Databases", verify_instruction_databases()))
    results.append(("Architecture Detection", verify_architecture_detection()))
    results.append(("Architecture Manager", verify_architecture_manager()))
    results.append(("Highlighter", verify_highlighter()))
    results.append(("Backward Compatibility", verify_backward_compatibility()))
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All verification checks passed!\n")
        return 0
    else:
        print("\n✗ Some verification checks failed.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
