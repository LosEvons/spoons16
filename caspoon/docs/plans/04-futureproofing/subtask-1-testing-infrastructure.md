# Subtask 1: Testing Infrastructure Setup

## Objective
Create comprehensive testing infrastructure with directory structure, pytest configuration, test fixtures, and initial unit tests. This is the **CRITICAL** foundation that blocks all feature development.

## Priority
🔴 **CRITICAL - Must complete first**

## Scope
- Create test directory structure
- Configure pytest
- Create test fixtures (sample binaries)
- Write initial unit tests for core models
- Write unit tests for FileInfoRecon
- Write one integration test
- Achieve 50%+ code coverage baseline

## Prerequisites
- Python 3.10+ installed
- Access to repository
- GCC or compatible compiler (for creating test binaries)

## Implementation Steps

### Step 1: Create Test Directory Structure (30 minutes)

Create the following directory structure:

```bash
caspoon/
├── tests/                          # CREATE THIS
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures and config
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py     # Test ExecutableReport, etc.
│   │   │   └── test_runner.py     # Test ReconRunner
│   │   ├── recon/
│   │   │   ├── __init__.py
│   │   │   └── test_file_info.py  # Test FileInfoRecon
│   │   ├── backends/
│   │   │   ├── __init__.py
│   │   │   └── test_r2_analyzer.py
│   │   └── ui/
│   │       └── __init__.py
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   └── test_pipeline.py       # Test full pipeline
│   └── fixtures/                   # Test data
│       ├── binaries/               # Test binaries
│       │   ├── src/                # Source code
│       │   │   ├── hello_world.c
│       │   │   └── Makefile
│       │   └── README.md
│       └── expected/               # Expected outputs
│           └── README.md
```

**Commands**:
```bash
cd /home/runner/work/spoons16/spoons16/caspoon
mkdir -p tests/{unit/{core,recon,backends,ui},integration,fixtures/{binaries/src,expected}}
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/core/__init__.py
touch tests/unit/recon/__init__.py
touch tests/unit/backends/__init__.py
touch tests/unit/ui/__init__.py
touch tests/integration/__init__.py
```

### Step 2: Configure pytest (30 minutes)

**File**: `caspoon/pyproject.toml`

Add pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=caspoon",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "requires_r2: marks tests that require radare2",
]

[tool.coverage.run]
source = ["caspoon"]
omit = [
    "*/tests/*",
    "*/__main__.py",
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
precision = 2
```

**File**: `caspoon/tests/conftest.py`

Create shared fixtures:

```python
"""Shared test fixtures and configuration."""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_binaries_dir(fixtures_dir):
    """Return path to test binaries directory."""
    return fixtures_dir / "binaries"


@pytest.fixture
def sample_binary(test_binaries_dir):
    """Return path to a sample test binary."""
    # Will use system binary initially, then custom test binary
    from shutil import which
    ls_path = which("ls")
    if ls_path:
        return ls_path
    # Fallback to test binary once created
    test_bin = test_binaries_dir / "test_hello_x64"
    if test_bin.exists():
        return str(test_bin)
    pytest.skip("No test binary available")
```

### Step 3: Create Test Fixtures (1 hour)

**File**: `caspoon/tests/fixtures/binaries/src/hello_world.c`

```c
#include <stdio.h>
#include <stdlib.h>

int helper_function(int a, int b) {
    return a + b;
}

int main(int argc, char *argv[]) {
    printf("Hello, World!\\n");
    printf("This is a test binary for caspoon\\n");
    
    int result = helper_function(5, 3);
    printf("5 + 3 = %d\\n", result);
    
    return 0;
}
```

**File**: `caspoon/tests/fixtures/binaries/src/Makefile`

```makefile
CC=gcc
CFLAGS=-Wall

all: test_hello_x64 test_hello_x86 test_stripped test_with_pie

test_hello_x64: hello_world.c
	$(CC) $(CFLAGS) -o ../test_hello_x64 hello_world.c

test_hello_x86: hello_world.c
	$(CC) $(CFLAGS) -m32 -o ../test_hello_x86 hello_world.c 2>/dev/null || echo "32-bit compilation not available"

test_stripped: hello_world.c
	$(CC) $(CFLAGS) -s -o ../test_stripped hello_world.c

test_with_pie: hello_world.c
	$(CC) $(CFLAGS) -fPIE -pie -fstack-protector-all -Wl,-z,relro,-z,now -o ../test_with_pie hello_world.c

clean:
	rm -f ../test_hello_x64 ../test_hello_x86 ../test_stripped ../test_with_pie

.PHONY: all clean
```

**File**: `caspoon/tests/fixtures/binaries/README.md`

```markdown
# Test Binary Fixtures

## Overview
This directory contains test binaries used for caspoon testing.

## Test Binaries

### test_hello_x64
- **Architecture**: x86-64
- **Purpose**: Basic functionality testing
- **Features**: Standard ELF, not stripped, PIE disabled

### test_hello_x86
- **Architecture**: x86 (32-bit)
- **Purpose**: 32-bit support testing
- **Features**: 32-bit ELF (if gcc -m32 available)

### test_stripped
- **Architecture**: x86-64
- **Purpose**: Test stripped binary detection
- **Features**: Debug symbols stripped

### test_with_pie
- **Architecture**: x86-64
- **Purpose**: Test security feature detection
- **Features**: PIE, stack canary, NX, full RELRO

## Building Test Binaries

```bash
cd src/
make
```

## Cleanup

```bash
cd src/
make clean
```
```

**Commands to build test binaries**:
```bash
cd /home/runner/work/spoons16/spoons16/caspoon/tests/fixtures/binaries/src
make
```

### Step 4: Write Unit Tests for Core Models (1.5 hours)

**File**: `caspoon/tests/unit/core/test_models.py`

```python
"""Unit tests for core data models."""
import pytest
from caspoon.core.models import (
    ExecutableReport,
    ProtectionInfo,
    FunctionInfo,
)


class TestProtectionInfo:
    """Test ProtectionInfo dataclass."""

    def test_default_protections(self):
        """Test default protection values."""
        pi = ProtectionInfo()
        
        assert pi.pie is False
        assert pi.nx is False
        assert pi.canary is False
        assert pi.relro == "Unknown"

    def test_full_protections(self):
        """Test fully protected binary."""
        pi = ProtectionInfo(
            pie=True,
            nx=True,
            canary=True,
            relro="full"
        )
        
        assert pi.pie is True
        assert pi.nx is True
        assert pi.canary is True
        assert pi.relro == "full"

    def test_partial_relro(self):
        """Test partial RELRO."""
        pi = ProtectionInfo(relro="partial")
        assert pi.relro == "partial"


class TestFunctionInfo:
    """Test FunctionInfo dataclass."""

    def test_create_function(self):
        """Test creating function info."""
        func = FunctionInfo(name="main", address=0x400000)
        
        assert func.name == "main"
        assert func.address == 0x400000
        assert func.imported is False

    def test_imported_function(self):
        """Test imported function flag."""
        func = FunctionInfo(
            name="printf",
            address=0x0,
            imported=True
        )
        
        assert func.imported is True


class TestExecutableReport:
    """Test ExecutableReport dataclass."""

    def test_create_empty_report(self):
        """Test creating empty report."""
        report = ExecutableReport(path="/test/binary")
        
        assert report.path == "/test/binary"
        assert report.arch == ""
        assert report.bits is None
        assert report.file_type == ""
        assert report.stripped is False
        assert report.protections is None
        assert len(report.strings) == 0
        assert len(report.imports) == 0
        assert len(report.exports) == 0
        assert len(report.raw_backend_data) == 0

    def test_create_full_report(self):
        """Test creating report with all fields."""
        protections = ProtectionInfo(
            pie=True,
            nx=True,
            canary=True,
            relro="full"
        )
        
        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            file_type="ELF 64-bit LSB executable",
            stripped=False,
            protections=protections,
            strings=["hello", "world"],
            imports=["printf", "exit"],
            exports=["main"],
            raw_backend_data={"test": "data"}
        )
        
        assert report.arch == "x86-64"
        assert report.bits == 64
        assert report.file_type == "ELF 64-bit LSB executable"
        assert report.stripped is False
        assert report.protections.pie is True
        assert len(report.strings) == 2
        assert "hello" in report.strings
        assert len(report.imports) == 2
        assert "printf" in report.imports
        assert len(report.exports) == 1
        assert "main" in report.exports

    def test_pretty_output(self):
        """Test pretty() method returns dict."""
        protections = ProtectionInfo(pie=True)
        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            protections=protections,
            strings=["test"]
        )
        
        pretty = report.pretty()
        
        assert isinstance(pretty, dict)
        assert pretty["path"] == "/test/binary"
        assert pretty["arch"] == "x86-64"
        assert pretty["bits"] == 64
        assert "protections" in pretty
        assert pretty["strings_count"] == 1

    def test_pretty_unknown_bits(self):
        """Test pretty() with None bits."""
        report = ExecutableReport(path="/test")
        pretty = report.pretty()
        
        assert pretty["bits"] == "unknown"
```

### Step 5: Write Unit Tests for FileInfoRecon (1.5 hours)

**File**: `caspoon/tests/unit/recon/test_file_info.py`

```python
"""Unit tests for FileInfoRecon module."""
import pytest
from caspoon.recon.file_info import FileInfoRecon
from caspoon.core.models import ExecutableReport


class TestFileInfoRecon:
    """Test FileInfoRecon module."""

    @pytest.fixture
    def recon(self):
        """Create FileInfoRecon instance."""
        return FileInfoRecon()

    def test_module_name(self, recon):
        """Test module has correct name."""
        assert recon.name == "file_info"

    def test_analyze_system_binary(self, recon, sample_binary):
        """Test analysis of system binary."""
        report = ExecutableReport(path=sample_binary)
        result = recon.run(sample_binary, report)
        
        # Should have some arch info
        assert result.arch != "" or result.file_type != ""
        assert result is not None

    def test_nonexistent_file(self, recon):
        """Test handling of nonexistent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)
        
        # Should handle gracefully, not crash
        assert result is not None
        assert result.path == "/nonexistent/file"

    def test_report_enrichment(self, recon, sample_binary):
        """Test that report is enriched with data."""
        report = ExecutableReport(path=sample_binary)
        
        # Before: empty
        assert report.arch == ""
        assert report.file_type == ""
        
        # After: enriched
        result = recon.run(sample_binary, report)
        
        # Should have at least one field populated
        # (arch or file_type, depending on file command output)
        assert result.arch != "" or result.file_type != ""
```

### Step 6: Write Integration Test (1 hour)

**File**: `caspoon/tests/integration/test_pipeline.py`

```python
"""Integration tests for full analysis pipeline."""
import pytest
from caspoon.core.runner import ReconRunner
from caspoon.core.models import ExecutableReport


@pytest.mark.integration
class TestFullPipeline:
    """Test complete analysis pipeline."""

    @pytest.fixture
    def runner(self):
        """Create ReconRunner instance."""
        return ReconRunner()

    def test_runner_has_steps(self, runner):
        """Test runner is configured with recon steps."""
        assert len(runner.steps) > 0
        assert hasattr(runner.steps[0], 'run')

    def test_analyze_system_binary(self, runner, sample_binary):
        """Test full analysis of system binary."""
        report = runner.run(sample_binary)
        
        # Verify basic analysis completed
        assert report is not None
        assert report.path == sample_binary
        
        # Should have some data from recon modules
        # (exact data depends on which modules succeed)
        assert isinstance(report, ExecutableReport)

    def test_report_structure(self, runner, sample_binary):
        """Test that report has expected structure."""
        report = runner.run(sample_binary)
        
        # Verify report structure
        assert hasattr(report, 'path')
        assert hasattr(report, 'arch')
        assert hasattr(report, 'bits')
        assert hasattr(report, 'protections')
        assert hasattr(report, 'strings')
        assert hasattr(report, 'imports')
        assert hasattr(report, 'exports')
        assert hasattr(report, 'raw_backend_data')
```

### Step 7: Add .gitignore Entries (5 minutes)

**File**: `.gitignore` (add these lines)

```
# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml
.tox/
*.cover
.hypothesis/

# Test binaries (except source)
tests/fixtures/binaries/test_*
!tests/fixtures/binaries/src/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
```

### Step 8: Verify Setup (30 minutes)

**Commands to run**:

```bash
# Navigate to caspoon directory
cd /home/runner/work/spoons16/spoons16/caspoon

# Install in development mode with test dependencies
pip install -e ".[dev]"

# Build test binaries
cd tests/fixtures/binaries/src
make
cd ../../../..

# Run tests
pytest tests/unit/core/test_models.py -v
pytest tests/unit/recon/test_file_info.py -v
pytest tests/integration/test_pipeline.py -v

# Run all tests with coverage
pytest --cov=caspoon --cov-report=term

# Check coverage percentage
pytest --cov=caspoon --cov-report=term | tail -1
```

## Testing Strategy

### Self-Testing
1. **Test structure exists**: Verify directories created
2. **pytest runs**: Command executes without errors
3. **Tests pass**: Initial tests pass with system binaries
4. **Coverage works**: Coverage report generates
5. **Fixtures build**: Test binaries compile successfully

### Manual Verification
- [ ] Can run `pytest` command
- [ ] Tests execute and show results
- [ ] Coverage report shows percentage
- [ ] Test binaries exist in fixtures/binaries/
- [ ] .gitignore excludes test artifacts

## Success Criteria

- [ ] Test directory structure exists with all folders
- [ ] pytest.ini or pyproject.toml has pytest configuration
- [ ] conftest.py with shared fixtures exists
- [ ] At least 3 test binaries exist (hello_x64, stripped, with_pie)
- [ ] Unit tests for ExecutableReport pass (10+ tests)
- [ ] Unit tests for ProtectionInfo pass (3+ tests)
- [ ] Unit tests for FunctionInfo pass (2+ tests)
- [ ] Unit tests for FileInfoRecon pass (4+ tests)
- [ ] Integration test for pipeline passes
- [ ] Tests can be run with `pytest` command
- [ ] Coverage report generates successfully
- [ ] Coverage is 50%+ for core models and FileInfoRecon
- [ ] .gitignore properly excludes test artifacts

## Estimated Time
**6-7 hours total**
- Directory setup: 30 min
- pytest configuration: 30 min
- Test fixtures: 1 hour
- Models tests: 1.5 hours
- FileInfoRecon tests: 1.5 hours
- Integration test: 1 hour
- Verification: 30 min

## Common Issues & Solutions

### Issue 1: gcc not available
**Solution**: Use system binaries for initial tests, skip test binary creation

### Issue 2: Tests fail due to missing dependencies
**Solution**: Install dev dependencies: `pip install -e ".[dev]"`

### Issue 3: radare2 not available
**Solution**: Mark r2-dependent tests with `@pytest.mark.requires_r2` and skip

### Issue 4: Coverage too low
**Solution**: Initial baseline is 50%, will improve with more tests in later subtasks

## Next Steps

After completing this subtask:
1. Verify all tests pass: `pytest -v`
2. Check coverage: `pytest --cov=caspoon`
3. Proceed to **Subtask 2: CI/CD Pipeline Implementation**

## Dependencies
- Python 3.10+
- GCC (for test binary compilation)
- pip (for installing pytest)

## Deliverables
- Complete `tests/` directory structure
- Configured pytest in pyproject.toml
- Working test fixtures (binaries)
- 20+ passing unit tests
- 1+ passing integration test
- 50%+ code coverage on core modules
