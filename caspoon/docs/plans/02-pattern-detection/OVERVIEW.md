# Implementation Plan: Pattern Detection & Recognition

## Overview

This plan focuses on automatically detecting and recognizing various patterns in binary code, including compiler signatures, cryptographic constants, obfuscation techniques, and security-relevant patterns. This enhances forensic analysis by automatically flagging interesting code sections.

## Goals

1. Detect common code patterns (function prologues, compiler signatures, etc.)
2. Identify cryptographic operations and constants
3. Recognize obfuscation and anti-analysis techniques
4. Categorize and highlight detected patterns in the UI
5. Provide pattern-based search and filtering capabilities

## Architecture Impact

### Modified Components
- **Recon Modules**: New pattern detection recon module
- **Models**: Add PatternMatch dataclass for storing detections
- **UI Views**: New pattern detection view tab
- **Backend**: Extend r2_analyzer to extract pattern-relevant data

### New Components
- `recon/pattern_detection.py` - Main pattern detection recon module
- `patterns/` - Pattern detection library
  - `patterns/crypto.py` - Cryptographic pattern detection
  - `patterns/compiler.py` - Compiler signature detection
  - `patterns/obfuscation.py` - Obfuscation technique detection
  - `patterns/security.py` - Security pattern detection
  - `patterns/engine.py` - Pattern matching engine
- `ui/views/patterns_view.py` - UI view for pattern results

## Technical Dependencies

### Required Libraries
- **yara-python** (optional): For advanced pattern matching with YARA rules
- **capstone** (optional): For instruction-level pattern analysis
- **pefile** (optional): For Windows PE-specific patterns
- **r2pipe**: Already available, for binary analysis
- **re**: Standard library, for regex-based patterns

### Analysis Sources
- Disassembly from radare2
- Binary content (raw bytes)
- String extraction results
- Function metadata

## Complexity Assessment

### Difficulty: Medium-High
- **Crypto Detection**: Medium - Known constants are well-documented
- **Compiler Patterns**: Medium - Requires database of known patterns
- **Obfuscation Detection**: High - Many variants and techniques
- **Performance**: Medium-High - Pattern matching can be expensive

### Estimated Effort
- Subtask 1 (Pattern Engine): 3-4 days
- Subtask 2 (Crypto Detection): 3-4 days
- Subtask 3 (Compiler Signatures): 2-3 days
- Subtask 4 (Obfuscation Detection): 4-5 days
- Subtask 5 (UI Integration): 2-3 days
- **Total**: 14-19 days

## Success Criteria

1. Detect at least 10 common cryptographic constants (AES S-boxes, SHA constants, etc.)
2. Identify compiler signatures for GCC, Clang, MSVC
3. Detect at least 5 common obfuscation techniques
4. Provide confidence scores for pattern matches
5. Display detected patterns in a dedicated UI view
6. Performance: Pattern detection completes in <5 seconds for typical binaries

## Implementation Phases

### Phase 1: Foundation (Subtask 1)
Build pattern matching engine and infrastructure.

### Phase 2: Crypto Detection (Subtask 2)
Implement cryptographic constant and algorithm detection.

### Phase 3: Compiler & Code Patterns (Subtask 3)
Add compiler signature and standard pattern detection.

### Phase 4: Security Patterns (Subtask 4)
Implement obfuscation and anti-analysis detection.

### Phase 5: Integration (Subtask 5)
Integrate with UI and existing recon pipeline.

## Risk Assessment

### Technical Risks
- **False Positives**: Pattern matching may flag benign code
  - *Mitigation*: Use confidence scoring, multiple validators
- **Performance Impact**: Complex pattern matching can be slow
  - *Mitigation*: Optimize patterns, use caching, make optional
- **Pattern Maintenance**: Patterns need updates as techniques evolve
  - *Mitigation*: Modular design, external pattern files (YARA)

### Integration Risks
- **Binary Size**: Very large binaries may timeout
  - *Mitigation*: Set timeouts, sample-based detection
- **Architecture Specific**: Some patterns are architecture-dependent
  - *Mitigation*: Architecture-aware pattern selection

## Dependencies on Other Plans

- **Point 1 (Syntax Highlighting)**: Patterns can be highlighted in disassembly
- **Point 3 (Syscall Detection)**: API patterns complement syscall detection
- **Point 13 (Forensic Features)**: Patterns support MITRE ATT&CK mapping

## Pattern Categories

### 1. Cryptographic Patterns
- AES S-boxes and round constants
- SHA-256/SHA-1 constants
- RSA key size indicators
- Base64 encoding tables
- Known crypto library function patterns

### 2. Compiler Signatures
- GCC stack frame patterns
- Clang optimization patterns
- MSVC runtime signatures
- Function prologue/epilogue styles
- Compiler-inserted security checks

### 3. Obfuscation Techniques
- Control flow flattening
- Dead code insertion
- Opaque predicates
- Instruction substitution
- Virtualization obfuscation

### 4. Anti-Analysis Patterns
- Debugger detection (ptrace, IsDebuggerPresent)
- VM detection (CPUID checks, timing)
- Sandbox detection
- Anti-disassembly tricks
- Self-modifying code

### 5. Code Patterns
- Function prologues/epilogues
- String formatting patterns
- Memory allocation patterns
- Error handling patterns

## Data Model

```python
@dataclass
class PatternMatch:
    pattern_name: str           # e.g., "AES S-box"
    category: str               # e.g., "cryptographic"
    confidence: float           # 0.0 to 1.0
    address: Optional[int]      # Where pattern was found
    description: str            # Human-readable description
    severity: str               # info/low/medium/high
    metadata: Dict[str, Any]    # Additional pattern-specific data
```

## Future Enhancements

- Custom pattern definition via YARA rules
- Machine learning-based pattern recognition
- Pattern correlation analysis
- Export pattern matches as IOCs
- Pattern-based binary classification

## References

- [YARA Documentation](https://yara.readthedocs.io/)
- [Cryptographic Constants Database](https://github.com/ReFirmLabs/binwalk)
- [Compiler Signatures Research](https://hex-rays.com/products/ida/tech/flirt/)
- [Anti-Debugging Techniques](https://anti-reversing.com/)

## Subtasks

1. [Pattern Matching Engine](subtask-1-pattern-engine.md)
2. [Cryptographic Detection](subtask-2-crypto-detection.md)
3. [Compiler Signatures](subtask-3-compiler-signatures.md)
4. [Obfuscation & Anti-Analysis](subtask-4-obfuscation-detection.md)
5. [UI Integration](subtask-5-ui-integration.md)
