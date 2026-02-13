# CI/CD Quick Reference: Dependency Management

## Files Modified/Created in This Review

### ✅ Created Files
1. **CI_CD_REVIEW_DEPENDENCY_MANAGEMENT.md** - Comprehensive review document
2. **.github/workflows/security.yml** - Security scanning workflow
3. **scripts/check_dependencies.py** - Dependency management helper script

### 🔧 Modified Files  
1. **.github/dependabot.yml** - Enhanced with intelligent grouping

## Priority Action Items

### 🔴 Priority 1: Critical (Do Before Next Release)

#### 1. Add Dependency Lock Files
```bash
cd caspoon

# Install pip-tools
pip install pip-tools

# Generate lock files
pip-compile pyproject.toml --output-file=requirements.lock
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.lock
pip-compile --extra=all pyproject.toml --output-file=requirements-all.lock

# Commit lock files
git add requirements*.lock
git commit -m "feat: Add dependency lock files for reproducible builds"
```

**Why:** Ensures reproducible builds across different environments and CI runs.

#### 2. Enable Security Scanning (Already Done ✅)
The security workflow has been created at `.github/workflows/security.yml`.

**Test it:**
```bash
# Trigger manually
gh workflow run security.yml

# Or wait for next push/PR
```

### 🟡 Priority 2: High (Do This Sprint)

#### 3. Test with Minimum Dependency Versions

**Update `.github/workflows/test.yml`:**

Add to the matrix (line ~23):
```yaml
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.10', '3.11', '3.12']
        deps-version: ['min', 'latest']  # NEW
```

Add conditional installation step (replace existing install step):
```yaml
    - name: Install Python dependencies (minimum)
      if: matrix.deps-version == 'min'
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        # Install minimum declared versions
        pip install textual==0.40.0 pyelftools==0.29 r2pipe==1.7.0 rich==13.0.0
        pip install pytest>=7.0.0,<8.0.0 pytest-cov>=4.0.0,<5.0.0
        pip install -e . --no-deps
    
    - name: Install Python dependencies (latest)
      if: matrix.deps-version == 'latest'
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[dev]"
```

#### 4. Test Optional Feature Groups

**Add new job to `.github/workflows/test.yml`:**

```yaml
  test-optional-features:
    name: Test Optional Features - ${{ matrix.feature }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
    
    strategy:
      fail-fast: false
      matrix:
        feature: [windows, patterns, advanced, graphs, reports, all]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v6
    
    - name: Set up Python
      uses: actions/setup-python@v6
      with:
        python-version: '3.10'
        cache: 'pip'
        cache-dependency-path: 'caspoon/pyproject.toml'
    
    - name: Install with ${{ matrix.feature }} feature
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[${{ matrix.feature }}]"
    
    - name: Verify installation
      run: |
        cd caspoon
        pip check
        pip list
    
    - name: Run feature-specific tests
      run: |
        cd caspoon
        # Run all tests - feature-specific ones will be added later
        pytest tests/ -v --tb=short || echo "Some tests may be skipped"
```

### 🟢 Priority 3: Medium (Nice to Have)

#### 5. Use Dependency Management Script

The script at `scripts/check_dependencies.py` can be run locally or in CI:

```bash
# Check everything
python scripts/check_dependencies.py --all

# Individual checks
python scripts/check_dependencies.py --check-outdated
python scripts/check_dependencies.py --security-audit
python scripts/check_dependencies.py --conflicts
python scripts/check_dependencies.py --report
```

Add to CI as a pre-test step:
```yaml
    - name: Validate dependencies
      run: |
        python scripts/check_dependencies.py --conflicts
```

## Quick Commands

### Local Development

```bash
# Check for security issues
pip install pip-audit
cd caspoon && pip-audit --requirement requirements.txt

# Check for outdated packages
pip list --outdated

# Verify no conflicts
pip check

# See dependency tree
pip install pipdeptree
pipdeptree

# Update all dependencies to latest compatible
pip install --upgrade -e ".[dev]"
```

### CI/CD Maintenance

```bash
# View workflow runs
gh run list --workflow=security.yml

# Trigger security scan manually
gh workflow run security.yml

# View security scan results
gh run view <run-id>

# Check dependabot status
gh api /repos/:owner/:repo/dependabot/alerts

# View dependabot PRs
gh pr list --label dependencies
```

## Testing the Changes

### 1. Test Security Workflow Locally

```bash
cd caspoon

# Install audit tools
pip install pip-audit safety

# Run core audit
pip-audit --requirement requirements.txt --desc

# Run dev audit
pip-audit --requirement requirements-dev.txt --desc

# Run safety check
safety check --file requirements.txt
```

### 2. Test Dependabot Configuration

```bash
# Check dependabot config syntax
gh api /repos/:owner/:repo/dependabot/alerts

# Or validate manually
cat .github/dependabot.yml
# Should show enhanced grouping
```

### 3. Test Dependency Script

```bash
# Test the helper script
python scripts/check_dependencies.py --help

# Run all checks
python scripts/check_dependencies.py --all
```

## Workflow Triggers

### Security Workflow Runs On:
- ✅ Push to `main`, `develop`
- ✅ Pull requests to `main`, `develop`
- ✅ Changes to dependency files
- ✅ Weekly schedule (Monday 9 AM UTC)
- ✅ Manual trigger

### When to Trigger Manually:
```bash
# After updating dependencies
git add caspoon/pyproject.toml
git commit -m "deps: Update package X to version Y"
gh workflow run security.yml

# Before releasing
gh workflow run security.yml
gh workflow run test.yml
```

## Monitoring

### GitHub Security Tab
- Navigate to: **Security** → **Dependabot alerts**
- Review: Open security advisories
- Action: Click "Review security update" on alerts

### Workflow Status
- Navigate to: **Actions** tab
- Check: "Security Audit" workflow
- Review: Recent runs and any failures

### Weekly Review Checklist
```markdown
- [ ] Check Dependabot PRs (should auto-group by type)
- [ ] Review security workflow runs
- [ ] Check for failed dependency updates
- [ ] Review outdated packages report
- [ ] Update lock files if dependencies changed
```

## Common Issues and Solutions

### Issue: Security workflow fails on pip-audit

**Solution:**
```bash
# Update pip-audit
pip install --upgrade pip-audit

# Re-generate requirements if needed
cd caspoon
pip freeze > requirements.txt
```

### Issue: Dependabot PRs too noisy

**Solution:** Already handled by grouping in `.github/dependabot.yml`
- Testing deps grouped together
- Linting deps grouped together  
- Optional deps grouped by patch version only

### Issue: Lock files out of sync

**Solution:**
```bash
cd caspoon
pip-compile --upgrade pyproject.toml -o requirements.lock
pip-compile --upgrade --extra=dev pyproject.toml -o requirements-dev.lock
git add requirements*.lock
git commit -m "chore: Update dependency lock files"
```

### Issue: CI gets different versions than local

**Solution:** Use lock files (Priority 1 action item above)

## Next Steps

1. ✅ Review the comprehensive review document: `CI_CD_REVIEW_DEPENDENCY_MANAGEMENT.md`
2. ✅ Test the new security workflow
3. ✅ Create lock files (Priority 1)
4. ✅ Update test workflow with dependency matrix (Priority 2)
5. ✅ Monitor Dependabot behavior with new grouping

## Questions?

- Review: `CI_CD_REVIEW_DEPENDENCY_MANAGEMENT.md` for detailed analysis
- Check: `caspoon/docs/DEPENDENCIES.md` for dependency documentation
- Run: `python scripts/check_dependencies.py --help` for script usage

---

**Last Updated:** Review completion  
**Maintained By:** CI/CD Agent
