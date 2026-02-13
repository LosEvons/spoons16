# Subtask 1: System Call Detection

## Objective
Detect direct system calls in binary disassembly across different architectures.

## Implementation

### Syscall Instruction Scanner (3 hours)
**Location**: `caspoon/api/syscalls.py`

```python
class SyscallDetector:
    # Architecture-specific syscall instructions
    SYSCALL_INSTRUCTIONS = {
        'x86_64': ['syscall'],
        'x86': ['int 0x80', 'sysenter'],
        'arm': ['svc #0', 'swi #0'],
        'arm64': ['svc #0'],
        'mips': ['syscall'],
    }
    
    def detect_syscalls(self, disasm: List[Dict], arch: str) -> List[SyscallInfo]:
        """Scan disassembly for syscall instructions."""
        syscalls = []
        patterns = self.SYSCALL_INSTRUCTIONS.get(arch, [])
        
        for op in disasm:
            opcode = op.get('opcode', '').lower()
            for pattern in patterns:
                if pattern in opcode:
                    syscall_info = self._extract_syscall_info(op, arch)
                    syscalls.append(syscall_info)
        
        return syscalls
```

### Syscall Number Resolution (3 hours)
Map syscall numbers to names:
```python
# Linux x86_64 syscall table
LINUX_X64_SYSCALLS = {
    0: 'read',
    1: 'write',
    2: 'open',
    3: 'close',
    # ... complete table
}

def resolve_syscall(number: int, arch: str, os: str) -> str:
    """Resolve syscall number to name."""
    table = self._get_syscall_table(arch, os)
    return table.get(number, f'syscall_{number}')
```

### Argument Extraction (4 hours)
Extract syscall arguments from registers:
```python
def extract_syscall_args(disasm_context: List[Dict], syscall_addr: int, arch: str):
    """Extract syscall arguments from preceding instructions."""
    # For x86_64: rdi, rsi, rdx, r10, r8, r9
    # For x86: ebx, ecx, edx, esi, edi, ebp
    # Look backwards for mov instructions to these registers
```

### Wrapper Detection (3 hours)
Identify libc wrapper functions:
```python
def detect_libc_wrappers(functions: List[Dict], imports: List[str]) -> List[APICallInfo]:
    """Detect libc wrappers that make syscalls."""
    wrappers = ['read', 'write', 'open', 'close', 'socket', 'connect', ...]
    detected = []
    for imp in imports:
        if imp in wrappers:
            detected.append(APICallInfo(
                name=imp,
                library='libc',
                category=self._categorize_syscall(imp),
                risk_level=self._assess_risk(imp)
            ))
    return detected
```

## Estimated Time: 13 hours

## Success Criteria
- [ ] Detects syscall instructions in x86/x64/ARM
- [ ] Resolves syscall numbers to names
- [ ] Extracts syscall arguments where possible
- [ ] Identifies libc wrapper functions
- [ ] Handles multiple architectures
