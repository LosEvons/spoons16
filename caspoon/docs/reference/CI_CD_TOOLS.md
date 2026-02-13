# CI/CD & Security Tools

This document describes the automated CI/CD and security tools available in the project.

## Security Scanning

### Automated Security Workflow

The project includes automated security scanning via `.github/workflows/security.yml`:

- **Runs**: Weekly on Mondays at 9 AM UTC, and on dependency changes
- **Tools**: pip-audit for CVE detection, CodeQL for security analysis
- **Reports**: Results appear in GitHub Security tab

### Manual Trigger

```bash
# Trigger security scan manually
gh workflow run security.yml
```

## Dependency Management

### Dependency Check Script

The `scripts/check_dependencies.py` helper script provides several useful operations:

```bash
# Run all checks
python scripts/check_dependencies.py --all

# Check for outdated packages
python scripts/check_dependencies.py --check-outdated

# Run security audit
python scripts/check_dependencies.py --security-audit

# Check for conflicts
python scripts/check_dependencies.py --conflicts

# Generate dependency report
python scripts/check_dependencies.py --report

# List installed packages
python scripts/check_dependencies.py --list
```

### Dependabot Configuration

Dependabot is configured to:
- Check for updates weekly (Mondays)
- Group related updates (testing tools, linting tools, optional deps)
- Limit to 5 open PRs maximum
- Ignore major version updates (review these manually)

## Lock Files

Use lock files for reproducible builds:

```bash
# Install exact versions (recommended for CI)
pip install -r requirements.lock

# Install dev dependencies with exact versions
pip install -r requirements-dev.lock
```

See [DEPENDENCIES.md](DEPENDENCIES.md) for more information on managing dependencies.
