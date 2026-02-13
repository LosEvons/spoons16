# Caspoon - Binary Analysis Toolkit

<div align="center">

[![Tests](https://img.shields.io/badge/tests-107%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

A modular, defensive binary analysis toolkit for reverse engineers and security researchers.

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

**Caspoon** is a reconnaissance and analysis tool designed for analyzing executable files safely and efficiently. It provides both a command-line interface for automation and an interactive terminal UI for manual exploration.

### Key Features

- 🔍 **Multi-Backend Analysis**: Integrates file, checksec, strings, and radare2
- 🛡️ **Security-First**: Designed for analyzing potentially malicious binaries safely
- 📊 **Comprehensive Reports**: Extract metadata, protections, strings, imports, exports, and disassembly
- 🖥️ **Dual Interface**: CLI for automation, TUI for interactive exploration
- 🧩 **Modular Architecture**: Easy to extend with new analysis modules
- ✅ **Well-Tested**: 107 tests with 84% coverage

### What It Detects

- **File Information**: Architecture (x86, x64, ARM, etc.), bit-width, stripped status
- **Security Protections**: PIE, NX, stack canaries, RELRO
- **Strings**: Printable ASCII strings in the binary
- **Imports/Exports**: Dynamic symbols and function references
- **Disassembly**: Function analysis via radare2 backend

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/spoons16.git
cd spoons16/caspoon

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
caspoon --help
```

### Basic Usage

#### Command-Line Mode (JSON output)

```bash
# Analyze a binary and output JSON report
caspoon /bin/ls

# Save output to file
caspoon /bin/ls > report.json
```

#### Interactive TUI Mode

```bash
# Launch interactive terminal UI
caspoon --ui

# Then enter path to binary in the input field
```

#### Programmatic Use

```python
from caspoon.core.runner import ReconRunner

# Run analysis
runner = ReconRunner()
report = runner.run("/path/to/binary")

# Access results
print(f"Architecture: {report.arch} ({report.bits}-bit)")
print(f"PIE: {report.protections.pie}")
print(f"Strings found: {len(report.strings)}")
print(f"Imports: {len(report.imports)}")
```

### Example Output

```json
{
  "path": "/bin/ls",
  "arch": "x86-64",
  "bits": 64,
  "file_type": "ELF",
  "stripped": false,
  "protections": {
    "pie": "full",
    "nx": true,
    "canary": true,
    "relro": "full"
  },
  "imports": ["printf", "malloc", "free", ...],
  "strings": ["Usage: ls [OPTION]...", ...]
}
```

---

## Dependencies

### Required

- **Python 3.10+**
- **pyelftools** - ELF file parsing
- **textual** - Terminal UI framework
- **rich** - Rich text formatting
- **r2pipe** - Radare2 integration

### External Tools (Optional)

Most features work without external tools, but some enhanced analysis requires:

- **file** - File type detection (usually pre-installed on Unix systems)
- **strings** - String extraction (usually pre-installed)
- **checksec** - Security features detection (install: `apt install checksec` or from [GitHub](https://github.com/slimm609/checksec.sh))
- **radare2** - Advanced disassembly and analysis (install: `apt install radare2` or from [radare.org](https://rada.re/))

Caspoon gracefully handles missing tools and provides fallback implementations where possible.

---

## Architecture

Caspoon follows a **pipeline-based modular design**:

```
┌──────────────────────────────────────┐
│    CLI or TUI Entry Point            │
└────────────────┬─────────────────────┘
                 │
         ┌───────▼───────┐
         │  ReconRunner  │  ← Orchestrates analysis
         └───────┬───────┘
                 │
         ┌───────▼───────────────────┐
         │  ExecutableReport         │  ← Central data model
         │  (accumulates all data)   │
         └───────┬───────────────────┘
                 │
     ┌───────────┼───────────┬────────────┐
     │           │           │            │
┌────▼─────┐ ┌──▼────┐ ┌───▼────┐ ┌────▼────┐
│FileInfo  │ │Protect│ │Strings │ │ Imports │
│Recon     │ │Recon  │ │Recon   │ │ Recon   │
└──────────┘ └───────┘ └────────┘ └─────────┘
```

Each **recon module** enriches the report with its findings. See [docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md) for detailed architecture documentation.

---

## Documentation

### User Documentation

- **[Quick Start](#quick-start)** - Get up and running quickly
- **[OVERVIEW.md](caspoon/docs/OVERVIEW.md)** - Comprehensive architecture and usage guide
- **[TESTING.md](TESTING.md)** - How to run tests and understand test coverage

### Developer Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to the project
- **[TESTING.md](TESTING.md)** - Testing infrastructure and guidelines
- **[Architecture Overview](caspoon/docs/OVERVIEW.md#architecture)** - Design philosophy and component breakdown

### Examples

```bash
# Example: Find all binaries with full RELRO in a directory
for bin in /usr/bin/*; do
  if file "$bin" | grep -q "ELF"; then
    result=$(caspoon "$bin" 2>/dev/null)
    if echo "$result" | jq -e '.protections.relro == "full"' >/dev/null 2>&1; then
      echo "$bin: Full RELRO"
    fi
  fi
done
```

---

## Testing

Caspoon has comprehensive test coverage to ensure reliability:

- **107 tests** covering unit, integration, and regression scenarios
- **84% code coverage** (94-100% on critical modules)
- **Golden tests** for detecting unintended behavior changes
- **Edge case testing** for robustness (corrupted files, large binaries, etc.)

### Running Tests

```bash
# Run all tests (fast)
pytest -m "not slow"

# Run with coverage report
pytest --cov=caspoon --cov-report=html
open htmlcov/index.html

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest -m golden                # Golden/regression tests
```

See **[TESTING.md](TESTING.md)** for detailed testing documentation.

---

## Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### Quick Contribution Guide

1. **Fork and clone** the repository
2. **Create a branch** for your changes: `git checkout -b feature/my-feature`
3. **Write tests** for your changes
4. **Run tests** to ensure everything passes: `pytest -m "not slow"`
5. **Submit a pull request** with a clear description

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines including:
- Code style and conventions
- How to add new recon modules
- Testing requirements
- Documentation standards

### Areas for Contribution

- 🔧 **New Analysis Modules**: Add support for new binary formats, architectures, or analysis techniques
- 🐛 **Bug Fixes**: Fix issues or improve error handling
- 📚 **Documentation**: Improve guides, add examples, fix typos
- ✅ **Tests**: Increase test coverage or add edge case tests
- 🎨 **UI Improvements**: Enhance the TUI or add new visualization views

---

## Security Considerations

⚠️ **Important**: Caspoon is designed to analyze potentially malicious binaries. Follow these best practices:

- **Isolate your environment**: Use VMs, containers, or sandboxes
- **Never execute analyzed binaries directly**: Caspoon analyzes without execution
- **Validate inputs**: Be cautious with untrusted file paths
- **Limit resources**: Consider timeouts and resource limits for automated analysis
- **Keep tools updated**: Ensure external analysis tools are up to date

---

## Project Status

Caspoon is actively developed and maintained. Current status:

- ✅ Core analysis pipeline complete
- ✅ Comprehensive test coverage (84%)
- ✅ CLI and TUI interfaces functional
- ✅ Multi-backend integration (file, checksec, strings, radare2)
- 🚧 Additional backends planned (Ghidra, Binary Ninja)
- 🚧 Advanced visualizations in development

---

## License

See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [radare2](https://rada.re/) - Reverse engineering framework
- [pyelftools](https://github.com/eliben/pyelftools) - ELF parsing library
- [pytest](https://pytest.org/) - Testing framework

---

## Contact & Support

- 📫 **Issues**: [GitHub Issues](https://github.com/yourusername/spoons16/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/spoons16/discussions)
- 📖 **Documentation**: See [docs/](caspoon/docs/) directory

---

<div align="center">

**[⬆ Back to Top](#caspoon---binary-analysis-toolkit)**

Made with 🔍 for reverse engineers and security researchers

</div>
