"""Radare2 backend reconnaissance module."""

import logging
from typing import Optional

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)


def _try_import_r2pipe() -> bool:
    """Check if r2pipe is available.
    
    Returns:
        True if r2pipe can be imported, False otherwise
    """
    try:
        import r2pipe
        return True
    except ImportError:
        return False


class R2BackendRecon:
    """Radare2 backend integration for deep binary analysis.
    
    Uses r2pipe to perform radare2 analysis including function detection,
    import analysis, string extraction, and disassembly.
    """
    
    name = "r2_backend"

    def __init__(self) -> None:
        """Initialize the radare2 backend module."""
        self.r2_available: bool = _try_import_r2pipe()
        if not self.r2_available:
            logger.warning("r2pipe not available. Radare2 analysis will be skipped.")

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run radare2 analysis.
        
        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with r2 analysis
            
        Returns:
            Updated ExecutableReport with r2 backend data
        """
        if not self.r2_available:
            logger.info("Skipping radare2 analysis (r2pipe not installed)")
            report.raw_backend_data["r2_error"] = "r2pipe not installed"
            return report

        from .r2_analyzer import analyze_with_r2

        try:
            logger.debug(f"Starting radare2 analysis on {path}")
            data = analyze_with_r2(path)
            report.raw_backend_data["r2"] = data
            logger.info("Radare2 analysis completed successfully")
        except FileNotFoundError as e:
            logger.error(f"File not found during r2 analysis: {e}")
            report.raw_backend_data["r2_error"] = f"File not found: {str(e)}"
        except ImportError as e:
            logger.error(f"r2pipe import error: {e}")
            report.raw_backend_data["r2_error"] = f"Import error: {str(e)}"
        except Exception as e:
            logger.error(f"Error during radare2 analysis: {e}")
            report.raw_backend_data["r2_error"] = str(e)

        return report
