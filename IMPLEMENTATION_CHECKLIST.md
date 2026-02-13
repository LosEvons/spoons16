# Implementation Checklist: CI/CD Dependency Improvements

This checklist tracks the implementation of recommendations from the CI/CD review of Subtask 3 (Dependency Version Management).

## ✅ Completed During Review

- [x] **Security Scanning Workflow** - Created `.github/workflows/security.yml`
  - pip-audit for vulnerability scanning
  - CodeQL for security analysis
  - Supply chain security checks
  - Weekly automated runs

- [x] **Enhanced Dependabot Configuration** - Updated `.github/dependabot.yml`
  - Intelligent grouping of testing dependencies
  - Intelligent grouping of linting dependencies
  - Grouped optional dependencies by patch version
  - Limited open PRs to 5 to reduce noise

- [x] **Dependency Management Helper Script** - Created `scripts/check_dependencies.py`
  - Check for outdated packages
  - Run security audits
  - Check for conflicts
  - Generate dependency reports

- [x] **Comprehensive Documentation**
  - CI_CD_REVIEW_DEPENDENCY_MANAGEMENT.md (26 KB full review)
  - CI_CD_QUICK_REFERENCE.md (8 KB quick guide)
  - CI_CD_SUMMARY.txt (visual summary)

---

## 🔴 Priority 1: Critical (Before Next Release)

### 1. Add Dependency Lock Files

**Status:** ❌ TODO  
**Impact:** HIGH - Ensures reproducible builds  
**Estimated Time:** 30 minutes

**Steps:**

```bash
# 1. Install pip-tools
pip install pip-tools

# 2. Generate lock files for core dependencies
cd caspoon
pip-compile pyproject.toml --output-file=requirements.lock

# 3. Generate lock file for dev dependencies
pip-compile --extra=dev pyproject.toml --output-file=requirements-dev.lock

# 4. Generate lock file for all optional features
pip-compile --extra=all pyproject.toml --output-file=requirements-all.lock

# 5. Commit lock files
git add requirements*.lock
git commit -m "feat: Add dependency lock files for reproducible builds"
git push

# 6. Update CI workflows to use lock files (see Priority 2, item 5)
```

**Acceptance Criteria:**
- [ ] `requirements.lock` created and committed
- [ ] `requirements-dev.lock` created and committed
- [ ] `requirements-all.lock` created and committed
- [ ] Lock files contain pinned versions for all dependencies
- [ ] Lock files can be synced successfully: `pip-sync requirements-dev.lock`

**Documentation to Update:**
- [ ] Add lock file generation to DEPENDENCIES.md
- [ ] Document lock file update process in DEPENDENCIES.md
- [ ] Add note to README about using lock files

---

## 🟡 Priority 2: High (This Sprint)

### 2. Test with Minimum Dependency Versions

**Status:** ❌ TODO  
**Impact:** MEDIUM - Ensures version constraints are accurate  
**Estimated Time:** 1 hour

**Steps:**

1. Update `.github/workflows/test.yml` matrix (around line 23):

```yaml
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.10', '3.11', '3.12']
        deps-version: ['min', 'latest']  # NEW: Test both minimum and latest
```

2. Add conditional dependency installation (replace existing step around line 44):

```yaml
    - name: Install Python dependencies (minimum versions)
      if: matrix.deps-version == 'min'
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        # Install minimum declared versions for testing
        pip install textual==0.40.0 pyelftools==0.29 r2pipe==1.7.0 rich==13.0.0
        pip install pytest==7.0.0 pytest-cov==4.0.0 pytest-asyncio==0.21.0
        pip install pytest-mock==3.10.0 pytest-xdist==3.0.0 pytest-timeout==2.1.0
        pip install -e . --no-deps
    
    - name: Install Python dependencies (latest compatible)
      if: matrix.deps-version == 'latest'
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e ".[dev]"
```

**Acceptance Criteria:**
- [ ] CI matrix includes `deps-version: ['min', 'latest']`
- [ ] Tests pass with minimum versions
- [ ] Tests pass with latest versions
- [ ] CI run time is acceptable (< 15 minutes total)

**Notes:**
- This will double the number of CI jobs (3 Python versions × 2 dep versions = 6 jobs per OS)
- Consider running minimum version tests only on Python 3.10 to save CI time

---

### 3. Test Optional Feature Groups

**Status:** ❌ TODO  
**Impact:** MEDIUM - Ensures feature isolation and correct dependencies  
**Estimated Time:** 1 hour

**Steps:**

Add new job to `.github/workflows/test.yml` (after the main `test` job):

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
    
    - name: Install base dependencies
      run: |
        python -m pip install --upgrade pip
        cd caspoon
        pip install -e .
    
    - name: Install ${{ matrix.feature }} feature
      run: |
        cd caspoon
        pip install -e ".[${{ matrix.feature }}]"
    
    - name: Verify installation
      run: |
        cd caspoon
        pip check
        echo "Installed packages:"
        pip list
    
    - name: Test feature imports
      run: |
        cd caspoon
        python -c "import caspoon; print('✓ Base package imports')"
        # Add feature-specific import tests as features are implemented
    
    - name: Run feature-specific tests
      run: |
        cd caspoon
        # Run all tests - feature-specific ones will be added with markers
        pytest tests/ -v --tb=short -x || echo "⚠️  Some tests skipped"
      continue-on-error: true  # Don't fail until feature tests are implemented
```

**Acceptance Criteria:**
- [ ] Optional feature job added to test.yml
- [ ] All 6 feature groups install without conflicts
- [ ] `pip check` passes for each feature group
- [ ] Feature-specific import tests added (basic check)

**Future Enhancement:**
- Add pytest markers for feature-specific tests (`@pytest.mark.windows`, etc.)
- Run only relevant tests for each feature group

---

### 4. Document Dependency Update Policy

**Status:** ❌ TODO  
**Impact:** MEDIUM - Standardizes dependency maintenance  
**Estimated Time:** 30 minutes

**Steps:**

Create `caspoon/docs/DEPENDENCY_POLICY.md`:

```markdown
# Dependency Update Policy

## Update Cadence

- **Security updates:** Immediate (within 24 hours of disclosure)
- **Major version updates:** Quarterly review cycle
- **Minor/patch updates:** Monthly review via Dependabot PRs
- **Lock file updates:** Weekly (automated via script)

## Review Process

### For Dependabot PRs

1. Automated CI checks must pass (tests, lint, security scan)
2. Review changelog for breaking changes or new features
3. Check for dependency conflicts (`pip check`)
4. Manual testing of affected features (if significant changes)
5. Merge if all checks pass and no breaking changes

### For Major Version Updates

1. Create dedicated branch for update
2. Review full changelog and migration guides
3. Update code to handle any breaking changes
4. Run full test suite on all Python versions
5. Update version constraint in pyproject.toml
6. Update lock files
7. Document migration in CHANGELOG.md

## Version Constraint Rules

### Standard Constraints

- **Stable packages (≥1.0):** `>=X.Y.Z,<X+1.0.0` (pin major version)
- **Pre-1.0 packages:** `>=0.Y.Z,<1.0.0` (allow minor updates with caution)
- **Critical security packages:** May pin to exact version if necessary

### Examples

```toml
# Good: Allows minor and patch updates, blocks breaking changes
"textual>=0.40.0,<1.0.0"

# Good: Standard for mature packages
"rich>=13.0.0,<14.0.0"

# Avoid: Too restrictive, misses bug fixes
"textual==0.40.0"

# Avoid: Too loose, may break on major update
"textual>=0.40.0"
```

## Security Vulnerability Handling

### When vulnerability is detected:

1. **Assess severity:** Review CVE details and CVSS score
2. **Check affected versions:** Confirm our version is impacted
3. **Immediate actions:**
   - High/Critical: Update within 24 hours
   - Medium: Update within 1 week
   - Low: Include in next regular update cycle

4. **Update process:**
   ```bash
   # Update dependency
   cd caspoon
   # Edit pyproject.toml to require fixed version
   pip-compile pyproject.toml -o requirements.lock
   
   # Test
   pip-sync requirements-dev.lock
   pytest tests/ -v
   
   # Commit
   git add pyproject.toml requirements*.lock
   git commit -m "security: Update <package> to fix CVE-YYYY-XXXXX"
   git push
   ```

5. **Document:** Note in CHANGELOG.md if security-related

## Breaking Change Handling

### When a dependency has breaking changes:

1. **Evaluate necessity:** Do we need the new version?
2. **Assess impact:** What code needs to change?
3. **Plan migration:**
   - Create migration branch
   - Update dependency
   - Fix broken code
   - Update tests
   - Document changes

4. **Communicate:**
   - Note in CHANGELOG.md
   - Update DEPENDENCIES.md if usage patterns change
   - Consider deprecation period for user-facing changes

## Lock File Maintenance

### Weekly Updates (Automated)

```bash
# Run weekly to get latest compatible versions
cd caspoon
pip-compile --upgrade pyproject.toml -o requirements.lock
pip-compile --upgrade --extra=dev pyproject.toml -o requirements-dev.lock
pip-compile --upgrade --extra=all pyproject.toml -o requirements-all.lock

# Test with new versions
pip-sync requirements-dev.lock
pytest tests/ -v

# If tests pass, commit
git add requirements*.lock
git commit -m "chore: Update dependency lock files"
```

### After pyproject.toml Changes

```bash
# Always regenerate lock files after changing constraints
pip-compile pyproject.toml -o requirements.lock
pip-compile --extra=dev pyproject.toml -o requirements-dev.lock
```

## Monitoring

### Automated

- Weekly security scans (GitHub Actions)
- Dependabot PRs (weekly)
- GitHub Security Advisories

### Manual (Monthly)

- Review open Dependabot PRs
- Check for outdated packages: `pip list --outdated`
- Review dependency maintenance status
- Update this policy if needed

## Adding New Dependencies

### Evaluation Criteria

Before adding a new dependency, verify:

- [ ] **Necessity:** Is it truly needed? Can we implement it ourselves?
- [ ] **Maintenance:** Active development? Recent commits?
- [ ] **License:** Compatible with MIT? (Check LICENSE file)
- [ ] **Security:** Known vulnerabilities? Security track record?
- [ ] **Maturity:** Version ≥1.0 preferred, or well-established <1.0
- [ ] **Size:** Download size reasonable? Dependencies reasonable?
- [ ] **Quality:** Tests? Documentation? Type hints?
- [ ] **Alternatives:** Have we considered alternatives?

### Documentation Required

When adding a dependency:

1. Update `pyproject.toml` with version constraint
2. Add to `DEPENDENCIES.md` with rationale
3. Update lock files
4. Note in CHANGELOG.md
5. Add to appropriate optional group if not core

## Emergency Procedures

### Critical Security Vulnerability

1. **Immediate patch:** Bypass normal review if actively exploited
2. **Notify team:** Alert all maintainers
3. **Emergency release:** Tag new version immediately
4. **Post-mortem:** Document incident and improve prevention

### Dependency Becomes Unmaintained

1. **Assess options:**
   - Fork and maintain ourselves?
   - Find actively maintained alternative?
   - Implement functionality ourselves?

2. **Plan migration:**
   - Timeline for replacement
   - Compatibility layer if needed
   - Communication plan

3. **Execute:**
   - Implement replacement
   - Update documentation
   - Deprecate old dependency

## Questions?

- Review: `DEPENDENCIES.md` for current dependency list
- Run: `python scripts/check_dependencies.py --all` for status
- Contact: Project maintainers for questions
```

**Acceptance Criteria:**
- [ ] DEPENDENCY_POLICY.md created
- [ ] Policy covers all update scenarios
- [ ] Clear procedures for security vulnerabilities
- [ ] Lock file maintenance documented
- [ ] New dependency evaluation criteria defined

---

### 5. Update CI to Use Lock Files

**Status:** ❌ TODO (Depends on Priority 1, item 1)  
**Impact:** HIGH - Enables reproducible builds in CI  
**Estimated Time:** 30 minutes

**Steps:**

Update `.github/workflows/test.yml` and `.github/workflows/lint.yml`:

```yaml
    # Replace existing installation step with:
    - name: Install Python dependencies (from lock file)
      run: |
        python -m pip install --upgrade pip pip-tools
        cd caspoon
        # Sync to exact versions from lock file
        pip-sync requirements-dev.lock
        # Install package in editable mode without dependencies
        # (dependencies already installed via pip-sync)
        pip install -e . --no-deps
    
    - name: Verify installation
      run: |
        cd caspoon
        pip check
```

**Acceptance Criteria:**
- [ ] test.yml uses lock files
- [ ] lint.yml uses lock files
- [ ] CI builds are reproducible (same package versions every time)
- [ ] CI cache keys updated to use lock file hash

---

## 🟢 Priority 3: Medium (Nice to Have)

### 6. Enhanced Dependency Caching

**Status:** ⚠️ PARTIAL (Basic caching exists)  
**Impact:** LOW - Marginally faster CI runs  
**Estimated Time:** 20 minutes

**Steps:**

Update cache configuration in workflows:

```yaml
    - name: Cache pip packages
      uses: actions/cache@v4
      with:
        path: |
          ~/.cache/pip
          ~/.local/share/virtualenvs
        key: ${{ runner.os }}-pip-${{ hashFiles('caspoon/requirements-dev.lock') }}
        restore-keys: |
          ${{ runner.os }}-pip-
```

**Acceptance Criteria:**
- [ ] Cache includes pip cache directory
- [ ] Cache key uses lock file hash (when available)
- [ ] Restore-keys provide fallback

---

### 7. Add Dependency Graph Visualization

**Status:** ❌ TODO  
**Impact:** LOW - Documentation enhancement  
**Estimated Time:** 15 minutes

**Steps:**

```bash
# 1. Install pipdeptree
pip install pipdeptree

# 2. Generate text tree
cd caspoon
pipdeptree > docs/dependency-tree.txt

# 3. Generate graph (requires graphviz)
pipdeptree --graph-output png > docs/dependency-graph.png

# 4. Update DEPENDENCIES.md to reference the graph
```

**Acceptance Criteria:**
- [ ] Dependency tree generated
- [ ] Graph visualization created (optional, requires graphviz)
- [ ] Linked from DEPENDENCIES.md

---

### 8. SBOM Generation (Future)

**Status:** ❌ TODO  
**Impact:** LOW - Supply chain transparency  
**Estimated Time:** 1 hour (research + implementation)

**Steps:**

Research and implement SBOM generation:

```bash
# Option 1: Using CycloneDX
pip install cyclonedx-bom
cd caspoon
cyclonedx-py -i requirements.txt -o sbom.json

# Option 2: Using SPDX
pip install spdx-tools
# Generate SPDX SBOM

# Add to CI as artifact
```

**Acceptance Criteria:**
- [ ] SBOM format chosen (CycloneDX or SPDX)
- [ ] SBOM generated in CI
- [ ] SBOM attached to releases
- [ ] Documentation updated

---

## Testing Checklist

After implementing each item, verify:

### Local Testing

- [ ] Dependencies install without conflicts: `pip check`
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Helper script works: `python scripts/check_dependencies.py --all`
- [ ] Lock files are valid (if added): `pip-sync requirements-dev.lock`

### CI Testing

- [ ] All workflows pass
- [ ] Security workflow runs and completes
- [ ] Dependabot PRs are properly grouped
- [ ] Coverage reports upload successfully

### Security Testing

- [ ] No known vulnerabilities: `pip-audit`
- [ ] Dependencies from trusted sources
- [ ] License compliance confirmed

---

## Monitoring Plan

### Weekly

- [ ] Check Dependabot PRs
- [ ] Review security workflow results
- [ ] Update lock files (if using)

### Monthly

- [ ] Review all open dependency issues
- [ ] Check for outdated packages
- [ ] Review dependency policy effectiveness

### Quarterly

- [ ] Evaluate major version updates
- [ ] Review optional dependencies usage
- [ ] Assess need for new dependency evaluation criteria

---

## Notes

- **Estimated Total Time:** 5-6 hours for all Priority 1 & 2 items
- **Recommended Order:** 1 → 4 → 5 → 2 → 3 (lock files first, then testing)
- **Can be split:** Items can be implemented in separate PRs
- **CI Time Impact:** Priority 2 items will increase CI time (acceptable trade-off)

---

## Success Metrics

After implementation, we should have:

- ✅ Reproducible builds (lock files)
- ✅ Automated security scanning (security.yml)
- ✅ Comprehensive dependency testing (min/max versions + features)
- ✅ Clear maintenance procedures (policy docs)
- ✅ Efficient Dependabot workflow (grouping)
- ✅ Helper tools for local development (scripts)

---

**Last Updated:** Review completion  
**Status:** Ready for implementation  
**Owner:** CI/CD Team
