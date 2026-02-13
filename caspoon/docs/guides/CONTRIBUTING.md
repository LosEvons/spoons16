# Contributing to Caspoon

Thank you for your interest in contributing to Caspoon! This guide will help you get started with contributing code, tests, documentation, or other improvements.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Adding New Features](#adding-new-features)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

---

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on what is best for the project and community
- Show empathy towards other community members
- Accept constructive criticism gracefully

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/spoons16.git
cd spoons16/caspoon

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/spoons16.git
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Verify setup
pytest --version
caspoon --help
```

### 3. Install External Tools (Optional)

For full functionality during development:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install radare2 checksec

# macOS
brew install radare2
brew install checksec
```

Tests gracefully skip when optional tools are unavailable.

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create your branch
git checkout -b feature/my-awesome-feature
# Or for bug fixes: git checkout -b fix/issue-123
```

### 2. Make Your Changes

Follow the [Code Standards](#code-standards) outlined below.

### 3. Write Tests

**All code changes must include tests.** See [Testing Requirements](#testing-requirements).

```bash
# Run tests as you develop
pytest tests/unit/your_module/test_your_feature.py -v

# Run the full test suite
pytest -m "not slow"
```

### 4. Check Coverage

```bash
# Generate coverage report
pytest --cov=caspoon --cov-report=term-missing

# Aim for 80%+ coverage on new code
# Critical modules (core, recon) should maintain 90%+
```

### 5. Run All Tests Before Committing

```bash
# Fast test suite
pytest -m "not slow"

# Full test suite (if you have time)
pytest
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: [brief description]

- Detailed point 1
- Detailed point 2
- Fixes #123 (if applicable)"
```

**Good commit messages:**
- ✅ `Add string deduplication in StringsRecon module`
- ✅ `Fix timeout handling in protections detection`
- ✅ `Update TESTING.md with property test examples`

**Avoid:**
- ❌ `fix bug`
- ❌ `update stuff`
- ❌ `wip`

---

## Code Standards

### Python Style

- **PEP 8 compliance**: Follow Python style guidelines
- **Type hints**: Use type annotations for function signatures
- **Docstrings**: Document all public classes and functions

```python
def analyze_binary(path: str, timeout: int = 30) -> ExecutableReport:
    """
    Analyze a binary file and return a report.
    
    Args:
        path: Path to the binary file
        timeout: Analysis timeout in seconds (default: 30)
    
    Returns:
        ExecutableReport containing analysis results
    
    Raises:
        FileNotFoundError: If binary does not exist
        TimeoutError: If analysis exceeds timeout
    """
    # Implementation...
```

### Code Organization

- **Keep modules focused**: One clear responsibility per module
- **Use dataclasses** for data models (see `core/models.py`)
- **Avoid circular imports**: Structure dependencies carefully
- **Error handling**: Always handle errors gracefully (see patterns below)

### Error Handling Patterns

```python
# ✅ Good: Graceful degradation
def get_protections(path: str) -> ProtectionInfo:
    try:
        result = subprocess.run(['checksec', path], ...)
        return parse_checksec(result.stdout)
    except FileNotFoundError:
        # Tool not available, return defaults
        return ProtectionInfo()
    except subprocess.TimeoutExpired:
        # Handle timeout
        return ProtectionInfo(error="timeout")

# ❌ Avoid: Crashing on errors
def get_protections(path: str) -> ProtectionInfo:
    result = subprocess.run(['checksec', path], ...)  # Crashes if not found
    return parse_checksec(result.stdout)
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `FileInfoRecon`, `ExecutableReport`)
- **Functions/Methods**: `snake_case` (e.g., `analyze_binary`, `get_strings`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_STRING_LENGTH`, `DEFAULT_TIMEOUT`)
- **Private members**: Leading underscore (e.g., `_internal_helper`)

---

## Testing Requirements

### Test Coverage Requirements

All contributions must include tests:

- **New features**: 80%+ coverage
- **Bug fixes**: Add test that reproduces the bug, then fix it
- **Recon modules**: 90%+ coverage (critical path)
- **Core modules**: 90%+ coverage (critical path)

### Types of Tests to Write

#### 1. Unit Tests

Test individual functions/classes in isolation:

```python
# tests/unit/recon/test_my_feature.py
import pytest
from unittest.mock import Mock, patch
from caspoon.recon.my_feature import MyFeatureRecon
from caspoon.core.models import ExecutableReport


class TestMyFeatureRecon:
    """Unit tests for MyFeatureRecon."""
    
    @pytest.fixture
    def recon(self):
        """Create MyFeatureRecon instance."""
        return MyFeatureRecon()
    
    def test_basic_analysis(self, recon):
        """Test basic feature detection."""
        report = ExecutableReport(path="/test/binary")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="expected")
            
            result = recon.run("/test/binary", report)
            
            assert result.my_field == "expected"
```

#### 2. Integration Tests

Test full pipeline or multiple components:

```python
# tests/integration/test_my_pipeline.py
@pytest.mark.integration
def test_my_feature_pipeline(self, sample_binary):
    """Test feature in full analysis pipeline."""
    runner = ReconRunner()
    report = runner.run(str(sample_binary))
    
    # Verify your feature's contribution
    assert report.my_field is not None
```

#### 3. Error Handling Tests

Test that errors are handled gracefully:

```python
def test_handles_missing_tool(self, recon):
    """Test behavior when external tool is missing."""
    with patch('subprocess.run', side_effect=FileNotFoundError):
        report = recon.run("/test/binary", ExecutableReport(path="/test/binary"))
        
        # Should not crash
        assert report is not None
        # Should indicate tool was missing
        assert "error" in report.raw_backend_data.get("my_feature", {})
```

#### 4. Edge Case Tests

Test boundary conditions and unusual inputs:

```python
@pytest.mark.parametrize("path,expected_error", [
    ("", "empty path"),
    ("/nonexistent", "not found"),
    (".", "is directory"),
])
def test_edge_cases(self, recon, path, expected_error):
    """Test edge cases."""
    report = recon.run(path, ExecutableReport(path=path))
    # Verify graceful handling
```

### Test Markers

Mark your tests appropriately:

```python
@pytest.mark.unit              # Unit test
@pytest.mark.integration       # Integration test
@pytest.mark.slow              # Takes >1 second
@pytest.mark.requires_r2       # Requires radare2
@pytest.mark.requires_checksec # Requires checksec
```

### Running Tests

```bash
# Run your new tests
pytest tests/unit/recon/test_my_feature.py -v

# Run all unit tests
pytest tests/unit/

# Check coverage
pytest --cov=caspoon.recon.my_feature --cov-report=term-missing

# Fast feedback loop (excludes slow tests)
pytest -m "not slow" -x  # -x stops on first failure
```

See **[TESTING.md](TESTING.md)** for comprehensive testing documentation.

---

## Adding New Features

### Adding a New Recon Module

Recon modules are the core analysis components. Here's how to add one:

#### 1. Create the Module

```python
# caspoon/recon/my_analysis.py
"""
My analysis module - detects [what it detects].
"""
from ..core.models import ExecutableReport
import subprocess


class MyAnalysisRecon:
    """Recon module for [description]."""
    
    name = "my_analysis"
    
    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """
        Analyze binary and enrich report.
        
        Args:
            path: Path to binary
            report: Existing report to enrich
            
        Returns:
            Enriched report
        """
        try:
            # Run your analysis
            result = self._analyze(path)
            
            # Update report
            report.my_new_field = result
            
        except Exception as e:
            # Handle errors gracefully
            report.raw_backend_data["my_analysis_error"] = str(e)
        
        return report
    
    def _analyze(self, path: str) -> str:
        """Internal analysis logic."""
        # Your implementation
        pass
```

#### 2. Register in Runner

```python
# caspoon/core/runner.py
from ..recon.my_analysis import MyAnalysisRecon

class ReconRunner:
    def __init__(self):
        self.steps = [
            FileInfoRecon(),
            ProtectionsRecon(),
            StringsRecon(),
            ImportExportRecon(),
            MyAnalysisRecon(),  # Add here
            R2BackendRecon(),
        ]
```

#### 3. Update Data Model (if needed)

```python
# caspoon/core/models.py
@dataclass
class ExecutableReport:
    # ... existing fields ...
    my_new_field: Optional[str] = None  # Add if needed
```

#### 4. Write Tests

```python
# tests/unit/recon/test_my_analysis.py
"""Unit tests for MyAnalysisRecon."""
import pytest
from caspoon.recon.my_analysis import MyAnalysisRecon
from caspoon.core.models import ExecutableReport


class TestMyAnalysisRecon:
    """Test MyAnalysisRecon class."""
    
    @pytest.fixture
    def recon(self):
        return MyAnalysisRecon()
    
    def test_basic_analysis(self, recon, sample_binary):
        """Test basic analysis."""
        report = ExecutableReport(path=str(sample_binary))
        result = recon.run(str(sample_binary), report)
        
        assert result.my_new_field is not None
    
    def test_error_handling(self, recon):
        """Test error handling for missing file."""
        report = ExecutableReport(path="/nonexistent")
        result = recon.run("/nonexistent", report)
        
        # Should not crash
        assert result is not None
```

#### 5. Document the Module

Update `docs/OVERVIEW.md` with your new module's capabilities.

### Adding a UI View

To add a new view to the TUI:

```python
# caspoon/ui/views/my_view.py
from textual.widgets import Static
from textual.containers import ScrollableContainer


class MyView(Static):
    """View for displaying my analysis."""
    
    def update_data(self, report):
        """Update view with report data."""
        content = self._format_data(report)
        self.update(content)
    
    def _format_data(self, report):
        """Format report data for display."""
        # Return Rich-formatted text
        pass
```

Register in `ui/app.py`:

```python
with TabPane("My View"):
    with ScrollableContainer():
        yield MyView(id="my_view")
```

---

## Documentation

### When to Update Documentation

Update documentation when you:

- Add a new feature or module
- Change existing behavior
- Add or change CLI flags
- Modify data models
- Add configuration options

### Documentation Files

- **README.md**: User-facing overview and quick start
- **CONTRIBUTING.md** (this file): Contributor guidelines
- **TESTING.md**: Testing infrastructure and guidelines
- **docs/OVERVIEW.md**: Detailed architecture and design
- **Docstrings**: In-code documentation for all public APIs

### Documentation Style

- **Be concise but complete**: Explain what, why, and how
- **Use examples**: Show usage patterns with code snippets
- **Keep it current**: Update docs in the same PR as code changes
- **Format consistently**: Use markdown formatting consistently

---

## Submitting Changes

### Before You Submit

- [ ] All tests pass: `pytest -m "not slow"`
- [ ] Coverage is adequate: `pytest --cov=caspoon`
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No unnecessary files committed (check `.gitignore`)

### Pull Request Process

1. **Push your branch**:
   ```bash
   git push origin feature/my-awesome-feature
   ```

2. **Create Pull Request** on GitHub:
   - Clear title: "Add [feature]" or "Fix [issue]"
   - Description explaining:
     - What changed
     - Why it changed
     - How it was tested
     - Related issues (use "Fixes #123" to auto-close issues)

3. **Respond to feedback**:
   - Address reviewer comments
   - Push updates to your branch
   - Re-request review when ready

4. **Merge**:
   - Maintainers will merge when approved
   - Delete your branch after merge

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Coverage
- Current coverage: X%
- Coverage change: +Y%

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] Commit messages are clear

## Related Issues
Fixes #123
```

---

## Questions or Issues?

- 📖 Check [TESTING.md](TESTING.md) for testing questions
- 📖 Check [docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md) for architecture questions
- 🐛 Open an issue for bugs or feature requests
- 💬 Start a discussion for design questions

---

## Recognition

Contributors are recognized in:
- GitHub contributor graphs
- Release notes
- Project acknowledgments

Thank you for contributing to Caspoon! 🎉
