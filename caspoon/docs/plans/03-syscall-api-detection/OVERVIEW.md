# Implementation Plan: System Call & API Detection

## Overview

This plan focuses on detecting, analyzing, and categorizing system calls and API usage in binaries. This provides critical forensic insights into what operations a binary performs.

## Goals

1. Detect and enumerate all system calls used
2. Identify and categorize API calls (Windows, POSIX, etc.)
3. Highlight dangerous or suspicious API usage
4. Visualize API call relationships and sequences
5. Provide security context for detected calls

## Architecture Impact

### Modified Components
- **Recon Modules**: New syscall/API detection module
- **Models**: Add SyscallInfo and APICallInfo dataclasses
- **UI Views**: New syscall/API view tab
- **Backend**: Extend r2_analyzer for syscall extraction

### New Components
- `recon/syscall_detection.py` - System call detection recon module
- `recon/api_detection.py` - API call detection recon module
- `api/` - API analysis library
  - `api/syscalls.py` - System call database and analysis
  - `api/windows_api.py` - Windows API database
  - `api/posix_api.py` - POSIX API database
  - `api/categorizer.py` - API categorization engine
- `ui/views/api_view.py` - UI view for API/syscall results

## Technical Dependencies

### Required Libraries
- **r2pipe**: Already available, for extraction
- **Standard library**: For syscall number mappings
- **Optional**: capstone for instruction analysis

### Analysis Sources
- Disassembly (syscall/int instructions)
- Imports table
- Symbol information
- Radare2 analysis

## Complexity Assessment

### Difficulty: Medium
- **Syscall Detection**: Low-Medium - Direct instruction scanning
- **API Categorization**: Medium - Requires comprehensive databases
- **Sequence Analysis**: Medium-High - Requires control flow tracking
- **Cross-Platform**: Medium - Different conventions per OS/arch

### Estimated Effort
- Subtask 1 (Syscall Detection): 2-3 days
- Subtask 2 (API Database): 2-3 days
- Subtask 3 (Categorization): 2-3 days
- Subtask 4 (Security Analysis): 2-3 days
- Subtask 5 (UI Integration): 2-3 days
- **Total**: 10-15 days

## Success Criteria

1. Detect all direct syscall instructions (syscall, int 0x80, svc, etc.)
2. Identify imported API functions from all dynamic libraries
3. Categorize APIs by function (file I/O, network, process, etc.)
4. Flag dangerous or suspicious API combinations
5. Display syscalls and APIs in organized, filterable views
6. Provide security context and documentation for each call

## Implementation Phases

### Phase 1: Syscall Detection (Subtask 1)
Detect direct system calls in disassembly.

### Phase 2: API Database (Subtask 2)
Build comprehensive API databases for Windows and POSIX.

### Phase 3: Categorization (Subtask 3)
Categorize detected calls by purpose and risk level.

### Phase 4: Security Analysis (Subtask 4)
Analyze API usage for security implications.

### Phase 5: Integration (Subtask 5)
Integrate with UI and display results.

## Risk Assessment

### Technical Risks
- **False Negatives**: May miss indirect syscalls
  - *Mitigation*: Use multiple detection methods, heuristics
- **Architecture Variations**: Different syscall conventions
  - *Mitigation*: Architecture-specific detection logic
- **Incomplete Database**: Can't cover all APIs
  - *Mitigation*: Graceful handling of unknown APIs, extensible design

### Performance Risks
- **Large Import Tables**: Some binaries import hundreds of APIs
  - *Mitigation*: Efficient data structures, pagination

## Dependencies on Other Plans

- **Point 1 (Syntax Highlighting)**: Syscalls can be highlighted in disassembly
- **Point 2 (Pattern Detection)**: API patterns support pattern detection
- **Point 13 (Forensic Features)**: API usage maps to MITRE ATT&CK techniques

## Data Model

```python
@dataclass
class SyscallInfo:
    number: int                 # Syscall number
    name: str                   # Syscall name (e.g., "read", "openat")
    address: int                # Address where syscall occurs
    category: str               # Category (file, network, process, etc.)
    arguments: Optional[List]   # Detected arguments if available
    risk_level: str             # low/medium/high

@dataclass
class APICallInfo:
    name: str                   # API function name
    library: str                # Library name (e.g., "kernel32.dll", "libc.so")
    category: str               # Category (file, network, registry, etc.)
    risk_level: str             # low/medium/high
    description: str            # What the API does
    addresses: List[int]        # Where API is called
```

## Syscall Detection Methods

### 1. Direct Instruction Scanning
- x86/x64: `syscall`, `int 0x80`, `sysenter`
- ARM: `svc #0`
- MIPS: `syscall`

### 2. Wrapper Function Detection
- Identify libc wrappers (read, write, open, etc.)
- Trace through wrapper to syscall

### 3. Import Analysis
- Parse imported functions from dynamic libraries
- Categorize based on function names

## API Categories

### File Operations
- open, read, write, close, fopen, fread, fwrite
- CreateFile, ReadFile, WriteFile, DeleteFile

### Network Operations
- socket, connect, bind, listen, send, recv
- WSAStartup, WSASocket, connect, send, recv

### Process Operations
- fork, exec, waitpid, kill
- CreateProcess, OpenProcess, TerminateProcess

### Memory Operations
- mmap, mprotect, malloc, free
- VirtualAlloc, VirtualProtect, HeapAlloc

### Registry (Windows)
- RegOpenKey, RegSetValue, RegQueryValue

### Dangerous Operations
- system, exec*, shellexecute
- chmod, chown (privilege changes)
- ptrace (anti-debugging)
- VirtualProtect with EXECUTE (code injection)

## Future Enhancements

- API call sequence analysis
- Data flow tracking through API calls
- API hooking detection
- Syscall filtering (seccomp) analysis
- API call graphs
- Frequency analysis of API usage

## References

- [Linux System Call Table](https://filippo.io/linux-syscall-table/)
- [Windows API Documentation](https://docs.microsoft.com/en-us/windows/win32/api/)
- [POSIX API Reference](https://pubs.opengroup.org/onlinepubs/9699919799/)
- [Dangerous Windows APIs](https://docs.microsoft.com/en-us/windows/security/threat-protection/)

## Subtasks

1. [System Call Detection](subtask-1-syscall-detection.md)
2. [API Database](subtask-2-api-database.md)
3. [API Categorization](subtask-3-api-categorization.md)
4. [Security Analysis](subtask-4-security-analysis.md)
5. [UI Integration](subtask-5-ui-integration.md)
