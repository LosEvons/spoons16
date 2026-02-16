# Subtask 2: Instruction Classification

**Status**: ✅ COMPLETED  
**Completion Date**: 2026-02-13  
**Related Changelog**: [2026-02-13-plan1-subtask3-architecture-schemes.md](../../changelogs/2026-02-13-plan1-subtask3-architecture-schemes.md)

## Objective
Enhance instruction classification to accurately categorize instructions across different architectures and instruction types.

## Scope
Build a comprehensive instruction classifier that handles x86/x64 instruction sets with detailed categorization.

## Technical Approach

### 1. Detailed Instruction Database
Create instruction mappings for:
- **Control Flow**: jmp, je, jne, jg, jl, ja, jb, jz, jnz, jo, jno, js, jns, jc, jnc, call, ret, iret
- **Data Movement**: mov, lea, movzx, movsx, movsb, movsw, movsd, cmov* variants
- **Arithmetic**: add, sub, mul, imul, div, idiv, inc, dec, neg
- **Logic/Bitwise**: and, or, xor, not, shl, shr, sal, sar, rol, ror
- **Stack Operations**: push, pop, pushf, popf, enter, leave
- **Comparison/Test**: cmp, test
- **String Operations**: cmps, lods, stos, scas
- **System/Privileged**: int, syscall, sysenter, sysexit, in, out, hlt
- **FPU/SIMD**: SSE, AVX, MMX instructions
- **Special**: nop, ud2, cpuid, rdtsc

### 2. Operand Analysis
Enhance highlighting to distinguish operands:
- **Registers**: Parse register names (rax, rbx, eax, etc.)
- **Immediate Values**: Numeric constants (0x400000, 42, etc.)
- **Memory References**: Address expressions [rbp-0x10], [rip+0x2000]
- **Symbols**: Function names, labels

### 3. Architecture-Specific Variants
Support instruction variants:
- Size prefixes (byte, word, dword, qword)
- Conditional variants (je, jne, etc.)
- REP/REPNE prefixes for string operations

## Implementation Steps

### Step 1: Build Instruction Database (3 hours)
**Location**: `caspoon/ui/syntax/instructions.py`

```python
# Instruction categories with comprehensive mappings
X86_64_INSTRUCTIONS = {
    InstructionType.JUMP: {
        'jmp', 'je', 'jne', 'jz', 'jnz', 'jg', 'jge', 'jl', 'jle',
        'ja', 'jae', 'jb', 'jbe', 'jo', 'jno', 'js', 'jns', 'jc', 'jnc',
        'jp', 'jnp', 'jcxz', 'jecxz', 'jrcxz', 'loop', 'loope', 'loopne'
    },
    InstructionType.CALL: {'call', 'callq'},
    InstructionType.RETURN: {'ret', 'retf', 'retq', 'iret', 'iretd', 'iretq'},
    # ... comprehensive mappings for all categories
}
```

### Step 2: Implement Operand Parser (4 hours)
**Location**: `caspoon/ui/syntax/operand_parser.py`

```python
class OperandParser:
    def parse_operand(self, operand: str) -> OperandInfo:
        """Parse operand and return type and highlighting."""
        if self.is_register(operand):
            return OperandInfo(OperandType.REGISTER, "bold cyan")
        elif self.is_immediate(operand):
            return OperandInfo(OperandType.IMMEDIATE, "bright_yellow")
        elif self.is_memory_ref(operand):
            return OperandInfo(OperandType.MEMORY, "bright_white")
        elif self.is_symbol(operand):
            return OperandInfo(OperandType.SYMBOL, "bright_green")
```

### Step 3: Enhanced Highlighter (4 hours)
Update `caspoon/ui/syntax/highlighter.py`:

```python
class AsmHighlighter:
    def __init__(self, architecture: str = "x86_64"):
        self.arch = architecture
        self.instructions = self._load_instruction_db(architecture)
        self.operand_parser = OperandParser()
    
    def highlight_instruction(self, line: str, address: str = "") -> Text:
        """Highlight entire instruction line with operand parsing."""
        text = Text()
        
        # Address
        if address:
            text.append(f"{address:16s}", style="dim cyan")
        
        # Parse instruction line
        parts = self._parse_instruction_line(line)
        
        # Opcode
        opcode = parts['opcode']
        instr_type = self.classify_instruction(opcode)
        opcode_color = self.get_color_for_type(instr_type)
        text.append(f"{opcode:8s}", style=opcode_color)
        
        # Operands
        for i, operand in enumerate(parts['operands']):
            if i > 0:
                text.append(", ", style="white")
            
            operand_info = self.operand_parser.parse_operand(operand)
            text.append(operand, style=operand_info.color)
        
        # Comments (if any)
        if parts.get('comment'):
            text.append(f"  ; {parts['comment']}", style="dim")
        
        return text
```

### Step 4: Regex-Based Parsing (2 hours)
Implement robust parsing for complex instruction formats:

```python
import re

INSTRUCTION_PATTERN = re.compile(
    r'^\s*(?P<address>[0-9a-fx]+):\s*'
    r'(?P<bytes>([0-9a-f]{2}\s*)+)\s*'
    r'(?P<opcode>\w+)\s*'
    r'(?P<operands>[^;]*?)\s*'
    r'(?:;\s*(?P<comment>.*))?$',
    re.IGNORECASE
)
```

### Step 5: Update Integration (2 hours)
Integrate enhanced highlighter into r2_view.py with proper error handling.

## Testing Strategy

### Unit Tests
Create comprehensive tests:
```python
def test_classify_jump_instructions():
    highlighter = AsmHighlighter("x86_64")
    assert highlighter.classify_instruction("jmp") == InstructionType.JUMP
    assert highlighter.classify_instruction("je") == InstructionType.JUMP
    assert highlighter.classify_instruction("jne") == InstructionType.JUMP

def test_parse_operands():
    parser = OperandParser()
    assert parser.parse_operand("rax").type == OperandType.REGISTER
    assert parser.parse_operand("0x400000").type == OperandType.IMMEDIATE
    assert parser.parse_operand("[rbp-0x10]").type == OperandType.MEMORY
```

### Integration Tests
- Test with real disassembly output from various binaries
- Verify all instruction types are classified correctly
- Test edge cases (prefixes, size specifiers, etc.)

### Performance Tests
- Benchmark classification speed on 1000+ instruction sequences
- Ensure classification adds <10% overhead

## Example Output

Before:
```
0x400500: mov    rax, qword [rbp-0x8]
0x400504: call   0x400450
0x400509: jne    0x400520
```

After (with colors):
```
0x400500:        mov      rax, qword [rbp-0x8]
                [dim]    [green]  [bold]      [bright_white]
0x400504:        call     0x400450
                [dim]    [bright_blue] [bright_yellow]
0x400509:        jne      0x400520
                [dim]    [cyan]   [bright_yellow]
```

## Dependencies
- Standard library (re module)
- Rich library (already available)
- No new external dependencies

## Estimated Time
**15 hours total**
- Instruction database: 3 hours
- Operand parser: 4 hours
- Enhanced highlighter: 4 hours
- Regex parsing: 2 hours
- Testing: 2 hours

## Success Criteria
- [x] All common x86/x64 instructions are correctly classified
- [x] Operands are parsed and highlighted by type
- [x] Register names are distinguished from other operands
- [x] Memory references are properly highlighted
- [x] Performance impact is minimal (<10% overhead)
- [x] Edge cases (prefixes, size specifiers) are handled

## Implementation Summary

### Completed Components
✅ **Created `caspoon/ui/syntax/instructions.py`** - Comprehensive x86/x64 instruction database (354 instructions)  
✅ **Created `caspoon/ui/syntax/operand_parser.py`** - Parser for registers, immediates, memory references, and symbols  
✅ **Enhanced `caspoon/ui/syntax/highlighter.py`** - Integrated operand parsing and instruction classification  
✅ **Tests created** - `test_highlighter_extended.py` with comprehensive coverage

### Key Features Implemented
- **Instruction Database**: 354 x86/x64 instructions across 9 categories
- **Operand Parsing**: Distinguishes REGISTER, IMMEDIATE, MEMORY, SYMBOL, UNKNOWN
- **Regex-based Parsing**: Robust parsing of instruction lines with comments
- **Detailed Highlighting**: Separate colors for opcode, operands, comments
- **Register Detection**: x86/x64 64-bit, 32-bit, 16-bit, 8-bit registers, plus segment and control registers

## Next Steps
✅ Completed - Proceed to Subtask 3: Architecture-Specific Schemes (also completed)
