# Caspoon Test Suite

> **📖 For comprehensive testing documentation, see [../docs/guides/TESTING.md](../docs/guides/TESTING.md)**

Comprehensive test suite for the Caspoon binary analysis tool.

**Quick Links:**
- **[TESTING.md](../docs/guides/TESTING.md)** - Complete testing guide (running tests, writing tests, coverage)
- **[TESTING_GUIDE.md](../docs/guides/TESTING_GUIDE.md)** - Quick reference for developers

---

## Quick Start

```bash
# Run all tests (fast)
pytest -m "not slow"

# Run with coverage
pytest --cov=caspoon --cov-report=html

# Run specific category
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest -m golden                # Golden tests
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data
│   ├── binaries/           # Test binaries (built from src/)
│   │   ├── test_hello_x64
│   │   ├── test_stripped
│   │   └── test_with_pie
│   └── expected/           # Golden test data (JSON)
├── unit/                    # Unit tests
│   ├── core/               # Core functionality tests
│   │   ├── test_models.py
│   │   └── test_runner.py
│   ├── recon/              # Recon module tests
│   │   ├── test_file_info.py
│   │   ├── test_protections.py
│   │   ├── test_strings_mod.py
│   │   └── test_imports_exports.py
│   └── test_edge_cases.py  # Robustness tests
└── integration/             # Integration tests
    ├── test_pipeline.py     # Full pipeline tests
    └── test_golden.py       # Regression tests
```

## Test Statistics

- **Total Tests**: 103 passing, 4 skipped
- **Coverage**: 84.07% overall
  - Core modules: 100%
  - Recon modules: 94-100%
  - Backends: 25-62% (deferred)

## Test Categories

### Unit Tests (83 tests)
Test individual components in isolation:
- Data models (dataclasses, serialization)
- Recon modules (file info, protections, strings, imports/exports)
- Runner orchestration
- Error handling

### Integration Tests (15 tests)
Test complete workflows:
- Full analysis pipeline
- Multi-binary analysis
- Report generation
- Error recovery

### Golden Tests (4 tests)
Regression detection:
- Compare outputs against known-good references
- Detect unintended behavior changes
- Update with `--update-golden` flag

### Edge Case Tests (15 tests)
Robustness and defensive testing:
- Malformed inputs (empty, corrupted, non-ELF)
- Resource limits (large files, truncation)
- Error conditions (permissions, timeouts)
- Special cases (unicode, symlinks, concurrent)

### Property Tests (2 tests)
Invariant verification:
- Path consistency
- Data enrichment (no data loss)

## Running Tests

### Basic Usage
```bash
# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Specific file
pytest tests/unit/recon/test_protections.py

# Specific test
pytest tests/unit/recon/test_protections.py::TestProtectionsRecon::test_full_protections_detection
```

### By Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Exclude slow tests
pytest -m "not slow"

# Golden tests only
pytest -m golden
```

### With Coverage
```bash
# Terminal report
pytest --cov=caspoon --cov-report=term-missing

# HTML report
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=caspoon --cov-report=xml
```

## Writing Tests

See [TESTING_GUIDE.md](../docs/guides/TESTING_GUIDE.md) for:
- Test patterns and best practices
- Common fixtures and markers
- Golden test workflow
- Mock examples
- Debugging tips

## Test Fixtures

### Available Fixtures
- `fixtures_dir` - Path to tests/fixtures/
- `test_binaries_dir` - Path to test binaries
- `sample_binary` - Sample binary for testing (ls or test_hello_x64)
- `tmp_path` - Temporary directory (pytest built-in)

### Test Binaries
Built from `fixtures/binaries/src/`:
```bash
cd fixtures/binaries/src/
make              # Build all test binaries
make clean        # Remove test binaries
```

Binaries:
- **test_hello_x64** - Standard x64 binary, not stripped, no PIE
- **test_stripped** - Stripped binary (no debug symbols)
- **test_with_pie** - Full protections (PIE, canary, NX, full RELRO)

## Test Markers

Use markers to categorize tests:
```python
@pytest.mark.unit              # Unit test
@pytest.mark.integration       # Integration test
@pytest.mark.slow              # Slow test (>1s)
@pytest.mark.golden            # Golden/regression test
@pytest.mark.requires_r2       # Requires radare2
@pytest.mark.requires_checksec # Requires checksec tool
```

Run by marker:
```bash
pytest -m integration          # Only integration tests
pytest -m "not slow"           # Exclude slow tests
pytest -m "unit and not requires_r2"  # Unit tests without r2
```

## Golden Tests

Regression detection using reference outputs.

### Running
```bash
# Run golden tests
pytest -m golden

# Update golden files (after intentional changes)
pytest tests/integration/test_golden.py --update-golden
```

### Workflow
1. Make changes to analysis code
2. Run `pytest -m golden` to check for regressions
3. If changes are intentional:
   ```bash
   pytest tests/integration/test_golden.py --update-golden
   git diff tests/fixtures/expected/  # Review changes
   git add tests/fixtures/expected/
   git commit -m "Update golden tests for [reason]"
   ```

## Coverage Goals

- **Minimum**: 70% overall
- **Target**: 80%+ overall (✅ achieved: 84.07%)
- **Critical modules** (recon, core): 90%+ (✅ achieved: 94-100%)

Check coverage:
```bash
pytest --cov=caspoon --cov-report=term-missing
```

## CI/CD Integration

Tests are designed to run in CI:
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=caspoon --cov-report=xml

- name: Check coverage
  run: coverage report --fail-under=80
```

## Debugging Tests

```bash
# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show full diff
pytest -vv

# See captured logs
pytest --log-cli-level=DEBUG
```

## Common Issues

### Test Binary Not Found
```bash
cd tests/fixtures/binaries/src/
make
```

### Tool Dependencies
Some tests require external tools:
- `file` - File type detection (usually pre-installed)
- `strings` - String extraction (usually pre-installed)
- `checksec` - Security feature detection (optional, tests skip if missing)
- `radare2` - Advanced analysis (optional, tests skip if missing)

Tests gracefully skip if tools are missing.

## Documentation

- **[TESTING_GUIDE.md](../docs/guides/TESTING_GUIDE.md)** - Developer quick reference
- **[TESTING.md](../docs/guides/TESTING.md)** - Comprehensive testing documentation

## Contributing

When adding new features:

1. **Write tests first** (TDD)
   ```python
   def test_my_new_feature():
       result = my_module.new_feature()
       assert result == expected
   ```

2. **Test error paths**
   ```python
   def test_my_feature_error_handling():
       result = my_module.new_feature(bad_input)
       assert result is not None  # No crash
   ```

3. **Run tests**
   ```bash
   pytest tests/ -m "not slow"
   ```

4. **Check coverage**
   ```bash
   pytest --cov=caspoon --cov-report=term-missing
   ```

5. **Update golden tests if needed**
   ```bash
   pytest -m golden --update-golden
   ```

## License

Same as parent project.
