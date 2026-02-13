"""Radare2 backend reconnaissance module."""

import logging
from typing import Optional

from ..core.models import ExecutableReport
from .manager import BackendManager

logger = logging.getLogger(__name__)


class R2BackendRecon:
    """Radare2 backend integration for deep binary analysis.
    
    Uses the backend manager to perform radare2 analysis including function detection,
    import analysis, string extraction, and disassembly.
    """
    
    name = "r2_backend"

    def __init__(self) -> None:
        """Initialize the radare2 backend module."""
        self.manager = BackendManager()

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run radare2 analysis.
        
        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with r2 analysis
            
        Returns:
            Updated ExecutableReport with r2 backend data
        """
        backend = self.manager.get_backend("radare2")
        
        if not backend:
            logger.warning("radare2 backend not available, skipping")
            report.raw_backend_data["r2_error"] = "radare2 not available"
            return report
        
        try:
            logger.debug(f"Starting radare2 analysis on {path}")
            result = backend.analyze(path)
            report.raw_backend_data["r2"] = result
            logger.info(f"radare2 analysis completed: {len(result.get('functions', []))} functions")
        except FileNotFoundError as e:
            logger.error(f"File not found during r2 analysis: {e}")
            report.raw_backend_data["r2_error"] = f"File not found: {str(e)}"
        except Exception as e:
            logger.error(f"Error during radare2 analysis: {e}")
            report.raw_backend_data["r2_error"] = str(e)
        
        return report
