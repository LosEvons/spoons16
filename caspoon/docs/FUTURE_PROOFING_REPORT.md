# Caspoon Future-Proofing Assessment Report

**Date**: 2026-02-12  
**Version**: 0.1.0  
**Prepared by**: Copilot AI  

## Executive Summary

This report evaluates the current implementation of the Caspoon reverse engineering toolkit to assess its readiness for future development and feature expansion. We analyze the suitability of chosen dependencies, architecture decisions, and identify potential limitations that could hinder planned enhancements.

**Key Findings**:
- ✅ **Overall Architecture**: Well-designed, modular, and extensible
- ⚠️ **UI Library (Textual)**: Has limitations for advanced features, but workable
- ✅ **Analysis Libraries**: Appropriate choices for current needs
- ⚠️ **Version Pinning**: Dependencies lack version constraints (risk)
- ⚠️ **Testing Infrastructure**: Currently missing, critical for future-proofing
- ✅ **Python Version**: Modern Python 3.10+ requirement is appropriate

**Recommendation**: Proceed with implementation plans, but prioritize establishing comprehensive testing infrastructure, add version constraints to dependencies, and consider UI library alternatives for advanced visualization features.

---

## 1. Dependency Analysis

### 1.1 Textual (UI Framework)

**Current Status**: Primary UI library for terminal-based interface

**Strengths**:
- ✅ Modern, actively maintained TUI framework
- ✅ Built on Rich, providing excellent text rendering
- ✅ React-like component model, familiar to web developers
- ✅ Good documentation and examples
- ✅ Supports async/await patterns
- ✅ CSS-like styling system
- ✅ Built-in widgets (tables, tabs, containers)
- ✅ Active community and rapid development

**Limitations for Planned Features**:

1. **Graph Visualization** ⚠️
   - **Issue**: Limited support for complex graphical layouts (CFG, call graphs)
   - **Impact**: Plans 1.4 (Interactive Navigation), 4 (Control Flow)
   - **Workaround**: ASCII-art graphs, external visualization, or use Rich's tree widgets
   - **Alternative**: Consider adding imgcat/kitty graphics protocol support for real graphs

2. **Split View / Multi-Pane Layouts** ⚠️
   - **Issue**: Split panes are possible but not as flexible as dedicated editors
   - **Impact**: Plan 9 (UI Improvements) - Split view disassembly
   - **Workaround**: Use Textual's containers and horizontal/vertical layouts
   - **Status**: Achievable but may require custom widgets

3. **Mouse Interactions** ⚠️
   - **Issue**: Mouse support is present but limited compared to GUI frameworks
   - **Impact**: Plan 1.4 (Interactive Navigation) - Clickable addresses
   - **Workaround**: Focus on keyboard-driven navigation, use selection/focus model
   - **Status**: Textual 0.40+ has improved mouse support

4. **Hex Editor Widget** ⚠️
   - **Issue**: No built-in hex editor widget
   - **Impact**: Plan 9 (UI Improvements) - Hex viewer
   - **Workaround**: Create custom widget using Static or DataTable
   - **Status**: Feasible to implement custom widget

5. **Performance with Large Datasets** ⚠️
   - **Issue**: Rendering 10,000+ lines can be slow
   - **Impact**: All plans dealing with large binaries
   - **Workaround**: Pagination, lazy loading, virtual scrolling
   - **Status**: Requires careful implementation

6. **Interactive Graphs** ❌
   - **Issue**: No native support for interactive node-graph editors
   - **Impact**: Plan 4 (Control Flow) - Interactive CFG
   - **Workaround**: External tool integration, ASCII art, or limited tree view
   - **Alternative**: Generate HTML reports with D3.js graphs

**Verdict**: ✅ **Suitable with caveats**
- Textual is appropriate for 80% of planned features
- Advanced visualization (interactive graphs) may require external tools
- Plan to keep Textual for TUI, add HTML export for complex visualizations

**Recommendations**:
1. Use Textual for main interface (good choice)
2. Implement pagination and lazy loading early
3. For complex graphs, add HTML report generation with JavaScript libraries
4. Consider adding image rendering support (kitty protocol) for future graph display
5. Keep monitoring Textual updates - it's rapidly evolving

### 1.2 Rich (Text Rendering)

**Current Status**: Text formatting and rendering library, used by Textual

**Strengths**:
- ✅ Excellent syntax highlighting capabilities
- ✅ Powerful table rendering
- ✅ Tree structures for hierarchical data
- ✅ Progress bars and status displays
- ✅ Export to HTML, SVG
- ✅ Well-maintained and widely used

**Limitations**:
- None significant for current use case

**Verdict**: ✅ **Excellent choice**
- Perfect for Plan 1 (Syntax Highlighting)
- Supports all planned text rendering needs
- HTML export capability useful for reporting (Plan 10)

**Recommendations**:
- Leverage Rich's syntax highlighting for assembly code
- Use Rich's export features for report generation
- Consider using Rich's Console for CLI mode enhancements

### 1.3 pyelftools (Binary Analysis)

**Current Status**: Used for ELF file parsing

**Strengths**:
- ✅ Comprehensive ELF parsing
- ✅ Pure Python (no C dependencies)
- ✅ Well-tested and stable
- ✅ Actively maintained

**Limitations**:
- ❌ ELF only (Linux, no Windows PE support)
- ⚠️ No support for Mach-O (macOS binaries)

**Verdict**: ✅ **Good for ELF, needs complementary libraries**

**Recommendations**:
1. **Add**: `pefile` for Windows PE file support
2. **Add**: `macholib` or `python-macholib` for macOS support
3. Keep pyelftools as primary for Linux/ELF binaries

**Code Example**:
```python
# Future multi-format support
if file_type == 'PE':
    import pefile
    pe = pefile.PE(path)
elif file_type == 'ELF':
    from elftools.elf.elffile import ELFFile
    with open(path, 'rb') as f:
        elf = ELFFile(f)
elif file_type == 'Mach-O':
    import macholib.MachO
    macho = macholib.MachO.MachO(path)
```

### 1.4 r2pipe (Radare2 Integration)

**Current Status**: Python interface to radare2

**Strengths**:
- ✅ Powerful disassembly and analysis
- ✅ Multi-architecture support
- ✅ Extensive command set
- ✅ Active development

**Limitations**:
- ⚠️ Requires radare2 installation (external dependency)
- ⚠️ r2 API can change between versions
- ⚠️ Performance can be slow on very large binaries
- ⚠️ JSON parsing overhead

**Risks**:
1. **Breaking Changes**: Radare2 commands may change
   - **Mitigation**: Version pin radare2, abstract r2 interactions
2. **Installation Requirement**: Users must install radare2 separately
   - **Mitigation**: Document clearly, provide install script
3. **Performance**: r2 analysis can be slow
   - **Mitigation**: Implement caching, incremental analysis

**Verdict**: ✅ **Appropriate choice**
- Best Python-accessible disassembly framework
- Multi-architecture support essential for plans
- Worth the external dependency

**Alternatives Considered**:
- **Capstone**: Disassembly only, no analysis engine
- **IDA Python**: Proprietary, expensive
- **Ghidra**: Java-based, more complex integration
- **Binary Ninja**: Commercial, Python API available

**Recommendations**:
1. Abstract r2pipe behind interface for easy switching
2. Add capability detection (graceful degradation if r2 unavailable)
3. Consider adding Capstone as lightweight fallback for disassembly-only needs
4. Version pin recommended radare2 version
5. Cache r2 analysis results to improve performance

**Proposed Interface**:
```python
class DisassemblyBackend(ABC):
    @abstractmethod
    def analyze(self, path: str) -> AnalysisResult:
        pass

class R2Backend(DisassemblyBackend):
    # Current implementation
    pass

class CapstoneBackend(DisassemblyBackend):
    # Lightweight fallback
    pass
```

---

## 2. Architecture Assessment

### 2.1 Modular Pipeline Design

**Current**: ReconRunner with sequential modules

**Strengths**:
- ✅ Clean separation of concerns
- ✅ Easy to add new modules
- ✅ Consistent data model (ExecutableReport)
- ✅ Each module is independent

**Recommendations for Future**:
1. **Parallel Execution**: Some modules can run in parallel
   ```python
   # Current: Sequential
   for module in self.steps:
       report = module.run(path, report)
   
   # Future: Parallel where possible
   async def run_parallel(self, path: str) -> ExecutableReport:
       # Run independent modules concurrently
       results = await asyncio.gather(
           self.file_info.run(path, report),
           self.strings.run(path, report),
           # ...
       )
   ```

2. **Progress Reporting**: Add progress callbacks for long-running analysis
3. **Cancellation**: Allow users to cancel analysis
4. **Caching**: Cache module results to avoid re-analysis

### 2.2 Data Model (ExecutableReport)

**Current**: Dataclass with all analysis results

**Strengths**:
- ✅ Type-safe with dataclasses
- ✅ Serializable to JSON
- ✅ Extensible via raw_backend_data dict

**Limitations**:
- ⚠️ Can grow very large for big binaries
- ⚠️ All data in memory

**Recommendations**:
1. **Consider**: Database backend for very large reports (optional)
2. **Add**: Lazy loading for large data sections
3. **Add**: Report persistence (save/load analysis)
4. **Add**: Incremental updates to report

```python
# Future: Lazy-loaded sections
@dataclass
class ExecutableReport:
    # ... existing fields ...
    
    _disassembly: Optional[LazySection] = None
    
    @property
    def disassembly(self):
        if self._disassembly is None:
            self._disassembly = self._load_disassembly()
        return self._disassembly
```

### 2.3 Error Handling

**Current**: Try-catch in modules, graceful degradation

**Strengths**:
- ✅ Modules don't crash entire pipeline
- ✅ Missing tools are handled

**Recommendations**:
1. **Add**: Structured logging throughout
2. **Add**: Error collection in report
3. **Add**: Severity levels for errors

```python
@dataclass
class AnalysisError:
    module: str
    severity: str  # warning, error, critical
    message: str
    exception: Optional[Exception] = None

# In ExecutableReport:
errors: List[AnalysisError] = field(default_factory=list)
```

---

## 3. Scalability Concerns

### 3.1 Large Binary Support

**Current Limits**:
- Disassembly truncated at MAX_DISASM_OPS (100-200 instructions)
- Strings truncated at MAX_DISPLAY_STRINGS (1000)
- Functions truncated at MAX_FUNCTIONS (50)

**Issues**:
- ⚠️ Large binaries (>10MB) may be slow to analyze
- ⚠️ Memory usage can be high with full disassembly
- ⚠️ UI can freeze with large data sets

**Recommendations**:
1. **Implement** (High Priority):
   - Streaming analysis (don't load entire binary)
   - Pagination in all views
   - Virtual scrolling in UI
   - Background analysis with progress bar

2. **Add Limits**:
   ```python
   MAX_BINARY_SIZE = 100 * 1024 * 1024  # 100MB
   ANALYSIS_TIMEOUT = 300  # 5 minutes
   MAX_MEMORY_MB = 500
   ```

3. **Sample-Based Analysis**:
   - For very large binaries, analyze samples
   - Focus on entry points, imports, specific sections

### 3.2 Performance Optimization

**Current**: Synchronous, blocking operations

**Recommendations**:
1. **Add async support** for UI responsiveness
2. **Cache analysis results** between runs
3. **Lazy load** large data sections
4. **Profile** and optimize hot paths

**Example Cache Strategy**:
```python
# Cache location: ~/.cache/caspoon/<sha256>.json
def get_cached_report(path: str) -> Optional[ExecutableReport]:
    sha256 = hash_file(path)
    cache_path = CACHE_DIR / f"{sha256}.json"
    if cache_path.exists():
        return ExecutableReport.from_json(cache_path.read_text())
    return None
```

---

## 4. Security Considerations

### 4.1 Analyzing Malicious Binaries

**Concerns**:
- ⚠️ Tool runs on analyst's machine
- ⚠️ Radare2 has had security vulnerabilities
- ⚠️ No sandboxing or isolation

**Recommendations**:
1. **Document**: Clearly warn about analyzing untrusted binaries
2. **Add**: Security checklist in documentation
3. **Consider**: Container/VM instructions
4. **Add**: Resource limits (CPU, memory, time)
5. **Never**: Execute analyzed binaries

**Documentation Addition**:
```markdown
## Security Best Practices

When analyzing potentially malicious binaries:
1. Run caspoon in a VM or container
2. Do not execute the binary
3. Set resource limits
4. Keep radare2 updated
5. Review analysis output for anomalies
```

### 4.2 Input Validation

**Current**: Basic file existence checks

**Recommendations**:
1. **Add**: File size validation before analysis
2. **Add**: File type validation
3. **Add**: Symbolic link handling
4. **Add**: Path traversal prevention

```python
def validate_binary(path: str) -> Tuple[bool, str]:
    """Validate binary before analysis."""
    # Check existence
    if not os.path.exists(path):
        return False, "File not found"
    
    # Check it's a regular file
    if not os.path.isfile(path):
        return False, "Not a regular file"
    
    # Check size
    size = os.path.getsize(path)
    if size > MAX_BINARY_SIZE:
        return False, f"File too large: {size} bytes"
    
    # Check it's actually a binary
    # ... magic number check ...
    
    return True, "OK"
```

---

## 5. Dependency Version Management

### 5.1 Current Issues

**Problem**: No version constraints in dependencies

```toml
# Current pyproject.toml
dependencies = [
  "textual",        # ❌ No version
  "pyelftools",     # ❌ No version
  "r2pipe",         # ❌ No version
  "rich"            # ❌ No version
]
```

**Risks**:
- Breaking changes in dependencies
- Inconsistent behavior across installations
- Difficult to reproduce issues

### 5.2 Recommendations

**Recommended Approach**: Specify minimum versions with flexibility

```toml
# Recommended
dependencies = [
  "textual>=0.40.0,<1.0.0",      # Pin major version
  "pyelftools>=0.29,<1.0",        # Allow minor updates
  "r2pipe>=1.7.0,<2.0.0",         # Pin major version
  "rich>=13.0.0,<14.0.0"          # Pin major version
]

# Or use requirements.txt with exact versions for reproducibility
```

**Create requirements-dev.txt**:
```txt
# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
mypy>=1.0.0
ruff>=0.1.0
```

### 5.3 Testing Strategy

**Add to testing**:
1. **Minimum version tests**: Test with minimum supported versions
2. **Latest version tests**: Test with latest versions
3. **Compatibility matrix**: Test across Python 3.10, 3.11, 3.12

---

## 6. Additional Libraries for Planned Features

Based on implementation plans, recommend adding:

### 6.1 For Pattern Detection (Plan 2)

```toml
# Optional, powerful pattern matching
"yara-python>=4.3.0; extra == 'patterns'",

# For instruction analysis
"capstone>=5.0.0; extra == 'patterns'",

# For Windows PE support
"pefile>=2023.2.7; extra == 'windows'",
```

### 6.2 For Enhanced Analysis

```toml
# For entropy analysis
"scipy>=1.10.0; extra == 'advanced'",

# For graph generation (export)
"networkx>=3.0; extra == 'graphs'",
"matplotlib>=3.7.0; extra == 'graphs'",

# For YARA rules
"yara-python>=4.3.0; extra == 'detection'",
```

### 6.3 For Reporting

```toml
# For HTML report generation
"jinja2>=3.1.0; extra == 'reports'",

# For PDF reports
"weasyprint>=59.0; extra == 'reports'",
```

**Updated pyproject.toml Structure**:
```toml
[project]
name = "caspoon"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
  "textual>=0.40.0,<1.0.0",
  "pyelftools>=0.29,<1.0",
  "r2pipe>=1.7.0,<2.0.0",
  "rich>=13.0.0,<14.0.0"
]

[project.optional-dependencies]
windows = ["pefile>=2023.2.7"]
patterns = ["capstone>=5.0.0", "yara-python>=4.3.0"]
advanced = ["scipy>=1.10.0"]
graphs = ["networkx>=3.0", "matplotlib>=3.7.0"]
reports = ["jinja2>=3.1.0", "weasyprint>=59.0"]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "black>=23.0.0",
  "mypy>=1.0.0",
  "ruff>=0.1.0"
]

# Install all optional features
all = [
  "caspoon[windows]",
  "caspoon[patterns]",
  "caspoon[advanced]",
  "caspoon[graphs]",
  "caspoon[reports]"
]
```

---

## 7. Alternative UI Approaches

### 7.1 Hybrid Approach (Recommended)

Keep Textual for TUI, add complementary interfaces:

1. **TUI (Textual)**: Main interactive interface ✅
   - Fast, terminal-native
   - Good for SSH sessions
   - Keyboard-driven workflow

2. **HTML Reports**: For complex visualizations
   - D3.js for interactive graphs
   - Better for call graphs, CFG
   - Shareable reports

3. **Web UI (Future)**: Optional web-based interface
   - Flask/FastAPI backend
   - React/Vue frontend
   - Better for collaboration
   - More visualization options

**Implementation Priority**:
- Phase 1: Textual TUI (current) ✅
- Phase 2: HTML report export
- Phase 3: Optional web UI (if needed)

### 7.2 Pure GUI Alternatives (Not Recommended)

**Qt (PyQt6/PySide6)**:
- ❌ Loses terminal nature
- ❌ More complex to develop
- ❌ Heavier dependency
- ✅ Better visualization

**Electron**:
- ❌ Not Python-native
- ❌ Very heavy
- ❌ Loses simplicity

**Verdict**: Stick with Textual, augment with HTML reports

---

## 8. Testing Strategy & Infrastructure

### 9.1 Current State: Critical Gap

**Status**: ❌ **NO TESTING INFRASTRUCTURE**

**Observations**:
- ❌ No test directory structure
- ❌ No unit tests
- ❌ No integration tests
- ❌ No CI/CD pipeline
- ❌ No test coverage tracking
- ❌ No automated testing on commits/PRs

**Risk Level**: 🔴 **CRITICAL**

Without tests, future development risks:
- Introducing regressions with new features
- Breaking existing functionality unknowingly
- Difficulty refactoring code safely
- Unable to verify bug fixes
- Reduced confidence in releases
- Harder to onboard contributors

### 9.2 Recommended Testing Architecture

#### 9.2.1 Test Directory Structure

```
caspoon/
├── caspoon/              # Source code
│   ├── core/
│   ├── recon/
│   ├── backends/
│   ├── ui/
│   └── ...
├── tests/                # Test suite (CREATE THIS)
│   ├── __init__.py
│   ├── conftest.py       # Shared fixtures
│   ├── unit/             # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── core/
│   │   │   ├── test_runner.py
│   │   │   └── test_models.py
│   │   ├── recon/
│   │   │   ├── test_file_info.py
│   │   │   ├── test_protections.py
│   │   │   ├── test_strings.py
│   │   │   └── test_imports_exports.py
│   │   ├── backends/
│   │   │   ├── test_r2_analyzer.py
│   │   │   └── test_r2_recon.py
│   │   └── ui/
│   │       ├── test_app.py
│   │       └── views/
│   │           ├── test_overview.py
│   │           ├── test_protections.py
│   │           └── test_r2_view.py
│   ├── integration/      # Integration tests
│   │   ├── __init__.py
│   │   ├── test_full_pipeline.py
│   │   ├── test_recon_chain.py
│   │   └── test_ui_workflows.py
│   ├── fixtures/         # Test binaries and data
│   │   ├── binaries/
│   │   │   ├── test_hello_x64     # Simple x64 binary
│   │   │   ├── test_hello_x86     # 32-bit binary
│   │   │   ├── test_stripped      # Stripped binary
│   │   │   ├── test_with_pie      # PIE enabled
│   │   │   └── README.md          # Fixture documentation
│   │   └── expected/
│   │       └── test_hello_x64.json  # Expected analysis output
│   ├── performance/      # Performance tests
│   │   ├── __init__.py
│   │   ├── test_large_binary.py
│   │   └── benchmarks.py
│   └── e2e/              # End-to-end tests
│       ├── __init__.py
│       ├── test_cli.py
│       └── test_tui.py
├── .github/
│   └── workflows/
│       ├── test.yml      # CI for tests
│       ├── coverage.yml  # Coverage reporting
│       └── release.yml   # Release testing
└── pytest.ini or pyproject.toml  # Pytest configuration
```

#### 9.2.2 Unit Testing Strategy

**Priority**: 🔴 **CRITICAL - Implement First**

**Goal**: Test individual components in isolation

**Example: Testing File Info Recon**
```python
# tests/unit/recon/test_file_info.py
import pytest
from pathlib import Path
from caspoon.recon.file_info import FileInfoRecon
from caspoon.core.models import ExecutableReport

class TestFileInfoRecon:
    """Test FileInfoRecon module."""
    
    @pytest.fixture
    def recon(self):
        """Create FileInfoRecon instance."""
        return FileInfoRecon()
    
    @pytest.fixture
    def test_binary(self, tmp_path):
        """Create a simple test binary."""
        # Copy test binary from fixtures
        import shutil
        src = Path("tests/fixtures/binaries/test_hello_x64")
        dst = tmp_path / "test_binary"
        shutil.copy(src, dst)
        return str(dst)
    
    def test_analyze_x64_binary(self, recon, test_binary):
        """Test analysis of x64 binary."""
        report = ExecutableReport(path=test_binary)
        result = recon.run(test_binary, report)
        
        assert result.arch == "x86-64"
        assert result.bits == 64
        assert result.file_type != ""
    
    def test_analyze_stripped_binary(self, recon):
        """Test detection of stripped binary."""
        binary_path = "tests/fixtures/binaries/test_stripped"
        report = ExecutableReport(path=binary_path)
        result = recon.run(binary_path, report)
        
        assert result.stripped == True
    
    def test_nonexistent_file(self, recon):
        """Test handling of nonexistent file."""
        report = ExecutableReport(path="/nonexistent/file")
        result = recon.run("/nonexistent/file", report)
        
        # Should handle gracefully, not crash
        assert result is not None
    
    def test_invalid_binary(self, recon, tmp_path):
        """Test handling of invalid binary."""
        # Create a text file, not a binary
        invalid = tmp_path / "not_a_binary.txt"
        invalid.write_text("Hello World")
        
        report = ExecutableReport(path=str(invalid))
        result = recon.run(str(invalid), report)
        
        # Should handle gracefully
        assert result is not None
```

**Example: Testing Data Models**
```python
# tests/unit/core/test_models.py
import pytest
from caspoon.core.models import (
    ExecutableReport, ProtectionInfo, FunctionInfo
)

class TestExecutableReport:
    """Test ExecutableReport dataclass."""
    
    def test_create_empty_report(self):
        """Test creating empty report."""
        report = ExecutableReport(path="/test/binary")
        
        assert report.path == "/test/binary"
        assert report.arch == ""
        assert report.bits is None
        assert len(report.strings) == 0
        assert len(report.imports) == 0
        assert len(report.exports) == 0
    
    def test_create_full_report(self):
        """Test creating report with all fields."""
        protections = ProtectionInfo(pie=True, nx=True, canary=True, relro="full")
        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            stripped=False,
            protections=protections,
            strings=["hello", "world"],
            imports=["printf", "exit"]
        )
        
        assert report.arch == "x86-64"
        assert report.bits == 64
        assert report.protections.pie == True
        assert len(report.strings) == 2
    
    def test_pretty_output(self):
        """Test pretty() method returns dict."""
        report = ExecutableReport(path="/test", arch="x86-64", bits=64)
        pretty = report.pretty()
        
        assert isinstance(pretty, dict)
        assert pretty["path"] == "/test"
        assert pretty["arch"] == "x86-64"
        assert pretty["bits"] == 64

class TestProtectionInfo:
    """Test ProtectionInfo dataclass."""
    
    def test_default_protections(self):
        """Test default protection values."""
        pi = ProtectionInfo()
        
        assert pi.pie == False
        assert pi.nx == False
        assert pi.canary == False
        assert pi.relro == "Unknown"
    
    def test_full_protections(self):
        """Test fully protected binary."""
        pi = ProtectionInfo(pie=True, nx=True, canary=True, relro="full")
        
        assert pi.pie == True
        assert pi.nx == True
        assert pi.canary == True
        assert pi.relro == "full"
```

**Example: Testing Backend**
```python
# tests/unit/backends/test_r2_analyzer.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from caspoon.backends.r2_analyzer import analyze_with_r2

class TestR2Analyzer:
    """Test radare2 analyzer backend."""
    
    @pytest.fixture
    def mock_r2pipe(self):
        """Mock r2pipe module."""
        with patch('caspoon.backends.r2_analyzer.r2pipe') as mock:
            yield mock
    
    def test_analyze_with_r2_success(self, mock_r2pipe):
        """Test successful r2 analysis."""
        # Setup mock
        mock_r2 = MagicMock()
        mock_r2.cmd.side_effect = [
            None,  # aa command
            '[{"offset": 4194304, "name": "main"}]',  # aflj
            '[{"name": "printf"}]',  # isj
            '[{"string": "Hello"}]',  # izj
            '[{"offset": 4194304, "opcode": "push rbp"}]'  # pdj
        ]
        mock_r2pipe.open.return_value = mock_r2
        
        # Run analysis
        result = analyze_with_r2("/test/binary")
        
        # Verify results
        assert 'functions' in result
        assert 'imports' in result
        assert 'strings' in result
        assert 'main_ops' in result
        assert len(result['functions']) == 1
        assert result['functions'][0]['name'] == 'main'
    
    def test_analyze_with_r2_json_error(self, mock_r2pipe):
        """Test handling of JSON parsing errors."""
        mock_r2 = MagicMock()
        mock_r2.cmd.side_effect = [
            None,  # aa command
            'invalid json{',  # aflj - bad JSON
            '[]',  # isj
            '[]',  # izj
            '[]'   # pdj
        ]
        mock_r2pipe.open.return_value = mock_r2
        
        # Should handle gracefully
        result = analyze_with_r2("/test/binary")
        
        assert 'functions' in result
        assert len(result['functions']) == 0  # Empty due to parse error
    
    @pytest.mark.skipif(
        not pytest.importorskip("r2pipe"),
        reason="r2pipe not installed"
    )
    def test_real_binary_analysis(self):
        """Integration test with real r2 (if available)."""
        # This test requires actual radare2 installation
        result = analyze_with_r2("tests/fixtures/binaries/test_hello_x64")
        
        assert 'functions' in result
        assert 'imports' in result
        # At minimum, should find main function
        assert any(f.get('name') == 'main' for f in result['functions'])
```

#### 9.2.3 Integration Testing Strategy

**Priority**: 🟡 **HIGH - Implement After Unit Tests**

**Goal**: Test component interactions and full pipeline

**Example: Testing Full Pipeline**
```python
# tests/integration/test_full_pipeline.py
import pytest
from caspoon.core.runner import ReconRunner
from caspoon.core.models import ExecutableReport

class TestFullPipeline:
    """Test complete analysis pipeline."""
    
    @pytest.fixture
    def runner(self):
        """Create ReconRunner instance."""
        return ReconRunner()
    
    def test_analyze_simple_binary(self, runner):
        """Test full analysis of simple binary."""
        binary_path = "tests/fixtures/binaries/test_hello_x64"
        report = runner.run(binary_path)
        
        # Verify all recon modules ran
        assert report.path == binary_path
        assert report.arch != ""  # FileInfoRecon ran
        assert report.protections is not None  # ProtectionsRecon ran
        assert len(report.strings) > 0  # StringsRecon ran
        assert len(report.imports) > 0  # ImportExportRecon ran
        assert 'r2' in report.raw_backend_data  # R2BackendRecon ran
    
    def test_analyze_stripped_binary(self, runner):
        """Test analysis of stripped binary."""
        binary_path = "tests/fixtures/binaries/test_stripped"
        report = runner.run(binary_path)
        
        assert report.stripped == True
        # Stripped binaries should still provide some analysis
        assert report.arch != ""
        assert report.protections is not None
    
    def test_analyze_pie_binary(self, runner):
        """Test analysis of PIE-enabled binary."""
        binary_path = "tests/fixtures/binaries/test_with_pie"
        report = runner.run(binary_path)
        
        assert report.protections.pie == True
    
    def test_recon_modules_order(self, runner):
        """Test that recon modules run in correct order."""
        # Verify module order
        module_names = [step.name for step in runner.steps]
        
        # FileInfo should be first (provides basic info)
        assert module_names[0] == "file_info"
        # Protections should be early
        assert "protections" in module_names
        # R2 backend should be last (most expensive)
        assert module_names[-1] == "r2_backend"
```

**Example: Testing Recon Chain**
```python
# tests/integration/test_recon_chain.py
import pytest
from caspoon.core.models import ExecutableReport
from caspoon.recon.file_info import FileInfoRecon
from caspoon.recon.protections import ProtectionsRecon
from caspoon.recon.strings_mod import StringsRecon

class TestReconChain:
    """Test recon modules work together."""
    
    def test_sequential_enrichment(self):
        """Test that report is enriched through chain."""
        binary_path = "tests/fixtures/binaries/test_hello_x64"
        report = ExecutableReport(path=binary_path)
        
        # Initially empty
        assert report.arch == ""
        assert report.protections is None
        assert len(report.strings) == 0
        
        # FileInfo enriches arch/bits
        report = FileInfoRecon().run(binary_path, report)
        assert report.arch != ""
        assert report.bits is not None
        
        # Protections enriches security info
        report = ProtectionsRecon().run(binary_path, report)
        assert report.protections is not None
        
        # Strings enriches string list
        report = StringsRecon().run(binary_path, report)
        assert len(report.strings) > 0
```

#### 9.2.4 UI Testing Strategy

**Priority**: 🟡 **MEDIUM - After Core Tests**

**Goal**: Test UI components and interactions

**Example: Testing UI Views**
```python
# tests/unit/ui/views/test_overview.py
import pytest
from caspoon.ui.views.overview import OverviewView
from caspoon.core.models import ExecutableReport

class TestOverviewView:
    """Test OverviewView component."""
    
    def test_update_with_full_report(self):
        """Test updating view with complete report."""
        view = OverviewView()
        report = ExecutableReport(
            path="/test/binary",
            arch="x86-64",
            bits=64,
            stripped=False,
            file_type="ELF 64-bit LSB executable"
        )
        
        # Should not raise exception
        view.update_data(report)
    
    def test_update_with_minimal_report(self):
        """Test updating view with minimal data."""
        view = OverviewView()
        report = ExecutableReport(path="/test/binary")
        
        # Should handle missing data gracefully
        view.update_data(report)
```

**Example: Testing TUI with Textual's pilot**
```python
# tests/e2e/test_tui.py
import pytest
from textual.pilot import Pilot
from caspoon.ui.app import CaspoonApp

@pytest.mark.asyncio
async def test_app_launches():
    """Test that app launches without errors."""
    app = CaspoonApp()
    async with app.run_test() as pilot:
        # App should be running
        assert app.is_running
        
        # Should have expected widgets
        assert pilot.app.query_one("#path_input") is not None

@pytest.mark.asyncio
async def test_load_binary(tmpdir):
    """Test loading a binary through the UI."""
    app = CaspoonApp()
    async with app.run_test() as pilot:
        # Enter path and submit
        await pilot.click("#path_input")
        await pilot.press("t", "e", "s", "t")
        await pilot.press("enter")
        
        # Should see status update
        # (actual verification depends on implementation)
```

#### 9.2.5 Performance Testing Strategy

**Priority**: 🟢 **LOW - After Feature Complete**

**Goal**: Ensure performance doesn't degrade

**Example: Performance Tests**
```python
# tests/performance/benchmarks.py
import pytest
import time
from caspoon.core.runner import ReconRunner

class TestPerformance:
    """Performance benchmarks."""
    
    @pytest.mark.benchmark
    def test_small_binary_analysis_time(self, benchmark):
        """Benchmark analysis of small binary (<1MB)."""
        runner = ReconRunner()
        binary = "tests/fixtures/binaries/test_hello_x64"
        
        result = benchmark(runner.run, binary)
        
        # Should complete in reasonable time
        assert result is not None
    
    @pytest.mark.slow
    def test_large_binary_analysis(self):
        """Test analysis of large binary (10MB+)."""
        runner = ReconRunner()
        # Create or use large test binary
        
        start = time.time()
        report = runner.run("tests/fixtures/binaries/large_binary")
        elapsed = time.time() - start
        
        # Should complete within timeout
        assert elapsed < 60  # 60 seconds max
    
    def test_memory_usage_bounded(self):
        """Test memory usage doesn't exceed limits."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        runner = ReconRunner()
        runner.run("tests/fixtures/binaries/test_hello_x64")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Should not use excessive memory
        assert memory_increase < 500  # < 500MB increase
```

#### 9.2.6 Test Fixtures & Data Management

**Priority**: 🔴 **CRITICAL**

**Goal**: Maintain consistent test data

**Strategy**:
1. **Source-controlled test binaries**: Small, purpose-built binaries
2. **Documented fixtures**: README explaining each test binary
3. **Expected outputs**: JSON files with expected analysis results
4. **Build scripts**: Scripts to regenerate test binaries if needed

**Example: Fixture Documentation**
```markdown
# tests/fixtures/binaries/README.md

## Test Binary Fixtures

### test_hello_x64
- **Architecture**: x86-64
- **Size**: ~16KB
- **Source**: hello_world.c compiled with GCC
- **Features**: Standard ELF, not stripped, PIE disabled
- **Purpose**: Basic functionality testing

### test_hello_x86
- **Architecture**: x86 (32-bit)
- **Size**: ~14KB
- **Source**: hello_world.c compiled with GCC -m32
- **Features**: 32-bit ELF
- **Purpose**: Test 32-bit support

### test_stripped
- **Architecture**: x86-64
- **Size**: ~14KB
- **Source**: hello_world.c compiled with GCC -s
- **Features**: Symbols stripped
- **Purpose**: Test stripped binary detection

### test_with_pie
- **Architecture**: x86-64
- **Features**: PIE enabled, stack canary, NX, full RELRO
- **Purpose**: Test security feature detection

### Regenerating Binaries

```bash
# Regenerate test binaries
cd tests/fixtures/binaries/src
make clean
make all
```
```

**Example: Build Script**
```makefile
# tests/fixtures/binaries/src/Makefile
CC=gcc
CFLAGS=-Wall

all: test_hello_x64 test_hello_x86 test_stripped test_with_pie

test_hello_x64: hello_world.c
	$(CC) $(CFLAGS) -o ../test_hello_x64 hello_world.c

test_hello_x86: hello_world.c
	$(CC) $(CFLAGS) -m32 -o ../test_hello_x86 hello_world.c

test_stripped: hello_world.c
	$(CC) $(CFLAGS) -s -o ../test_stripped hello_world.c

test_with_pie: hello_world.c
	$(CC) $(CFLAGS) -fPIE -pie -fstack-protector-all -Wl,-z,relro,-z,now \
		-o ../test_with_pie hello_world.c

clean:
	rm -f ../test_hello_x64 ../test_hello_x86 ../test_stripped ../test_with_pie
```

#### 9.2.7 Continuous Integration Setup

**Priority**: 🔴 **CRITICAL**

**Goal**: Automated testing on every commit

**GitHub Actions Configuration**:
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y radare2 binutils
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run linters
      run: |
        ruff check caspoon/
        black --check caspoon/
    
    - name: Run type checker
      run: |
        mypy caspoon/ --ignore-missing-imports
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov=caspoon --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  test-e2e:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y radare2
        pip install -e .[dev]
    
    - name: Run E2E tests
      run: |
        pytest tests/e2e -v

  test-performance:
    name: Performance Tests
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt-get install -y radare2
        pip install -e .[dev]
        pip install pytest-benchmark
    
    - name: Run performance tests
      run: |
        pytest tests/performance -v --benchmark-only
```

#### 9.2.8 Test Coverage Goals

**Priority**: 🟡 **HIGH**

**Target Coverage Levels**:
- **Core modules** (models, runner): 95%+ coverage
- **Recon modules**: 85%+ coverage
- **Backend integrations**: 70%+ coverage (due to external dependencies)
- **UI components**: 60%+ coverage (UI testing is harder)
- **Overall project**: 75%+ coverage

**Coverage Tracking**:
```bash
# Generate coverage report
pytest --cov=caspoon --cov-report=html --cov-report=term

# View in browser
open htmlcov/index.html
```

**Coverage Configuration**:
```ini
# .coveragerc or pyproject.toml
[tool.coverage.run]
source = ["caspoon"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

#### 9.2.9 Testing Best Practices for Future Development

**For All New Features**:
1. ✅ **Write tests first** (TDD when possible)
2. ✅ **Aim for 80%+ coverage** for new code
3. ✅ **Include edge cases** in tests
4. ✅ **Mock external dependencies** (r2pipe, file system)
5. ✅ **Test error conditions** not just happy paths
6. ✅ **Use fixtures** for consistent test data
7. ✅ **Keep tests fast** (<1 second per unit test)
8. ✅ **Make tests deterministic** (no random behavior)

**Testing Checklist for PRs**:
```markdown
- [ ] Unit tests added for new functions/classes
- [ ] Integration tests updated if workflow changed
- [ ] Tests pass locally
- [ ] Coverage doesn't decrease
- [ ] Performance tests pass (if applicable)
- [ ] CI pipeline passes
- [ ] Edge cases covered
- [ ] Error handling tested
```

#### 9.2.10 Test Maintenance Strategy

**Regular Maintenance**:
1. **Review test suite monthly** for:
   - Flaky tests (intermittent failures)
   - Slow tests (>5 seconds)
   - Outdated fixtures
   - Redundant tests

2. **Update test binaries** when:
   - Toolchain versions change
   - New architectures added
   - Security features evolve

3. **Refactor tests** when:
   - Multiple tests have duplicate code
   - Fixtures become complex
   - Test readability suffers

**Test Documentation**:
```python
# Good test documentation example
def test_analyze_malformed_elf(self, runner):
    """Test analysis of malformed ELF binary.
    
    This tests the error handling when encountering a binary with:
    - Invalid ELF magic number
    - Corrupted section headers
    
    Expected behavior:
    - Should not crash
    - Should return report with error information
    - Should continue with other analysis steps
    
    Related issue: #42
    """
    # Test implementation
```

### 9.3 Testing Tool Recommendations

**Core Testing Stack**:
- ✅ **pytest**: Test framework (industry standard)
- ✅ **pytest-cov**: Coverage reporting
- ✅ **pytest-asyncio**: For async tests
- ✅ **pytest-mock**: Mocking utilities
- ✅ **pytest-benchmark**: Performance testing

**Additional Tools**:
- **hypothesis**: Property-based testing
- **tox**: Test across Python versions
- **pytest-xdist**: Parallel test execution
- **pytest-timeout**: Prevent hanging tests

**Update dependencies**:
```toml
[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "pytest-asyncio>=0.21.0",
  "pytest-mock>=3.10.0",
  "pytest-benchmark>=4.0.0",
  "pytest-xdist>=3.0.0",  # Parallel testing
  "pytest-timeout>=2.1.0",  # Test timeouts
  "hypothesis>=6.0.0",  # Property-based testing
  "tox>=4.0.0",  # Multi-version testing
  "black>=23.0.0",
  "mypy>=1.0.0",
  "ruff>=0.1.0",
  "types-pyelftools",
]
```

### 9.4 Testing Implementation Roadmap

**Phase 1: Foundation (Week 1-2)**
- [ ] Create test directory structure
- [ ] Set up pytest configuration
- [ ] Create test fixtures (binaries)
- [ ] Set up CI pipeline (GitHub Actions)
- [ ] Add coverage tracking

**Phase 2: Core Tests (Week 2-4)**
- [ ] Write unit tests for models
- [ ] Write unit tests for core/runner
- [ ] Write unit tests for each recon module
- [ ] Aim for 70%+ coverage of core

**Phase 3: Integration Tests (Week 4-5)**
- [ ] Test full pipeline
- [ ] Test module interactions
- [ ] Test error propagation

**Phase 4: UI Tests (Week 5-6)**
- [ ] Test view components
- [ ] Test app integration
- [ ] Basic E2E tests

**Phase 5: Advanced Testing (Week 6+)**
- [ ] Performance benchmarks
- [ ] Property-based tests
- [ ] Fuzz testing for parsers

**Minimum Viable Test Suite** (for starting implementation):
1. ✅ Unit tests for ExecutableReport
2. ✅ Unit tests for FileInfoRecon
3. ✅ Integration test for basic pipeline
4. ✅ CI pipeline running on PRs
5. ✅ Coverage reporting

### 9.5 Testing Anti-Patterns to Avoid

❌ **Don't**:
- Write tests that depend on external services
- Test implementation details instead of behavior
- Make tests dependent on execution order
- Use sleep() for timing (use proper mocking)
- Commit commented-out tests
- Skip tests without explanation
- Test external library behavior

✅ **Do**:
- Test public interfaces and contracts
- Make tests independent and isolated
- Use clear, descriptive test names
- Mock external dependencies
- Keep tests maintainable and readable
- Document why tests are skipped
- Focus on your code's behavior

---

## 9. Documentation Needs

### 9.1 Current Documentation

**Exists**:
- ✅ Excellent OVERVIEW.md
- ✅ Good inline code documentation

**Missing**:
- ⚠️ API documentation
- ⚠️ User guide
- ⚠️ Installation instructions
- ⚠️ Contribution guidelines
- ⚠️ Example workflows

### 9.2 Recommended Documentation Structure

```
caspoon/docs/
├── OVERVIEW.md (exists) ✅
├── README.md (exists in root?)
├── INSTALLATION.md (needed)
├── USER_GUIDE.md (needed)
├── API_REFERENCE.md (needed)
├── CONTRIBUTING.md (needed)
├── ARCHITECTURE.md (enhance current OVERVIEW)
├── SECURITY.md (needed)
├── plans/ (this effort) ✅
│   ├── 01-syntax-highlighting/
│   ├── 02-pattern-detection/
│   └── 03-syscall-api-detection/
└── examples/
    ├── basic_usage.md
    ├── custom_module.md
    └── advanced_features.md
```

---

## 10. Summary & Roadmap

### 10.1 Immediate Actions (Before Implementation)

1. **Add version constraints** to dependencies ⚠️ HIGH PRIORITY
2. **Set up testing framework** (pytest) 🔴 CRITICAL PRIORITY
3. **Create test fixtures** and basic test suite 🔴 CRITICAL PRIORITY
4. **Add basic CI/CD** (GitHub Actions) 🔴 CRITICAL PRIORITY
5. **Abstract r2pipe** behind interface for future flexibility

### 10.2 During Implementation

1. **Write tests first** for all new features (TDD approach)
2. **Monitor Textual** for new features that could help
3. **Implement pagination** early for all views
4. **Add caching** for analysis results
5. **Create HTML export** for complex visualizations
6. **Add optional dependencies** as features are implemented
7. **Maintain 75%+ test coverage** throughout development

### 10.3 Future Considerations (Post-Plans 1-3)

1. **Evaluate** web UI need after TUI is feature-complete
2. **Consider** adding Capstone as lightweight disassembly fallback
3. **Add** pefile and macholib for Windows/macOS support
4. **Implement** database backend for large binary caching
5. **Build** plugin system for third-party extensions

### 10.4 Risk Mitigation Priority

| Risk | Priority | Action |
|------|----------|--------|
| No testing infrastructure | CRITICAL | Implement comprehensive test suite |
| Textual performance with large data | HIGH | Implement pagination/lazy loading |
| Dependency version conflicts | HIGH | Add version constraints |
| Test coverage gaps | HIGH | Aim for 75%+ coverage |
| radare2 API changes | MEDIUM | Abstract r2 interactions |
| Large binary analysis | MEDIUM | Add resource limits, caching |
| Security issues | MEDIUM | Document best practices |
| Missing graph visualization | LOW | Plan HTML export alternative |

---

## 11. Conclusion

**Overall Assessment**: ✅ **READY TO PROCEED WITH CAUTION**

The current caspoon architecture and dependencies are well-suited for the planned enhancements, but **testing infrastructure must be established first**:

**Strengths**:
- ✅ Solid modular architecture
- ✅ Appropriate library choices for core functionality
- ✅ Modern Python practices
- ✅ Clean, maintainable code

**Critical Gaps**:
- 🔴 **No testing infrastructure** - MUST BE ADDRESSED FIRST
- ⚠️ No dependency version constraints
- ⚠️ No CI/CD pipeline
- ⚠️ No type checking

**Areas for Improvement**:
- ⚠️ Add dependency version constraints (CRITICAL)
- ⚠️ Implement testing and CI/CD (CRITICAL - BLOCKING)
- ⚠️ Plan for UI performance (pagination, lazy loading)
- ⚠️ Consider HTML export for complex visualizations

**Recommendation**: 

**STOP** - Do not proceed with feature implementation until basic testing infrastructure is in place. The following must be completed first:

1. **Week 1**: Set up testing infrastructure
   - Create test directory structure
   - Add pytest configuration
   - Set up CI/CD pipeline
   - Create initial test fixtures

2. **Week 2**: Create minimum viable test suite
   - Unit tests for core models
   - Unit tests for at least one recon module
   - One integration test for basic pipeline
   - Achieve 50%+ coverage baseline

3. **Week 3+**: Proceed with feature implementation
   - Use TDD for all new features
   - Maintain/improve test coverage
   - Add integration tests for each major feature

Without testing, the risk of introducing regressions and breaking changes is too high. The modular architecture is excellent, but it needs test coverage to ensure that modularity is maintained as features are added.

**Bottom Line**: The architectural foundation is solid, but testing infrastructure is the critical missing piece that will enable confident, sustainable development of the planned features.

---

## Appendix A: Testing Implementation Checklist

**Before Starting Any Feature Implementation**:
- [ ] Create `tests/` directory structure
- [ ] Set up `pytest.ini` or pytest config in `pyproject.toml`
- [ ] Create test fixtures directory with sample binaries
- [ ] Set up GitHub Actions CI workflow
- [ ] Add coverage reporting with codecov
- [ ] Write first unit test (even if trivial)
- [ ] Verify CI pipeline runs successfully
- [ ] Document testing practices in CONTRIBUTING.md

**Minimum Test Suite (MVP)**:
- [ ] Test ExecutableReport creation and methods
- [ ] Test ProtectionInfo dataclass
- [ ] Test FileInfoRecon with sample binary
- [ ] Test ReconRunner basic pipeline
- [ ] One integration test for full analysis
- [ ] Achieve 50%+ code coverage
- [ ] All tests pass in CI

**Once MVP Testing is Complete**:
- [ ] Add tests for remaining recon modules
- [ ] Add UI component tests
- [ ] Add performance benchmarks
- [ ] Achieve 75%+ code coverage
- [ ] Ready to proceed with feature implementation

---

## Appendix B: Recommended pyproject.toml Updates

```toml
[project]
name = "caspoon"
version = "0.1.0"
description = "Caspoon Reverse Engineering Toolkit"
authors = [
  { name = "LosEvons" }
]
requires-python = ">=3.10"
readme = "README.md"
license = { text = "MIT" }  # Update as appropriate

dependencies = [
  "textual>=0.40.0,<1.0.0",
  "pyelftools>=0.29,<1.0",
  "r2pipe>=1.7.0,<2.0.0",
  "rich>=13.0.0,<14.0.0"
]

[project.optional-dependencies]
windows = ["pefile>=2023.2.7"]
patterns = ["capstone>=5.0.0", "yara-python>=4.3.0"]
advanced = ["scipy>=1.10.0"]
graphs = ["networkx>=3.0"]
reports = ["jinja2>=3.1.0"]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "pytest-asyncio>=0.21.0",
  "black>=23.0.0",
  "mypy>=1.0.0",
  "ruff>=0.1.0",
  "types-pyelftools"
]
all = [
  "pefile>=2023.2.7",
  "capstone>=5.0.0",
  "yara-python>=4.3.0",
  "scipy>=1.10.0",
  "networkx>=3.0",
  "jinja2>=3.1.0"
]

[project.scripts]
caspoon = "caspoon.main:main"

[project.urls]
Homepage = "https://github.com/LosEvons/spoons16"
Repository = "https://github.com/LosEvons/spoons16"
Documentation = "https://github.com/LosEvons/spoons16/tree/main/caspoon/docs"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Enable gradually
```

---

**End of Report**
