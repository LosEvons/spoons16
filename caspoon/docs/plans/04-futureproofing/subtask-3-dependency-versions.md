# Subtask 3: Dependency Version Management

## Status
**✅ COMPLETED** - 2026-02-13

## Objective
Add proper version constraints to all dependencies to prevent breaking changes and ensure reproducible builds. This is critical for project stability.

## Completion Summary

All deliverables have been completed:
- ✅ Version constraints added to pyproject.toml
- ✅ Optional dependency groups structured (windows, patterns, advanced, graphs, reports, dev, all)
- ✅ DEPENDENCIES.md documentation created
- ✅ requirements.txt and requirements-dev.txt created
- ✅ **Dependency lock files added** (requirements.lock, requirements-dev.lock)
- ✅ Security scanning workflow implemented (.github/workflows/security.yml)
- ✅ Dependency check helper script created (scripts/check_dependencies.py)
- ✅ Enhanced Dependabot configuration

See [CI_CD_TOOLS.md](../../reference/CI_CD_TOOLS.md) for information on using the security and dependency tools.

## Priority
🟡 **HIGH - Should complete early**

## Scope
- Update pyproject.toml with version constraints
- Add version ranges for all dependencies
- Structure optional dependencies properly
- Document dependency rationale

## Prerequisites
- None (can be done in parallel with Subtasks 1-2)

## Implementation Steps

### Step 1: Update Main Dependencies (20 minutes)

**File**: `caspoon/pyproject.toml`

Replace existing dependencies section:

```toml
[project]
name = "caspoon"
version = "0.1.0"
description = "Caspoon Reverse Engineering Toolkit"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}  # Update if different
authors = [
  { name = "LosEvons" }
]

dependencies = [
  "textual>=0.40.0,<1.0.0",     # TUI framework
  "pyelftools>=0.29,<1.0",       # ELF file parsing
  "r2pipe>=1.7.0,<2.0.0",        # radare2 interface
  "rich>=13.0.0,<14.0.0",        # Text rendering
]
```

### Step 2: Add Optional Dependencies (30 minutes)

Add optional dependency groups:

```toml
[project.optional-dependencies]
# Windows PE file support
windows = [
  "pefile>=2023.2.7,<2024.0.0",
]

# Pattern detection features
patterns = [
  "capstone>=5.0.0,<6.0.0",
  "yara-python>=4.3.0,<5.0.0",
]

# Advanced analysis
advanced = [
  "scipy>=1.10.0,<2.0.0",
]

# Graph generation and visualization
graphs = [
  "networkx>=3.0,<4.0",
]

# Report generation
reports = [
  "jinja2>=3.1.0,<4.0.0",
]

# Development tools
dev = [
  # Testing
  "pytest>=7.0.0,<8.0.0",
  "pytest-cov>=4.0.0,<5.0.0",
  "pytest-asyncio>=0.21.0,<1.0.0",
  "pytest-mock>=3.10.0,<4.0.0",
  "pytest-xdist>=3.0.0,<4.0.0",
  "pytest-timeout>=2.1.0,<3.0.0",
  
  # Code quality
  "black>=23.0.0,<24.0.0",
  "mypy>=1.0.0,<2.0.0",
  "ruff>=0.1.0,<1.0.0",
  
  # Type stubs
  "types-pyelftools",
]

# All optional features
all = [
  "pefile>=2023.2.7,<2024.0.0",
  "capstone>=5.0.0,<6.0.0",
  "yara-python>=4.3.0,<5.0.0",
  "scipy>=1.10.0,<2.0.0",
  "networkx>=3.0,<4.0",
  "jinja2>=3.1.0,<4.0.0",
]
```

### Step 3: Document Dependencies (20 minutes)

**File**: `caspoon/docs/DEPENDENCIES.md`

```markdown
# Caspoon Dependencies

## Core Dependencies

### textual (>=0.40.0, <1.0.0)
- **Purpose**: Terminal User Interface framework
- **Usage**: Main UI for interactive mode
- **Why**: Modern TUI with good widget support
- **Alternatives**: urwid (older), asciimatics (limited)

### pyelftools (>=0.29, <1.0)
- **Purpose**: ELF file parsing
- **Usage**: Parse Linux binaries, extract sections/symbols
- **Why**: Pure Python, well-maintained
- **Alternatives**: pyelftools (no good alternatives for Python)

### r2pipe (>=1.7.0, <2.0.0)
- **Purpose**: radare2 interface
- **Usage**: Disassembly, binary analysis
- **Why**: Powerful, multi-architecture support
- **Alternatives**: capstone (disasm only), IDA Pro (proprietary)
- **Note**: Requires radare2 installed on system

### rich (>=13.0.0, <14.0.0)
- **Purpose**: Text rendering and formatting
- **Usage**: Syntax highlighting, tables, formatting
- **Why**: Excellent formatting, used by Textual
- **Alternatives**: colorama (basic), termcolor (limited)

## Optional Dependencies

### Windows Support (windows)
- **pefile**: Windows PE file parsing
- **When needed**: Analyzing Windows executables
- **Install**: `pip install caspoon[windows]`

### Pattern Detection (patterns)
- **capstone**: Disassembly engine
- **yara-python**: YARA rule engine
- **When needed**: Implementing pattern detection features
- **Install**: `pip install caspoon[patterns]`

### Advanced Analysis (advanced)
- **scipy**: Scientific computing
- **When needed**: Entropy analysis, statistics
- **Install**: `pip install caspoon[advanced]`

### Visualization (graphs)
- **networkx**: Graph data structures
- **When needed**: Call graphs, CFG generation
- **Install**: `pip install caspoon[graphs]`

### Reporting (reports)
- **jinja2**: Template engine
- **When needed**: HTML report generation
- **Install**: `pip install caspoon[reports]`

### All Features (all)
- **Install all optional dependencies**
- **Install**: `pip install caspoon[all]`

## Development Dependencies (dev)

### Testing
- pytest: Test framework
- pytest-cov: Coverage reporting
- pytest-asyncio: Async test support
- pytest-mock: Mocking utilities
- pytest-xdist: Parallel testing
- pytest-timeout: Test timeouts

### Code Quality
- black: Code formatter
- mypy: Type checker
- ruff: Fast linter
- types-pyelftools: Type stubs

### Installation
```bash
pip install -e ".[dev]"
```

## Version Constraints

### Philosophy
- **Major version pinning**: Prevent breaking changes
- **Minor version flexibility**: Allow bug fixes and features
- **Example**: `>=1.0.0,<2.0.0` allows 1.x updates, blocks 2.0

### Updating Dependencies
1. Check for security updates: `pip list --outdated`
2. Review changelogs for breaking changes
3. Update version constraints in pyproject.toml
4. Run full test suite
5. Update this document

## System Dependencies

### Required
- Python 3.10 or higher
- file command (standard on Unix)
- binutils (standard on Unix)

### Optional
- radare2 (for binary analysis)
- GCC (for building test fixtures)
- checksec (for protection detection)

### Installation (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3.10 python3-pip binutils file
sudo apt-get install radare2  # optional
sudo apt-get install gcc       # for test fixtures
```

## Troubleshooting

### Issue: r2pipe fails to import
- **Cause**: radare2 not installed
- **Solution**: Install radare2 or disable r2-dependent features

### Issue: yara-python won't install
- **Cause**: Missing build dependencies
- **Solution**: `sudo apt-get install libyara-dev`

### Issue: pefile conflicts
- **Cause**: Incompatible version
- **Solution**: Update to latest compatible version
```

### Step 4: Create requirements.txt for reference (10 minutes)

**File**: `caspoon/requirements.txt`

```txt
# Core dependencies
# Install with: pip install -r requirements.txt
textual>=0.40.0,<1.0.0
pyelftools>=0.29,<1.0
r2pipe>=1.7.0,<2.0.0
rich>=13.0.0,<14.0.0
```

**File**: `caspoon/requirements-dev.txt`

```txt
# Development dependencies
# Install with: pip install -r requirements-dev.txt
-r requirements.txt

# Testing
pytest>=7.0.0,<8.0.0
pytest-cov>=4.0.0,<5.0.0
pytest-asyncio>=0.21.0,<1.0.0
pytest-mock>=3.10.0,<4.0.0
pytest-xdist>=3.0.0,<4.0.0
pytest-timeout>=2.1.0,<3.0.0

# Code quality
black>=23.0.0,<24.0.0
mypy>=1.0.0,<2.0.0
ruff>=0.1.0,<1.0.0
types-pyelftools
```

### Step 5: Verify Installation (20 minutes)

Test that installations work:

```bash
cd /home/runner/work/spoons16/spoons16/caspoon

# Test base installation
pip install -e .
python -c "import caspoon; print('Base install OK')"

# Test dev installation
pip install -e ".[dev]"
python -c "import pytest; print('Dev dependencies OK')"

# Test optional installations
pip install -e ".[windows]" || echo "Windows deps failed (expected on Linux)"
pip install -e ".[patterns]" || echo "Pattern deps failed (build tools needed)"

# Verify versions
pip list | grep textual
pip list | grep pytest
```

## Testing Strategy

### Self-Testing
1. **Dependencies resolve**: pip install succeeds
2. **Version constraints work**: No conflicts
3. **Optional groups work**: Can install selectively
4. **Documentation complete**: DEPENDENCIES.md accurate

### Manual Verification
- [ ] `pip install -e .` succeeds
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pip list` shows correct versions
- [ ] No dependency conflicts reported
- [ ] Optional dependencies can be installed

## Success Criteria

- [ ] pyproject.toml has version constraints for all core dependencies
- [ ] Optional dependencies are properly structured
- [ ] Dev dependencies are in `[dev]` group
- [ ] DEPENDENCIES.md documents all dependencies
- [ ] requirements.txt and requirements-dev.txt exist
- [ ] Installation succeeds: `pip install -e .`
- [ ] Dev installation succeeds: `pip install -e ".[dev]"`
- [ ] No dependency conflicts
- [ ] CI uses versioned dependencies

## Estimated Time
**1.5 hours total**
- pyproject.toml updates: 30 min
- DEPENDENCIES.md: 30 min
- requirements files: 10 min
- Verification: 20 min

## Common Issues & Solutions

### Issue 1: Dependency conflicts
**Solution**: Adjust version ranges, check for incompatibilities

### Issue 2: Optional deps won't install
**Solution**: Install system dependencies first (libyara-dev, etc.)

### Issue 3: Version too restrictive
**Solution**: Allow minor version updates, only pin major

## Next Steps

After completing this subtask:
1. Verify installations work
2. Update CI to use versioned deps
3. Proceed to **Subtask 5: Code Quality Tools Setup**
4. Optional: **Subtask 4: Backend Abstraction** can be done in parallel

## Dependencies
- None (can be done immediately)

## Deliverables
- Updated pyproject.toml with version constraints
- DEPENDENCIES.md documentation
- requirements.txt and requirements-dev.txt
- Verified working installations
