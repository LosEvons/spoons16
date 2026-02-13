# Subtask 7: Optional Dependencies Structure

## Status: ✅ COMPLETED (Minimal Implementation)

## Objective
Properly structure optional dependencies for future features without requiring them for basic usage.

## Priority
🟢 **LOW - Can be deferred**

## Implementation Summary

**What was implemented:**
- ✅ Created `caspoon/utils/capabilities.py` with capability detection
- ✅ Added `--capabilities` CLI flag to `main.py`
- ✅ Created comprehensive unit tests in `tests/unit/utils/test_capabilities.py`
- ✅ All tests passing (8 new tests, 132 total tests passing)
- ✅ Code quality validated with ruff

**What was kept minimal:**
- Simple detection-only implementation
- No complex conditional import helpers (deferred)
- No extensive documentation file (code is self-documenting)
- Fast and lightweight detection

## Scope
- Organize optional dependency groups
- Add capability detection
- Document when to use each group
- Create conditional imports

## Prerequisites
- Subtask 3 completed (version management)

## Implementation Steps

### Step 1: Review Optional Dependencies (Already Done)

This was largely completed in Subtask 3. Verify `pyproject.toml` has:

```toml
[project.optional-dependencies]
windows = ["pefile>=2023.2.7,<2024.0.0"]
patterns = ["capstone>=5.0.0,<6.0.0", "yara-python>=4.3.0,<5.0.0"]
advanced = ["scipy>=1.10.0,<2.0.0"]
graphs = ["networkx>=3.0,<4.0"]
reports = ["jinja2>=3.1.0,<4.0.0"]
dev = [...]
all = [...]
```

### Step 2: Create Capability Detection Module (45 minutes)

**File**: `caspoon/utils/capabilities.py`

```python
"""Detect available optional features."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class Capabilities:
    """Detect which optional features are available."""
    
    def __init__(self):
        self._capabilities: Dict[str, bool] = {}
        self._detect_all()
    
    def _detect_all(self):
        """Detect all capabilities."""
        self._capabilities = {
            'windows_pe': self._check_pefile(),
            'patterns': self._check_patterns(),
            'yara': self._check_yara(),
            'advanced_math': self._check_scipy(),
            'graphs': self._check_networkx(),
            'reports': self._check_jinja2(),
            'radare2': self._check_r2pipe(),
        }
    
    def _check_pefile(self) -> bool:
        """Check if pefile is available."""
        try:
            import pefile
            return True
        except ImportError:
            return False
    
    def _check_patterns(self) -> bool:
        """Check if capstone is available."""
        try:
            import capstone
            return True
        except ImportError:
            return False
    
    def _check_yara(self) -> bool:
        """Check if yara is available."""
        try:
            import yara
            return True
        except ImportError:
            return False
    
    def _check_scipy(self) -> bool:
        """Check if scipy is available."""
        try:
            import scipy
            return True
        except ImportError:
            return False
    
    def _check_networkx(self) -> bool:
        """Check if networkx is available."""
        try:
            import networkx
            return True
        except ImportError:
            return False
    
    def _check_jinja2(self) -> bool:
        """Check if jinja2 is available."""
        try:
            import jinja2
            return True
        except ImportError:
            return False
    
    def _check_r2pipe(self) -> bool:
        """Check if r2pipe is available."""
        try:
            import r2pipe
            # Try to create a connection
            r2 = r2pipe.open('-')
            r2.quit()
            return True
        except Exception:
            return False
    
    def has(self, capability: str) -> bool:
        """Check if a capability is available."""
        return self._capabilities.get(capability, False)
    
    def get_all(self) -> Dict[str, bool]:
        """Get all capabilities."""
        return self._capabilities.copy()
    
    def get_missing(self) -> List[str]:
        """Get list of missing capabilities."""
        return [k for k, v in self._capabilities.items() if not v]
    
    def print_summary(self):
        """Print capability summary."""
        print("Caspoon Capabilities:")
        for cap, available in sorted(self._capabilities.items()):
            status = "✓" if available else "✗"
            print(f"  {status} {cap}")


# Global instance
_capabilities = None


def get_capabilities() -> Capabilities:
    """Get global capabilities instance."""
    global _capabilities
    if _capabilities is None:
        _capabilities = Capabilities()
    return _capabilities
```

### Step 3: Add Conditional Imports Helper (30 minutes)

**File**: `caspoon/utils/imports.py`

```python
"""Helper for conditional imports."""
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def try_import(module_name: str, feature_name: str = None) -> Optional[Any]:
    """Try to import a module, return None if not available.
    
    Args:
        module_name: Name of module to import
        feature_name: Optional feature name for logging
        
    Returns:
        Imported module or None
    """
    try:
        return __import__(module_name)
    except ImportError as e:
        if feature_name:
            logger.debug(f"{feature_name} not available: {module_name} not installed")
        else:
            logger.debug(f"Optional module {module_name} not available")
        return None


class OptionalImport:
    """Context manager for optional imports."""
    
    def __init__(self, module_name: str, feature_name: str = None):
        self.module_name = module_name
        self.feature_name = feature_name or module_name
        self.module = None
    
    def __enter__(self):
        self.module = try_import(self.module_name, self.feature_name)
        return self.module
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ImportError:
            logger.info(f"{self.feature_name} feature not available")
            return True  # Suppress ImportError
        return False


# Usage examples:
# 
# # Simple import
# pefile = try_import('pefile', 'Windows PE support')
# if pefile:
#     # Use pefile
#     pass
# 
# # Context manager
# with OptionalImport('yara', 'YARA patterns') as yara:
#     if yara:
#         # Use yara
#         pass
```

### Step 4: Update Documentation (30 minutes)

**File**: `caspoon/docs/OPTIONAL_FEATURES.md`

```markdown
# Optional Features

Caspoon supports optional features that require additional dependencies.

## Core vs Optional

### Core Features (Always Available)
- Basic file analysis
- ELF file parsing
- String extraction
- Security protection detection
- TUI interface
- CLI interface

### Optional Features (Require Additional Dependencies)
- Windows PE file support
- Pattern detection
- YARA rule scanning
- Advanced analysis (entropy, etc.)
- Graph generation
- HTML report generation

## Installing Optional Features

### Individual Feature Groups

```bash
# Windows PE support
pip install caspoon[windows]

# Pattern detection (capstone, yara)
pip install caspoon[patterns]

# Advanced analysis (scipy)
pip install caspoon[advanced]

# Graph generation (networkx)
pip install caspoon[graphs]

# Report generation (jinja2)
pip install caspoon[reports]
```

### Multiple Features

```bash
# Windows + patterns
pip install caspoon[windows,patterns]

# All optional features
pip install caspoon[all]
```

## Feature Capabilities

### Windows PE Support (`windows`)
- **Dependencies**: pefile
- **Enables**: Analysis of Windows executables
- **When to use**: Analyzing .exe, .dll files
- **Install**: `pip install caspoon[windows]`

### Pattern Detection (`patterns`)
- **Dependencies**: capstone, yara-python
- **Enables**: 
  - Advanced instruction analysis
  - YARA rule scanning
  - Pattern matching
- **When to use**: Malware analysis, pattern detection
- **Install**: `pip install caspoon[patterns]`
- **Note**: yara-python may require libyara-dev

### Advanced Analysis (`advanced`)
- **Dependencies**: scipy
- **Enables**:
  - Entropy analysis
  - Statistical analysis
  - Advanced math operations
- **When to use**: Packed binary detection, statistical analysis
- **Install**: `pip install caspoon[advanced]`

### Graph Generation (`graphs`)
- **Dependencies**: networkx
- **Enables**:
  - Call graph generation
  - Control flow graphs
  - Dependency graphs
- **When to use**: Visualizing code structure
- **Install**: `pip install caspoon[graphs]`

### Report Generation (`reports`)
- **Dependencies**: jinja2
- **Enables**:
  - HTML report generation
  - Custom report templates
- **When to use**: Sharing analysis results
- **Install**: `pip install caspoon[reports]`

## Checking Available Features

### Command Line

```bash
# Check capabilities
python -m caspoon --capabilities
```

### Programmatically

```python
from caspoon.utils.capabilities import get_capabilities

caps = get_capabilities()
caps.print_summary()

# Check specific capability
if caps.has('windows_pe'):
    print("Windows PE support available")

# Get all capabilities
all_caps = caps.get_all()
print(f"Available features: {[k for k, v in all_caps.items() if v]}")
```

## Graceful Degradation

Caspoon handles missing optional dependencies gracefully:

1. **Feature Detection**: Checks if dependencies are available
2. **Conditional Execution**: Skips unavailable features
3. **User Notification**: Warns about missing features
4. **No Crashes**: Never crashes due to missing optional deps

### Example

```python
# This works even without pefile installed
from caspoon.core.runner import ReconRunner

runner = ReconRunner()
report = runner.run("some_binary.exe")

# PE-specific analysis will be skipped if pefile not installed
# Other analysis continues normally
```

## Troubleshooting

### Issue: Optional dependency won't install

#### yara-python
**Problem**: Build fails
**Solution**: Install system dependencies
```bash
# Ubuntu/Debian
sudo apt-get install libyara-dev

# macOS
brew install yara
```

#### pefile
**Problem**: Import error
**Solution**: Usually works without issues, try reinstalling
```bash
pip uninstall pefile
pip install pefile
```

#### scipy
**Problem**: Build fails
**Solution**: Install system BLAS/LAPACK libraries
```bash
# Ubuntu/Debian
sudo apt-get install libopenblas-dev liblapack-dev

# macOS
brew install openblas lapack
```

### Issue: Feature not available after install
**Solution**: Reinstall in correct environment
```bash
# Ensure in correct venv
which python

# Reinstall
pip install --force-reinstall caspoon[feature]

# Verify
python -c "import feature_module; print('OK')"
```

## Development

When adding new optional features:

1. Add dependency to pyproject.toml optional-dependencies
2. Add detection to `utils/capabilities.py`
3. Use conditional imports in code
4. Update this documentation
5. Add tests (with skip if not available)

## Future Optional Features

Planned optional dependencies:
- `binary_ninja`: Binary Ninja Python API
- `ghidra`: Ghidra bridge
- `angr`: Symbolic execution
- `z3`: SMT solver
```

### Step 5: Add Capability Check to CLI (Optional, 30 minutes)

**File**: `caspoon/main.py` (add option)

```python
def main():
    parser = argparse.ArgumentParser(description="Caspoon RE Toolkit")
    parser.add_argument("binary", nargs="?", help="Binary to analyze")
    parser.add_argument("--ui", action="store_true", help="Launch TUI")
    parser.add_argument("--capabilities", action="store_true", 
                       help="Show available capabilities")
    # ... other arguments
    
    args = parser.parse_args()
    
    if args.capabilities:
        from caspoon.utils.capabilities import get_capabilities
        caps = get_capabilities()
        caps.print_summary()
        return 0
    
    # ... rest of main
```

## Testing Strategy

- Test with and without optional deps
- Verify graceful degradation
- Test capability detection
- Mock missing dependencies

## Success Criteria

- [ ] Optional dependencies properly structured in pyproject.toml
- [ ] Capability detection module exists
- [ ] Conditional import helpers available
- [ ] OPTIONAL_FEATURES.md documentation
- [ ] CLI capability check command
- [ ] Tests pass with and without optional deps
- [ ] No crashes from missing optional deps

## Estimated Time
**2 hours total**

## Deliverables
- Capability detection system
- Conditional import helpers
- Documentation for optional features
- CLI capability checking
