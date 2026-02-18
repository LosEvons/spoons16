# GitHub Copilot Instructions for Caspoon

This file provides context and conventions for GitHub Copilot when working in the Caspoon repository.

---

## Project Overview

**Caspoon** is a modular, defensive binary analysis toolkit designed for reverse engineers and security researchers. It provides safe reconnaissance and analysis of executable files (primarily ELF binaries) without execution, featuring CLI and optional GUI interfaces.

**Purpose**: Extract metadata, security features, strings, symbols, and disassembly from potentially malicious binaries in an isolated, safe environment.

**Security Context**: This is a DEFENSIVE tool for analyzing potentially dangerous binaries. Code should never execute analyzed binaries directly and should handle untrusted input safely.

---

## Key Technologies

- **Python 3.10+** (target versions: 3.10, 3.11, 3.12)
- **pyelftools** - ELF file parsing and manipulation
- **r2pipe** - Integration with radare2 for advanced disassembly
- **rich** - Terminal text formatting and rendering
- **PySide6** - Optional GUI framework (via `--gui` flag)
- **pytest** - Testing framework with extensive plugin ecosystem

### External Tool Integration

- `file` - File type detection
- `strings` - String extraction (with fallback implementation)
- `checksec` - Security feature detection
- `radare2` - Advanced binary analysis and disassembly

*Note*: Caspoon gracefully handles missing external tools with fallback implementations.

---

## Architecture

Caspoon follows a **pipeline-based modular design**:

```
Entry Point (CLI)
        ↓
  ReconRunner ← Orchestrates all analysis
        ↓
ExecutableReport ← Central data model (accumulates results)
        ↓
  ┌─────┴─────┬─────────┬──────────┐
  ↓           ↓         ↓          ↓
FileInfo  Protections Strings  Imports/Exports
  Recon      Recon     Recon      Recon
```

### Key Components

1. **ReconRunner** (`caspoon/core/runner.py`): Orchestrates the analysis pipeline
2. **ExecutableReport** (`caspoon/core/models.py`): Central data model holding all analysis results
3. **Recon Modules** (`caspoon/recon/`): Independent analysis modules that enrich the report
4. **Backends** (`caspoon/backends/`): Integrations with external tools (radare2, etc.)
5. **GUI Layer** (`caspoon/gui/`): Optional PySide6-based GUI (via `--gui` flag)

### Data Flow

1. User provides binary path via CLI or GUI
2. `ReconRunner` creates empty `ExecutableReport`
3. Each recon module runs and enriches the report
4. Final report is returned as JSON (CLI) or displayed in GUI

---

## Project Structure

```
caspoon/
├── backends/          # External tool integrations
│   ├── base.py       # Base backend interface
│   ├── manager.py    # Backend lifecycle management
│   ├── r2_backend.py # Radare2 integration
│   ├── r2_analyzer.py # High-level r2 analysis
│   └── r2_recon.py   # Radare2 recon module
│
├── core/             # Core data models and orchestration
│   ├── models.py     # ExecutableReport and data classes
│   └── runner.py     # ReconRunner (pipeline orchestrator)
│
├── recon/            # Analysis modules (pipeline components)
│   ├── file_info.py  # File metadata extraction
│   ├── protections.py # Security features detection
│   ├── strings_mod.py # String extraction
│   └── imports_exports.py # Symbol analysis
│
├── docs/             # All documentation
│   ├── guides/       # User and developer guides
│   ├── plans/        # Design and implementation plans
│   ├── reference/    # API references and technical docs
│   └── changelogs/   # Change log entries
│       └── INDEX.md  # Changelog index (update when adding entries)
│
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── fixtures/     # Test binaries and data
│
├── main.py           # CLI entry point
└── pyproject.toml    # Project configuration
```

### Important Files to Reference

- **`pyproject.toml`** - Dependencies, tool configuration, test markers
- **`caspoon/core/models.py`** - All data models and type definitions
- **`caspoon/core/runner.py`** - Main orchestration logic
- **`caspoon/docs/reference/OVERVIEW.md`** - Comprehensive architecture documentation
- **`caspoon/docs/guides/TESTING.md`** - Testing guidelines and conventions

---

## Code Style & Conventions

### Formatting & Linting

- **Black** (line length: **100**)
  ```bash
  black caspoon/ tests/
  ```
  
- **Ruff** for linting (replaces flake8, isort, pyupgrade)
  ```bash
  ruff check caspoon/ tests/
  ruff check --fix  # Auto-fix issues
  ```

### Type Hints

- Use type hints for function signatures (mypy compatible)
- Gradually typed codebase (not yet fully strict)
- Check types with: `mypy caspoon/`
- External libraries (r2pipe, elftools) have `ignore_missing_imports = true`

### Code Quality Standards

- **DRY**: Avoid repetition, extract reusable functions
- **SOLID**: Single responsibility, open/closed principle
- **Error Handling**: Use specific exceptions, handle external tool failures gracefully
- **Logging**: Use Python's `logging` module, not print statements (except CLI output)
- **Type Safety**: Prefer typed data classes over dictionaries

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ExecutableReport`, `ReconRunner`)
- **Functions/Methods**: `snake_case` (e.g., `run_analysis`, `extract_strings`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_STRING_LENGTH`)
- **Private**: Prefix with `_` (e.g., `_internal_helper`)

---

## Important Project Conventions

### 🚨 Critical Rules

1. **NO `CONTRIBUTING.md` file**
   - All contribution information is in `README.md`
   - Do NOT suggest creating `CONTRIBUTING.md`

2. **Documentation must be in `caspoon/docs/` subdirectories**
   - `caspoon/docs/guides/` - User and developer guides
   - `caspoon/docs/plans/` - Design and implementation plans
   - `caspoon/docs/reference/` - API references and technical documentation
   - `caspoon/docs/changelogs/` - Change log entries
   - **NEVER** create documentation at repository root
   - **NEVER** create files in `caspoon/docs/reviews/` (reserved for architecture agent)

3. **Changelog System**
   - When making significant changes, update `caspoon/docs/changelogs/INDEX.md`
   - Create dated changelog entries: `YYYY-MM-DD-description.md`
   - Keep `INDEX.md` as the single source of truth for change history

4. **No Unnecessary Meta-Documentation**
   - Do not create summary files, review documents, or meta-documentation
   - Focus on actionable, technical content only
   - Leave architectural reviews to the architecture agent

---

## Testing Conventions

### Test Categories (pytest markers)

```python
@pytest.mark.unit           # Fast, isolated unit tests
@pytest.mark.integration    # Tests with external dependencies
@pytest.mark.slow           # Tests taking >1 second
@pytest.mark.golden         # Regression/golden tests
@pytest.mark.requires_r2    # Requires radare2 installed
@pytest.mark.requires_checksec  # Requires checksec installed
@pytest.mark.requires_strings   # Requires strings command
```

### Running Tests

```bash
# Fast tests only (default for CI)
pytest -m "not slow"

# With coverage
pytest --cov=caspoon --cov-report=html

# Specific categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest -m golden                # Golden/regression tests

# Parallel execution
pytest -n auto
```

### Test Coverage Target

- **84% overall** (current baseline)
- **94-100%** on critical modules (core, recon)
- **Coverage exclusions**: UI code, main entry points, `__main__.py`

### Test Structure

```python
# tests/unit/test_module.py
import pytest
from caspoon.module import function_to_test

class TestFunctionName:
    """Test suite for function_to_test."""
    
    def test_normal_case(self):
        """Test normal operation."""
        result = function_to_test("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            function_to_test(None)
    
    @pytest.mark.integration
    def test_with_external_tool(self):
        """Test requiring external tool."""
        # Test with real tool
        pass
```

### Golden Tests

- Used for regression detection
- Compare current output with known-good "golden" output
- Located in `tests/integration/` with `@pytest.mark.golden`
- Update golden files deliberately when behavior changes intentionally

---

## Common Patterns

### Adding a New Recon Module

1. Create new file in `caspoon/recon/`
2. Inherit from base recon class (if exists) or follow existing pattern
3. Implement analysis logic
4. Update `ExecutableReport` model if needed
5. Register module in `ReconRunner`
6. Add unit tests in `tests/unit/recon/`
7. Add integration test in `tests/integration/`

Example structure:
```python
# caspoon/recon/new_module.py
from caspoon.core.models import ExecutableReport

class NewRecon:
    """Description of what this module analyzes."""
    
    def run(self, report: ExecutableReport) -> None:
        """
        Enrich the report with new analysis data.
        
        Args:
            report: The report to enrich (modified in-place)
        """
        # Analysis logic here
        report.new_field = self._analyze(report.path)
    
    def _analyze(self, binary_path: str):
        """Internal analysis logic."""
        pass
```

### Working with External Tools

```python
# Use shutil to check tool availability
import shutil
import subprocess

def tool_available() -> bool:
    """Check if external tool is available."""
    return shutil.which("tool_name") is not None

def run_tool(args: list[str]) -> str:
    """Run external tool safely."""
    if not tool_available():
        raise RuntimeError("Tool not found")
    
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=30,  # Always use timeouts
        check=True
    )
    return result.stdout
```

### Error Handling Pattern

```python
import logging

logger = logging.getLogger(__name__)

def analyze_binary(path: str):
    """Analyze binary with proper error handling."""
    try:
        # Validation
        if not Path(path).exists():
            raise FileNotFoundError(f"Binary not found: {path}")
        
        # Analysis
        result = perform_analysis(path)
        return result
    
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    
    except Exception as e:
        logger.warning(f"Analysis failed for {path}: {e}")
        # Return partial results or raise
        raise
```

---

## Security Considerations

### Safe Binary Analysis

- **Never execute** the analyzed binary
- **Validate paths** before opening files
- **Use timeouts** for all external tool calls
- **Limit resource usage** (memory, file size)
- **Sanitize output** before displaying to users

### Code Review Checklist

- ❌ No `exec()`, `eval()`, or code execution from binary
- ✅ All file operations use `Path` validation
- ✅ External tool calls have timeouts
- ✅ User input is validated and sanitized
- ✅ Error messages don't leak sensitive paths

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone and install with dev dependencies
cd caspoon/
pip install -e ".[dev]"

# Verify setup
caspoon --help
pytest -m "not slow"
```

### Pre-Commit Checks

```bash
# Format code
black caspoon/ tests/

# Lint
ruff check caspoon/ tests/ --fix

# Type check
mypy caspoon/

# Run tests
pytest -m "not slow" --cov=caspoon
```

### Adding Dependencies

1. Add to `pyproject.toml` under appropriate section:
   - `dependencies` - Required runtime dependencies
   - `optional-dependencies` - Optional feature groups
   - `dev` - Development tools only

2. Update lock files:
   ```bash
   pip-compile pyproject.toml
   ```

---

## CLI Entry Point

### CLI Mode (`main.py`)

```python
# Usage: caspoon /path/to/binary
# Output: JSON to stdout
# Errors: stderr

from caspoon.core.runner import ReconRunner

runner = ReconRunner()
report = runner.run(binary_path)
print(report.to_json())
```

---

## Common Tasks

### Adding a CLI Flag

```python
# In main.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--new-flag", action="store_true", help="Description")
args = parser.parse_args()
```

### Modifying Data Model

```python
# In caspoon/core/models.py
from dataclasses import dataclass

@dataclass
class ExecutableReport:
    # Add new field
    new_field: list[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        # Update serialization if needed
        pass
```

### Debugging Tips

- Use `pytest -vv -s` to see print statements in tests
- Use `breakpoint()` for interactive debugging (Python 3.7+)
- Check `htmlcov/index.html` after coverage runs for line-by-line coverage
- GUI debugging: Use PySide6 debug tools when running with `--gui` flag

---

## External Resources

- **pyelftools Docs**: https://github.com/eliben/pyelftools
- **radare2 Docs**: https://book.rada.re/
- **pytest Docs**: https://docs.pytest.org/

---

## Questions & Context

When suggesting code:

1. **Follow the pipeline pattern** - Recon modules enrich `ExecutableReport`
2. **Handle tool failures gracefully** - External tools may be missing
3. **Test thoroughly** - Add unit and integration tests for new features
4. **Document in docstrings** - Follow Google-style docstrings
5. **Security first** - Never execute analyzed binaries, always validate input
6. **Check existing patterns** - Review similar modules before creating new ones

---

*Last Updated: 2025*
*For questions or clarifications, see `caspoon/docs/` or raise an issue.*
