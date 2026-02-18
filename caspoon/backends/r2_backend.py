"""Radare2 backend implementation."""

import logging
import shutil
from typing import Any

from .base import BackendCapabilities, DisassemblyBackend
from .r2_analyzer import analyze_with_r2

logger = logging.getLogger(__name__)


class Radare2Backend(DisassemblyBackend):
    """Radare2 disassembly backend."""

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "radare2"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Return the backend capabilities."""
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
        """Check if radare2 and r2pipe are available."""
        try:
            import r2pipe  # noqa: F401
        except ImportError:
            return False
        return shutil.which("r2") is not None or shutil.which("radare2") is not None

    def analyze(self, path: str) -> dict[str, Any]:
        """Analyze binary with radare2."""
        return analyze_with_r2(path)
