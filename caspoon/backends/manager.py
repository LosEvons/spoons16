"""Backend manager for selecting appropriate backend."""

import logging

from .base import DisassemblyBackend
from .r2_backend import Radare2Backend

logger = logging.getLogger(__name__)


class BackendManager:
    """Manages disassembly backends."""

    def __init__(self):
        self._backends: list[DisassemblyBackend] = [
            Radare2Backend(),
            # Future: CapstoneBackend(), GhidraBackend(), etc.
        ]
        self._preferred_backend: str | None = None

    def get_available_backends(self) -> list[DisassemblyBackend]:
        """Get list of available backends."""
        return [b for b in self._backends if b.is_available()]

    def get_backend(self, name: str | None = None) -> DisassemblyBackend | None:
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
