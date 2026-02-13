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
