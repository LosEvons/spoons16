# Contributing to Caspoon

Thank you for your interest in contributing to Caspoon! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Pull Request Process](#pull-request-process)
- [Coding Guidelines](#coding-guidelines)
- [Security Considerations](#security-considerations)
- [Getting Help](#getting-help)

---

## Development Setup

### Prerequisites

- **Python 3.10+** (3.10, 3.11, or 3.12 recommended)
- **Git**
- **System tools**: binutils, file, gcc, make
- **Optional**: radare2 (for advanced analysis features)

### Initial Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/spoons16.git
   cd spoons16/caspoon
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Build test fixtures**

   ```bash
   cd tests/fixtures/binaries/src
   make
   cd ../../../..
   ```

5. **Verify installation**

   ```bash
   # Run tests to ensure everything works
   pytest -v
   
   # Check that caspoon command is available
   caspoon --help
   ```

### System Dependencies

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y binutils file gcc make radare2
```

#### macOS

```bash
brew install binutils radare2
```

#### Windows

Use WSL2 (Windows Subsystem for Linux) for the best experience.

---

## Making Changes

### Workflow

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

2. **Make your changes**

   - Write clear, focused commits
   - Add/update tests for your changes
   - Update documentation as needed
   - Follow existing code patterns and conventions

3. **Keep your branch up to date**

   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed explanation of what changed and why.

Fixes #issue-number
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

**Example**:
```
feat(recon): add ARM64 architecture detection

Extend FileInfoRecon to detect ARM64 binaries using
pyelftools EM_AARCH64 constant.

Fixes #123
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only

# Run tests with coverage
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html  # View coverage report

# Run fast tests only (skip slow tests)
pytest -m "not slow"

# Run tests in parallel (faster)
pytest -n auto
```

### Writing Tests

1. **Place tests in appropriate directory**
   - Unit tests: `tests/unit/`
   - Integration tests: `tests/integration/`

2. **Use descriptive names**

   ```python
   def test_file_info_recon_detects_x86_64_architecture():
       """Test that FileInfoRecon correctly identifies x86-64 binaries."""
       # Test implementation
   ```

3. **Test edge cases**

   - Empty inputs
   - Invalid inputs
   - Boundary conditions
   - Error handling

4. **Use fixtures for test data**

   ```python
   @pytest.fixture
   def sample_binary(tmp_path):
       """Provide a sample test binary."""
       return tmp_path / "test_binary"
   ```

### Test Requirements

- **Coverage**: Maintain at least 50% overall coverage (aim for 75%+)
- **All tests must pass**: No broken tests in PRs
- **No regressions**: Existing tests must continue to pass
- **Golden tests**: Update golden outputs if behavior changes intentionally

---

## Code Quality

### Style Guidelines

- **Follow PEP 8** with maximum line length of 100 characters
- **Use type hints** for function signatures
- **Write docstrings** for all public functions, classes, and modules
- **Use Google-style docstrings**

Example:

```python
def analyze_binary(path: str, enable_disasm: bool = False) -> ExecutableReport:
    """Analyze a binary file and return a comprehensive report.
    
    Args:
        path: Path to the binary file to analyze.
        enable_disasm: Whether to include disassembly in the report.
    
    Returns:
        ExecutableReport containing all analysis results.
    
    Raises:
        FileNotFoundError: If the binary file does not exist.
        ValueError: If the file is not a valid executable.
    """
```

### Code Quality Tools (Coming in Subtask 5)

Once installed, run before submitting PRs:

```bash
# Format code
black caspoon/ tests/

# Check linting
ruff check caspoon/

# Type checking
mypy caspoon/ --ignore-missing-imports
```

### Best Practices

- **Keep functions small and focused**: One responsibility per function
- **Avoid global state**: Use dependency injection
- **Handle errors gracefully**: Provide helpful error messages
- **Log appropriately**: Use Python logging module
- **Document complex logic**: Add comments for non-obvious code
- **Use meaningful names**: Variables and functions should be self-documenting

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**

   ```bash
   pytest
   ```

2. **Check code coverage**

   ```bash
   pytest --cov=caspoon
   # Coverage should not decrease
   ```

3. **Update documentation**

   - Add/update docstrings
   - Update README.md if adding user-facing features
   - Update relevant docs/ files

4. **Run code quality checks** (when available)

   ```bash
   black caspoon/ tests/
   ruff check caspoon/
   mypy caspoon/
   ```

### Submitting PR

1. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**

   - Use a descriptive title
   - Fill out the PR template
   - Reference related issues
   - Add screenshots for UI changes

3. **Wait for CI to pass**

   - GitHub Actions will run tests automatically
   - Fix any failures before requesting review

4. **Respond to feedback**

   - Address reviewer comments
   - Push updates to the same branch
   - CI will re-run automatically

### PR Checklist

- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] CI passes

---

## Coding Guidelines

### Python Style

- **Imports**: Use absolute imports, group by standard library → third-party → local
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private: `_leading_underscore`
- **Line length**: 100 characters maximum
- **Strings**: Use double quotes `"` for user-facing strings, single `'` for internal

### Architecture Principles

- **Modularity**: Keep components loosely coupled
- **Single Responsibility**: Each class/function does one thing well
- **Open/Closed**: Open for extension, closed for modification
- **Dependency Injection**: Pass dependencies explicitly
- **Fail Fast**: Validate inputs early, provide clear errors

### Security Best Practices

⚠️ **Important**: Caspoon analyzes potentially malicious binaries.

- **Never execute analyzed binaries**
- **Validate all file paths**: Check for path traversal
- **Use subprocess safely**: Avoid shell injection
- **Timeout external tools**: Prevent infinite hangs
- **Limit resource usage**: Memory and file size limits
- **Sanitize outputs**: Don't include raw binary data in logs/reports
- **Be defensive**: Assume inputs are malicious

Example:

```python
import subprocess
from pathlib import Path

def safe_analyze(path: str, timeout: int = 30) -> dict:
    """Safely analyze a binary with timeouts and validation."""
    # Validate path
    binary_path = Path(path).resolve()
    if not binary_path.exists():
        raise FileNotFoundError(f"Binary not found: {path}")
    
    # Use timeout to prevent hangs
    try:
        result = subprocess.run(
            ["file", str(binary_path)],
            capture_output=True,
            timeout=timeout,
            check=True
        )
        return {"output": result.stdout.decode()}
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Analysis timed out after {timeout}s")
```

---

## Project Structure

```
spoons16/
├── caspoon/                  # Main package
│   ├── core/                 # Core analysis engine
│   │   ├── runner.py         # Main orchestration
│   │   └── report.py         # Report data models
│   ├── recon/                # Analysis modules
│   │   ├── file_info.py      # File type detection
│   │   ├── protections.py    # Security features
│   │   └── ...
│   ├── backends/             # External tool integrations
│   ├── ui/                   # Terminal UI
│   ├── tests/                # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   └── docs/                 # Documentation
├── .github/
│   └── workflows/            # CI/CD pipelines
├── README.md
└── CONTRIBUTING.md           # This file
```

---

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """Short one-line summary.
    
    Longer description if needed. Explain what the function does,
    when to use it, and any important details.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2. Defaults to 0.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When arg2 is negative.
        RuntimeError: If something goes wrong.
    
    Example:
        >>> function("test", 5)
        True
    """
```

### Updating Documentation

When making changes:

- Update docstrings in the code
- Update README.md for user-facing changes
- Update relevant files in `docs/` for architectural changes
- Add examples for new features

---

## Getting Help

### Resources

- **Documentation**: See [docs/](caspoon/docs/) directory
- **Architecture**: [docs/reference/OVERVIEW.md](caspoon/docs/reference/OVERVIEW.md)
- **Testing Guide**: [docs/guides/TESTING.md](caspoon/docs/guides/TESTING.md)

### Support Channels

- **Issues**: [GitHub Issues](https://github.com/LosEvons/spoons16/issues) - Bug reports and feature requests
- **Discussions**: [GitHub Discussions](https://github.com/LosEvons/spoons16/discussions) - Questions and discussions

### Reporting Issues

When reporting bugs, include:

1. **Description**: What went wrong?
2. **Steps to reproduce**: How can we reproduce it?
3. **Expected behavior**: What should happen?
4. **Actual behavior**: What actually happened?
5. **Environment**: Python version, OS, relevant tool versions
6. **Logs/output**: Any error messages or stack traces

**Security Issues**: Report security vulnerabilities privately via GitHub Security Advisories.

---

## License

By contributing to Caspoon, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE) file).

---

## Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect
- **Be constructive**: Provide helpful feedback
- **Be collaborative**: Work together toward common goals
- **Be patient**: Remember everyone is learning

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Spam or self-promotion
- Publishing others' private information

---

## Recognition

Contributors are recognized in:

- Git commit history
- GitHub contributors page
- Release notes (for significant contributions)

---

Thank you for contributing to Caspoon! 🔍

