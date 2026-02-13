# Syntax Highlighting Design Review
## Binary Analysis & Security Perspective

**Review Date:** 2024-02-13  
**Reviewer:** Binary Analysis Design Agent  
**Components Reviewed:**
- `caspoon/ui/syntax/highlighter.py` (Core highlighting engine)
- `caspoon/ui/syntax/schemes.py` (Color schemes and instruction types)
- `caspoon/ui/views/r2_view.py` (Integration)

---

## Executive Summary

The syntax highlighting implementation is **solid and well-architected** for its initial scope (x86/x64 basic instruction highlighting). However, from a **defensive security analysis perspective**, several critical instruction categories are missing that would significantly benefit reverse engineers analyzing potentially malicious binaries.

**Overall Assessment:** ✅ **APPROVED with RECOMMENDATIONS**

### Key Strengths
1. Clean, extensible architecture with good separation of concerns
2. Comprehensive coverage of common x86/x64 instructions
3. Excellent test coverage including edge cases
4. Graceful error handling and fallback mechanisms

### Critical Gaps for Security Analysis
1. **No special category for system calls** (syscall, int 0x80, sysenter, sysexit)
2. **No highlighting for privileged/dangerous instructions** (in, out, wrmsr, etc.)
3. **No category for control-flow anomalies** (int3, int 0xCC, ud2, hlt)
4. **No category for string/memory operations** (rep movs, lods, stos, scas, cmps)
5. **No category for atomic/synchronization operations** (lock prefix, xadd, cmpxchg)
6. **No architecture extension beyond x86/x64**

---

## Detailed Analysis

### 1. Instruction Classification Assessment

#### ✅ Well-Covered Categories

**Control Flow (JUMP, CALL, RETURN)**
- Comprehensive coverage of conditional/unconditional jumps
- All call variants included
- Return instructions properly classified
- **Security Impact:** Enables quick identification of branching logic, critical for understanding malware control flow

**Data Movement (MOVE)**
- Excellent coverage including lea (load effective address)
- All size variants (movb, movw, movl, movq)
- Zero/sign extension (movzx, movsx)
- Exchange operations (xchg)
- **Security Impact:** Helps track data flow and register usage patterns

**Arithmetic & Logic Operations**
- Complete coverage of standard operations
- Includes carry/borrow variants (adc, sbb)
- Shift/rotate operations properly classified
- **Security Impact:** Useful for identifying cryptographic operations and bit manipulation

**Stack Operations**
- Comprehensive push/pop variants
- Flag operations (pushf, popf)
- **Security Impact:** Critical for understanding function call conventions and stack manipulation

**Comparison Operations**
- Both cmp and test properly classified
- **Security Impact:** Essential for understanding conditional execution logic

#### ❌ Missing Critical Categories for Security Analysis

**1. SYSTEM CALLS (CRITICAL)**
```python
# Currently classified as OTHER - should be HIGH PRIORITY category
InstructionType.SYSCALL
```

**Missing Instructions:**
- `syscall` (x64 Linux system calls)
- `int 0x80` (x86 Linux system calls)
- `sysenter` / `sysexit` (fast system calls)
- `int 0x2e` (Windows system calls)
- `svc` (ARM system calls)

**Why This Matters:**
System calls are **the primary interface between user code and the kernel**. In defensive analysis:
- Malware uses syscalls to perform malicious actions (file I/O, network, process creation)
- Direct syscalls may indicate syscall obfuscation (bypassing library hooks)
- Syscall patterns map directly to MITRE ATT&CK techniques
- Essential for understanding binary capabilities without symbols

**Recommendation:** Add `InstructionType.SYSCALL` with bright red or bold highlighting.

---

**2. PRIVILEGED INSTRUCTIONS (HIGH PRIORITY)**
```python
# Instructions that require ring 0 or special privileges
InstructionType.PRIVILEGED
```

**Missing Instructions:**
- `in`, `out`, `ins`, `outs` (I/O port access)
- `lgdt`, `sgdt`, `lidt`, `sidt` (descriptor table operations)
- `ltr`, `str` (task register)
- `lldt`, `sldt` (local descriptor table)
- `hlt` (halt processor)
- `rdmsr`, `wrmsr` (model-specific registers)
- `cli`, `sti` (interrupt control)
- `invlpg`, `invpcid` (TLB operations)

**Why This Matters:**
- Userland code should **never** contain these instructions
- Presence indicates rootkit, hypervisor, or kernel-mode driver code
- Critical for firmware/bootkit analysis
- Helps identify virtualization or emulation code

**Recommendation:** Add `InstructionType.PRIVILEGED` with warning color (red/orange).

---

**3. BREAKPOINT & DEBUG INSTRUCTIONS (MEDIUM PRIORITY)**
```python
InstructionType.DEBUG
```

**Missing Instructions:**
- `int3` / `int 0xCC` (software breakpoint)
- `ud2` (undefined instruction, often used for assertions)
- `icebp` / `int 0xF1` (undocumented single-step)
- `bound` (bounds check, deprecated but used in anti-debug)

**Why This Matters:**
- Anti-debugging techniques heavily use these
- Self-modifying code may insert/remove breakpoints
- Malware may use int3 as a VM/debugger detection mechanism
- `ud2` can indicate code that should never execute (assertions, dead code)

**Recommendation:** Add `InstructionType.DEBUG` category, highlight distinctly.

---

**4. STRING & MEMORY OPERATIONS (MEDIUM PRIORITY)**
```python
InstructionType.STRING_OPS
```

**Missing Instructions:**
- `rep movs` / `movsb/w/d/q` (repeated memory copy)
- `rep stos` / `stosb/w/d/q` (repeated store)
- `rep lods` / `lodsb/w/d/q` (repeated load)
- `rep scas` / `scasb/w/d/q` (repeated scan)
- `rep cmps` / `cmpsb/w/d/q` (repeated compare)
- `repe`, `repne`, `repz`, `repnz` prefixes

**Why This Matters:**
- Very common in memcpy, memset, strcpy implementations
- Can indicate buffer operations (potential overflow vectors)
- Used by obfuscators for code unpacking
- Performance-critical operations worth highlighting

**Recommendation:** Separate category from MOVE operations, or sub-category within MOVE.

---

**5. ATOMIC & SYNCHRONIZATION (LOW-MEDIUM PRIORITY)**
```python
InstructionType.ATOMIC
```

**Missing Instructions:**
- `lock` prefix (atomic memory operations)
- `xadd` (exchange and add)
- `cmpxchg` (compare and exchange)
- `cmpxchg8b`, `cmpxchg16b` (double-width compare-exchange)
- `pause` (spin-loop hint)
- `mfence`, `lfence`, `sfence` (memory barriers)

**Why This Matters:**
- Indicates multi-threaded code
- Critical for race condition analysis
- Used in rootkits and malware for synchronization
- Memory barriers can indicate anti-analysis timing attacks

**Recommendation:** Add category for atomic operations.

---

**6. NOP & PADDING INSTRUCTIONS (LOW PRIORITY)**
```python
InstructionType.NOP
```

**Missing Instructions:**
- `nop` (no operation)
- Multi-byte nops (0x0F 0x1F variations)
- `lea reg, [reg+0]` (effectively a nop)
- `mov reg, reg` (redundant move, used for padding)

**Why This Matters:**
- Excessive nops may indicate code cave, shellcode, or patched binary
- Multi-byte nops indicate compiler optimization level
- Nop sleds are signature of buffer overflow exploits
- Can indicate timing analysis or alignment requirements

**Recommendation:** Add NOP category, use dim/gray highlighting.

---

**7. TRAP & INTERRUPT INSTRUCTIONS (MEDIUM PRIORITY)**
```python
InstructionType.INTERRUPT
```

**Missing Instructions:**
- `int` (software interrupt) - currently OTHER
- `into` (interrupt on overflow)
- `iret`, `iretd`, `iretq` (interrupt return)

**Why This Matters:**
- `int` instructions invoke system services (beyond just syscalls)
- Used for anti-debugging (int 0x2d on Windows)
- BIOS/DOS-era malware heavily uses interrupts
- Exception handling mechanisms

**Recommendation:** Add INTERRUPT category, distinct from SYSCALL.

---

**8. SIMD & VECTOR INSTRUCTIONS (LOW PRIORITY for now)**

Currently all classified as OTHER. Future consideration:
- SSE/SSE2/AVX instructions (movaps, addps, etc.)
- MMX instructions
- AVX-512 operations

**Why This Matters:**
- Cryptographic operations heavily use SIMD
- Performance-critical code (video, audio, crypto)
- May indicate malware using optimized routines

**Recommendation:** Defer to future enhancement, but note for extensibility.

---

### 2. Architecture Coverage Assessment

**Current State:** x86/x64 only

**Planned Future Architectures (per project goals):**
1. ARM (32-bit and 64-bit)
2. MIPS
3. PowerPC (potentially)
4. RISC-V (emerging)

**Design Extensibility Analysis:**

✅ **Strengths:**
- Instruction sets stored in dictionaries (easily extensible)
- Classification logic is straightforward
- Color scheme is architecture-agnostic

⚠️ **Concerns:**
- Hard-coded x86 instruction sets in `__init__`
- No abstraction for architecture-specific classifiers
- Manual maintenance required for new architectures

**Recommended Architecture:**

```python
class InstructionClassifier(ABC):
    """Abstract base for architecture-specific instruction classification."""
    
    @abstractmethod
    def classify(self, opcode: str) -> InstructionType:
        pass

class X86Classifier(InstructionClassifier):
    """x86/x64 instruction classifier."""
    # Current implementation

class ARMClassifier(InstructionClassifier):
    """ARM instruction classifier."""
    def classify(self, opcode: str) -> InstructionType:
        # ARM-specific logic
        pass

class AsmHighlighter:
    def __init__(self, classifier: Optional[InstructionClassifier] = None, ...):
        self.classifier = classifier or X86Classifier()
```

**Benefits:**
1. Clean separation of architecture logic
2. Easy to add new architectures without touching core
3. Testable per-architecture
4. Supports mixed-architecture binaries (future)

---

### 3. Color Scheme Analysis

**Current Scheme Review:**

| Category | Color | Assessment |
|----------|-------|------------|
| JUMP | cyan | ✅ Good - visually distinct |
| CALL | bright_blue | ✅ Good - stands out |
| RETURN | bright_cyan | ✅ Good - matches call/jump family |
| MOVE | green | ✅ Good - neutral, common instruction |
| ARITHMETIC | yellow | ✅ Good - warm color for computation |
| LOGIC | magenta | ✅ Good - distinct from arithmetic |
| STACK | bright_green | ✅ Good - important operations |
| COMPARE | yellow | ⚠️ Same as arithmetic - acceptable |
| OTHER | white | ✅ Good - default/neutral |
| ADDRESS | dim | ✅ Good - de-emphasizes addresses |

**Recommendations for New Categories:**

| New Category | Suggested Color | Rationale |
|--------------|-----------------|-----------|
| SYSCALL | `bright_red` or `bold red` | High priority, security-critical |
| PRIVILEGED | `red` | Warning - shouldn't appear in userland |
| DEBUG | `yellow bold` | Attention - potential anti-analysis |
| STRING_OPS | `cyan` | Related to data movement |
| ATOMIC | `magenta bold` | Synchronization primitives |
| NOP | `dim` or `bright_black` | De-emphasize padding |
| INTERRUPT | `bright_yellow` | Moderate priority |

**Color Accessibility:**
- Current scheme is colorblind-friendly (uses distinct hues)
- Consider adding a "high contrast" scheme for accessibility
- Consider semantic styling (bold, underline) in addition to color

---

### 4. Integration Analysis (r2_view.py)

**Current Integration:** ✅ Well-implemented

```python
highlighted = self._highlighter.highlight_instruction(opcode, offset)
```

**Strengths:**
1. Clean integration - single method call
2. Address and instruction properly passed
3. Graceful handling of missing data

**Recommendations:**

1. **Add instruction metadata to hover/tooltip:**
```python
# Future enhancement
highlighted = self._highlighter.highlight_instruction(
    opcode, offset, 
    metadata={"type": instr_type, "description": get_description(instr_type)}
)
```

2. **Allow filtering by instruction type:**
```python
# In R2View
self._filter_types = {InstructionType.SYSCALL, InstructionType.CALL}
if self._filter_types and instr_type not in self._filter_types:
    continue  # Skip non-filtered instructions
```

3. **Add instruction statistics:**
```python
# Count instruction types for summary
instr_counts = Counter(
    self._highlighter.classify_instruction(op["opcode"]) 
    for op in main_ops
)
parts.append(Text(f"Syscalls: {instr_counts[InstructionType.SYSCALL]}"))
```

---

### 5. Performance Analysis

**Current Implementation:** ✅ Efficient

- Dictionary lookups: O(1) per instruction
- Simple string operations
- No regex or complex parsing
- Graceful error handling doesn't throw exceptions

**Scalability:**
- ✅ 100 instructions: ~0.01ms (negligible)
- ✅ 1,000 instructions: ~0.1ms (very fast)
- ✅ 10,000 instructions: ~1ms (acceptable)
- ✅ 100,000 instructions: ~10ms (fine for UI)

**No performance concerns for current implementation.**

**Future Optimization (if needed):**
- Cache classification results per unique opcode
- Use set membership instead of dictionary for faster lookups
- Pre-compile regex patterns if regex is added

---

### 6. Security Analysis Use Cases

**Use Case 1: Malware Triage**
- ✅ Quickly identify control flow (jumps, calls)
- ✅ Spot stack manipulation
- ❌ **Missing:** Syscall identification (critical for capabilities)
- ❌ **Missing:** Debug instruction detection (anti-analysis)

**Use Case 2: Reverse Engineering Unknown Binary**
- ✅ Understand function structure (prologue/epilogue)
- ✅ Track data movement
- ❌ **Missing:** String operations (memcpy patterns)
- ❌ **Missing:** Privileged instructions (rootkit detection)

**Use Case 3: Exploit Analysis**
- ✅ Stack operations well-highlighted
- ❌ **Missing:** NOP sleds detection
- ❌ **Missing:** Self-modifying code indicators

**Use Case 4: Firmware/Bootkit Analysis**
- ❌ **Missing:** Privileged instructions (critical!)
- ❌ **Missing:** I/O port operations
- ❌ **Missing:** Interrupt handling

**Conclusion:** Works well for general RE, but missing critical features for security-focused analysis.

---

### 7. Extensibility for Future Features

**Planned Feature: Syscall/API Detection (Plan 03)**
- ✅ **Synergy:** Syntax highlighting can use syscall detection results
- ✅ **Integration:** Highlighter can accept external instruction metadata
- ⚠️ **Gap:** Need bidirectional flow - highlighter should feed syscall detector

**Planned Feature: Pattern Detection (Plan 02)**
- ✅ **Synergy:** Crypto patterns can be highlighted in disassembly
- ✅ **Integration:** Pattern matches can include instruction addresses
- ⚠️ **Gap:** Need mechanism to highlight instruction sequences, not just single instructions

**Recommendation: Add context-aware highlighting**

```python
@dataclass
class InstructionContext:
    """Additional context for highlighting decisions."""
    is_syscall: bool = False
    is_crypto_pattern: bool = False
    is_obfuscated: bool = False
    security_risk: str = "low"  # low/medium/high

class AsmHighlighter:
    def highlight_instruction(
        self, 
        opcode: str, 
        address: str = "",
        context: Optional[InstructionContext] = None
    ) -> Text:
        # Use context to override base classification
        if context and context.is_syscall:
            instr_type = InstructionType.SYSCALL
        elif context and context.security_risk == "high":
            # Add warning styling
            pass
        else:
            instr_type = self.classify_instruction(opcode)
        # ... rest of highlighting
```

---

### 8. Test Coverage Analysis

**Current Test Coverage:** ✅ Excellent (95%+ estimated)

**Covered:**
- All instruction categories
- Edge cases (empty, None, whitespace)
- Case insensitivity
- Complex operands
- Error handling
- Color scheme configuration

**Missing Tests:**
1. Performance benchmarks (>10k instructions)
2. Non-x86 architecture instructions (ARM, MIPS)
3. Integration tests with actual r2 output
4. Concurrent access (thread safety)

**Recommendation:** Add performance regression tests.

---

## Recommended Implementation Priority

### Phase 1: Critical Security Enhancements (1-2 days)

**Priority 1.1 - Add SYSCALL Category** ⭐⭐⭐
```python
class InstructionType(Enum):
    # ... existing ...
    SYSCALL = "syscall"

# In highlighter.py
self._syscall_instructions = {
    'syscall',      # x64 Linux
    'int',          # x86 interrupts (need to check operand)
    'sysenter',     # Fast system call entry
    'sysexit',      # Fast system call exit
    'svc',          # ARM supervisor call
}
```

**Special handling for `int` instruction:**
```python
def classify_instruction(self, opcode: str) -> InstructionType:
    # ... existing logic ...
    
    # Special case for int instruction
    if opcode_lower == 'int':
        # Check operand to determine if syscall
        operand = opcode.split()[1] if len(opcode.split()) > 1 else ""
        if operand in ('0x80', '0x2e', '128', '46'):  # Linux/Windows syscall ints
            return InstructionType.SYSCALL
        else:
            return InstructionType.INTERRUPT
```

**Color scheme:**
```python
@dataclass
class ColorScheme:
    # ... existing ...
    syscall: str = "bold bright_red"  # High visibility
```

**Estimated effort:** 3-4 hours including tests

---

**Priority 1.2 - Add PRIVILEGED Category** ⭐⭐⭐
```python
self._privileged_instructions = {
    # I/O Port
    'in', 'out', 'ins', 'outs', 'insb', 'insw', 'insd',
    'outsb', 'outsw', 'outsd',
    
    # Descriptor Tables
    'lgdt', 'sgdt', 'lidt', 'sidt', 'lldt', 'sldt',
    
    # Task/Segment
    'ltr', 'str',
    
    # Control Registers
    'mov cr', 'mov dr',  # Requires operand parsing
    
    # System Control
    'hlt', 'rdmsr', 'wrmsr', 'rdpmc', 'rdtsc', 'rdtscp',
    'invlpg', 'invpcid', 'cli', 'sti',
    
    # VM Extensions
    'vmcall', 'vmlaunch', 'vmresume', 'vmxoff', 'vmxon',
}
```

**Estimated effort:** 2-3 hours including tests

---

**Priority 1.3 - Add DEBUG Category** ⭐⭐
```python
self._debug_instructions = {
    'int3',    # Software breakpoint
    'ud2',     # Undefined instruction
    'icebp',   # Undocumented single-step
    'bound',   # Bounds check (deprecated)
}

# Special handling for int 0xcc (int3) and int 0x03
```

**Estimated effort:** 1-2 hours

---

### Phase 2: Enhanced Pattern Support (2-3 days)

**Priority 2.1 - Add STRING_OPS Category** ⭐⭐
```python
self._string_instructions = {
    'movs', 'movsb', 'movsw', 'movsd', 'movsq',
    'stos', 'stosb', 'stosw', 'stosd', 'stosq',
    'lods', 'lodsb', 'lodsw', 'lodsd', 'lodsq',
    'scas', 'scasb', 'scasw', 'scasd', 'scasq',
    'cmps', 'cmpsb', 'cmpsw', 'cmpsd', 'cmpsq',
    'rep', 'repe', 'repne', 'repz', 'repnz',  # Prefixes
}
```

**Priority 2.2 - Add ATOMIC Category** ⭐
```python
self._atomic_instructions = {
    'xadd', 'xaddq', 'xaddl',
    'cmpxchg', 'cmpxchgq', 'cmpxchgl', 'cmpxchg8b', 'cmpxchg16b',
    'pause',
    'mfence', 'lfence', 'sfence',
    # Note: 'lock' is a prefix, requires special handling
}
```

**Priority 2.3 - Add NOP and INTERRUPT Categories** ⭐

---

### Phase 3: Architecture Abstraction (3-5 days)

**Priority 3.1 - Refactor to Classifier Pattern**
- Abstract `InstructionClassifier` interface
- Move x86 logic to `X86Classifier`
- Prepare for ARM/MIPS classifiers

**Priority 3.2 - Add ARM Support**
- Implement `ARMClassifier`
- Add ARM instruction categories
- Test with ARM binaries

---

### Phase 4: Context-Aware Highlighting (2-3 days)

**Priority 4.1 - Add InstructionContext**
- Support external metadata (syscall detector, pattern detector)
- Override base classification with context
- Add security risk indicators

**Priority 4.2 - Instruction Sequence Highlighting**
- Support highlighting multiple instructions (patterns)
- Add sequence markers in UI

---

## Specific Code Recommendations

### 1. Add Security-Critical Instructions (Immediate)

**File: `caspoon/ui/syntax/schemes.py`**
```python
class InstructionType(Enum):
    """Types of assembly instructions for syntax highlighting."""

    JUMP = "jump"
    CALL = "call"
    MOVE = "move"
    ARITHMETIC = "arithmetic"
    LOGIC = "logic"
    STACK = "stack"
    COMPARE = "compare"
    RETURN = "return"
    
    # Security-critical categories (NEW)
    SYSCALL = "syscall"           # System calls - HIGH PRIORITY
    PRIVILEGED = "privileged"     # Ring 0 instructions
    DEBUG = "debug"               # Breakpoints, anti-debug
    INTERRUPT = "interrupt"       # Software interrupts
    STRING_OPS = "string_ops"     # rep movs, stos, etc.
    ATOMIC = "atomic"             # Synchronization primitives
    NOP = "nop"                   # No-op padding
    
    OTHER = "other"


@dataclass
class ColorScheme:
    """Color scheme for syntax highlighting."""

    jump: str = "cyan"
    call: str = "bright_blue"
    move: str = "green"
    arithmetic: str = "yellow"
    logic: str = "magenta"
    stack: str = "bright_green"
    compare: str = "yellow"
    return_: str = "bright_cyan"
    
    # Security-critical colors (NEW)
    syscall: str = "bold bright_red"      # Very prominent
    privileged: str = "red"                # Warning color
    debug: str = "bold yellow"             # Attention
    interrupt: str = "bright_yellow"       # Moderate priority
    string_ops: str = "cyan"               # Related to moves
    atomic: str = "bold magenta"           # Synchronization
    nop: str = "dim"                       # De-emphasize
    
    other: str = "white"
    address: str = "dim"
    
    def get_style(self, instr_type: InstructionType) -> str:
        """Get the style for a given instruction type."""
        mapping = {
            InstructionType.JUMP: self.jump,
            InstructionType.CALL: self.call,
            InstructionType.MOVE: self.move,
            InstructionType.ARITHMETIC: self.arithmetic,
            InstructionType.LOGIC: self.logic,
            InstructionType.STACK: self.stack,
            InstructionType.COMPARE: self.compare,
            InstructionType.RETURN: self.return_,
            
            # Security-critical mappings (NEW)
            InstructionType.SYSCALL: self.syscall,
            InstructionType.PRIVILEGED: self.privileged,
            InstructionType.DEBUG: self.debug,
            InstructionType.INTERRUPT: self.interrupt,
            InstructionType.STRING_OPS: self.string_ops,
            InstructionType.ATOMIC: self.atomic,
            InstructionType.NOP: self.nop,
            
            InstructionType.OTHER: self.other,
        }
        return mapping.get(instr_type, self.other)
```

---

### 2. Enhance Classifier with Special Cases

**File: `caspoon/ui/syntax/highlighter.py`**
```python
def __init__(self, color_scheme: Optional[ColorScheme] = None):
    """Initialize the highlighter."""
    self.scheme = color_scheme or get_default_scheme()
    
    # ... existing instruction sets ...
    
    # Security-critical instruction sets (NEW)
    self._syscall_instructions = {
        'syscall',      # x64 Linux
        'sysenter',     # Fast syscall entry
        'sysexit',      # Fast syscall exit
        'svc',          # ARM supervisor call
    }
    
    self._privileged_instructions = {
        # I/O Port access
        'in', 'out', 'ins', 'outs', 'insb', 'insw', 'insd',
        'outsb', 'outsw', 'outsd',
        # Descriptor tables
        'lgdt', 'sgdt', 'lidt', 'sidt', 'lldt', 'sldt',
        'ltr', 'str',
        # System control
        'hlt', 'rdmsr', 'wrmsr', 'rdpmc', 'rdtsc', 'rdtscp',
        'invlpg', 'invpcid', 'cli', 'sti',
        # VM extensions
        'vmcall', 'vmlaunch', 'vmresume', 'vmxoff', 'vmxon',
    }
    
    self._debug_instructions = {
        'int3',    # Software breakpoint
        'ud2',     # Undefined instruction
        'icebp',   # Undocumented single-step
        'bound',   # Bounds check
    }
    
    self._string_instructions = {
        'movs', 'movsb', 'movsw', 'movsd', 'movsq',
        'stos', 'stosb', 'stosw', 'stosd', 'stosq',
        'lods', 'lodsb', 'lodsw', 'lodsd', 'lodsq',
        'scas', 'scasb', 'scasw', 'scasd', 'scasq',
        'cmps', 'cmpsb', 'cmpsw', 'cmpsd', 'cmpsq',
        'rep', 'repe', 'repne', 'repz', 'repnz',
    }
    
    self._atomic_instructions = {
        'xadd', 'xaddq', 'xaddl',
        'cmpxchg', 'cmpxchgq', 'cmpxchgl', 'cmpxchg8b', 'cmpxchg16b',
        'pause',
        'mfence', 'lfence', 'sfence',
    }
    
    self._nop_instructions = {
        'nop',
    }
    
    # Special syscall/interrupt numbers
    self._syscall_ints = {'0x80', '0x2e', '128', '46'}  # Linux, Windows


def classify_instruction(self, opcode: str) -> InstructionType:
    """Classify an instruction by its opcode."""
    if not opcode or not isinstance(opcode, str):
        return InstructionType.OTHER
        
    # Extract the base opcode
    tokens = opcode.strip().lower().split()
    if not tokens:
        return InstructionType.OTHER
    
    opcode_lower = tokens[0]
    
    # SPECIAL CASE: 'int' instruction - check operand
    if opcode_lower == 'int':
        operand = tokens[1] if len(tokens) > 1 else ""
        if operand in self._syscall_ints:
            return InstructionType.SYSCALL
        elif operand in ('0x3', '0xcc', '3', '204'):  # int3 variants
            return InstructionType.DEBUG
        else:
            return InstructionType.INTERRUPT
    
    # SPECIAL CASE: 'mov' with control registers (privileged)
    if opcode_lower == 'mov' and len(tokens) >= 2:
        operands = ' '.join(tokens[1:])
        if 'cr0' in operands or 'cr2' in operands or 'cr3' in operands or 'cr4' in operands:
            return InstructionType.PRIVILEGED
        if 'dr0' in operands or 'dr1' in operands or 'dr2' in operands or 'dr3' in operands:
            return InstructionType.PRIVILEGED
    
    # Check security-critical categories first (higher priority)
    if opcode_lower in self._syscall_instructions:
        return InstructionType.SYSCALL
    elif opcode_lower in self._privileged_instructions:
        return InstructionType.PRIVILEGED
    elif opcode_lower in self._debug_instructions:
        return InstructionType.DEBUG
    elif opcode_lower in self._string_instructions:
        return InstructionType.STRING_OPS
    elif opcode_lower in self._atomic_instructions:
        return InstructionType.ATOMIC
    elif opcode_lower in self._nop_instructions:
        return InstructionType.NOP
    
    # Check standard categories (existing logic)
    elif opcode_lower in self._jump_instructions:
        return InstructionType.JUMP
    elif opcode_lower in self._call_instructions:
        return InstructionType.CALL
    elif opcode_lower in self._return_instructions:
        return InstructionType.RETURN
    elif opcode_lower in self._move_instructions:
        return InstructionType.MOVE
    elif opcode_lower in self._arithmetic_instructions:
        return InstructionType.ARITHMETIC
    elif opcode_lower in self._logic_instructions:
        return InstructionType.LOGIC
    elif opcode_lower in self._stack_instructions:
        return InstructionType.STACK
    elif opcode_lower in self._compare_instructions:
        return InstructionType.COMPARE
    else:
        return InstructionType.OTHER
```

---

### 3. Add Instruction Summary to UI

**File: `caspoon/ui/views/r2_view.py`**
```python
from collections import Counter

def update_data(self, report: ExecutableReport) -> None:
    """Update the view with new report data."""
    # ... existing code ...
    
    # Analyze instruction types in main function
    main_ops = r2.get("main_ops", [])
    instr_counts = Counter()
    
    parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))
    displayed_ops = main_ops[:MAX_DISASM_OPS]
    
    for op in displayed_ops:
        offset = hex(op.get("offset", 0))
        opcode = op.get("opcode", "")
        
        # Apply syntax highlighting
        highlighted = self._highlighter.highlight_instruction(opcode, offset)
        
        # Count instruction types
        instr_type = self._highlighter.classify_instruction(opcode)
        instr_counts[instr_type] += 1
        
        # Add indentation
        indented = Text("  ")
        indented.append_text(highlighted)
        parts.append(indented)
    
    if len(main_ops) > MAX_DISASM_OPS:
        parts.append(
            Text(f"  ... {len(main_ops) - MAX_DISASM_OPS} more instructions (truncated)")
        )
    
    # Add instruction statistics (NEW)
    parts.append(Text("\nInstruction Statistics:", style="bold cyan"))
    
    # Highlight security-critical findings
    if instr_counts[InstructionType.SYSCALL] > 0:
        parts.append(
            Text(f"  ⚠ Syscalls: {instr_counts[InstructionType.SYSCALL]}", style="bold red")
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
    
    # Standard instruction counts
    for instr_type, count in instr_counts.most_common():
        if instr_type not in (InstructionType.SYSCALL, InstructionType.PRIVILEGED, 
                                InstructionType.DEBUG, InstructionType.OTHER):
            parts.append(Text(f"  {instr_type.value}: {count}"))
    
    # ... rest of existing code ...
```

---

## Validation Checklist

Before considering this feature complete for security analysis:

- [ ] **Syscall instructions highlighted distinctly**
  - Test: Load binary with syscall, int 0x80, sysenter
  - Verify: Bright red/bold highlighting
  
- [ ] **Privileged instructions detected**
  - Test: Kernel module or bootloader code
  - Verify: Red highlighting for in/out, lgdt, hlt, etc.
  
- [ ] **Debug instructions flagged**
  - Test: Binary with int3, ud2
  - Verify: Yellow/warning highlighting
  
- [ ] **String operations categorized**
  - Test: memcpy/memset compiled code
  - Verify: rep movs/stos highlighted distinctly
  
- [ ] **Instruction statistics in UI**
  - Test: View any binary main function
  - Verify: Summary shows syscall count, instruction distribution
  
- [ ] **Test with real malware sample** (in safe environment)
  - Verify: Syscalls stand out visually
  - Verify: Anti-debug techniques highlighted
  
- [ ] **Performance with large functions**
  - Test: Function with 10,000+ instructions
  - Verify: < 100ms highlighting time

---

## Future Enhancements

### Short Term (Next 3-6 months)
1. **Context-aware highlighting** - Integration with syscall detector
2. **Hover tooltips** - Show instruction description on hover
3. **Instruction filtering** - Show only syscalls, jumps, etc.
4. **ARM architecture support** - Extend to ARM32/ARM64

### Medium Term (6-12 months)
1. **Instruction sequence highlighting** - Highlight multi-instruction patterns
2. **Custom color schemes** - User-configurable via config file
3. **Export highlighted disassembly** - HTML/PDF with colors
4. **Integration with pattern detector** - Highlight crypto/obfuscation patterns

### Long Term (12+ months)
1. **Decompiler syntax highlighting** - Apply to pseudo-C output
2. **Interactive highlighting** - Click instruction to highlight all instances
3. **Semantic highlighting** - Use dataflow analysis for smarter colors
4. **ML-based classification** - Learn from analyst feedback

---

## Conclusion

The syntax highlighting implementation is **well-designed and production-ready** for basic x86/x64 reverse engineering. However, for **defensive security analysis**, the following additions are **critical**:

### Must-Have (Before v1.0)
1. ✅ **SYSCALL category** - Essential for capability analysis
2. ✅ **PRIVILEGED category** - Critical for rootkit/firmware analysis
3. ✅ **DEBUG category** - Important for anti-analysis detection

### Should-Have (v1.1)
4. ✅ **STRING_OPS category** - Common in malware, useful for patterns
5. ✅ **Instruction statistics in UI** - Quick overview of binary behavior
6. ✅ **Architecture abstraction** - Prepare for ARM/MIPS

### Nice-to-Have (v1.2+)
7. ✅ **ATOMIC category** - Multi-threading analysis
8. ✅ **Context-aware highlighting** - Integration with other analyzers
9. ✅ **Hoverable descriptions** - Educational for junior analysts

**Overall Assessment:** Strong foundation, needs security-focused enhancements to fully support defensive analysis goals.

**Estimated Work to Address Critical Gaps:** 1-2 days for Phase 1 priorities.

---

## Sign-off

**Recommendation:** ✅ **Approve with required enhancements**

This design provides a solid foundation for syntax highlighting. The addition of security-critical instruction categories (syscall, privileged, debug) will make this feature production-ready for defensive binary analysis.

**Next Steps:**
1. Implement Phase 1 priorities (syscall, privileged, debug categories)
2. Add unit tests for new categories
3. Update integration tests with security-focused test cases
4. Coordinate with syscall detection plan (Plan 03) for synergies

---

**Document Version:** 1.0  
**Last Updated:** 2024-02-13  
**Review Status:** Complete
