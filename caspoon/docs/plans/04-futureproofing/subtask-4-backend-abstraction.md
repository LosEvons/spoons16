# Subtask 4: Backend Abstraction Layer

## Objective
Create an abstraction layer for backend integrations (radare2, etc.) to allow easy switching between backends and graceful degradation when tools are unavailable.

## Priority
🟢 **MEDIUM - Optional, can be deferred**

## Scope
- Create abstract backend interface
- Refactor r2_analyzer to use interface
- Add capability detection
- Enable graceful fallback

## Prerequisites
- None (independent task)

## Implementation Steps

### Step 1: Create Backend Interface (1 hour)

**File**: `caspoon/backends/base.py`

```python
"""Abstract base class for disassembly backends."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class BackendCapabilities:
    """Capabilities of a backend."""
    name: str
    disassembly: bool = False
    analysis: bool = False
    functions: bool = False
    imports: bool = False
    strings: bool = False
    xrefs: bool = False


class DisassemblyBackend(ABC):
    """Abstract base for disassembly backends."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        """Return backend capabilities."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on system."""
        pass
    
    @abstractmethod
    def analyze(self, path: str) -> Dict[str, Any]:
        """Analyze binary and return results."""
        pass
    
    def get_functions(self, path: str) -> List[Dict]:
        """Get functions from binary."""
        if not self.capabilities.functions:
            return []
        return self.analyze(path).get('functions', [])
    
    def get_imports(self, path: str) -> List[Dict]:
        """Get imports from binary."""
        if not self.capabilities.imports:
            return []
        return self.analyze(path).get('imports', [])
```

### Step 2: Refactor R2 Backend (45 minutes)

**File**: `caspoon/backends/r2_backend.py` (new)

```python
"""Radare2 backend implementation."""
import logging
from typing import Dict, Any
from .base import DisassemblyBackend, BackendCapabilities
from .r2_analyzer import analyze_with_r2

logger = logging.getLogger(__name__)


class Radare2Backend(DisassemblyBackend):
    """Radare2 disassembly backend."""
    
    @property
    def name(self) -> str:
        return "radare2"
    
    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name="radare2",
            disassembly=True,
            analysis=True,
            functions=True,
            imports=True,
            strings=True,
            xrefs=True,
        )
    
    def is_available(self) -> bool:
        """Check if radare2 is available."""
        try:
            import r2pipe
            # Try to open a test connection
            r2 = r2pipe.open('-')
            r2.quit()
            return True
        except Exception as e:
            logger.debug(f"radare2 not available: {e}")
            return False
    
    def analyze(self, path: str) -> Dict[str, Any]:
        """Analyze binary with radare2."""
        return analyze_with_r2(path)
```

### Step 3: Create Backend Manager (1 hour)

**File**: `caspoon/backends/manager.py`

```python
"""Backend manager for selecting appropriate backend."""
import logging
from typing import Optional, List
from .base import DisassemblyBackend
from .r2_backend import Radare2Backend

logger = logging.getLogger(__name__)


class BackendManager:
    """Manages disassembly backends."""
    
    def __init__(self):
        self._backends: List[DisassemblyBackend] = [
            Radare2Backend(),
            # Future: CapstoneBackend(), GhidraBackend(), etc.
        ]
        self._preferred_backend: Optional[str] = None
    
    def get_available_backends(self) -> List[DisassemblyBackend]:
        """Get list of available backends."""
        return [b for b in self._backends if b.is_available()]
    
    def get_backend(self, name: Optional[str] = None) -> Optional[DisassemblyBackend]:
        """Get backend by name, or first available."""
        if name:
            for backend in self._backends:
                if backend.name == name and backend.is_available():
                    return backend
            logger.warning(f"Backend '{name}' not available")
            return None
        
        # Return first available backend
        available = self.get_available_backends()
        if available:
            return available[0]
        
        logger.error("No backends available")
        return None
    
    def set_preferred_backend(self, name: str):
        """Set preferred backend."""
        self._preferred_backend = name
```

### Step 4: Update R2 Recon Module (30 minutes)

**File**: `caspoon/backends/r2_recon.py` (update)

```python
"""R2 backend recon module."""
import logging
from ..core.models import ExecutableReport
from .manager import BackendManager

logger = logging.getLogger(__name__)


class R2BackendRecon:
    """Radare2 backend reconnaissance."""
    name = "r2_backend"
    
    def __init__(self):
        self.manager = BackendManager()
    
    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run radare2 analysis."""
        backend = self.manager.get_backend("radare2")
        
        if not backend:
            logger.warning("radare2 backend not available, skipping")
            report.raw_backend_data["r2_error"] = "radare2 not available"
            return report
        
        try:
            result = backend.analyze(path)
            report.raw_backend_data["r2"] = result
            logger.info(f"radare2 analysis completed: {len(result.get('functions', []))} functions")
        except Exception as e:
            logger.error(f"radare2 analysis failed: {e}")
            report.raw_backend_data["r2_error"] = str(e)
        
        return report
```

### Step 5: Add Tests (45 minutes)

**File**: `caspoon/tests/unit/backends/test_backend_abstraction.py`

```python
"""Tests for backend abstraction."""
import pytest
from caspoon.backends.base import BackendCapabilities
from caspoon.backends.r2_backend import Radare2Backend
from caspoon.backends.manager import BackendManager


class TestBackendCapabilities:
    """Test BackendCapabilities."""
    
    def test_create_capabilities(self):
        caps = BackendCapabilities(
            name="test",
            disassembly=True,
            analysis=True
        )
        assert caps.name == "test"
        assert caps.disassembly is True
        assert caps.analysis is True


class TestRadare2Backend:
    """Test Radare2Backend."""
    
    def test_backend_name(self):
        backend = Radare2Backend()
        assert backend.name == "radare2"
    
    def test_capabilities(self):
        backend = Radare2Backend()
        caps = backend.capabilities
        assert caps.name == "radare2"
        assert caps.disassembly is True
        assert caps.functions is True


class TestBackendManager:
    """Test BackendManager."""
    
    def test_manager_creation(self):
        manager = BackendManager()
        assert manager is not None
    
    def test_get_available_backends(self):
        manager = BackendManager()
        backends = manager.get_available_backends()
        # Should be list (may be empty if r2 not installed)
        assert isinstance(backends, list)
```

## Testing Strategy

- Unit tests for abstract base
- Unit tests for R2 backend
- Integration tests with backend manager
- Mock unavailable backends

## Success Criteria

- [ ] Backend abstract base class exists
- [ ] Radare2Backend implements interface
- [ ] BackendManager can select backends
- [ ] Graceful fallback when r2 unavailable
- [ ] Tests pass
- [ ] Documentation updated

## Estimated Time
**3-4 hours total**

## Deliverables
- Backend abstraction interface
- Refactored r2 backend
- Backend manager
- Updated recon module
- Tests for new code
