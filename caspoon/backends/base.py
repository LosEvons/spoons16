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
