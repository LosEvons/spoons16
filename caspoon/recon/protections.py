"""Security protections reconnaissance module."""

import logging
import subprocess

from ..core.models import ExecutableReport, ProtectionInfo

logger = logging.getLogger(__name__)


class ProtectionsRecon:
    """Analyzes security protections using the 'checksec' tool.

    Detects security features including PIE, NX, stack canary, and RELRO.
    """

    name = "protections"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run protections reconnaissance.

        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with protection information

        Returns:
            Updated ExecutableReport with protection information
        """
        try:
            result = subprocess.run(
                ["checksec", "--file", path], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                logger.warning(
                    f"checksec returned non-zero exit code {result.returncode}. "
                    f"stderr: {result.stderr.strip() if result.stderr else 'none'}"
                )
                report.protections = ProtectionInfo(relro="checksec_error")
                return report

            output = result.stdout

        except FileNotFoundError:
            logger.warning("'checksec' command not found. Protection detection unavailable.")
            report.protections = ProtectionInfo(relro="checksec_not_found")
            return report
        except subprocess.TimeoutExpired:
            logger.error(f"'checksec' command timed out on {path}")
            report.protections = ProtectionInfo(relro="checksec_timeout")
            return report
        except Exception as e:
            logger.error(f"Unexpected error in ProtectionsRecon: {e}")
            report.protections = ProtectionInfo(relro=f"error: {str(e)}")
            return report

        pi = ProtectionInfo()

        pi.pie = "PIE enabled" in output
        pi.nx = "NX enabled" in output
        pi.canary = "Canary found" in output

        if "Full RELRO" in output:
            pi.relro = "full"
        elif "Partial RELRO" in output:
            pi.relro = "partial"
        else:
            pi.relro = "none"

        report.protections = pi
        return report
