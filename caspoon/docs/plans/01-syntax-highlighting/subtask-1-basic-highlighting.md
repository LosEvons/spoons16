# Subtask 1: Basic Syntax Highlighting

## Objective
Implement foundational syntax highlighting for assembly instructions using the Rich library.

## Scope
Create a basic highlighting system that can colorize assembly code based on instruction types.

## Technical Approach

### 1. Create Syntax Highlighting Module
**Location**: `caspoon/ui/syntax/highlighter.py`

```python
# Key components:
- InstructionType enum (JUMP, CALL, MOV, ARITHMETIC, etc.)
- AsmHighlighter class with classify_instruction() method
- Color mapping for different instruction types
- Integration with Rich's Text API
```

### 2. Define Color Scheme
**Location**: `caspoon/ui/syntax/schemes.py`

```python
# Default color scheme:
- Jumps/Branches: cyan/blue
- Calls: bright blue
- Data movement (mov, lea): green
- Arithmetic (add, sub, mul): yellow
- Logic (and, or, xor): magenta
- Stack operations (push, pop): bright green
- Comparison (cmp, test): yellow
- Return: bright cyan
- Registers: bold
- Immediate values: bright yellow
- Memory references: bright white
- Comments: dim/gray
```

### 3. Implement Basic Parser
Parse assembly lines into components:
- Address/offset
- Opcode
- Operands (registers, immediates, memory references)

### 4. Update R2View Widget
**Location**: `caspoon/ui/views/r2_view.py`

**Changes**:
- Import the new highlighter
- Replace plain Text() calls with highlighted versions
- Apply highlighting to disassembly output

```python
# Before:
parts.append(Text(f"  {offset}: {opcode}"))

# After:
highlighted = highlighter.highlight_instruction(opcode, offset)
parts.append(highlighted)
```

## Implementation Steps

1. **Create highlighter.py** (2 hours)
   - Define InstructionType enum
   - Implement AsmHighlighter class
   - Create classify_instruction() method with basic patterns
   - Implement highlight_line() method

2. **Create schemes.py** (1 hour)
   - Define ColorScheme dataclass
   - Create default color scheme
   - Add scheme selection logic

3. **Update r2_view.py** (2 hours)
   - Import highlighter
   - Modify update_data() to use highlighting
   - Handle errors gracefully (fallback to non-highlighted)

4. **Testing** (2 hours)
   - Test with various binaries
   - Verify colors display correctly
   - Test performance with large disassembly outputs
   - Edge case handling (empty lines, invalid instructions)

## Code Example

```python
# caspoon/ui/syntax/highlighter.py
from enum import Enum
from rich.text import Text
from typing import Dict

class InstructionType(Enum):
    JUMP = "jump"
    CALL = "call"
    MOVE = "move"
    ARITHMETIC = "arithmetic"
    LOGIC = "logic"
    STACK = "stack"
    COMPARE = "compare"
    RETURN = "return"
    OTHER = "other"

class AsmHighlighter:
    def __init__(self, color_scheme: Dict[InstructionType, str]):
        self.scheme = color_scheme
        
    def classify_instruction(self, opcode: str) -> InstructionType:
        """Classify instruction by opcode."""
        opcode_lower = opcode.lower().split()[0]  # Get base opcode
        
        if opcode_lower in ('jmp', 'je', 'jne', 'jg', 'jl', 'ja', 'jb', 'jz'):
            return InstructionType.JUMP
        elif opcode_lower in ('call',):
            return InstructionType.CALL
        elif opcode_lower in ('mov', 'lea', 'movzx', 'movsx'):
            return InstructionType.MOVE
        # ... more classifications
        
        return InstructionType.OTHER
    
    def highlight_instruction(self, opcode: str, address: str = "") -> Text:
        """Return highlighted Text object for an instruction."""
        instr_type = self.classify_instruction(opcode)
        color = self.scheme.get(instr_type, "white")
        
        text = Text()
        if address:
            text.append(f"{address}: ", style="dim")
        text.append(opcode, style=color)
        
        return text
```

## Testing Strategy

### Unit Tests
Create `tests/ui/syntax/test_highlighter.py`:
- Test instruction classification for each type
- Test color application
- Test edge cases (empty strings, invalid opcodes)

### Integration Tests
- Load test binaries through caspoon TUI
- Verify highlighting appears in R2 Analysis tab
- Test with different architectures

### Manual Testing
1. Launch caspoon TUI: `python -m caspoon --ui`
2. Load a binary (e.g., `/bin/ls`)
3. Navigate to R2 Analysis tab
4. Verify:
   - Jump instructions are cyan/blue
   - Call instructions are bright blue
   - Mov instructions are green
   - Colors are readable and distinct

## Dependencies
- Rich library (already available)
- Textual (already available)
- No new external dependencies required

## Estimated Time
**7 hours total**
- Implementation: 5 hours
- Testing: 2 hours

## Success Criteria
- [ ] Assembly instructions are colored by type
- [ ] At least 5 instruction categories are distinguished
- [ ] Colors are consistent and readable
- [ ] No performance degradation on normal-sized functions (<200 instructions)
- [ ] Graceful fallback if highlighting fails

## Next Steps
After completion, proceed to Subtask 2: Instruction Classification for more sophisticated categorization.
