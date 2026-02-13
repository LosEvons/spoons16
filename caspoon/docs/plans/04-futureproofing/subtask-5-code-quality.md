# Subtask 5: Code Quality Tools Setup

## Objective
Configure and enable code quality tools (ruff, black, mypy) to maintain code standards and catch issues early.

## Priority
🟡 **HIGH - Should complete early**

## Scope
- Configure ruff (linter)
- Configure black (formatter)
- Configure mypy (type checker)
- Add configuration files
- Document usage

## Prerequisites
- Subtask 3 completed (dev dependencies installed)

## Implementation Steps

### Step 1: Configure Black (15 minutes)

**File**: `caspoon/pyproject.toml` (add section)

```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.pytest_cache
  | \\.venv
  | build
  | dist
)/
'''
```

**Commands**:
```bash
# Format code
black caspoon/ tests/

# Check formatting
black --check caspoon/ tests/

# Show diff without modifying
black --diff caspoon/
```

### Step 2: Configure Ruff (20 minutes)

**File**: `caspoon/pyproject.toml` (add section)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

# Enable select rule sets
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

# Ignore specific rules
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex (can enable later)
]

# Exclude directories
exclude = [
    ".git",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    ".venv",
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/**/*.py" = ["F401", "F811"]  # Allow test fixtures

[tool.ruff.isort]
known-first-party = ["caspoon"]
```

**Commands**:
```bash
# Check code
ruff check caspoon/ tests/

# Auto-fix issues
ruff check --fix caspoon/ tests/

# Show available rules
ruff linter
```

### Step 3: Configure Mypy (20 minutes)

**File**: `caspoon/pyproject.toml` (add section)

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Enable gradually
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true

# Module-specific overrides
[[tool.mypy.overrides]]
module = [
    "r2pipe.*",
    "elftools.*",
    "textual.*",
]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Commands**:
```bash
# Check types
mypy caspoon/

# Check specific file
mypy caspoon/core/models.py

# Generate coverage report
mypy --html-report mypy-report caspoon/
```

### Step 4: Create Pre-commit Hooks Config (Optional, 15 minutes)

**File**: `.pre-commit-config.yaml` (in repo root)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements
  
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.10
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

**Setup**:
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Step 5: Create Code Quality Script (15 minutes)

**File**: `caspoon/scripts/check_quality.sh`

```bash
#!/bin/bash
# Code quality check script

set -e

echo "=== Running Code Quality Checks ==="
echo

echo "1. Running ruff..."
ruff check caspoon/ tests/
echo "✓ Ruff passed"
echo

echo "2. Running black..."
black --check caspoon/ tests/
echo "✓ Black passed"
echo

echo "3. Running mypy..."
mypy caspoon/ --ignore-missing-imports
echo "✓ Mypy passed"
echo

echo "=== All checks passed! ==="
```

Make executable:
```bash
chmod +x caspoon/scripts/check_quality.sh
```

### Step 6: Update Documentation (20 minutes)

**File**: `caspoon/docs/CODE_QUALITY.md`

```markdown
# Code Quality Guidelines

## Tools

### Black (Code Formatter)
- **Purpose**: Consistent code formatting
- **Configuration**: pyproject.toml [tool.black]
- **Line length**: 100 characters
- **Usage**: `black caspoon/ tests/`

### Ruff (Linter)
- **Purpose**: Fast Python linter
- **Configuration**: pyproject.toml [tool.ruff]
- **Rules**: pycodestyle, pyflakes, isort, flake8-bugbear
- **Usage**: `ruff check caspoon/ tests/`

### Mypy (Type Checker)
- **Purpose**: Static type checking
- **Configuration**: pyproject.toml [tool.mypy]
- **Mode**: Gradual typing (not strict initially)
- **Usage**: `mypy caspoon/`

## Running Checks

### Individual Tools
```bash
# Format code
black caspoon/ tests/

# Check formatting (no changes)
black --check caspoon/ tests/

# Lint code
ruff check caspoon/ tests/

# Fix auto-fixable issues
ruff check --fix caspoon/ tests/

# Type check
mypy caspoon/
```

### All Checks
```bash
# Run all quality checks
./scripts/check_quality.sh

# Or use pre-commit
pre-commit run --all-files
```

### In CI
All checks run automatically in CI:
- On every push
- On every pull request
- Before merge

## Code Style

### Formatting
- Use black for all formatting
- 100 character line length
- Double quotes for strings

### Imports
- Standard library first
- Third-party second
- Local imports last
- Alphabetically sorted within groups

### Type Hints
- Add type hints to new functions
- Use `from typing import` for types
- Return types are preferred
- Parameter types are encouraged

### Naming
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
- Descriptive names over short names

## Ignoring Checks

### Black
Not applicable (don't fight the formatter)

### Ruff
```python
# Ignore specific line
result = some_function()  # noqa: E501

# Ignore specific rule for file
# At top of file:
# ruff: noqa: F401
```

### Mypy
```python
# Ignore specific line
x = some_untyped_library()  # type: ignore

# Ignore missing imports
# In pyproject.toml mypy.overrides
```

## Pre-commit Hooks

Optional but recommended:

```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks run:
- Before every commit
- Format with black
- Lint with ruff
- Check for common issues

## CI Integration

See `.github/workflows/lint.yml`:
- Runs on every push/PR
- All tools must pass
- Blocks merge if failing

## Gradual Improvement

### Current State
- Black: Enforced
- Ruff: Enforced
- Mypy: Optional (warnings only)

### Future Goal
- Mypy: Enforced with strict mode
- 100% type coverage
- Additional ruff rule sets

## Tips

### Auto-fix on Save
Configure your editor:
- VSCode: Use extensions
- PyCharm: Use built-in tools
- Vim: Use ALE or similar

### Before Committing
```bash
# Quick check
black caspoon/ tests/
ruff check --fix caspoon/ tests/

# Full check
./scripts/check_quality.sh
```
```

## Testing Strategy

- Run each tool individually
- Verify configurations work
- Test on existing code
- Verify CI integration

## Success Criteria

- [ ] Black configured in pyproject.toml
- [ ] Ruff configured in pyproject.toml
- [ ] Mypy configured in pyproject.toml
- [ ] All tools run without errors
- [ ] Quality check script exists
- [ ] CODE_QUALITY.md documentation exists
- [ ] Pre-commit hooks configured (optional)
- [ ] CI runs quality checks

## Estimated Time
**1.5 hours total**

## Deliverables
- Configured code quality tools
- Quality check script
- Documentation
- Optional: Pre-commit hooks
