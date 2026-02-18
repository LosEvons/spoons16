# Quick Testing Guide for Developers

> **📖 For comprehensive testing documentation, see [../TESTING.md](../TESTING.md)**

This is a quick reference guide. For complete testing documentation including best practices, golden tests, coverage guidelines, and troubleshooting, see the main **[TESTING.md](../TESTING.md)** file.

---

## Running Tests

```bash
# All tests (excluding slow ones)
pytest -m "not slow"

# Just unit tests
pytest tests/unit/

# Just integration tests
pytest tests/integration/

# With coverage report
pytest --cov=caspoon --cov-report=term-missing

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/unit/recon/test_protections.py

# Run specific test
pytest tests/unit/recon/test_protections.py::TestProtectionsRecon::test_full_protections_detection
```

## Writing New Tests

### Test File Structure
```python
"""Unit tests for MyModule."""
import pytest
from unittest.mock import Mock, patch
from caspoon.my_module import MyModule
from caspoon.core.models import ExecutableReport


class TestMyModule:
    """Test MyModule class."""

    @pytest.fixture
    def module(self):
        """Create MyModule instance."""
        return MyModule()

    def test_basic_functionality(self, module):
        """Test basic functionality."""
        # Arrange
        input_data = "test"
        
        # Act
        result = module.process(input_data)
        
        # Assert
        assert result is not None
        assert result.some_field == "expected"
```

### Common Patterns

#### 1. Mock Subprocess Calls
```python
def test_subprocess_call(self, module):
    """Test subprocess handling."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="output")
        
        result = module.run_command()
        
        assert result == "output"
```

#### 2. Test Error Handling
```python
def test_file_not_found(self, module):
    """Test handling of missing file."""
    result = module.analyze("/nonexistent/path")
    
    # Should not crash
    assert result is not None
    assert "error" in result.raw_backend_data
```

#### 3. Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_inputs(self, module, input, expected):
    """Test with multiple inputs."""
    result = module.process(input)
    assert result == expected
```

#### 4. Integration Tests
```python
@pytest.mark.integration
def test_with_real_binary(self, module, test_binaries_dir):
    """Test with real binary."""
    binary_path = test_binaries_dir / "test_hello_x64"
    if not binary_path.exists():
        pytest.skip("Binary not available")
    
    result = module.analyze(str(binary_path))
    assert result is not None
```

#### 5. Property Tests
```python
def test_invariant(self, module, sample_binary):
    """Test that invariant holds."""
    result = module.analyze(sample_binary)
    
    # Invariant: output path must match input
    assert result.path == sample_binary
```

## Test Markers

Mark your tests appropriately:

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow test (>1s)
@pytest.mark.golden        # Golden/regression test
@pytest.mark.requires_r2   # Requires radare2

```

Run specific markers:
```bash
pytest -m "integration"           # Only integration tests
pytest -m "not slow"              # Exclude slow tests
pytest -m "unit and not requires_r2"  # Unit tests that don't need r2
```

## Fixtures

### Available Fixtures

- `fixtures_dir` - Path to tests/fixtures/
- `test_binaries_dir` - Path to test binaries
- `sample_binary` - Path to a sample binary (ls or test_hello_x64)
- `tmp_path` - Pytest built-in temporary directory

### Using Fixtures

```python
def test_with_fixtures(self, test_binaries_dir, tmp_path):
    """Test using multiple fixtures."""
    # Use test binary
    binary = test_binaries_dir / "test_hello_x64"
    
    # Use temporary directory for output
    output = tmp_path / "output.json"
    
    # Test logic...
```

## Golden Tests

### Running Golden Tests
```bash
# Run golden tests
pytest -m golden

# Update golden files (after intentional changes)
pytest tests/integration/test_golden.py --update-golden
```

### Adding a New Golden Test

1. Add test in `tests/integration/test_golden.py`:
```python
def test_golden_my_binary(self, test_binaries_dir, golden_dir, update_golden):
    """Golden test for my_binary."""
    binary_name = "my_binary"
    binary_path = test_binaries_dir / binary_name
    golden_path = golden_dir / f"{binary_name}.json"
    
    if not binary_path.exists():
        pytest.skip(f"{binary_name} not available")
    
    runner = ReconRunner()
    report = runner.run(str(binary_path))
    current_output = self._normalize_report(report.pretty())
    
    if update_golden:
        with open(golden_path, 'w') as f:
            json.dump(current_output, f, indent=2, sort_keys=True)
        pytest.skip(f"Updated golden file: {golden_path}")
    
    if not golden_path.exists():
        pytest.skip(f"Golden file not found. Run with --update-golden")
    
    with open(golden_path) as f:
        expected = json.load(f)
    
    assert current_output == expected
```

2. Generate golden file:
```bash
pytest tests/integration/test_golden.py::test_golden_my_binary --update-golden
```

3. Verify and commit:
```bash
git diff tests/fixtures/expected/my_binary.json
git add tests/fixtures/expected/my_binary.json
git commit -m "Add golden test for my_binary"
```

## Coverage

### Check Coverage
```bash
# Terminal report
pytest --cov=caspoon --cov-report=term-missing

# HTML report (detailed)
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=caspoon --cov-report=xml
```

### What's Covered?
- ✅ All modules in `caspoon/` package
- ❌ Tests themselves (`*/tests/*`)
- ❌ Main entry point (`main.py`)
- ❌ UI components (`ui/*`)

### Coverage Goals
- **Minimum**: 70% overall
- **Target**: 80%+ overall
- **Critical modules** (recon, core): 90%+

## Debugging Tests

### Print Output
```python
def test_debug(self, caplog):
    """Test with debug output."""
    import logging
    
    with caplog.at_level(logging.DEBUG):
        result = module.run()
    
    # Print captured logs
    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")
```

### Interactive Debugging
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### See Full Output
```bash
# Show print statements
pytest -s

# Show full diff on assertion failure
pytest -vv
```

## Best Practices

### ✅ DO

1. **Test one thing at a time**
   - Each test should verify one behavior
   - Use descriptive test names: `test_handles_empty_file`

2. **Use mocks for external dependencies**
   - Mock subprocess calls
   - Mock file I/O when appropriate
   - Keep tests fast and deterministic

3. **Test error paths**
   - File not found
   - Permission denied
   - Timeout
   - Invalid input

4. **Use fixtures for setup**
   - Avoid repetitive setup code
   - Share fixtures across tests

5. **Mark tests appropriately**
   - Use `@pytest.mark.integration` for integration tests
   - Use `@pytest.mark.slow` for slow tests
   - Use `@pytest.mark.requires_*` for tool dependencies

### ❌ DON'T

1. **Don't rely on external state**
   - Tests should be independent
   - Don't rely on specific files existing outside test fixtures

2. **Don't test implementation details**
   - Test behavior, not internal structure
   - Avoid testing private methods directly

3. **Don't use hardcoded paths**
   - Use fixtures and tmp_path
   - Use relative paths in test fixtures

4. **Don't skip error testing**
   - Error paths are critical for robustness
   - Test what happens when things go wrong

5. **Don't commit failing tests**
   - Fix or skip with `@pytest.mark.skip(reason="...")`
   - Use `pytest.xfail()` for known failures

## Common Issues

### Test Isolation
```python
# ❌ Bad: Shared mutable state
class TestBad:
    state = []  # Shared across all tests!
    
    def test_one(self):
        self.state.append(1)  # Affects other tests

# ✅ Good: Fresh state per test
class TestGood:
    @pytest.fixture
    def state(self):
        return []  # Fresh list for each test
    
    def test_one(self, state):
        state.append(1)  # Isolated
```

### Mocking Pitfalls
```python
# ❌ Bad: Mock doesn't match real API
with patch('subprocess.run') as mock:
    mock.return_value = "string"  # Real API returns CompletedProcess!

# ✅ Good: Mock matches real API
with patch('subprocess.run') as mock:
    mock.return_value = Mock(returncode=0, stdout="output")
```

### File Handling
```python
# ❌ Bad: Hardcoded path
def test_bad():
    result = analyze("/tmp/test.bin")  # May not exist!

# ✅ Good: Use fixtures
def test_good(self, tmp_path):
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"data")
    result = analyze(str(test_file))
```

## Quick Reference

```bash
# Fast feedback loop during development
pytest tests/unit/my_module/ -v -x

# Before committing
pytest -m "not slow" --cov=caspoon

# Full test suite
pytest --cov=caspoon --cov-report=html

# Update golden files after intentional changes
pytest tests/integration/test_golden.py --update-golden
```

## Need Help?

- 📖 **[See TESTING.md for comprehensive testing documentation](../TESTING.md)**
- 📖 See [TEST_REVIEW.md](TEST_REVIEW.md) for detailed testing strategy
- 📖 See [TESTING_IMPROVEMENTS.md](TESTING_IMPROVEMENTS.md) for what's been implemented
- 📖 See `tests/` for examples
- 📖 Check pytest docs: https://docs.pytest.org/
