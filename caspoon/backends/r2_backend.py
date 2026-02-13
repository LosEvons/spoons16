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
