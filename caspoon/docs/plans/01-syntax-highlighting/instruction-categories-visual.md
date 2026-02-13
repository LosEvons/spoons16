# Instruction Category Hierarchy
## Visual Reference for Syntax Highlighting

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ASSEMBLY INSTRUCTION UNIVERSE                        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                              │
          ┌─────────▼─────────┐        ┌─────────▼──────────┐
          │  SECURITY-CRITICAL │        │  GENERAL PURPOSE    │
          │    (Priority 1)     │        │   (Existing)        │
          └─────────┬─────────┘        └─────────┬──────────┘
                    │                              │
    ┌───────────────┼───────────────┐             │
    │               │               │             │
┌───▼────┐    ┌────▼─────┐   ┌────▼────┐        │
│SYSCALL │    │PRIVILEGED│   │  DEBUG  │        │
│  ⚠️⚠️⚠️  │    │   ⚠️⚠️    │   │   ⚠️    │        │
└────────┘    └──────────┘   └─────────┘        │
                                                  │
                              ┌───────────────────┼───────────────────┐
                              │                   │                   │
                         ┌────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
                         │  CONTROL │      │   DATA    │      │  COMPUTE  │
                         │   FLOW   │      │  MOVEMENT │      │ OPERATIONS│
                         └────┬─────┘      └─────┬─────┘      └─────┬─────┘
                              │                   │                   │
                    ┌─────────┼─────────┐        │           ┌───────┼───────┐
                    │         │         │        │           │       │       │
                 ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐    ┌───▼───┐  ┌──▼───┐
                 │JUMP │  │CALL │  │ RET │  │MOVE │    │ARITH  │  │LOGIC │
                 └─────┘  └─────┘  └─────┘  └─────┘    └───────┘  └──────┘
```

---

## Category Tree (Hierarchical View)

```
INSTRUCTIONS
├── SECURITY-CRITICAL (NEW) ⚠️
│   ├── SYSCALL          [syscall, int 0x80, sysenter]
│   ├── PRIVILEGED       [in, out, lgdt, hlt, vmcall]
│   ├── DEBUG            [int3, ud2, icebp]
│   └── INTERRUPT        [int 0x10, int 0x13, iret]
│
├── CONTROL FLOW
│   ├── JUMP             [jmp, je, jne, jz, ja, jb, ...]
│   ├── CALL             [call, callq]
│   └── RETURN           [ret, retq, retn]
│
├── DATA MOVEMENT
│   ├── MOVE             [mov, lea, xchg, movzx, movsx]
│   └── STRING_OPS (NEW) [rep movs, rep stos, scas, cmps]
│
├── COMPUTATION
│   ├── ARITHMETIC       [add, sub, mul, div, inc, dec]
│   ├── LOGIC            [and, or, xor, not, shl, shr]
│   └── COMPARE          [cmp, test]
│
├── MEMORY & STACK
│   ├── STACK            [push, pop, pushf, popf]
│   └── ATOMIC (NEW)     [xadd, cmpxchg, lock, mfence]
│
├── UTILITY
│   └── NOP (NEW)        [nop, xchg ax ax, mov reg reg]
│
└── OTHER (FALLBACK)     [everything else]
```

---

## Security Priority Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTRUCTION PRIORITY                          │
├────────────┬─────────────┬──────────────┬─────────────────────┤
│ Category   │ Priority    │ Visibility   │ Security Impact      │
├────────────┼─────────────┼──────────────┼─────────────────────┤
│ SYSCALL    │ ⭐⭐⭐ CRIT │ MAXIMUM      │ Malware capabilities │
│ PRIVILEGED │ ⭐⭐⭐ HIGH │ HIGH         │ Rootkit detection    │
│ DEBUG      │ ⭐⭐ HIGH   │ HIGH         │ Anti-analysis        │
│ INTERRUPT  │ ⭐⭐ MED    │ MEDIUM       │ Legacy malware       │
│ STRING_OPS │ ⭐⭐ MED    │ MEDIUM       │ Buffer operations    │
│ ATOMIC     │ ⭐ MED     │ MEDIUM       │ Multi-threading      │
│ NOP        │ ⭐ LOW     │ LOW (DIM)    │ Padding, code caves  │
│ JUMP       │ ⭐ NORM    │ NORMAL       │ Control flow         │
│ CALL       │ ⭐ NORM    │ NORMAL       │ Function calls       │
│ MOVE       │ ⭐ NORM    │ NORMAL       │ Data flow            │
└────────────┴─────────────┴──────────────┴─────────────────────┘
```

---

## Color Scheme (Visual Reference)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COLOR SCHEME                                 │
├────────────┬──────────────┬────────────────────────────────────────┤
│ Category   │ Color        │ Example                                 │
├────────────┼──────────────┼────────────────────────────────────────┤
│ SYSCALL    │ bold red     │ 🔴🔴 syscall                             │
│ PRIVILEGED │ red          │ 🔴 hlt                                  │
│ DEBUG      │ bold yellow  │ 🟡🟡 int3                                │
│ INTERRUPT  │ bright yellow│ 🟡 int 0x10                             │
│ JUMP       │ cyan         │ 🔵 jmp 0x1234                           │
│ CALL       │ bright blue  │ 💙 call printf                          │
│ RETURN     │ bright cyan  │ 🔷 ret                                  │
│ MOVE       │ green        │ 🟢 mov rax, rbx                         │
│ STRING_OPS │ cyan         │ 🔵 rep movsb                            │
│ ARITHMETIC │ yellow       │ 🟡 add rax, 5                           │
│ LOGIC      │ magenta      │ 🟣 xor rax, rax                         │
│ ATOMIC     │ bold magenta │ 🟣🟣 xadd [rax], rbx                     │
│ STACK      │ bright green │ 🟩 push rbp                             │
│ COMPARE    │ yellow       │ 🟡 cmp rax, 0                           │
│ NOP        │ dim          │ ⚫ nop                                   │
│ OTHER      │ white        │ ⚪ rdrand rax                            │
└────────────┴──────────────┴────────────────────────────────────────┘

Legend:
  🔴 = Red (Warning)
  🟡 = Yellow (Attention)
  🔵 = Cyan (Info)
  💙 = Bright Blue (Important)
  🟢 = Green (Neutral)
  🟣 = Magenta (Special)
  ⚫ = Dim/Gray (De-emphasize)
  ⚪ = White (Default)
```

---

## Classification Decision Tree

```
START: Instruction Opcode
    │
    ├─ Is it "int" instruction?
    │   ├─ Operand = 0x80, 0x2e, 128, 46? → SYSCALL ⚠️⚠️⚠️
    │   ├─ Operand = 0x3, 0xcc, 0xf1?     → DEBUG ⚠️
    │   └─ Other operand?                  → INTERRUPT
    │
    ├─ Is it "mov" instruction?
    │   ├─ Operand contains cr0-cr4, dr0-dr7? → PRIVILEGED ⚠️⚠️
    │   └─ Normal operands?                    → MOVE
    │
    ├─ Starts with "lock " prefix?      → ATOMIC
    ├─ Starts with "rep" prefix?        → STRING_OPS
    │
    ├─ In syscall_instructions set?     → SYSCALL ⚠️⚠️⚠️
    ├─ In privileged_instructions set?  → PRIVILEGED ⚠️⚠️
    ├─ In debug_instructions set?       → DEBUG ⚠️
    ├─ In string_instructions set?      → STRING_OPS
    ├─ In atomic_instructions set?      → ATOMIC
    ├─ In nop_instructions set?         → NOP
    │
    ├─ In jump_instructions set?        → JUMP
    ├─ In call_instructions set?        → CALL
    ├─ In return_instructions set?      → RETURN
    ├─ In move_instructions set?        → MOVE
    ├─ In arithmetic_instructions set?  → ARITHMETIC
    ├─ In logic_instructions set?       → LOGIC
    ├─ In stack_instructions set?       → STACK
    ├─ In compare_instructions set?     → COMPARE
    │
    └─ None of the above?               → OTHER
```

---

## Instruction Examples by Category

### SYSCALL ⚠️⚠️⚠️
```asm
syscall               ; x64 Linux system call
sysenter              ; Fast system call entry
int 0x80              ; x86 Linux system call
int 0x2e              ; Windows NT system call
svc #0                ; ARM supervisor call (future)
```

### PRIVILEGED ⚠️⚠️
```asm
hlt                   ; Halt processor
in al, 0x60          ; Read from I/O port
out 0x64, al         ; Write to I/O port
lgdt [rbx]           ; Load Global Descriptor Table
mov cr3, rax         ; Load page directory base
rdmsr                ; Read model-specific register
vmcall               ; Virtual machine call
cli                  ; Clear interrupts
```

### DEBUG ⚠️
```asm
int3                 ; Software breakpoint
int 0xcc             ; Breakpoint (alternate form)
ud2                  ; Undefined instruction
icebp                ; Undocumented single-step
```

### INTERRUPT
```asm
int 0x10             ; BIOS video service
int 0x13             ; BIOS disk service
int 0x21             ; DOS service
iret                 ; Return from interrupt
```

### STRING_OPS
```asm
rep movsb            ; Repeated byte copy
rep stosq            ; Repeated qword store
scasb                ; Scan byte
cmpsw                ; Compare word
lodsq                ; Load qword
```

### ATOMIC
```asm
lock xadd [rax], rbx  ; Atomic exchange and add
cmpxchg [rcx], rdx    ; Compare and exchange
xadd [rsp], rax       ; Exchange and add
mfence                ; Memory fence
pause                 ; Spin-loop hint
```

### NOP
```asm
nop                   ; No operation
xchg ax, ax          ; Equivalent to nop
mov rax, rax         ; Redundant move (effective nop)
lea rax, [rax+0]     ; LEA with zero offset
```

### JUMP
```asm
jmp 0x401000         ; Unconditional jump
je 0x401020          ; Jump if equal
jne label            ; Jump if not equal
jg target            ; Jump if greater
ja 0x401040          ; Jump if above (unsigned)
```

### CALL
```asm
call printf          ; Function call
callq 0x401000       ; Function call (x64)
call [rax+0x10]      ; Indirect call
```

### RETURN
```asm
ret                  ; Return from function
retq                 ; Return (x64)
retn 8               ; Return and pop 8 bytes
```

### MOVE
```asm
mov rax, rbx         ; Move register to register
mov [rsp], rdi       ; Move to memory
lea rax, [rbp-16]    ; Load effective address
movzx eax, byte [rsi] ; Move with zero-extend
xchg rax, rcx        ; Exchange registers
```

### ARITHMETIC
```asm
add rax, 5           ; Addition
sub rsp, 0x20        ; Subtraction
imul rax, rcx, 4     ; Multiply
div rbx              ; Division
inc rax              ; Increment
neg rax              ; Negate
```

### LOGIC
```asm
and rax, 0xff        ; Bitwise AND
or rax, rbx          ; Bitwise OR
xor rax, rax         ; Bitwise XOR (clear register)
not rax              ; Bitwise NOT
shl rax, 2           ; Shift left
shr rbx, 4           ; Shift right
```

### STACK
```asm
push rbp             ; Push to stack
pop rax              ; Pop from stack
pushq 0x10           ; Push immediate
pushf                ; Push flags
popf                 ; Pop flags
```

### COMPARE
```asm
cmp rax, rbx         ; Compare
test rax, rax        ; Test (bitwise AND, set flags)
cmpq rax, 0          ; Compare with immediate
```

---

## Real-World Examples

### Malware Syscall Pattern
```asm
0x401000: xor rax, rax          LOGIC    - Clear rax
0x401003: mov rax, 59           MOVE     - execve syscall number
0x401007: lea rdi, [rip+0x100]  MOVE     - Pointer to "/bin/sh"
0x40100e: xor rsi, rsi          LOGIC    - NULL argv
0x401011: xor rdx, rdx          LOGIC    - NULL envp
0x401014: syscall               SYSCALL ⚠️⚠️⚠️ - Execute /bin/sh!
```

### Rootkit Pattern
```asm
0x502000: push rbp              STACK
0x502001: mov rbp, rsp          MOVE
0x502004: mov rax, cr3          PRIVILEGED ⚠️⚠️ - Read page tables
0x502007: and rax, 0xf...000    LOGIC    - Mask
0x50200e: mov cr3, rax          PRIVILEGED ⚠️⚠️ - Flush TLB
0x502011: pop rbp               STACK
0x502012: ret                   RETURN
```

### Anti-Debug Pattern
```asm
0x601000: call IsDebuggerPresent CALL
0x601005: test eax, eax         COMPARE
0x601007: jz normal_path        JUMP
0x601009: int3                  DEBUG ⚠️ - Crash if debugged
0x60100a: ud2                   DEBUG ⚠️ - Undefined instruction
```

### Memcpy Pattern
```asm
0x701000: push rdi              STACK
0x701001: push rsi              STACK
0x701002: mov rcx, rdx          MOVE     - Length
0x701005: rep movsb             STRING_OPS - Copy bytes
0x701007: pop rsi               STACK
0x701008: pop rdi               STACK
0x701009: ret                   RETURN
```

---

## UI Display Example

```
Main Function Disassembly:
  0x401000: push rbp                STACK
  0x401001: mov rbp, rsp            MOVE
  0x401004: sub rsp, 0x10           ARITHMETIC
  0x401008: xor rax, rax            LOGIC
  0x40100b: mov rax, 59             MOVE
  0x40100f: lea rdi, [rip+0x200]    MOVE
  0x401016: syscall                 SYSCALL ⚠️⚠️⚠️
  0x401018: mov cr0, rax            PRIVILEGED ⚠️⚠️
  0x40101b: int3                    DEBUG ⚠️
  0x40101c: add rsp, 0x10           ARITHMETIC
  0x401020: pop rbp                 STACK
  0x401021: ret                     RETURN

Instruction Statistics:
  ⚠ Syscalls: 1                    (direct kernel interaction)
  ⚠ Privileged instructions: 1     (ring 0 operation!)
  ⚠ Debug/Anti-analysis: 1         (potential anti-debug)
  
  Control flow: 2 (jump, call, return)
  Data movement: 3 (mov, lea, etc.)
  Stack operations: 2 (push, pop)
  Arithmetic: 2 (add, sub, mul, div, inc, dec)
  Logic: 1 (and, or, xor, shl, shr)
```

---

## Edge Cases & Special Handling

### 1. The "int" Instruction
```
int 0x80     → SYSCALL    (Linux x86 syscall)
int 0x2e     → SYSCALL    (Windows NT syscall)
int 0x3      → DEBUG      (Breakpoint)
int 0xcc     → DEBUG      (Breakpoint alternate)
int 0xf1     → DEBUG      (Single-step)
int 0x10     → INTERRUPT  (BIOS video)
int 0x21     → INTERRUPT  (DOS services)
```

### 2. Control Register Moves
```
mov rax, rbx      → MOVE          (normal move)
mov cr0, rax      → PRIVILEGED    (control register)
mov rax, cr3      → PRIVILEGED    (control register)
mov dr0, rbx      → PRIVILEGED    (debug register)
```

### 3. Lock Prefix
```
add [rax], 1          → ARITHMETIC
lock add [rax], 1     → ATOMIC
xadd [rsp], rax       → ATOMIC
lock xadd [rsp], rax  → ATOMIC
```

### 4. Rep Prefix
```
movsb              → STRING_OPS
rep movsb          → STRING_OPS
stosq              → STRING_OPS
rep stosq          → STRING_OPS
```

### 5. Effective NOPs
```
nop                → NOP
xchg ax, ax        → NOP (same encoding as nop)
mov rax, rax       → NOP (redundant move)
lea rax, [rax+0]   → NOP (zero offset LEA)
```

---

## Future: Architecture Support

### ARM (Planned)
```asm
# Syscalls
svc #0             → SYSCALL
swi 0              → SYSCALL (ARM32)

# Privileged
mrs x0, SCTLR_EL1  → PRIVILEGED
msr TTBR0_EL1, x0  → PRIVILEGED
cps #0x13          → PRIVILEGED

# Barriers
dmb sy             → ATOMIC
dsb sy             → ATOMIC
isb                → ATOMIC
```

### MIPS (Planned)
```asm
# Syscalls
syscall            → SYSCALL

# Privileged
mtc0 $2, $12       → PRIVILEGED (Move to Coprocessor 0)
mfc0 $2, $12       → PRIVILEGED (Move from Coprocessor 0)
eret               → PRIVILEGED (Exception return)

# Atomic
ll $2, 0($3)       → ATOMIC (Load-linked)
sc $2, 0($3)       → ATOMIC (Store-conditional)
```

---

## Summary Statistics

```
┌────────────────────────────────────────────────────────┐
│          SYNTAX HIGHLIGHTING COVERAGE                   │
├────────────────┬────────────┬──────────────────────────┤
│ Category       │ Instrs     │ Status                    │
├────────────────┼────────────┼──────────────────────────┤
│ EXISTING       │            │                           │
│   JUMP         │     20     │ ✅ Implemented            │
│   CALL         │      2     │ ✅ Implemented            │
│   RETURN       │      4     │ ✅ Implemented            │
│   MOVE         │     15     │ ✅ Implemented            │
│   ARITHMETIC   │     25     │ ✅ Implemented            │
│   LOGIC        │     20     │ ✅ Implemented            │
│   STACK        │     12     │ ✅ Implemented            │
│   COMPARE      │      6     │ ✅ Implemented            │
│   OTHER        │      ∞     │ ✅ Implemented (fallback) │
├────────────────┼────────────┼──────────────────────────┤
│ NEW            │            │                           │
│   SYSCALL      │      5     │ ⏭ Proposed (Phase 1)     │
│   PRIVILEGED   │     30     │ ⏭ Proposed (Phase 1)     │
│   DEBUG        │      5     │ ⏭ Proposed (Phase 1)     │
│   INTERRUPT    │      3     │ ⏭ Proposed (Phase 1)     │
│   STRING_OPS   │     15     │ ⏭ Proposed (Phase 2)     │
│   ATOMIC       │     10     │ ⏭ Proposed (Phase 2)     │
│   NOP          │      1     │ ⏭ Proposed (Phase 2)     │
├────────────────┼────────────┼──────────────────────────┤
│ TOTAL          │    ~173    │ 104 ✅ / 69 ⏭             │
└────────────────┴────────────┴──────────────────────────┘

Architecture Coverage:
  ✅ x86/x64: Comprehensive
  ⏭ ARM:     Planned (Phase 3+)
  ⏭ MIPS:    Planned (Phase 3+)
  ⏭ RISC-V:  Future consideration
```

---

**Document Version:** 1.0  
**Purpose:** Quick visual reference for instruction categorization  
**Target Audience:** Developers, security analysts, project stakeholders
