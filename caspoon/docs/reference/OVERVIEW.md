# Caspoon - Reverse Engineering Toolkit

## Overview

Caspoon is a modular toolkit for analyzing and reverse engineering executable files. It provides a command-line interface for automated analysis of binary files.

## Purpose

Caspoon serves as a reconnaissance and analysis tool for reverse engineers, security researchers, and binary analysts. It automates the collection of key information about executables including:

- File metadata and architecture details
- Security protections and hardening features
- String extraction
- Import/export functions
- Disassembly and function analysis via radare2

## Architecture

### Core Design Philosophy

The architecture follows a **pipeline-based modular design** where multiple recon modules sequentially enrich a central `ExecutableReport` object. This design allows:

- Easy addition of new analysis modules
- Clear separation of concerns
- Extensibility through new backends
- Consistent data model across all analysis steps

### Component Layers

```
┌─────────────────────────────────────┐
│        Entry Points                  │
│  main.py (CLI launcher)             │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐          │
│   CLI Mode     │          │
│ (JSON output)  │          │
└───────┬────────┘          │
        │                   │
        └──────────┬────────┘
                   │
        ┌──────────▼──────────┐
        │   ReconRunner       │
        │  (core/runner.py)   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────────┐
        │  ExecutableReport       │
        │   (core/models.py)      │
        │  - Accumulates data     │
        │  - Shared state         │
        └──────────┬──────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌─────▼─────┐  ┌────▼────┐
│ Recon  │  │  Recon    │  │  Recon  │
│ Module │  │  Module   │  │  Module │
│   1    │  │    2      │  │   ...   │
└────────┘  └───────────┘  └─────────┘
```

### Directory Structure

```
caspoon/
├── main.py              # Entry point (CLI and UI launcher)
├── __main__.py          # Python module entry point
├── core/                # Core functionality
│   ├── models.py        # Data models (ExecutableReport, ProtectionInfo, etc.)
│   └── runner.py        # ReconRunner - orchestrates analysis pipeline
├── recon/               # Reconnaissance modules (analysis steps)
│   ├── file_info.py     # Basic file metadata (arch, bits, stripped)
│   ├── protections.py   # Security features (PIE, NX, canary, RELRO)
│   ├── strings_mod.py   # String extraction
│   └── imports_exports.py  # Import/export function analysis
├── backends/            # Analysis backend integrations
│   ├── r2_analyzer.py   # Core radare2 analysis functions
│   └── r2_recon.py      # Radare2 recon module wrapper
└── docs/                # Documentation
```

## Key Components

### 1. Data Models (`core/models.py`)

Central data structures that represent analysis results:

- **`ExecutableReport`**: Main report object containing all analysis data
  - `path`: Path to analyzed file
  - `arch`, `bits`, `file_type`: Architecture and file information
  - `stripped`: Whether symbols are stripped
  - `protections`: Security features (ProtectionInfo object)
  - `strings`, `imports`, `exports`: Lists of extracted data
  - `raw_backend_data`: Dictionary for backend-specific data (e.g., radare2 JSON)

- **`ProtectionInfo`**: Security hardening features
  - `pie`: Position Independent Executable
  - `nx`: No-Execute bit
  - `canary`: Stack canary protection
  - `relro`: RELRO (full/partial/none)

- **`FunctionInfo`**: Function metadata
  - `name`, `address`, `imported` flag

### 2. Recon Runner (`core/runner.py`)

**`ReconRunner`** is the orchestration engine that:
- Maintains a list of recon modules (steps)
- Executes each module sequentially
- Passes the evolving `ExecutableReport` through the pipeline
- Each module enriches the report with its findings

Pipeline steps (in order):
1. FileInfoRecon
2. ProtectionsRecon
3. StringsRecon
4. ImportExportRecon
5. R2BackendRecon

### 3. Recon Modules

Each recon module follows a consistent interface:

```python
class SomeRecon:
    name = "module_name"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        # Analyze the binary at path
        # Enrich the report object
        return report
```

**Current Modules:**

- **FileInfoRecon** (`recon/file_info.py`): Uses pyelftools to extract basic metadata (architecture, bit-width, stripped status)

- **ProtectionsRecon** (`recon/protections.py`): Uses pyelftools to identify security features (PIE, NX, canary, RELRO)

- **StringsRecon** (`recon/strings_mod.py`): Extracts printable strings from the binary

- **ImportExportRecon** (`recon/imports_exports.py`): Analyzes imported and exported functions

- **R2BackendRecon** (`backends/r2_recon.py`): Integrates radare2 analysis including functions list, imports, strings, and disassembly of main

### 4. Backends

Backends provide deeper analysis through external tools:

**Radare2 Backend** (`backends/r2_analyzer.py`):
- Uses `r2pipe` to communicate with radare2
- Performs lightweight analysis (`aa` command)
- Extracts:
  - Functions list (`aflj`)
  - Imported symbols (`isj`)
  - Strings (`izj`)
  - Disassembly of main function (`pdj`)
- Returns structured JSON data stored in `raw_backend_data["r2"]`

### 5. User Interfaces

**CLI Mode** (`main.py`):
- Run: `python -m caspoon <binary_path>`
- Executes ReconRunner and outputs JSON report
- Suitable for automation and scripting

## Dependencies

Defined in `pyproject.toml`:

- **pyelftools**: ELF file parsing and analysis
- **r2pipe**: Python interface to radare2 for disassembly and binary analysis
- **rich**: Rich text and formatting for terminal output

External tools used via subprocess:
- **radare2**: Binary analysis backend (via r2pipe)

## Usage Patterns

### As a CLI Tool

```bash
# Analyze a binary and output JSON
python -m caspoon /path/to/binary

# Or using the installed script
caspoon /path/to/binary
```

### Programmatic Usage

```python
from caspoon.core.runner import ReconRunner

runner = ReconRunner()
report = runner.run("/path/to/binary")

# Access analysis results
print(report.arch, report.bits)
print(report.protections.pie)
print(len(report.strings))

# Access raw backend data
r2_data = report.raw_backend_data.get("r2", {})
functions = r2_data.get("functions", [])
```

## Extensibility

### Adding a New Recon Module

1. Create a new file in `caspoon/recon/` (e.g., `my_analysis.py`)
2. Implement the recon interface:

```python
from ..core.models import ExecutableReport

class MyAnalysisRecon:
    name = "my_analysis"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        # Perform your analysis
        # Modify the report object
        return report
```

3. Register it in `core/runner.py`:

```python
from ..recon.my_analysis import MyAnalysisRecon

class ReconRunner:
    def __init__(self):
        self.steps = [
            # ... existing modules
            MyAnalysisRecon(),
        ]
```

### Adding a New Backend

1. Create backend implementation in `backends/` (e.g., `ghidra_analyzer.py`)
2. Create a recon wrapper in `backends/` (e.g., `ghidra_recon.py`) following the recon interface
3. Store backend-specific data in `report.raw_backend_data["backend_name"]`
4. Register the backend recon module in `ReconRunner`

## Development Guidelines

### Code Style
- Use dataclasses for data models
- Follow the recon module interface pattern
- Store backend-specific data in `raw_backend_data` dictionary
- Use pyelftools for ELF parsing and analysis
- Handle non-ELF files gracefully

### Error Handling
- Recon modules should handle errors internally and return report
- Use try-except for external command failures
- Provide fallback values when tools are unavailable

### Testing Approach

Caspoon has comprehensive test coverage (84%, 107 tests). See **[TESTING.md](../../../TESTING.md)** for detailed testing documentation.

**Quick testing commands:**
```bash
# Run all fast tests
pytest -m "not slow"

# Run with coverage
pytest --cov=caspoon --cov-report=html

# Run specific test category
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest -m golden                # Regression tests
```

**Testing principles:**
- Test each recon module independently with mocked dependencies
- Use sample binaries with known characteristics for integration tests
- Verify report enrichment at each pipeline stage
- Test error paths (missing tools, timeouts, corrupted files)
- Test across different binary types (stripped, protected, etc.)
- Maintain 80%+ coverage on all new code
- Use golden tests to detect unintended behavior changes

For detailed testing guidelines, see:
- **[TESTING.md](../../../TESTING.md)** - Comprehensive testing guide
- **[tests/README.md](../../tests/README.md)** - Test suite overview

## Future Enhancement Areas

- Additional architecture support (ARM, MIPS, etc.)
- Binary diffing capabilities
- CFG (Control Flow Graph) visualization
- Entropy analysis for packed binaries
- Signature-based detection (YARA integration)
- Export to multiple formats (JSON, XML, HTML report)
- Plugin system for third-party modules
- Database backend for storing analysis results
- Collaborative analysis features

## Security Considerations

Caspoon analyzes potentially malicious binaries. Best practices:

- Run in isolated environments (VMs, containers)
- Never execute analyzed binaries directly
- Be cautious with path traversal in file operations
- Validate all external tool outputs
- Limit resource consumption (memory, CPU) for large binaries
- Consider sandboxing for automated analysis pipelines

## License

Check repository root for license information.
