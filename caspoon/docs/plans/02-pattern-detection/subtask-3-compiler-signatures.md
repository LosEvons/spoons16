# Subtask 3: Compiler Signatures

## Objective
Identify which compiler was used and detect compiler-specific patterns.

## Implementation

### Compiler Database (3 hours)
**Location**: `caspoon/patterns/compiler.py`

```python
COMPILER_PATTERNS = {
    'gcc': {
        'prologue': [
            b'\x55\x48\x89\xe5',  # push rbp; mov rbp, rsp
            b'\x55\x89\xe5',      # push ebp; mov ebp, esp (32-bit)
        ],
        'stack_protector': b'\x64\x48\x8b\x04\x25\x28\x00\x00\x00',
        'markers': ['__stack_chk_fail', '__libc_start_main'],
    },
    'clang': {
        'prologue': [
            b'\x55\x48\x89\xe5',
        ],
        'optimization_patterns': [...],
        'markers': ['__clang_call_terminate'],
    },
    'msvc': {
        'prologue': [
            b'\x55\x8b\xec',  # push ebp; mov ebp, esp
        ],
        'markers': ['__security_cookie', '_guard_check_icall'],
    }
}
```

### Function Prologue Analysis (3 hours)
Analyze function entry patterns to identify compiler.

### Library Detection (2 hours)
Detect standard library implementations (glibc, musl, MSVCRT).

### Optimization Level Detection (2 hours)
Identify optimization flags used (-O0, -O2, -O3).

## Estimated Time: 10 hours

## Success Criteria
- [ ] Identifies GCC, Clang, MSVC correctly
- [ ] Detects optimization levels
- [ ] Recognizes standard library implementations
- [ ] Provides confidence score for identification
