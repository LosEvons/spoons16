# Subtask 3: Architecture-Specific Schemes

**Status**: ✅ COMPLETED  
**Completion Date**: 2026-02-13  
**Related Changelog**: [2026-02-13-plan1-subtask3-architecture-schemes.md](../../changelogs/2026-02-13-plan1-subtask3-architecture-schemes.md)

## Objective
Extend syntax highlighting to support multiple architectures (ARM, MIPS, etc.) with appropriate color schemes and instruction classifications.

## Scope
- ARM (32-bit and 64-bit)
- MIPS architecture
- Extensible framework for future architectures

## Implementation Steps

### 1. Architecture Detection (2 hours)
**Location**: `caspoon/ui/syntax/arch_detector.py`

Detect architecture from ExecutableReport:
```python
def detect_architecture(report: ExecutableReport) -> str:
    """Detect architecture from report metadata."""
    arch = report.arch.lower()
    if 'x86' in arch or 'amd64' in arch:
        return 'x86_64'
    elif 'arm' in arch or 'aarch64' in arch:
        return 'arm' if report.bits == 32 else 'arm64'
    elif 'mips' in arch:
        return 'mips'
    return 'unknown'
```

### 2. ARM Instruction Database (3 hours)
**Location**: `caspoon/ui/syntax/instructions_arm.py`

ARM-specific instruction mappings:
- Branch instructions: b, bl, bx, blx, b<cond>
- Data processing: mov, mvn, add, sub, and, orr, eor
- Load/Store: ldr, str, ldm, stm, push, pop
- Compare: cmp, cmn, tst, teq
- ARM64 additions: br, blr, ret, adrp

### 3. MIPS Instruction Database (3 hours)
**Location**: `caspoon/ui/syntax/instructions_mips.py`

MIPS-specific instruction mappings:
- Branch: beq, bne, bgtz, blez, j, jal, jr
- Load/Store: lw, sw, lb, sb, lh, sh
- Arithmetic: add, addi, sub, mult, div
- Logic: and, andi, or, ori, xor, xori

### 4. Architecture Manager (3 hours)
**Location**: `caspoon/ui/syntax/arch_manager.py`

```python
class ArchitectureManager:
    def __init__(self):
        self.architectures = {
            'x86_64': X86_64Architecture(),
            'arm': ARMArchitecture(),
            'arm64': ARM64Architecture(),
            'mips': MIPSArchitecture(),
        }
    
    def get_highlighter(self, arch: str) -> AsmHighlighter:
        """Get appropriate highlighter for architecture."""
        arch_impl = self.architectures.get(arch)
        if not arch_impl:
            return self.architectures['x86_64']  # default fallback
        return AsmHighlighter(arch_impl)
```

### 5. Update R2View Integration (2 hours)
Modify r2_view.py to use architecture-aware highlighting:

```python
def update_data(self, report: ExecutableReport) -> None:
    arch = detect_architecture(report)
    highlighter = arch_manager.get_highlighter(arch)
    
    # Use highlighter for disassembly
    for op in main_ops:
        highlighted = highlighter.highlight_instruction(op.get("opcode", ""))
        parts.append(highlighted)
```

## Testing Strategy
- Test with ARM binaries
- Test with MIPS binaries
- Verify architecture detection works correctly
- Ensure fallback to x86_64 for unknown architectures

## Estimated Time
**13 hours total**

## Success Criteria
- [x] ARM instructions are correctly classified and highlighted
- [x] MIPS instructions are correctly classified and highlighted
- [x] Architecture is auto-detected from binary metadata
- [x] Graceful fallback for unsupported architectures
- [x] Extensible design for adding new architectures

## Implementation Summary

### Completed Components
✅ **Created `caspoon/ui/syntax/instructions_arm.py`** - 446 ARM/ARM64 instructions across 9 categories  
✅ **Created `caspoon/ui/syntax/instructions_mips.py`** - 381 MIPS/MIPS64 instructions across 8 categories  
✅ **Created `caspoon/ui/syntax/arch_detector.py`** - Automatic architecture detection from `ExecutableReport`  
✅ **Created `caspoon/ui/syntax/arch_manager.py`** - Centralized architecture-specific classifier management  
✅ **Enhanced `caspoon/ui/views/r2_view.py`** - Integrated architecture detection and automatic highlighter selection  
✅ **Comprehensive test suite** - 163 tests with 100% coverage

### Architecture Support Matrix

| Architecture | Instructions | Instruction Types | Status |
|-------------|-------------|------------------|---------|
| x86/x86_64  | 354         | 9 types          | ✅ Complete |
| ARM/ARM64   | 446         | 9 types          | ✅ Complete |
| MIPS/MIPS64 | 381         | 8 types          | ✅ Complete |

### Key Features Implemented
- **Auto-detection**: Automatically detects architecture from binary metadata
- **Fallback**: Gracefully defaults to x86_64 for unknown architectures
- **Extensible**: Easy to add new architectures following established patterns
- **Backward Compatible**: No breaking changes to existing API

## Next Steps
✅ Completed - Proceed to Subtask 4: Interactive Navigation (NOT YET STARTED)
