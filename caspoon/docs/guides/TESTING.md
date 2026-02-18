# Testing Guide

Comprehensive guide to testing in Caspoon. This document covers running tests, writing new tests, understanding coverage, and testing best practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Suite Overview](#test-suite-overview)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Golden Tests](#golden-tests)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Running Tests

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run all fast tests (recommended for development)
pytest -m "not slow"

# Run with coverage report
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/unit/recon/test_protections.py -v

# Stop on first failure (fast feedback)
pytest -x
```

### Test Categories

```bash
# Unit tests only (fast, isolated)
pytest tests/unit/

# Integration tests (slower, end-to-end)
pytest tests/integration/

# Golden tests (regression detection)
pytest -m golden

# Exclude slow tests
pytest -m "not slow"

# Tests that require radare2
pytest -m requires_r2
```

---

## Test Suite Overview

### Statistics

- **Total Tests**: 107 passing, 4 skipped
- **Code Coverage**: 84.07% overall
  - Core modules: 100%
  - Recon modules: 94-100%
  - Backends: 25-62% (deferred - requires r2)
- **Test Files**: 15 files, ~2,500 lines of test code
- **Execution Time**: ~3 seconds (without slow tests)

### Test Organization

```
tests/
├── conftest.py                  # Shared fixtures & configuration
├── fixtures/                    # Test data
│   ├── binaries/               # Compiled test binaries
│   │   ├── src/                # Source code for test binaries
│   │   ├── test_hello_x64      # Standard x64 binary
│   │   ├── test_stripped       # Stripped binary (no symbols)
│   │   └── test_with_pie       # Full protections enabled
│   └── expected/               # Golden test references
│       ├── test_hello_x64.json
│       └── ...
├── unit/                        # Unit tests (83 tests)
│   ├── core/
│   │   ├── test_models.py      # Data model tests
│   │   └── test_runner.py      # Pipeline orchestration
│   ├── recon/
│   │   ├── test_file_info.py   # File metadata detection
│   │   ├── test_protections.py # Security feature detection
│   │   ├── test_strings_mod.py # String extraction
│   │   └── test_imports_exports.py # Symbol analysis
│   ├── backends/
│   │   └── test_r2_analyzer.py # Radare2 integration (deferred)
│   └── test_edge_cases.py      # Robustness tests (15 tests)
└── integration/                 # Integration tests (15 tests)
    ├── test_pipeline.py        # Full pipeline tests
    └── test_golden.py          # Regression tests (4 tests)
```

### Test Categories Explained

#### Unit Tests (83 tests)
Test individual components in isolation, using mocks for external dependencies.

**Examples:**
- Data model serialization
- Recon module logic (with mocked subprocesses)
- Error handling paths
- Input validation

#### Integration Tests (15 tests)
Test complete workflows with real components and sample binaries.

**Examples:**
- Full analysis pipeline
- Multi-binary batch processing
- Report generation
- Real subprocess execution

#### Golden Tests (4 tests)
Compare current outputs against known-good reference files to detect regressions.

**Examples:**
- Complete analysis output for `test_hello_x64`
- Analysis output for stripped binary
- Analysis output for hardened binary (PIE, canary, etc.)

#### Edge Case Tests (15 tests)
Test robustness with unusual or malformed inputs.

**Examples:**
- Empty files
- Corrupted ELF headers
- Permission denied scenarios
- Large files
- Unicode file paths
- Concurrent execution

#### Property Tests (2 tests)
Verify invariants that should always hold true.

**Examples:**
- Report path must match input path
- Pipeline must not lose data (enrichment only)

---

## Running Tests

### Basic Commands

```bash
# All tests
pytest

# Verbose output (shows each test name)
pytest -v

# Very verbose (shows full diffs on failure)
pytest -vv

# Stop on first failure
pytest -x

# Show output (including print statements)
pytest -s

# Specific test file
pytest tests/unit/recon/test_protections.py

# Specific test class
pytest tests/unit/recon/test_protections.py::TestProtectionsRecon

# Specific test method
pytest tests/unit/recon/test_protections.py::TestProtectionsRecon::test_full_protections_detection
```

### Using Test Markers

Tests are marked with categories for easy filtering:

```python
# In test files, you'll see:
@pytest.mark.unit              # Unit test
@pytest.mark.integration       # Integration test
@pytest.mark.slow              # Takes >1 second
@pytest.mark.golden            # Golden/regression test
@pytest.mark.requires_r2       # Requires radare2
@pytest.mark.requires_checksec # Requires checksec tool
```

Run tests by marker:

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Exclude slow tests (recommended for development)
pytest -m "not slow"

# Exclude tests that need radare2
pytest -m "not requires_r2"

# Combine markers (unit tests that don't need r2)
pytest -m "unit and not requires_r2"

# Only golden tests
pytest -m golden
```

### Parallel Execution

Speed up test execution using pytest-xdist:

```bash
# Run tests in parallel (uses all CPU cores)
pytest -n auto

# Run tests on 4 cores
pytest -n 4

# Parallel + exclude slow tests
pytest -n auto -m "not slow"
```

### Filtering by Name

```bash
# Run all tests with "protection" in the name
pytest -k protection

# Run all tests with "error" in the name
pytest -k error

# Exclude tests with "slow" in the name
pytest -k "not slow"

# Combine patterns
pytest -k "protection and not timeout"
```

---

## Writing Tests

### Test Structure Template

```python
"""
Unit tests for MyModule.

This module tests [what it tests].
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from caspoon.my_module import MyModule
from caspoon.core.models import ExecutableReport


class TestMyModule:
    """Test MyModule class."""
    
    @pytest.fixture
    def module(self):
        """Create MyModule instance for testing."""
        return MyModule()
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        return ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
        )
    
    def test_basic_functionality(self, module, sample_report):
        """Test basic functionality with valid input."""
        # Arrange
        expected_result = "expected_value"
        
        # Act
        result = module.process(sample_report)
        
        # Assert
        assert result is not None
        assert result.some_field == expected_result
    
    def test_error_handling(self, module):
        """Test error handling with invalid input."""
        # Should not crash
        result = module.process(None)
        assert result is not None
```

### Common Testing Patterns

#### 1. Mocking Subprocess Calls

Most recon modules call external tools via subprocess:

```python
def test_subprocess_call(self, module):
    """Test subprocess handling."""
    with patch('subprocess.run') as mock_run:
        # Configure mock
        mock_run.return_value = Mock(
            returncode=0,
            stdout="mocked output",
            stderr=""
        )
        
        # Run test
        result = module.analyze("/test/binary")
        
        # Verify
        assert result is not None
        mock_run.assert_called_once()
```

#### 2. Testing Error Paths

Always test what happens when things go wrong:

```python
def test_file_not_found(self, module):
    """Test handling of missing file."""
    result = module.analyze("/nonexistent/path")
    
    # Should not crash
    assert result is not None
    # Should indicate error
    assert "error" in result.raw_backend_data

def test_tool_not_available(self, module):
    """Test handling when external tool is missing."""
    with patch('subprocess.run', side_effect=FileNotFoundError):
        result = module.analyze("/test/binary")
        
        # Should degrade gracefully
        assert result is not None

def test_timeout_handling(self, module):
    """Test timeout handling."""
    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", 30)):
        result = module.analyze("/test/binary")
        
        assert result is not None
        # Should record timeout
        assert "timeout" in str(result.raw_backend_data)
```

#### 3. Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("input,expected", [
    ("x86-64", 64),
    ("i386", 32),
    ("ARM", 32),
    ("aarch64", 64),
])
def test_arch_detection(self, module, input, expected):
    """Test architecture detection for various inputs."""
    result = module.detect_bits(input)
    assert result == expected

@pytest.mark.parametrize("protection,value,expected", [
    ("pie", "full", True),
    ("pie", "none", False),
    ("relro", "full", "full"),
    ("relro", "partial", "partial"),
])
def test_protection_parsing(self, module, protection, value, expected):
    """Test protection value parsing."""
    result = module.parse_protection(protection, value)
    assert result == expected
```

#### 4. Using Fixtures

Fixtures provide reusable test data and setup:

```python
# Available fixtures (defined in conftest.py):
def test_with_fixtures(
    self,
    fixtures_dir,        # Path to tests/fixtures/
    test_binaries_dir,   # Path to test binaries
    sample_binary,       # Path to a sample binary
    tmp_path            # Pytest built-in: temporary directory
):
    """Test using multiple fixtures."""
    # Use test binary
    binary = test_binaries_dir / "test_hello_x64"
    assert binary.exists()
    
    # Use temporary directory for output
    output = tmp_path / "output.json"
    
    # Test logic...
```

#### 5. Testing with Real Binaries

```python
@pytest.mark.integration
def test_with_real_binary(self, test_binaries_dir):
    """Integration test with real binary."""
    binary_path = test_binaries_dir / "test_hello_x64"
    
    if not binary_path.exists():
        pytest.skip("Test binary not available")
    
    runner = ReconRunner()
    report = runner.run(str(binary_path))
    
    # Verify analysis results
    assert report.arch == "x86-64"
    assert report.bits == 64
    assert len(report.strings) > 0
```

#### 6. Testing Invariants (Property Tests)

```python
def test_path_invariant(self, module, sample_binary):
    """Test that output path matches input path."""
    report = module.analyze(str(sample_binary))
    
    # Invariant: path must be preserved
    assert report.path == str(sample_binary)

def test_enrichment_only(self, module, sample_report):
    """Test that processing only adds data, never removes."""
    original_strings = len(sample_report.strings)
    
    result = module.process(sample_report)
    
    # Invariant: should only enrich, not remove
    assert len(result.strings) >= original_strings
```

### Test Organization Guidelines

#### File Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_it_tests>`

#### Test Naming
Be descriptive:

✅ **Good names:**
- `test_detects_full_pie_protection`
- `test_handles_missing_checksec_gracefully`
- `test_extracts_strings_from_stripped_binary`

❌ **Avoid:**
- `test_1`
- `test_it_works`
- `test_something`

#### Test Structure
Follow Arrange-Act-Assert pattern:

```python
def test_something(self):
    """Test something specific."""
    # Arrange: Set up test data
    input_data = create_test_data()
    
    # Act: Execute the code under test
    result = process(input_data)
    
    # Assert: Verify the results
    assert result == expected
```

---

## Test Coverage

### Checking Coverage

```bash
# Terminal report
pytest --cov=caspoon --cov-report=term-missing

# HTML report (detailed, interactive)
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html  # On macOS
# Or: xdg-open htmlcov/index.html  # On Linux
# Or: start htmlcov/index.html     # On Windows

# XML report (for CI systems)
pytest --cov=caspoon --cov-report=xml

# Generate all formats at once
pytest --cov=caspoon --cov-report=term-missing --cov-report=html --cov-report=xml
```

### Current Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| **core/models.py** | 100% | ✅ Excellent |
| **core/runner.py** | 100% | ✅ Excellent |
| **recon/file_info.py** | 100% | ✅ Excellent |
| **recon/protections.py** | 100% | ✅ Excellent |
| **recon/strings_mod.py** | 100% | ✅ Excellent |
| **recon/imports_exports.py** | 94% | ✅ Very Good |
| **backends/r2_recon.py** | 62% | ⚠️ Deferred |
| **backends/r2_analyzer.py** | 25% | ⚠️ Deferred |
| **Overall** | **84.07%** | ✅ Excellent |

**Note**: Backend coverage is deferred because radare2 is not available in all test environments. Tests gracefully skip when r2 is missing.

### Coverage Goals

- **Minimum acceptable**: 70% overall
- **Target**: 80%+ overall ✅ (achieved: 84%)
- **Critical modules** (core, recon): 90%+ ✅ (achieved: 94-100%)

### Interpreting Coverage Reports

When viewing the HTML report (`htmlcov/index.html`):

- **Green lines**: Covered by tests
- **Red lines**: Not covered by tests
- **Yellow lines**: Partially covered (e.g., branches)

Focus on covering:
1. **Error paths**: What happens when things fail?
2. **Branch conditions**: Both if/else paths
3. **Edge cases**: Boundary conditions

### Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["caspoon"]
omit = [
    "*/tests/*",      # Don't measure test code
    "*/__main__.py",  # Entry points excluded
    "*/main.py",      # CLI entry excluded
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

---

## Golden Tests

Golden tests detect unintended changes in behavior by comparing current outputs against known-good reference files.

### What Are Golden Tests?

Golden tests:
- Store "golden" (reference) output from a known-good version
- Run analysis and compare against the golden output
- Fail if output differs (potential regression)
- Can be updated when changes are intentional

### Running Golden Tests

```bash
# Run all golden tests
pytest -m golden

# Run specific golden test
pytest tests/integration/test_golden.py::TestGoldenOutputs::test_golden_test_hello_x64 -v

# Check if golden test framework is working
pytest tests/integration/test_golden.py::test_golden_framework_available
```

### Updating Golden Files

When you make **intentional** changes that affect output:

```bash
# Update all golden files
pytest tests/integration/test_golden.py --update-golden

# Review what changed
git diff tests/fixtures/expected/

# If changes look correct, commit them
git add tests/fixtures/expected/
git commit -m "Update golden tests after [reason for change]"
```

⚠️ **Important**: Always review the diffs before committing. Unexpected changes may indicate a bug.

### Adding a New Golden Test

1. **Add test in `tests/integration/test_golden.py`**:

```python
def test_golden_my_binary(self, test_binaries_dir, golden_dir, update_golden):
    """Golden test for my_binary."""
    binary_name = "my_binary"
    binary_path = test_binaries_dir / binary_name
    golden_path = golden_dir / f"{binary_name}.json"
    
    if not binary_path.exists():
        pytest.skip(f"{binary_name} not available")
    
    # Run analysis
    runner = ReconRunner()
    report = runner.run(str(binary_path))
    current_output = self._normalize_report(report.pretty())
    
    # Update mode: save new golden file
    if update_golden:
        with open(golden_path, 'w') as f:
            json.dump(current_output, f, indent=2, sort_keys=True)
        pytest.skip(f"Updated golden file: {golden_path}")
    
    # Test mode: compare against golden file
    if not golden_path.exists():
        pytest.skip(f"Golden file not found. Run with --update-golden")
    
    with open(golden_path) as f:
        expected = json.load(f)
    
    assert current_output == expected, "Output differs from golden file"
```

2. **Generate the golden file**:

```bash
pytest tests/integration/test_golden.py::test_golden_my_binary --update-golden
```

3. **Verify and commit**:

```bash
# Check what was generated
cat tests/fixtures/expected/my_binary.json

# Commit
git add tests/fixtures/expected/my_binary.json
git commit -m "Add golden test for my_binary"
```

### Golden Test Best Practices

✅ **Do:**
- Use golden tests for complex outputs
- Normalize outputs (remove timestamps, paths, etc.)
- Review diffs carefully before committing updates
- Document why you updated golden files

❌ **Don't:**
- Use golden tests for simple assertions (use regular tests)
- Update golden files without reviewing changes
- Include environment-specific data (paths, timestamps)

---

## Best Practices

### General Testing Principles

#### ✅ DO

1. **Test one thing at a time**
   ```python
   # Good: Focused test
   def test_detects_pie_enabled(self):
       result = parse_checksec("PIE enabled")
       assert result.pie == "full"
   
   # Avoid: Testing multiple things
   def test_everything(self):
       # Tests PIE, NX, canary, RELRO, errors...
       # Too much in one test!
   ```

2. **Use descriptive names**
   ```python
   # Good
   def test_handles_corrupted_elf_gracefully(self):
       ...
   
   # Bad
   def test_case_5(self):
       ...
   ```

3. **Mock external dependencies**
   ```python
   # Good: Fast, deterministic
   with patch('subprocess.run') as mock:
       mock.return_value = Mock(returncode=0, stdout="output")
       result = module.analyze("/test")
   
   # Avoid: Slow, depends on system
   result = module.analyze("/bin/ls")  # Calls real subprocess
   ```

4. **Test error paths**
   ```python
   # Always test what happens when things fail
   def test_handles_file_not_found(self):
       result = analyze("/nonexistent")
       assert result is not None  # No crash
   ```

5. **Use fixtures for setup**
   ```python
   # Good: Reusable setup
   @pytest.fixture
   def configured_module(self):
       module = MyModule()
       module.timeout = 10
       return module
   
   def test_with_fixture(self, configured_module):
       result = configured_module.run()
       assert result is not None
   ```

#### ❌ DON'T

1. **Don't rely on external state**
   ```python
   # Bad: Depends on specific file existing
   def test_bad(self):
       result = analyze("/tmp/test.bin")  # May not exist!
   
   # Good: Use fixtures
   def test_good(self, tmp_path):
       test_file = tmp_path / "test.bin"
       test_file.write_bytes(b"data")
       result = analyze(str(test_file))
   ```

2. **Don't test implementation details**
   ```python
   # Bad: Testing internal structure
   def test_bad(self):
       module = MyModule()
       assert hasattr(module, '_internal_cache')  # Implementation detail
   
   # Good: Testing behavior
   def test_good(self):
       result = MyModule().process(data)
       assert result == expected  # Public behavior
   ```

3. **Don't use hardcoded paths**
   ```python
   # Bad
   def test_bad(self):
       result = analyze("/home/user/test.bin")
   
   # Good
   def test_good(self, test_binaries_dir):
       binary = test_binaries_dir / "test.bin"
       result = analyze(str(binary))
   ```

4. **Don't skip error testing**
   ```python
   # Always test the sad path, not just the happy path
   def test_only_success(self):
       result = module.run(valid_input)  # Only tests success
   
   # Better: Also test errors
   def test_error_handling(self):
       result = module.run(invalid_input)
       assert result is not None  # Handles errors
   ```

5. **Don't commit failing tests**
   ```python
   # If test can't pass yet:
   @pytest.mark.skip(reason="Feature not implemented yet")
   def test_future_feature(self):
       ...
   
   # Or if it's a known failure:
   @pytest.mark.xfail(reason="Bug #123")
   def test_known_bug(self):
       ...
   ```

### Test Isolation

Tests must be independent:

```python
# ❌ Bad: Shared mutable state
class TestBad:
    results = []  # Shared across all tests!
    
    def test_one(self):
        self.results.append(1)  # Affects test_two
    
    def test_two(self):
        assert len(self.results) == 1  # Breaks if test_one ran first!

# ✅ Good: Fresh state per test
class TestGood:
    @pytest.fixture
    def results(self):
        return []  # New list for each test
    
    def test_one(self, results):
        results.append(1)
        assert len(results) == 1
    
    def test_two(self, results):
        assert len(results) == 0  # Always starts fresh
```

### Debugging Failed Tests

```bash
# Show full output
pytest -vv -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace

# Show captured logs
pytest --log-cli-level=DEBUG

# Run only the failed test
pytest tests/unit/recon/test_protections.py::TestProtectionsRecon::test_timeout_handling -vv
```

---

## CI/CD Integration

### GitHub Actions Example

Tests are designed to run in CI environments:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest --cov=caspoon --cov-report=xml --cov-report=term
      
      - name: Check coverage
        run: |
          coverage report --fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

Run tests before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest -m "not slow" -x
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Troubleshooting

### Common Issues

#### "Test binary not found"

```bash
# Build test binaries
cd tests/fixtures/binaries/src/
make clean && make
```

#### "ModuleNotFoundError: No module named 'caspoon'"

```bash
# Install in editable mode
pip install -e .
```

#### "Tool not available" (checksec, radare2, etc.)

Tests should skip gracefully, but if you want full coverage:

```bash
# Ubuntu/Debian
sudo apt install checksec radare2

# macOS
brew install checksec radare2
```

#### "Coverage doesn't match expected"

```bash
# Clean coverage data
rm .coverage coverage.xml
rm -rf htmlcov/

# Re-run tests
pytest --cov=caspoon --cov-report=html
```

#### "Tests pass locally but fail in CI"

Common causes:
- External tool not installed in CI
- Environment variables different
- File paths hardcoded
- Tests not isolated (shared state)

Solution: Check CI logs and ensure tests use fixtures, not hardcoded paths.

### Getting Help

- 📖 See test examples in `tests/unit/` and `tests/integration/`
- 📖 Read [pytest documentation](https://docs.pytest.org/)
- 🐛 Open an issue for test infrastructure bugs

---

## Quick Reference

```bash
# Development workflow
pytest -m "not slow" -x              # Fast feedback, stop on failure
pytest tests/unit/my_module/ -v     # Test specific module
pytest --cov=caspoon --cov-report=term-missing  # Check coverage

# Before committing
pytest -m "not slow"                 # All fast tests
pytest --cov=caspoon                 # With coverage

# Full test suite
pytest                               # All tests
pytest --cov=caspoon --cov-report=html  # With detailed coverage

# Golden tests
pytest -m golden                     # Check for regressions
pytest tests/integration/test_golden.py --update-golden  # Update after intentional changes
```

---

**For more information:**
- [README.md](README.md) - Project overview
- [docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md) - Architecture details
