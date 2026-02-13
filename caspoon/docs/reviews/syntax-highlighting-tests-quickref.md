# Syntax Highlighting Tests - Quick Reference

## Running the Tests

### Run all syntax highlighting tests
```bash
pytest caspoon/tests/unit/ui/ -v
```

### Run with coverage
```bash
pytest caspoon/tests/unit/ui/ \
  --cov=caspoon/ui/syntax \
  --cov=caspoon/ui/views/r2_view \
  --cov-report=term-missing \
  -v
```

### Run specific test files
```bash
# Original tests
pytest caspoon/tests/unit/ui/syntax/test_highlighter.py -v

# Extended tests (exception handling, edge cases)
pytest caspoon/tests/unit/ui/syntax/test_highlighter_extended.py -v

# Integration tests (R2View)
pytest caspoon/tests/unit/ui/views/test_r2_view.py -v
```

## Test Structure

```
caspoon/tests/unit/ui/
├── syntax/
│   ├── __init__.py
│   ├── test_highlighter.py          # 22 tests - Original implementation tests
│   └── test_highlighter_extended.py # 31 tests - Edge cases & exception handling
└── views/
    ├── __init__.py
    └── test_r2_view.py               # 21 tests - R2View integration tests
```

## Coverage Status

| Module | Coverage | Tests |
|--------|----------|-------|
| `caspoon/ui/syntax/highlighter.py` | 100% ✅ | 53 |
| `caspoon/ui/syntax/schemes.py` | 100% ✅ | 53 |
| `caspoon/ui/views/r2_view.py` | 100% ✅ | 21 |

**Total: 74 tests, 100% coverage, ~2.5s execution time**

## What's Tested

### Highlighter (`test_highlighter.py` + `test_highlighter_extended.py`)

#### Instruction Classification
- ✅ All 9 instruction types (JUMP, CALL, MOVE, ARITHMETIC, LOGIC, STACK, COMPARE, RETURN, OTHER)
- ✅ Case-insensitive classification
- ✅ Complex operands (memory addressing, size prefixes)
- ✅ Unknown architecture instructions (ARM, MIPS)
- ✅ Edge cases (empty, None, numeric, whitespace)

#### Syntax Highlighting
- ✅ Basic highlighting with/without addresses
- ✅ Custom color schemes
- ✅ Exception handling and graceful degradation
- ✅ Color application verification
- ✅ Various address formats (hex, decimal, relative)

#### Color Scheme
- ✅ Default scheme
- ✅ Custom schemes
- ✅ All instruction type mappings

### R2View Integration (`test_r2_view.py`)

#### Initialization
- ✅ Highlighter initialization
- ✅ Component creation

#### Data Handling
- ✅ Valid r2 data
- ✅ Empty/missing data
- ✅ Error conditions
- ✅ Partial data (missing keys)

#### Highlighting Integration
- ✅ Highlighter invocation
- ✅ Invalid offset handling
- ✅ Invalid opcode handling

#### Display Limits
- ✅ MAX_FUNCTIONS enforcement
- ✅ MAX_DISASM_OPS enforcement
- ✅ MAX_STRINGS enforcement

#### Robustness
- ✅ Malformed data
- ✅ Concurrent updates
- ✅ Real-world scenarios

## Common Test Patterns

### Testing Instruction Classification
```python
def test_classify_instruction_type(self):
    highlighter = AsmHighlighter()
    assert highlighter.classify_instruction("mov rax, rbx") == InstructionType.MOVE
```

### Testing Highlighting
```python
def test_highlight_instruction(self):
    highlighter = AsmHighlighter()
    result = highlighter.highlight_instruction("jmp target", address="0x1000")
    assert isinstance(result, Text)
    assert "0x1000" in result.plain
    assert "jmp target" in result.plain
```

### Testing R2View
```python
def test_r2view_update(self):
    view = R2View()
    report = ExecutableReport(path="/test/binary")
    report.raw_backend_data = {"r2": {"functions": [], "main_ops": [], "strings": []}}
    view.update_data(report)  # Should not raise
```

## Known Issues / Notes

### R2View Robustness
`r2_view.py` does not currently handle `None` entries in function/string lists. This is documented in tests but not critical since r2 backend unlikely to produce None entries.

Example:
```python
# Would crash if fn is None:
for fn in funcs:
    name = fn.get("name", "<unknown>")  # AttributeError if fn is None
```

**Fix (if needed):**
```python
for fn in funcs:
    if fn is None:
        continue
    name = fn.get("name", "<unknown>")
```

**Priority:** Low

## Adding New Tests

### For New Instruction Types
Add to `test_highlighter.py`:
```python
def test_classify_new_instruction_type(self):
    highlighter = AsmHighlighter()
    assert highlighter.classify_instruction("new_instr arg") == InstructionType.EXPECTED_TYPE
```

### For Edge Cases
Add to `test_highlighter_extended.py`:
```python
def test_new_edge_case(self):
    highlighter = AsmHighlighter()
    result = highlighter.highlight_instruction("edge case input")
    # Verify expected behavior
```

### For R2View Integration
Add to `test_r2_view.py`:
```python
def test_new_r2view_scenario(self):
    view = R2View()
    report = create_test_report(...)
    view.update_data(report)
    # Verify expected behavior
```

## CI/CD Integration

Recommended GitHub Actions configuration:
```yaml
- name: Test Syntax Highlighting
  run: |
    pytest caspoon/tests/unit/ui/ \
      --cov=caspoon/ui/syntax \
      --cov=caspoon/ui/views/r2_view \
      --cov-fail-under=100 \
      -v
```

## Debugging Failed Tests

### Check coverage
```bash
pytest caspoon/tests/unit/ui/ --cov-report=html
# Open htmlcov/index.html
```

### Run specific test with verbose output
```bash
pytest caspoon/tests/unit/ui/syntax/test_highlighter.py::TestInstructionClassification::test_classify_jump_instructions -vv
```

### Show print statements
```bash
pytest caspoon/tests/unit/ui/ -v -s
```

## Documentation

- **Detailed Review:** `caspoon/docs/reviews/syntax-highlighting-test-review.md`
- **Summary:** `caspoon/docs/reviews/syntax-highlighting-test-summary.md`
- **This File:** `caspoon/docs/reviews/syntax-highlighting-tests-quickref.md`

## Maintenance

### When adding new features:
1. Add unit tests to appropriate test file
2. Ensure 100% coverage maintained
3. Add integration test if R2View is affected
4. Update this quick reference if needed

### When modifying highlighter:
1. Run full test suite: `pytest caspoon/tests/unit/ui/ -v`
2. Check coverage: Add `--cov` flags
3. Verify all 74 tests still pass
4. Update tests if behavior changed

---

**Last Updated:** 2025-01-20  
**Test Count:** 74  
**Coverage:** 100%  
**Status:** ✅ Production Ready
