"""Reconnaissance runner that orchestrates analysis pipeline."""

import logging

from ..backends.r2_recon import R2BackendRecon
from ..recon.file_info import FileInfoRecon
from ..recon.imports_exports import ImportExportRecon
from ..recon.protections import ProtectionsRecon
from ..recon.strings_mod import StringsRecon
from .models import ExecutableReport

logger = logging.getLogger(__name__)


class ReconRunner:
    """Orchestrates the execution of multiple reconnaissance modules.

    The runner maintains a pipeline of recon modules and executes them
    sequentially, passing the ExecutableReport through each step.
    """

    def __init__(self) -> None:
        """Initialize the runner with the default pipeline of recon modules."""
        self.steps: list = [
            FileInfoRecon(),
            ProtectionsRecon(),
            StringsRecon(),
            ImportExportRecon(),
            R2BackendRecon(),
        ]

    def run(self, path: str) -> ExecutableReport:
        """Execute all reconnaissance modules on the target executable.

        Args:
            path: Path to the executable file to analyze

        Returns:
            ExecutableReport containing all analysis results

        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        report = ExecutableReport(path=path)

        for step in self.steps:
            logger.debug(f"Running step: {step.name}")
            try:
                report = step.run(path, report)
            except Exception as e:
                logger.error(f"Error in step {step.name}: {e}")
                # Continue with other steps even if one fails

        return report
