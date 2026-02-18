"""Radare2 backend implementation."""

import logging
import shutil
import sys
from typing import Any

from .base import BackendCapabilities, DisassemblyBackend
from .r2_analyzer import analyze_with_r2

logger = logging.getLogger(__name__)


def _radare2_install_hint() -> str:
    """Return a platform-specific install hint for the radare2 binary."""
    if sys.platform == "win32":
        return (
            "Install radare2 with:\n"
            "    scoop install radare2\n"
            "    Download: https://rada.re/n/radare2.html"
        )
    elif sys.platform == "darwin":
        return "Install radare2 with:\n    brew install radare2"
    else:
        return (
            "Install radare2 with:\n"
            "    apt install radare2   (or)   snap install radare2"
        )


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
        """Check if radare2 is available.

        Distinguishes between two failure modes:
          1. r2pipe Python package not installed — solvable via pip
          2. radare2 binary missing from PATH — requires system install
        """
        try:
            import r2pipe  # noqa: F401
        except ImportError:
            logger.warning(
                "r2pipe Python package not installed. Run: pip install r2pipe"
            )
            return False

        # Optionally hint r2pipe toward the binary; don't gate on this.
        import os

        r2_bin = shutil.which("radare2") or shutil.which("r2")
        if r2_bin:
            os.environ.setdefault("R2PIPE_EXECUTABLE", r2_bin)

        try:
            r2 = r2pipe.open("-")
            r2.quit()
            return True
        except Exception as e:
            logger.warning(
                f"radare2 not available ({e}). "
                + _radare2_install_hint()
            )
            return False

    def analyze(self, path: str) -> dict[str, Any]:
        """Analyze binary with radare2."""
        return analyze_with_r2(path)
