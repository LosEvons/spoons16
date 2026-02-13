# Code Quality Tools

## Overview

This project uses three code quality tools to maintain consistent, clean, and correct Python code:

- **Black**: Automatic code formatting
- **Ruff**: Fast Python linting (replaces flake8, isort, etc.)
- **Mypy**: Optional static type checking

## Quick Commands

```bash
# Format code
black caspoon/

# Check formatting (no changes)
black --check caspoon/

# Lint and auto-fix
ruff check --fix caspoon/

# Type check
mypy caspoon/ --ignore-missing-imports

# Run all checks
./scripts/check_quality.sh
```

## Configuration

All tools are configured in `caspoon/pyproject.toml`:

- **Line length**: 100 characters (Black and Ruff)
- **Target Python**: 3.10+ (all tools)
- **Ruff rules**: E, W, F, I, B, C4, UP (pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade)

## Tool Details

### Black

Opinionated code formatter. No configuration needed beyond line length.

**What it fixes**: indentation, spacing, quotes, line breaks

### Ruff

Fast all-in-one linter that replaces multiple tools.

**What it checks**:
- Pycodestyle errors (E, W)
- Pyflakes (F) - unused imports, undefined names
- Import sorting (I) - isort replacement
- Bugbear (B) - common bugs and design problems
- Comprehensions (C4) - simplify list/dict comprehensions
- Pyupgrade (UP) - modernize Python syntax

**Per-file ignores**:
- `__init__.py`: Allows unused imports (F401)
- `tests/**/*.py`: Allows test fixtures (F401, F811, F841)

### Mypy

Type checker. Currently in gradual mode (not strict).

**What it checks**: type consistency, attribute access, return types

**Ignored modules**: r2pipe, elftools, textual (no type stubs)

## Running in CI

All checks run automatically in CI via `.github/workflows/lint.yml`.

## Suppressing Warnings

```python
# Ruff: ignore specific line
result = long_function_call()  # noqa: E501

# Mypy: ignore type on specific line
x = untyped_library()  # type: ignore
```

## Tips

1. **Run checks before committing**: `./scripts/check_quality.sh`
2. **Auto-format on save**: Configure your editor to run Black
3. **Fix most issues automatically**: `ruff check --fix caspoon/`
4. **Type hints are optional but encouraged** for new code

## Gradual Adoption

- **Black**: Fully enforced (all code formatted)
- **Ruff**: Fully enforced (all checks must pass)
- **Mypy**: Gradual (warnings only, not strict mode)

Future improvements may enable stricter mypy checking and additional ruff rules.
