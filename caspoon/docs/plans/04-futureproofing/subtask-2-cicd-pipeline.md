# Subtask 2: CI/CD Pipeline Implementation

**Status**: ✅ COMPLETED (2026-02-13)

## Objective
Set up automated CI/CD pipeline using GitHub Actions to run tests, linting, and type checking on every push and pull request. This ensures code quality is maintained automatically.

## Priority
🔴 **CRITICAL - Must complete after Subtask 1**

## Scope
- Create GitHub Actions workflows
- Configure test automation
- Set up code coverage reporting
- Add status badges to README
- Configure branch protection rules (optional)

## Prerequisites
- **Subtask 1 completed**: Testing infrastructure must be in place
- Repository on GitHub
- Tests passing locally
- GitHub Actions enabled for repository

## Implementation Steps

### Step 1: Create GitHub Actions Directory (5 minutes)

```bash
cd /home/runner/work/spoons16/spoons16
mkdir -p .github/workflows
```

### Step 2: Create Main Test Workflow (30 minutes)

**File**: `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop, copilot/** ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Test Python ${{ matrix.python-version }} on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y binutils file
        # Try to install radare2, but don't fail if unavailable
        sudo apt-get install -y radare2 || echo "radare2 not available"
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[dev]"
    
    - name: Build test fixtures
      run: |
        cd caspoon/tests/fixtures/binaries/src
        make || echo "Failed to build some test binaries"
        cd ../../../../..
    
    - name: Run unit tests
      run: |
        cd caspoon
        pytest tests/unit -v --cov=caspoon --cov-report=xml --cov-report=term
    
    - name: Run integration tests
      run: |
        cd caspoon
        pytest tests/integration -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      if: matrix.python-version == '3.10' && matrix.os == 'ubuntu-latest'
      with:
        file: ./caspoon/coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false
      env:
        CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
    
    - name: Check coverage threshold
      run: |
        cd caspoon
        coverage report --fail-under=50
```

### Step 3: Create Linting Workflow (20 minutes)

**File**: `.github/workflows/lint.yml`

```yaml
name: Code Quality

on:
  push:
    branches: [ main, develop, copilot/** ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint and Format Check
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[dev]"
    
    - name: Run ruff
      run: |
        cd caspoon
        ruff check caspoon/ --output-format=github
    
    - name: Run black
      run: |
        cd caspoon
        black --check caspoon/ tests/
    
    - name: Run mypy
      run: |
        cd caspoon
        mypy caspoon/ --ignore-missing-imports
      continue-on-error: true  # Don't fail CI on type errors initially
```

### Step 4: Create PR Comment Workflow (Optional, 20 minutes)

**File**: `.github/workflows/pr-comment.yml`

```yaml
name: PR Coverage Comment

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  coverage-comment:
    name: Comment Coverage Report
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[dev]"
    
    - name: Run tests with coverage
      run: |
        cd caspoon
        pytest --cov=caspoon --cov-report=term --cov-report=json
    
    - name: Coverage comment
      uses: py-cov-action/python-coverage-comment-action@v3
      with:
        GITHUB_TOKEN: ${{ github.token }}
        MINIMUM_GREEN: 75
        MINIMUM_ORANGE: 50
```

### Step 5: Add Dependabot Configuration (Optional, 15 minutes)

**File**: `.github/dependabot.yml`

```yaml
version: 2
updates:
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
  
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/caspoon"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"
```

### Step 6: Update README with Badges (20 minutes)

**File**: `caspoon/README.md` (create if doesn't exist)

Add to top of README:

```markdown
# Caspoon - Reverse Engineering Toolkit

[![Test Suite](https://github.com/LosEvons/spoons16/actions/workflows/test.yml/badge.svg)](https://github.com/LosEvons/spoons16/actions/workflows/test.yml)
[![Code Quality](https://github.com/LosEvons/spoons16/actions/workflows/lint.yml/badge.svg)](https://github.com/LosEvons/spoons16/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/LosEvons/spoons16/branch/main/graph/badge.svg)](https://codecov.io/gh/LosEvons/spoons16)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A modular toolkit for analyzing and reverse engineering executable files.

## Features

- 🔍 Binary analysis and reconnaissance
- 🛡️ Security feature detection
- 🔤 String extraction
- 📊 Import/export analysis
- 🖥️ Interactive TUI

## Quick Start

```bash
# Install
cd caspoon
pip install -e .

# Run CLI
python -m caspoon /path/to/binary

# Run TUI
python -m caspoon --ui
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=caspoon

# Run linting
ruff check caspoon/
black --check caspoon/
mypy caspoon/
```

## Documentation

See [docs/](docs/) for detailed documentation:
- [Overview](docs/OVERVIEW.md) - Architecture and design
- [Implementation Plans](docs/plans/) - Feature development roadmaps
- [Future-Proofing Report](docs/FUTURE_PROOFING_REPORT.md) - Infrastructure analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

See [LICENSE](../LICENSE) file for details.
```

### Step 7: Configure Codecov (Optional, 10 minutes)

**File**: `codecov.yml` (in repository root)

```yaml
coverage:
  status:
    project:
      default:
        target: 50%
        threshold: 5%
    patch:
      default:
        target: 50%

ignore:
  - "caspoon/tests/"
  - "caspoon/**/__main__.py"
  - "setup.py"

comment:
  layout: "header, diff, files"
  behavior: default
  require_changes: false
```

**Note**: To enable Codecov, you need to:
1. Sign up at https://codecov.io
2. Enable codecov for the repository
3. Add `CODECOV_TOKEN` as repository secret

### Step 8: Create CONTRIBUTING.md (30 minutes)

**File**: `CONTRIBUTING.md` (in repository root)

```markdown
# Contributing to Caspoon

Thank you for your interest in contributing to Caspoon!

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/spoons16.git
   cd spoons16/caspoon
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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

## Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following existing patterns
   - Add/update tests for your changes
   - Update documentation as needed

3. **Run tests**
   ```bash
   pytest
   ```

4. **Check code quality**
   ```bash
   ruff check caspoon/
   black caspoon/ tests/
   mypy caspoon/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

## Pull Request Process

1. **Ensure all tests pass**
   - All existing tests must pass
   - Coverage should not decrease
   - New code should have tests

2. **Update documentation**
   - Update README if adding features
   - Update docstrings
   - Update relevant docs/ files

3. **Submit PR**
   - Push to your fork
   - Open a PR against main branch
   - Fill in the PR template
   - Wait for CI to pass

4. **Code review**
   - Address reviewer feedback
   - Push updates to same branch
   - CI will re-run automatically

## Coding Guidelines

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use black for formatting
- Use ruff for linting

### Testing
- Write tests for all new features
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests fast and focused

### Documentation
- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Update README for user-facing changes
- Add examples where helpful

## Testing Requirements

- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions
- **Coverage**: Maintain 75%+ coverage
- **Performance**: Tests should run in <5 seconds

## Need Help?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
```

### Step 9: Verify CI/CD Setup (30 minutes)

**Local verification**:
```bash
# Ensure tests pass locally
cd /home/runner/work/spoons16/spoons16/caspoon
pytest -v

# Ensure linting passes
ruff check caspoon/
black --check caspoon/ tests/
```

**Commit and push**:
```bash
cd /home/runner/work/spoons16/spoons16
git add .github/ codecov.yml CONTRIBUTING.md caspoon/README.md
git commit -m "Add CI/CD workflows and contributing guidelines"
git push
```

**Monitor GitHub Actions**:
1. Go to repository on GitHub
2. Click "Actions" tab
3. Watch workflows run
4. Verify all checks pass

### Step 10: Optional - Branch Protection Rules

Go to GitHub repository settings:
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select status checks: `Test Suite`, `Lint and Format Check`
   - ✅ Require conversation resolution before merging
4. Save changes

## Testing Strategy

### Self-Testing
1. **Workflows exist**: Check `.github/workflows/` has files
2. **Workflows are valid**: GitHub validates YAML syntax
3. **CI runs**: Push triggers workflows
4. **Tests run in CI**: Verify output in Actions tab
5. **Badges work**: Check README displays badges

### Manual Verification
- [ ] Push code triggers CI
- [ ] PRs trigger CI
- [ ] Test workflow runs and passes
- [ ] Lint workflow runs and passes
- [ ] Coverage is reported
- [ ] Badges display in README
- [ ] Failed tests cause CI to fail

## Success Criteria

- [ ] GitHub Actions workflows exist in `.github/workflows/`
- [ ] Test workflow (`test.yml`) runs on push/PR
- [ ] Lint workflow (`lint.yml`) runs on push/PR
- [ ] CI runs on multiple Python versions (3.10, 3.11, 3.12)
- [ ] Tests run automatically in CI
- [ ] Linting runs automatically in CI
- [ ] Type checking runs automatically in CI
- [ ] Coverage reports are generated
- [ ] Coverage is uploaded to Codecov (optional)
- [ ] README has status badges
- [ ] CONTRIBUTING.md exists with clear guidelines
- [ ] CI passes on main/develop branches
- [ ] Failed tests cause CI to fail
- [ ] Branch protection rules configured (optional)

## Estimated Time
**2-3 hours total**
- GitHub Actions setup: 1 hour
- README/badges: 30 min
- CONTRIBUTING.md: 30 min
- Codecov setup: 30 min (optional)
- Verification: 30 min

## Common Issues & Solutions

### Issue 1: CI fails due to missing dependencies
**Solution**: Ensure all dependencies are in pyproject.toml and installed in workflow

### Issue 2: radare2 not available in CI
**Solution**: Install with apt-get, or mark tests as skipped if not available

### Issue 3: Tests timeout in CI
**Solution**: Add timeout to pytest commands, optimize slow tests

### Issue 4: Coverage upload fails
**Solution**: Codecov token needed, set as repository secret or skip upload

### Issue 5: Workflows don't trigger
**Solution**: Check branch names in `on:` section match your branches

## Workflow Triggers

### Test Workflow Triggers
- Push to main, develop, or copilot/** branches
- Pull requests to main or develop
- Manual trigger (workflow_dispatch)

### When CI Should Pass
- All tests pass
- Coverage >= 50%
- Code follows style guidelines
- No critical linting errors

### When CI Should Fail
- Any test fails
- Coverage < 50%
- Critical linting errors
- Type checking errors (future)

## Monitoring and Maintenance

### Regular Checks
- Monitor CI failure rate
- Review failed runs weekly
- Update dependencies via Dependabot
- Optimize slow tests

### When CI Fails
1. Check the "Actions" tab
2. Click on failed workflow
3. Review logs for errors
4. Fix issues locally
5. Push fixes
6. Verify CI passes

## Next Steps

After completing this subtask:
1. Verify CI runs: Check GitHub Actions tab
2. Verify all checks pass
3. Check badges display in README
4. Proceed to **Subtask 3: Dependency Version Management**

## Dependencies
- GitHub repository with Actions enabled
- Subtask 1 (Testing Infrastructure) completed
- Tests passing locally

## Deliverables
- Working GitHub Actions CI/CD pipeline
- Test automation on every push/PR
- Code quality checks (linting, formatting)
- Coverage reporting
- README with badges
- CONTRIBUTING.md with guidelines
- Optional: Codecov integration
- Optional: Branch protection rules
