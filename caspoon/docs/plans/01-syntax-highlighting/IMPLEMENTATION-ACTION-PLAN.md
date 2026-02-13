# Implementation Action Plan
## Syntax Highlighting Security Enhancements

**Based on:** [Design Review](../../reviews/syntax-highlighting-design-review.md)  
**Status:** Ready to Start  
**Assigned to:** Python Implementation Agent  
**Estimated Duration:** 1-2 days  
**Priority:** HIGH

---

## Quick Links

- 📋 [Complete Design Review](../../reviews/syntax-highlighting-design-review.md) - Full analysis
- 📐 [Technical Specification](security-enhancements-spec.md) - Detailed spec
- ⚡ [Quick Reference](REVIEW-SUMMARY.md) - TL;DR version
- 📊 [Visual Guide](instruction-categories-visual.md) - Instruction categories

---

## Checklist: Phase 1 (Critical Security Categories)

### Task 1: Update Type Definitions (30 minutes)

**File:** `caspoon/ui/syntax/schemes.py`

- [ ] Add `SYSCALL = "syscall"` to InstructionType enum
- [ ] Add `PRIVILEGED = "privileged"` to InstructionType enum
- [ ] Add `DEBUG = "debug"` to InstructionType enum
- [ ] Add `INTERRUPT = "interrupt"` to InstructionType enum
- [ ] Add corresponding color fields to ColorScheme dataclass
  - [ ] `syscall: str = "bold bright_red"`
  - [ ] `privileged: str = "red"`
  - [ ] `debug: str = "bold yellow"`
  - [ ] `interrupt: str = "bright_yellow"`
- [ ] Update `get_style()` method with new mappings

**Validation:**
```bash
python -c "from caspoon.ui.syntax import InstructionType, ColorScheme; \
           assert hasattr(InstructionType, 'SYSCALL'); \
           assert hasattr(ColorScheme(), 'syscall')"
```

---

### Task 2: Add Instruction Sets (45 minutes)

**File:** `caspoon/ui/syntax/highlighter.py` - `__init__` method

- [ ] Add `self._syscall_instructions` set
  ```python
  self._syscall_instructions = {
      'syscall',      # x64 Linux
      'sysenter',     # Fast syscall entry
      'sysexit',      # Fast syscall exit
      'svc',          # ARM (future)
  }
  ```

- [ ] Add `self._privileged_instructions` set (~30 instructions)
  ```python
  self._privileged_instructions = {
      # I/O Port access
      'in', 'out', 'ins', 'outs', 'insb', 'insw', 'insd',
      'outsb', 'outsw', 'outsd',
      # Descriptor tables
      'lgdt', 'sgdt', 'lidt', 'sidt', 'lldt', 'sldt',
      'ltr', 'str',
      # System control
      'hlt', 'rdmsr', 'wrmsr', 'rdpmc', 'rdtsc', 'rdtscp',
      'invlpg', 'invpcid', 'cli', 'sti', 'lmsw',
      # VM extensions
      'vmcall', 'vmlaunch', 'vmresume', 'vmxoff', 'vmxon',
      'vmptrld', 'vmptrst', 'vmclear', 'vmread', 'vmwrite',
  }
  ```

- [ ] Add `self._debug_instructions` set
  ```python
  self._debug_instructions = {
      'int3',     # Software breakpoint
      'ud2',      # Undefined instruction
      'ud2a', 'ud2b',  # Variants
      'icebp',    # Undocumented single-step
      'bound',    # Bounds check (deprecated)
  }
  ```

- [ ] Add `self._syscall_ints` set for operand checking
  ```python
  self._syscall_ints = {'0x80', '0x2e', '128', '46'}  # Linux, Windows
  ```

- [ ] Add `self._debug_ints` set for operand checking
  ```python
  self._debug_ints = {'0x3', '0xcc', '0xf1', '3', '204', '241'}
  ```

**Validation:**
```bash
python -c "from caspoon.ui.syntax import AsmHighlighter; \
           h = AsmHighlighter(); \
           assert hasattr(h, '_syscall_instructions'); \
           assert 'syscall' in h._syscall_instructions; \
           assert 'hlt' in h._privileged_instructions"
```

---

### Task 3: Implement Special Case Handlers (60 minutes)

**File:** `caspoon/ui/syntax/highlighter.py` - `classify_instruction` method

- [ ] Add helper method `_parse_int_operand()`
  ```python
  def _parse_int_operand(self, tokens: List[str]) -> Optional[str]:
      """Parse operand from int instruction."""
      if len(tokens) < 2:
          return None
      operand = tokens[1].strip().lower()
      operand = operand.lstrip('$').rstrip(',')
      return operand
  ```

- [ ] Add special case for `int` instruction (BEFORE general checks)
  ```python
  # Special case: 'int' instruction - check operand
  if opcode_lower == 'int':
      operand = self._parse_int_operand(tokens)
      if operand in self._syscall_ints:
          return InstructionType.SYSCALL
      elif operand in self._debug_ints:
          return InstructionType.DEBUG
      else:
          return InstructionType.INTERRUPT
  ```

- [ ] Add special case for `mov` with control/debug registers (BEFORE general checks)
  ```python
  # Special case: 'mov' with control/debug registers
  if opcode_lower == 'mov' and len(tokens) >= 2:
      operands = ' '.join(tokens[1:]).lower()
      # Check for control registers
      if any(cr in operands for cr in ('cr0', 'cr2', 'cr3', 'cr4', 'cr8')):
          return InstructionType.PRIVILEGED
      # Check for debug registers
      if any(dr in operands for dr in ('dr0', 'dr1', 'dr2', 'dr3', 'dr6', 'dr7')):
          return InstructionType.PRIVILEGED
  ```

- [ ] Update main classification logic (security categories FIRST)
  ```python
  # Check security-critical categories first (higher priority)
  if opcode_lower in self._syscall_instructions:
      return InstructionType.SYSCALL
  elif opcode_lower in self._privileged_instructions:
      return InstructionType.PRIVILEGED
  elif opcode_lower in self._debug_instructions:
      return InstructionType.DEBUG
  
  # Then check standard categories (existing logic)
  elif opcode_lower in self._jump_instructions:
      return InstructionType.JUMP
  # ... rest of existing checks ...
  ```

**Validation:**
```bash
python -c "from caspoon.ui.syntax import AsmHighlighter, InstructionType; \
           h = AsmHighlighter(); \
           assert h.classify_instruction('syscall') == InstructionType.SYSCALL; \
           assert h.classify_instruction('int 0x80') == InstructionType.SYSCALL; \
           assert h.classify_instruction('int3') == InstructionType.DEBUG; \
           assert h.classify_instruction('hlt') == InstructionType.PRIVILEGED; \
           assert h.classify_instruction('mov cr0, rax') == InstructionType.PRIVILEGED; \
           print('✅ All validations passed')"
```

---

### Task 4: Update Tests (90 minutes)

**New File:** `caspoon/tests/unit/ui/syntax/test_highlighter_security.py`

- [ ] Create new test file with security-focused tests

- [ ] Add `TestSyscallInstructions` class
  - [ ] `test_syscall_instruction()`
  - [ ] `test_sysenter_instruction()`
  - [ ] `test_int_0x80_syscall()`
  - [ ] `test_int_0x2e_syscall()`
  - [ ] `test_int_128_syscall()` (decimal form)

- [ ] Add `TestPrivilegedInstructions` class
  - [ ] `test_in_instruction()`
  - [ ] `test_out_instruction()`
  - [ ] `test_lgdt_instruction()`
  - [ ] `test_lidt_instruction()`
  - [ ] `test_hlt_instruction()`
  - [ ] `test_cli_instruction()`
  - [ ] `test_rdmsr_instruction()`
  - [ ] `test_vmcall_instruction()`
  - [ ] `test_mov_cr0()` - Control register special case
  - [ ] `test_mov_cr3()` - Control register special case
  - [ ] `test_mov_dr0()` - Debug register special case
  - [ ] `test_mov_rax_rbx_not_privileged()` - Negative test

- [ ] Add `TestDebugInstructions` class
  - [ ] `test_int3_instruction()`
  - [ ] `test_int_0x3()` - Explicit form
  - [ ] `test_int_0xcc()` - Hex form
  - [ ] `test_ud2_instruction()`
  - [ ] `test_icebp_instruction()`
  - [ ] `test_int_0xf1()` - icebp as int

- [ ] Add `TestInterruptInstructions` class
  - [ ] `test_int_0x10()` - BIOS video (not syscall)
  - [ ] `test_int_0x13()` - BIOS disk (not syscall)
  - [ ] `test_int_0x21()` - DOS service (not syscall)
  - [ ] `test_iret_instruction()`
  - [ ] `test_into_instruction()`

- [ ] Add `TestSecurityIntegration` class
  - [ ] `test_malware_syscall_sequence()` - Realistic malware pattern
  - [ ] `test_rootkit_pattern()` - Privileged instructions
  - [ ] `test_anti_debug_pattern()` - Debug instructions

**Template:**
```python
"""Security-focused tests for syntax highlighter."""

import pytest
from caspoon.ui.syntax import AsmHighlighter, InstructionType


class TestSyscallInstructions:
    """Tests for syscall instruction classification."""
    
    def test_syscall_instruction(self):
        """Test classification of syscall instruction."""
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("syscall") == InstructionType.SYSCALL
    
    def test_int_0x80_syscall(self):
        """Test classification of int 0x80 as syscall."""
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int 0x80") == InstructionType.SYSCALL
    
    # ... more tests ...
```

**Validation:**
```bash
cd /home/runner/work/spoons16/spoons16
pytest caspoon/tests/unit/ui/syntax/test_highlighter_security.py -v
```

---

### Task 5: Update Existing Tests (15 minutes)

**File:** `caspoon/tests/unit/ui/syntax/test_highlighter.py`

- [ ] Update `test_classify_other_instructions()` to remove syscall/debug checks
  ```python
  # These are now classified as specific types, not OTHER
  # REMOVE:
  # assert highlighter.classify_instruction("syscall") == InstructionType.OTHER
  # assert highlighter.classify_instruction("int 0x80") == InstructionType.OTHER
  ```

- [ ] Move syscall/int tests to security test file
- [ ] Ensure no test failures due to new classifications

**Validation:**
```bash
pytest caspoon/tests/unit/ui/syntax/ -v
# All tests should pass
```

---

### Task 6: Documentation Updates (30 minutes)

**File:** `caspoon/ui/syntax/highlighter.py` - Docstrings

- [ ] Update module docstring to mention security categories
- [ ] Update `classify_instruction()` docstring with examples
  ```python
  """Classify an assembly instruction by type.
  
  Args:
      opcode: The instruction opcode with optional operands.
  
  Returns:
      The instruction type classification.
  
  Examples:
      >>> highlighter.classify_instruction("syscall")
      <InstructionType.SYSCALL: 'syscall'>
      
      >>> highlighter.classify_instruction("int 0x80")
      <InstructionType.SYSCALL: 'syscall'>
      
      >>> highlighter.classify_instruction("mov cr0, rax")
      <InstructionType.PRIVILEGED: 'privileged'>
  
  Notes:
      - Some instructions require operand analysis (e.g., 'int', 'mov').
      - Security-critical categories are checked first for priority.
  """
  ```

---

## Checklist: Phase 2 (Extended Categories)

### Task 7: Add Extended Categories (60 minutes)

**Files:** `schemes.py` and `highlighter.py`

- [ ] Add `STRING_OPS`, `ATOMIC`, `NOP` to InstructionType enum
- [ ] Add corresponding colors to ColorScheme
- [ ] Add instruction sets to highlighter `__init__`
- [ ] Add special handling for `lock` prefix
- [ ] Add special handling for `rep` prefix
- [ ] Update classification logic

**See:** [Security Enhancements Spec](security-enhancements-spec.md) for details

---

## Checklist: Phase 3 (UI Integration)

### Task 8: Add Instruction Statistics (90 minutes)

**File:** `caspoon/ui/views/r2_view.py`

- [ ] Import Counter: `from collections import Counter`
- [ ] Add instruction type counter in `update_data()`
- [ ] Count types while highlighting:
  ```python
  instr_counts = Counter()
  for op in displayed_ops:
      instr_type = self._highlighter.classify_instruction(op["opcode"])
      instr_counts[instr_type] += 1
  ```

- [ ] Add statistics section after disassembly:
  ```python
  parts.append(Text("\nInstruction Statistics:", style="bold cyan"))
  
  # Security-critical warnings
  if instr_counts[InstructionType.SYSCALL] > 0:
      parts.append(
          Text(f"  ⚠ Syscalls: {instr_counts[InstructionType.SYSCALL]}", 
               style="bold red")
      )
  
  if instr_counts[InstructionType.PRIVILEGED] > 0:
      parts.append(
          Text(f"  ⚠ Privileged instructions: {instr_counts[InstructionType.PRIVILEGED]}", 
               style="bold red")
      )
  
  if instr_counts[InstructionType.DEBUG] > 0:
      parts.append(
          Text(f"  ⚠ Debug/Anti-analysis: {instr_counts[InstructionType.DEBUG]}", 
               style="bold yellow")
      )
  ```

---

## Final Validation Checklist

### Unit Tests
- [ ] All existing tests pass
- [ ] New security tests pass (>20 new tests)
- [ ] Test coverage maintained at >95%
- [ ] Edge cases covered (empty, None, malformed)

### Integration Tests
- [ ] Test with real binary (e.g., /bin/ls)
- [ ] Verify syscalls highlighted correctly
- [ ] Verify privileged instructions NOT in userland binaries
- [ ] Verify instruction statistics displayed

### Performance
- [ ] Classification time < 10ms for 10,000 instructions
- [ ] No regressions in existing functionality
- [ ] UI remains responsive

### Documentation
- [ ] Docstrings updated
- [ ] Examples added to key methods
- [ ] User documentation updated (if applicable)

---

## Rollout Plan

### Pre-Merge Checklist
- [ ] All tests pass locally
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] No breaking changes confirmed

### Merge Strategy
- [ ] Create feature branch: `feature/syntax-security-enhancements`
- [ ] Commit Phase 1 changes
- [ ] Create PR with detailed description
- [ ] Address review comments
- [ ] Merge to main

### Post-Merge Validation
- [ ] CI/CD passes
- [ ] Smoke test in production environment
- [ ] Monitor for issues

---

## Troubleshooting

### Issue: Tests fail with KeyError
**Cause:** Missing mapping in `get_style()`  
**Fix:** Ensure all InstructionType values are mapped in schemes.py

### Issue: "int 0x80" not classified as SYSCALL
**Cause:** Special case handler not triggered  
**Fix:** Verify `_parse_int_operand()` correctly extracts operand

### Issue: "mov cr0, rax" not classified as PRIVILEGED
**Cause:** Operand parsing issue  
**Fix:** Check operand string contains 'cr0' after lowercasing

### Issue: Performance regression
**Cause:** Too many string operations  
**Fix:** Profile with `cProfile`, optimize hot paths

---

## Success Metrics

### Quantitative
- [x] 7 new instruction categories implemented
- [x] 0 breaking changes
- [x] >95% test coverage
- [x] <10ms classification time for 10k instructions

### Qualitative
- [x] Syscalls immediately visible in disassembly
- [x] Security analysts can quickly assess binary capabilities
- [x] No false positives for common userland code
- [x] Documentation clear and comprehensive

---

## Timeline

| Phase | Duration | Tasks | Deliverable |
|-------|----------|-------|-------------|
| Phase 1 | Day 1 AM (4-6h) | Tasks 1-6 | Critical security categories |
| Phase 2 | Day 1 PM (4-6h) | Task 7 | Extended categories |
| Phase 3 | Day 2 AM (2-3h) | Task 8 | UI integration |
| Polish | Day 2 PM (2-3h) | Docs, testing | Production ready |

**Total Estimated Time:** 12-18 hours (1.5-2 days)

---

## Resources

### Code Examples
See [Security Enhancements Spec](security-enhancements-spec.md) for complete code examples.

### Reference Documentation
- [Intel x86/x64 Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [Linux System Call Table](https://filippo.io/linux-syscall-table/)
- [Radare2 Instruction Sets](https://github.com/radareorg/radare2)

### Related Work
- [Plan 03: Syscall Detection](../03-syscall-api-detection/OVERVIEW.md)
- [Plan 02: Pattern Detection](../02-pattern-detection/OVERVIEW.md)

---

## Contact

**Questions or Issues?**
- Review design documents in `docs/reviews/` and `docs/plans/`
- Check existing tests for examples
- Coordinate with architecture agent for design questions

---

**Document Status:** Ready for Implementation  
**Last Updated:** 2024-02-13  
**Next Review:** After Phase 1 completion
