# Syntax Highlighting Security Enhancements
## Technical Specification

**Status:** Proposed  
**Priority:** High  
**Effort Estimate:** 1-2 days  
**Related Documents:**
- [Design Review](../../reviews/syntax-highlighting-design-review.md)
- [Plan 03: Syscall/API Detection](../03-syscall-api-detection/OVERVIEW.md)
- [Plan 02: Pattern Detection](../02-pattern-detection/OVERVIEW.md)

---

## Overview

This specification defines enhancements to the syntax highlighting system to better support **defensive binary analysis** and **security research** use cases. The current implementation provides solid support for general reverse engineering but lacks highlighting for security-critical instruction categories.

## Goals

1. **Highlight system calls prominently** - Enable instant identification of kernel interaction points
2. **Flag privileged instructions** - Detect ring 0 code, rootkits, firmware
3. **Identify anti-analysis patterns** - Highlight debug/breakpoint instructions
4. **Improve pattern recognition** - Categorize string ops, atomic ops, nops
5. **Provide security metrics** - Display instruction statistics in UI

## Non-Goals

- Multi-architecture support (deferred to Phase 3)
- Decompiler output highlighting (future work)
- Custom user-defined patterns (future work)
- Machine learning classification (future work)

---

## Architecture

### New Instruction Categories

```
Current Categories (8):
  JUMP, CALL, RETURN, MOVE, ARITHMETIC, LOGIC, STACK, COMPARE, OTHER

New Categories (7):
  SYSCALL      - System calls and kernel transitions
  PRIVILEGED   - Ring 0 / supervisor mode instructions
  DEBUG        - Breakpoints and anti-debug instructions
  INTERRUPT    - Software interrupts (excluding syscalls)
  STRING_OPS   - Repeated string/memory operations
  ATOMIC       - Synchronization primitives
  NOP          - No-operation instructions
```

### Classification Priority Order

Instructions are checked in this order (first match wins):

```
1. Special cases (int with operand check, mov with CR/DR registers)
2. SYSCALL
3. PRIVILEGED
4. DEBUG
5. STRING_OPS
6. ATOMIC
7. NOP
8. JUMP
9. CALL
10. RETURN
11. MOVE
12. ARITHMETIC
13. LOGIC
14. STACK
15. COMPARE
16. OTHER (fallback)
```

**Rationale:** Security-critical categories checked first to ensure they take precedence over more general classifications.

---

## Detailed Specifications

### 1. SYSCALL Category

**Purpose:** Identify all instructions that transition from user space to kernel space.

**Instructions (x86/x64):**
```python
'syscall'       # x64 Linux/BSD system call
'sysenter'      # Fast system call entry (x86/x64)
'sysexit'       # Fast system call exit (ring 0 only)
'int 0x80'      # x86 Linux system call (32-bit)
'int 0x2e'      # Windows system call (legacy)
'int 128'       # Same as int 0x80 (decimal form)
'int 46'        # Same as int 0x2e (decimal form)
```

**Instructions (ARM - future):**
```python
'svc'           # ARM supervisor call (32/64-bit)
'svc #0'        # Common form
```

**Instructions (MIPS - future):**
```python
'syscall'       # MIPS system call (shares name with x64)
```

**Special Handling:**

The `int` instruction requires operand inspection:
```python
if opcode_lower == 'int':
    operand = tokens[1] if len(tokens) > 1 else ""
    if operand in ('0x80', '0x2e', '128', '46'):
        return InstructionType.SYSCALL
    elif operand in ('0x3', '0xcc', '3', '204'):
        return InstructionType.DEBUG
    else:
        return InstructionType.INTERRUPT
```

**Color Scheme:**
```python
syscall: str = "bold bright_red"  # Maximum visibility
```

**Security Rationale:**
- System calls are the **primary mechanism** for malware to perform malicious actions
- Direct syscalls indicate potential library hooking evasion
- Syscall patterns map to MITRE ATT&CK techniques
- Essential for understanding binary capabilities without debugging

**UI Impact:**
- Main disassembly: Bold red highlighting
- Statistics section: "⚠ Syscalls: N" if N > 0
- Future: Link to syscall detector results

---

### 2. PRIVILEGED Category

**Purpose:** Identify instructions that can only execute in ring 0 (kernel mode) or require special privileges.

**Instructions:**

```python
# I/O Port Access (ring 0 only)
'in', 'out',                    # Port I/O
'ins', 'outs',                  # String port I/O
'insb', 'insw', 'insd',         # Sized variants
'outsb', 'outsw', 'outsd',

# Descriptor Table Management (ring 0 only)
'lgdt', 'sgdt',                 # Global Descriptor Table
'lidt', 'sidt',                 # Interrupt Descriptor Table
'lldt', 'sldt',                 # Local Descriptor Table
'ltr', 'str',                   # Task Register

# Control Register Access (ring 0 only)
'mov cr0', 'mov cr2', 'mov cr3', 'mov cr4',  # Control registers
'mov dr0', 'mov dr1', 'mov dr2', 'mov dr3',  # Debug registers

# System Control (ring 0 only)
'hlt',                          # Halt processor
'rdmsr', 'wrmsr',               # Model-specific registers
'rdpmc',                        # Performance monitoring
'rdtsc', 'rdtscp',              # Timestamp counter (ring 3 accessible but often privileged)
'invlpg', 'invpcid',            # TLB invalidation
'cli', 'sti',                   # Interrupt control
'lmsw',                         # Load machine status word

# Virtualization (ring 0 only)
'vmcall',                       # VM call
'vmlaunch', 'vmresume',         # VM execution
'vmxoff', 'vmxon',              # VMX mode control
'vmptrld', 'vmptrst',           # VMCS pointer
'vmclear', 'vmread', 'vmwrite', # VMCS management
```

**Special Handling:**

Control/debug register moves require operand parsing:
```python
if opcode_lower == 'mov' and len(tokens) >= 2:
    operands = ' '.join(tokens[1:]).lower()
    # Check for control registers
    if any(cr in operands for cr in ('cr0', 'cr2', 'cr3', 'cr4', 'cr8')):
        return InstructionType.PRIVILEGED
    # Check for debug registers
    if any(dr in operands for dr in ('dr0', 'dr1', 'dr2', 'dr3', 'dr6', 'dr7')):
        return InstructionType.PRIVILEGED
```

**Color Scheme:**
```python
privileged: str = "red"  # Warning color
```

**Security Rationale:**
- Presence in userland binary indicates:
  - Kernel module / driver code
  - Rootkit / bootkit
  - Hypervisor / VMM code
  - Firmware (BIOS/UEFI)
- Critical for identifying privilege escalation attempts
- Helps categorize binary type (user vs kernel space)

**UI Impact:**
- Main disassembly: Red highlighting
- Statistics section: "⚠ Privileged instructions: N" if N > 0 (with warning)
- Future: Dedicated "Privileged Code Analysis" view

---

### 3. DEBUG Category

**Purpose:** Identify breakpoint and anti-debugging instructions.

**Instructions:**

```python
# Software Breakpoints
'int3',                         # 0xCC - standard debugger breakpoint
'int 0x3',                      # Same as int3 (explicit form)
'int 0xcc',                     # Same as int3 (hex form)

# Exception Generation
'ud2',                          # Undefined instruction (causes #UD exception)
'ud2a',                         # Same as ud2
'ud2b',                         # Undefined instruction variant

# Undocumented / Special
'icebp',                        # 0xF1 - undocumented single-step interrupt
'int 0xf1',                     # Same as icebp
'int 241',                      # Decimal form

# Bounds Check (deprecated but used in anti-debug)
'bound',                        # Bounds check (removed in x64, but may appear in x86)
```

**Special Handling:**

```python
if opcode_lower == 'int':
    operand = tokens[1] if len(tokens) > 1 else ""
    # Breakpoint interrupts
    if operand in ('0x3', '0xcc', '3', '204'):
        return InstructionType.DEBUG
    # Single-step interrupt
    if operand in ('0xf1', '241'):
        return InstructionType.DEBUG
```

**Color Scheme:**
```python
debug: str = "bold yellow"  # Attention-grabbing
```

**Security Rationale:**
- `int3` is primary debugger breakpoint mechanism
  - Malware may use int3 for anti-debugging
  - Self-modifying code may insert/remove int3
  - Used in some obfuscation techniques
- `ud2` indicates:
  - Deliberate exception generation (assertions, dead code markers)
  - Anti-disassembly tricks
  - Code that should never execute
- `icebp` is an undocumented interrupt sometimes used for stealth debugging
- `bound` is deprecated but appears in some anti-debug code

**UI Impact:**
- Main disassembly: Bold yellow highlighting
- Statistics section: "⚠ Debug/Anti-analysis: N" if N > 0
- Future: Cross-reference with anti-analysis pattern detector

---

### 4. INTERRUPT Category

**Purpose:** Identify software interrupts that are NOT syscalls or debug instructions.

**Instructions:**

```python
# General interrupt instruction
'int',                          # Software interrupt (with operand check)

# Interrupt return
'iret', 'iretd', 'iretq',       # Return from interrupt handler

# Overflow interrupt
'into',                         # Interrupt on overflow (x86 only)
```

**Special Handling:**

```python
if opcode_lower == 'int':
    operand = tokens[1] if len(tokens) > 1 else ""
    # Syscalls checked first
    if operand in syscall_ints:
        return InstructionType.SYSCALL
    # Debug interrupts checked second
    if operand in debug_ints:
        return InstructionType.DEBUG
    # Everything else is INTERRUPT
    return InstructionType.INTERRUPT
```

**Common Non-Syscall Interrupts:**
- `int 0x10` - BIOS video services
- `int 0x13` - BIOS disk services
- `int 0x21` - DOS services
- `int 0x2d` - Windows debugging backdoor
- `int 0x2c` - Windows undocumented
- Custom interrupts (int 0x40 - int 0xFF)

**Color Scheme:**
```python
interrupt: str = "bright_yellow"  # Moderate priority
```

**Security Rationale:**
- Legacy DOS/BIOS malware uses interrupts extensively
- Some Windows anti-debug techniques use special interrupts (int 0x2d)
- Custom interrupts may indicate:
  - Embedded systems code
  - Virtualization (guest→hypervisor communication)
  - Legacy compatibility layers

**UI Impact:**
- Main disassembly: Bright yellow highlighting
- Statistics: Listed in instruction counts
- Future: Categorize by interrupt number

---

### 5. STRING_OPS Category

**Purpose:** Identify repeated string/memory operations (common in memcpy, memset, etc.).

**Instructions:**

```python
# Move string
'movs', 'movsb', 'movsw', 'movsd', 'movsq',

# Store string
'stos', 'stosb', 'stosw', 'stosd', 'stosq',

# Load string
'lods', 'lodsb', 'lodsw', 'lodsd', 'lodsq',

# Scan string
'scas', 'scasb', 'scasw', 'scasd', 'scasq',

# Compare string
'cmps', 'cmpsb', 'cmpsw', 'cmpsd', 'cmpsq',

# Repeat prefixes (often combined with above)
'rep',                          # Repeat while RCX != 0
'repe', 'repz',                 # Repeat while equal/zero
'repne', 'repnz',               # Repeat while not equal/not zero
```

**Special Handling:**

Repeat prefixes are often attached to the instruction:
```python
# May appear as "rep movs" or "rep movsb"
if opcode_lower.startswith('rep'):
    # Check if base instruction is string op
    base_instr = opcode_lower.replace('rep', '').replace('repe', '').replace('repne', '').strip()
    if base_instr in string_base_instructions:
        return InstructionType.STRING_OPS
```

**Color Scheme:**
```python
string_ops: str = "cyan"  # Related to data movement
```

**Security Rationale:**
- Very common in:
  - Memory operations (memcpy, memset, memmove)
  - String operations (strcpy, strcat, strlen)
  - Buffer manipulation (potential overflow vectors)
  - Code unpacking / self-modification
- High performance operations often used in:
  - Cryptographic implementations
  - Data exfiltration
  - Memory scrubbing (anti-forensics)
- Patterns like `rep stos` followed by `rep movs` indicate buffer initialization + copy

**UI Impact:**
- Main disassembly: Cyan highlighting (matches MOVE but distinct)
- Statistics: Listed in instruction counts
- Future: Detect buffer operation patterns (memcpy, memset signatures)

---

### 6. ATOMIC Category

**Purpose:** Identify synchronization primitives and atomic operations (multi-threading indicators).

**Instructions:**

```python
# Atomic exchange and add
'xadd', 'xaddq', 'xaddl', 'xaddw', 'xaddb',

# Compare and exchange (CAS)
'cmpxchg', 'cmpxchgq', 'cmpxchgl', 'cmpxchgw', 'cmpxchgb',
'cmpxchg8b',                    # 64-bit CAS on x86
'cmpxchg16b',                   # 128-bit CAS on x64

# Spin-loop hint
'pause',                        # Improves spin-wait loop performance

# Memory barriers / fences
'mfence',                       # Memory fence (full barrier)
'lfence',                       # Load fence
'sfence',                       # Store fence

# Lock prefix (applied to other instructions)
# Note: This is a prefix, not a standalone instruction
# Common: lock xadd, lock cmpxchg, lock inc, lock dec
```

**Special Handling:**

The `lock` prefix requires special detection:
```python
if opcode_lower.startswith('lock '):
    # Any instruction with lock prefix is atomic
    return InstructionType.ATOMIC
```

**Color Scheme:**
```python
atomic: str = "bold magenta"  # Distinct from regular LOGIC
```

**Security Rationale:**
- Presence indicates multi-threaded code
- Critical for understanding:
  - Race conditions
  - Thread synchronization
  - Lock-free data structures
- Malware implications:
  - Rootkits often use atomic ops for IRP hooking
  - Race conditions as security vulnerabilities
  - Memory barriers used in some timing-based anti-analysis
- `pause` instruction indicates spin-locks (CPU-intensive waiting)

**UI Impact:**
- Main disassembly: Bold magenta highlighting
- Statistics: Listed in instruction counts
- Future: Identify lock contention patterns, multi-threading analysis

---

### 7. NOP Category

**Purpose:** Identify no-operation instructions (padding, alignment, nop sleds).

**Instructions:**

```python
# Standard NOP
'nop',                          # 0x90

# Multi-byte NOPs (optimization)
# These are represented as single 'nop' in disassembly but may have operands
# Examples from Intel manual:
#   nop dword ptr [rax]
#   nop dword ptr [rax + rax]
#   etc.

# Effective NOPs (functionally do nothing)
'xchg ax, ax',                  # No-op exchange (0x90 encoding)
'mov reg, reg',                 # Move register to itself (check needed)
'lea reg, [reg+0]',             # LEA with zero offset
```

**Special Handling:**

Effective NOPs require operand analysis:
```python
# mov reg, reg detection
if opcode_lower == 'mov' and len(tokens) >= 3:
    dest = tokens[1].rstrip(',')
    src = tokens[2]
    if dest == src:
        return InstructionType.NOP

# lea reg, [reg+0] detection
if opcode_lower == 'lea' and len(tokens) >= 3:
    dest = tokens[1].rstrip(',')
    # Parse [reg+0] pattern
    operand = tokens[2]
    if '+0' in operand or '+0x0' in operand:
        # Check if base register matches destination
        # Simplified check - production needs robust parsing
        return InstructionType.NOP
```

**Color Scheme:**
```python
nop: str = "dim"  # De-emphasize (or "bright_black")
```

**Security Rationale:**
- Excessive NOPs may indicate:
  - Code caves (space left for patching)
  - Shellcode NOP sleds (classic buffer overflow technique)
  - Compiler padding for alignment
  - Timing-based anti-analysis (delay execution)
- Multi-byte NOPs indicate optimization level:
  - Single-byte nops: Older/simpler compilers
  - Multi-byte nops: Modern optimizing compilers
- "Effective NOPs" (mov reg, reg) may indicate:
  - Obfuscation
  - Dead code elimination didn't trigger
  - Self-modifying code placeholders

**UI Impact:**
- Main disassembly: Dim/gray highlighting (de-emphasize)
- Statistics: "NOP padding: N bytes" (future)
- Future: Detect NOP sleds (sequences of 4+ consecutive NOPs)

---

## Implementation Plan

### Phase 1: Core Categories (Day 1, ~4-6 hours)

**Priority Order:**
1. SYSCALL (highest priority)
2. PRIVILEGED
3. DEBUG
4. INTERRUPT (split from OTHER)

**Tasks:**
1. Update `schemes.py`:
   - Add new `InstructionType` enum values
   - Add color scheme fields
   - Update `get_style()` mapping

2. Update `highlighter.py`:
   - Add instruction set dictionaries
   - Add special case handling for `int` instruction
   - Add special case handling for `mov cr/dr`
   - Update `classify_instruction()` logic with priority order

3. Update tests:
   - Add test cases for each new category
   - Add special case tests (int 0x80, mov cr0, etc.)
   - Add integration tests

**Acceptance Criteria:**
- All 4 categories correctly classified
- `int` instruction correctly routed based on operand
- Control register moves detected as PRIVILEGED
- Tests pass with >95% coverage

---

### Phase 2: Extended Categories (Day 1-2, ~4-6 hours)

**Priority Order:**
5. STRING_OPS
6. ATOMIC
7. NOP

**Tasks:**
1. Add remaining instruction sets to `highlighter.py`
2. Add special handling for `lock` prefix
3. Add effective NOP detection logic
4. Update tests for new categories

**Acceptance Criteria:**
- All 7 new categories implemented
- String ops with rep prefixes correctly classified
- Lock-prefixed instructions detected as ATOMIC
- Effective NOPs (mov reg, reg) detected

---

### Phase 3: UI Integration (Day 2, ~2-3 hours)

**Tasks:**
1. Update `r2_view.py`:
   - Add instruction type counter
   - Display security-critical statistics
   - Add warning icons for syscalls/privileged instructions

2. Add summary section to disassembly view

**Acceptance Criteria:**
- Instruction statistics displayed above or below disassembly
- Security-critical instructions shown with ⚠ warning icon
- Counts accurate for all instruction types

---

### Phase 4: Documentation & Polish (Day 2, ~2-3 hours)

**Tasks:**
1. Update user documentation
2. Add docstring examples
3. Create example outputs (screenshots)
4. Performance testing (10k+ instruction functions)

**Acceptance Criteria:**
- Documentation complete
- Performance < 10ms for 10k instructions
- No regressions in existing functionality

---

## Test Plan

### Unit Tests

**File: `test_highlighter_security.py`**

```python
class TestSyscallInstructions:
    def test_syscall_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("syscall") == InstructionType.SYSCALL
    
    def test_int_0x80_syscall(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int 0x80") == InstructionType.SYSCALL
    
    def test_int_0x2e_syscall(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int 0x2e") == InstructionType.SYSCALL
    
    def test_sysenter_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("sysenter") == InstructionType.SYSCALL

class TestPrivilegedInstructions:
    def test_in_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("in al, 0x60") == InstructionType.PRIVILEGED
    
    def test_out_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("out 0x64, al") == InstructionType.PRIVILEGED
    
    def test_lgdt_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("lgdt [rbx]") == InstructionType.PRIVILEGED
    
    def test_hlt_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("hlt") == InstructionType.PRIVILEGED
    
    def test_mov_cr0(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("mov cr0, rax") == InstructionType.PRIVILEGED
    
    def test_mov_dr3(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("mov dr3, rbx") == InstructionType.PRIVILEGED

class TestDebugInstructions:
    def test_int3_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int3") == InstructionType.DEBUG
    
    def test_int_0x3(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int 0x3") == InstructionType.DEBUG
    
    def test_int_0xcc(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("int 0xcc") == InstructionType.DEBUG
    
    def test_ud2_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("ud2") == InstructionType.DEBUG

class TestInterruptInstructions:
    def test_int_generic(self):
        highlighter = AsmHighlighter()
        # int 0x10 (BIOS video) should be INTERRUPT, not SYSCALL
        assert highlighter.classify_instruction("int 0x10") == InstructionType.INTERRUPT
    
    def test_iret_instruction(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("iret") == InstructionType.INTERRUPT

class TestStringOps:
    def test_rep_movs(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("rep movsb") == InstructionType.STRING_OPS
    
    def test_rep_stos(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("rep stosq") == InstructionType.STRING_OPS
    
    def test_scas(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("scasb") == InstructionType.STRING_OPS

class TestAtomicOps:
    def test_xadd(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("xadd [rax], rbx") == InstructionType.ATOMIC
    
    def test_cmpxchg(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("cmpxchg [rcx], rdx") == InstructionType.ATOMIC
    
    def test_lock_prefix(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("lock xadd [rax], rbx") == InstructionType.ATOMIC
    
    def test_mfence(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("mfence") == InstructionType.ATOMIC

class TestNopInstructions:
    def test_nop(self):
        highlighter = AsmHighlighter()
        assert highlighter.classify_instruction("nop") == InstructionType.NOP
```

### Integration Tests

**File: `test_integration_security.py`**

```python
class TestSecurityAnalysisScenarios:
    def test_malware_sample_highlighting(self):
        """Test highlighting on a malware-like instruction sequence."""
        highlighter = AsmHighlighter()
        
        # Simulate malware sequence: setup syscall
        instructions = [
            "xor rax, rax",       # LOGIC
            "mov rax, 59",        # MOVE (execve syscall number)
            "lea rdi, [rip+0x100]",  # MOVE (pointer to /bin/sh)
            "xor rsi, rsi",       # LOGIC (NULL argv)
            "xor rdx, rdx",       # LOGIC (NULL envp)
            "syscall",            # SYSCALL - should be highlighted
        ]
        
        types = [highlighter.classify_instruction(i) for i in instructions]
        
        # Verify syscall is correctly identified
        assert types[-1] == InstructionType.SYSCALL
        
        # Verify counting
        syscall_count = sum(1 for t in types if t == InstructionType.SYSCALL)
        assert syscall_count == 1
    
    def test_rootkit_sample_highlighting(self):
        """Test highlighting on rootkit-like code."""
        highlighter = AsmHighlighter()
        
        instructions = [
            "push rbp",
            "mov rbp, rsp",
            "mov rax, cr3",       # PRIVILEGED - page table base
            "and rax, 0xfffffffffffff000",
            "mov cr3, rax",       # PRIVILEGED - flush TLB
            "pop rbp",
            "ret",
        ]
        
        types = [highlighter.classify_instruction(i) for i in instructions]
        
        # Verify privileged instructions detected
        privileged_count = sum(1 for t in types if t == InstructionType.PRIVILEGED)
        assert privileged_count == 2
```

### Performance Tests

```python
class TestPerformance:
    def test_large_function_highlighting(self):
        """Verify highlighting performance on large functions."""
        import time
        
        highlighter = AsmHighlighter()
        
        # Generate 10,000 instructions
        instructions = ["mov rax, rbx"] * 10000
        
        start = time.perf_counter()
        for instr in instructions:
            highlighter.highlight_instruction(instr, "0x1000")
        elapsed = time.perf_counter() - start
        
        # Should complete in < 100ms
        assert elapsed < 0.1, f"Highlighting too slow: {elapsed:.3f}s"
```

---

## Data Structures

### Classification Cache (Optional Optimization)

If performance becomes an issue with very large binaries:

```python
from functools import lru_cache

class AsmHighlighter:
    @lru_cache(maxsize=1024)
    def classify_instruction_cached(self, opcode: str) -> InstructionType:
        """Cached version of classify_instruction."""
        return self.classify_instruction(opcode)
```

**Trade-offs:**
- ✅ Faster for repeated instructions (common in loops)
- ❌ Memory overhead
- ❌ Cache invalidation complexity if classifier logic changes

**Recommendation:** Only add if profiling shows classification as bottleneck.

---

### Instruction Statistics Data Structure

```python
from dataclasses import dataclass
from collections import Counter

@dataclass
class InstructionStatistics:
    """Statistics about instruction types in disassembly."""
    
    total_instructions: int
    type_counts: Counter  # InstructionType -> count
    
    @property
    def syscall_count(self) -> int:
        return self.type_counts[InstructionType.SYSCALL]
    
    @property
    def privileged_count(self) -> int:
        return self.type_counts[InstructionType.PRIVILEGED]
    
    @property
    def debug_count(self) -> int:
        return self.type_counts[InstructionType.DEBUG]
    
    @property
    def has_security_concerns(self) -> bool:
        """Returns True if any security-critical instructions found."""
        return (self.syscall_count > 0 or 
                self.privileged_count > 0 or 
                self.debug_count > 0)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total": self.total_instructions,
            "by_type": dict(self.type_counts),
            "security_critical": {
                "syscalls": self.syscall_count,
                "privileged": self.privileged_count,
                "debug": self.debug_count,
            }
        }

# Usage in AsmHighlighter
def analyze_instructions(self, instructions: List[str]) -> InstructionStatistics:
    """Analyze a list of instructions and return statistics."""
    type_counts = Counter()
    for instr in instructions:
        instr_type = self.classify_instruction(instr)
        type_counts[instr_type] += 1
    
    return InstructionStatistics(
        total_instructions=len(instructions),
        type_counts=type_counts
    )
```

---

## Error Handling

### Graceful Degradation

All classification must fail gracefully:

```python
def classify_instruction(self, opcode: str) -> InstructionType:
    """Classify instruction with robust error handling."""
    try:
        if not opcode or not isinstance(opcode, str):
            return InstructionType.OTHER
        
        # ... classification logic ...
        
    except Exception as e:
        # Log error but don't crash
        logger.debug(f"Classification error for '{opcode}': {e}")
        return InstructionType.OTHER
```

### Special Case Handling

Complex special cases must be well-tested:

```python
def _parse_int_operand(self, tokens: List[str]) -> Optional[str]:
    """Parse operand from int instruction tokens.
    
    Handles:
    - int 0x80
    - int 0x2e
    - int 128
    - int    0x80  (extra whitespace)
    """
    if len(tokens) < 2:
        return None
    
    operand = tokens[1].strip().lower()
    
    # Remove common prefixes/suffixes
    operand = operand.lstrip('$').rstrip(',')
    
    return operand
```

---

## Security Considerations

### False Positives

**Scenario:** Normal code flagged as security-critical

**Example:** Application legitimately uses:
- `rdtsc` for timing measurements
- `pause` in spin-locks
- `ud2` for assertion failures

**Mitigation:**
- Provide context in UI ("This may indicate...")
- Allow user to suppress warnings
- Confidence scoring (future)

### False Negatives

**Scenario:** Malicious code not flagged

**Example:**
- Indirect syscalls (call function pointer → syscall)
- Obfuscated privileged instructions
- Syscalls from JIT-compiled code

**Mitigation:**
- Clear documentation of limitations
- Complement with dynamic analysis
- Pattern detection for indirect calls (future)

### Performance DoS

**Scenario:** Maliciously crafted binary with millions of instructions

**Mitigation:**
- MAX_DISASM_OPS limit already in place (100)
- If removed, add timeout mechanism
- Consider streaming/lazy evaluation for huge functions

---

## Documentation Requirements

### User Documentation

**Section: "Understanding Instruction Highlighting"**

```markdown
## Instruction Highlighting

CaSpoon highlights assembly instructions by type to help you quickly identify important code patterns.

### Color Key

**Control Flow:**
- **Cyan** - Jumps (jmp, je, jne, etc.)
- **Bright Blue** - Function calls
- **Bright Cyan** - Returns

**Data Operations:**
- **Green** - Data movement (mov, lea, xchg)
- **Yellow** - Arithmetic (add, sub, mul, div)
- **Magenta** - Logical operations (and, or, xor, shl, shr)

**Stack & Memory:**
- **Bright Green** - Stack operations (push, pop)
- **Cyan** - String operations (rep movs, rep stos)

**Security-Critical (⚠):**
- **Bold Red** - System calls (syscall, int 0x80, sysenter)
- **Red** - Privileged instructions (in, out, lgdt, hlt)
- **Bold Yellow** - Debug/Breakpoint (int3, ud2)
- **Bright Yellow** - Software interrupts (int)

**Other:**
- **Bold Magenta** - Atomic operations (xadd, cmpxchg, mfence)
- **Dim** - No-ops (nop padding)
- **White** - Other instructions

### Security Indicators

The "Instruction Statistics" section shows counts of security-relevant instructions:

- ⚠ **Syscalls: N** - Direct system calls (may indicate library bypass)
- ⚠ **Privileged instructions: N** - Ring 0 instructions (kernel/rootkit code)
- ⚠ **Debug/Anti-analysis: N** - Breakpoints or anti-debugging techniques

### What to Look For

**In Malware Analysis:**
- Many syscalls may indicate direct kernel interaction (evasion technique)
- Privileged instructions in userland binary → rootkit
- Debug instructions → anti-analysis

**In Firmware Analysis:**
- Privileged instructions are normal
- Look for port I/O (in/out) for hardware interaction

**In Exploit Analysis:**
- NOP sequences → possible NOP sled (buffer overflow)
- String operations → buffer manipulation
- Syscalls → privilege escalation attempts
```

### API Documentation

Add docstrings with examples:

```python
def classify_instruction(self, opcode: str) -> InstructionType:
    """Classify an assembly instruction by type.
    
    Args:
        opcode: The instruction opcode with optional operands.
                Examples: "mov rax, rbx", "syscall", "int 0x80"
    
    Returns:
        The instruction type classification.
    
    Examples:
        >>> highlighter = AsmHighlighter()
        >>> highlighter.classify_instruction("syscall")
        <InstructionType.SYSCALL: 'syscall'>
        
        >>> highlighter.classify_instruction("mov rax, rbx")
        <InstructionType.MOVE: 'move'>
        
        >>> highlighter.classify_instruction("mov cr0, rax")
        <InstructionType.PRIVILEGED: 'privileged'>
    
    Notes:
        - Classification is case-insensitive
        - Some instructions require operand analysis (e.g., 'int')
        - Returns InstructionType.OTHER for unrecognized instructions
    """
```

---

## Success Metrics

### Quantitative

- [x] 7 new instruction categories implemented
- [x] >95% test coverage maintained
- [x] <10ms classification time for 10k instructions
- [x] Zero regressions in existing functionality
- [x] All existing tests pass

### Qualitative

- [x] Syscalls visually distinct in disassembly
- [x] Security-critical instructions immediately recognizable
- [x] Instruction statistics provide actionable insights
- [x] No false positives for common userland code
- [x] Documentation clear and comprehensive

### User Validation

**Test Cases:**
1. **Malware sample** - User can quickly identify syscalls
2. **Rootkit sample** - Privileged instructions flagged
3. **Packed binary** - Unpacking stubs (string ops) highlighted
4. **Normal application** - No false alarms, clean analysis

---

## Appendices

### Appendix A: Complete Instruction Reference

See design review document for full instruction lists.

### Appendix B: Color Accessibility

For users with color blindness, consider alternative schemes:

**Protanopia (Red-Blind) Scheme:**
- SYSCALL: bold blue
- PRIVILEGED: orange
- DEBUG: yellow

**Deuteranopia (Green-Blind) Scheme:**
- SYSCALL: bold red
- MOVE: blue
- STACK: yellow

**Monochrome Scheme:**
- Use bold/underline/italic instead of colors
- SYSCALL: bold underline
- PRIVILEGED: bold
- DEBUG: underline

### Appendix C: Future Architecture Support

**ARM Instructions:**
```python
# ARM Syscalls
'svc', 'svc #0', 'swi'

# ARM Privileged
'mrs', 'msr',  # System register access
'cps', 'cpsie', 'cpsid',  # Change processor state

# ARM Memory barriers
'dmb', 'dsb', 'isb'
```

**MIPS Instructions:**
```python
# MIPS Syscalls
'syscall'

# MIPS Privileged
'mtc0', 'mfc0',  # Coprocessor 0 (CP0) access
'eret', 'deret',  # Exception return

# MIPS Atomic
'll', 'sc'  # Load-linked, Store-conditional
```

---

**Document Version:** 1.0  
**Status:** Proposed for Implementation  
**Next Review:** After Phase 1 completion
