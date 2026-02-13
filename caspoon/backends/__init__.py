"""Backend integrations for deep binary analysis tools."""

from .base import BackendCapabilities, DisassemblyBackend
from .r2_backend import Radare2Backend
from .manager import BackendManager
from .r2_recon import R2BackendRecon

__all__ = [
    "BackendCapabilities",
    "DisassemblyBackend",
    "Radare2Backend",
    "BackendManager",
    "R2BackendRecon",
]