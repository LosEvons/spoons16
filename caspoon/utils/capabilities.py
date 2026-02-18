"""Detect available optional features."""

import logging
import shutil
import sys
import threading

logger = logging.getLogger(__name__)


def _radare2_install_hint() -> str:
    """Return a platform-specific install hint for the radare2 binary."""
    if sys.platform == "win32":
        return (
            "winget install radare2   (or)   choco install radare2\n"
            "    Download: https://rada.re/n/radare2.html"
        )
    elif sys.platform == "darwin":
        return "brew install radare2"
    else:
        return "apt install radare2   (or)   snap install radare2"


class Capabilities:
    """Detect which optional features are available."""

    def __init__(self):
        """Initialize and detect all capabilities."""
        self._capabilities: dict[str, bool] = {}
        self._detect_all()

    def _detect_all(self):
        """Detect all optional capabilities."""
        self._capabilities = {
            "radare2": self._check_radare2(),
            "windows_pe": self._check_pefile(),
            "capstone": self._check_capstone(),
            "yara": self._check_yara(),
            "advanced_math": self._check_scipy(),
            "graphs": self._check_networkx(),
            "reports": self._check_jinja2(),
        }

    def _check_radare2(self) -> bool:
        """Check if both the r2pipe package and radare2 binary are available."""
        try:
            import r2pipe  # noqa: F401
        except ImportError:
            return False
        # Accept either 'radare2' or the legacy 'r2' executable name
        return (shutil.which("radare2") is not None) or (shutil.which("r2") is not None)

    def _check_pefile(self) -> bool:
        """Check if pefile is available for Windows PE analysis."""
        try:
            import pefile  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_capstone(self) -> bool:
        """Check if capstone is available for disassembly."""
        try:
            import capstone  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_yara(self) -> bool:
        """Check if yara-python is available for pattern matching."""
        try:
            import yara  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_scipy(self) -> bool:
        """Check if scipy is available for advanced math."""
        try:
            import scipy  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_networkx(self) -> bool:
        """Check if networkx is available for graph generation."""
        try:
            import networkx  # noqa: F401

            return True
        except ImportError:
            return False

    def _check_jinja2(self) -> bool:
        """Check if jinja2 is available for report generation."""
        try:
            import jinja2  # noqa: F401

            return True
        except ImportError:
            return False

    def has(self, capability: str) -> bool:
        """Check if a specific capability is available.

        Args:
            capability: Name of the capability to check

        Returns:
            True if capability is available, False otherwise
        """
        return self._capabilities.get(capability, False)

    def get_all(self) -> dict[str, bool]:
        """Get all capabilities and their availability status.

        Returns:
            Dictionary mapping capability names to availability
        """
        return self._capabilities.copy()

    def get_missing(self) -> list[str]:
        """Get list of missing capabilities.

        Returns:
            List of capability names that are not available
        """
        return [k for k, v in self._capabilities.items() if not v]

    def print_summary(self):
        """Print a formatted summary of all capabilities."""
        print("\nCaspoon Optional Features:")
        print("=" * 50)

        for cap, available in sorted(self._capabilities.items()):
            status = "✓ Available  " if available else "✗ Not installed"
            print(f"  {status} - {cap}")

        missing = self.get_missing()
        if missing:
            print("\nTo install missing features:")

            if "radare2" in missing:
                print("\n  radare2 (system binary — not pip-installable):")
                print(f"    {_radare2_install_hint()}")

            pip_missing = [m for m in missing if m != "radare2"]
            if pip_missing:
                print("\n  Python packages:")
                print("    pip install caspoon[all]")
                print("\n  Or install specific features:")
                print("    pip install caspoon[windows]   # Windows PE support")
                print("    pip install caspoon[patterns]  # capstone + yara")
                print("    pip install caspoon[advanced]  # scipy")
                print("    pip install caspoon[graphs]    # networkx")
                print("    pip install caspoon[reports]   # jinja2")
        else:
            print("\n✓ All optional features are installed!")


# Global singleton instance
_capabilities = None
_capabilities_lock = threading.Lock()


def get_capabilities() -> Capabilities:
    """Get the global capabilities instance (singleton).

    Thread-safe lazy initialization of the global Capabilities instance.

    Returns:
        Capabilities instance
    """
    global _capabilities
    if _capabilities is None:
        with _capabilities_lock:
            if _capabilities is None:
                _capabilities = Capabilities()
    return _capabilities
