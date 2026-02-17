"""File information reconnaissance module."""

import logging
import os
import subprocess

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)

# Configuration
FILE_CMD_TIMEOUT = 10  # Timeout for file command in seconds

# Architecture patterns for detection
ARCH_PATTERNS: dict[str, str] = {
    "x86-64": "x86_64",
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "x86": "x86",
    "i386": "x86",
    "i686": "x86",
    "ARM": "ARM",
    "aarch64": "ARM64",
    "MIPS": "MIPS",
    "PowerPC": "PowerPC",
}


class FileInfoRecon:
    """Extracts basic file information using the 'file' command.

    Analyzes the executable to determine architecture, bit width,
    file type, and whether debug symbols are stripped.
    """

    name = "file_info"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run file information reconnaissance.

        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with file information

        Returns:
            Updated ExecutableReport with file information
        """
        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            report.file_type = "Error: File not found"
            return report

        if not os.path.isfile(path):
            logger.error(f"Path is not a file: {path}")
            report.file_type = "Error: Not a file"
            return report

        try:
            result = subprocess.run(
                ["file", path],
                capture_output=True,
                text=True,
                timeout=FILE_CMD_TIMEOUT,
            )

            if result.returncode != 0:
                logger.error(f"'file' command failed with return code {result.returncode}")
                report.file_type = "Error: file command failed"
                return report

            output = result.stdout.strip()
            report.file_type = output

            # Detect architecture more robustly
            report.arch = self._detect_architecture(output)

            # Detect bit width
            if "64-bit" in output:
                report.bits = 64
            elif "32-bit" in output:
                report.bits = 32
            else:
                report.bits = None  # Unknown bit width

            # Check if stripped
            report.stripped = "not stripped" not in output.lower()

        except FileNotFoundError:
            logger.error("'file' command not found. Please install it.")
            report.file_type = "Error: 'file' command not available"
        except subprocess.TimeoutExpired:
            logger.error(f"'file' command timed out on {path}")
            report.file_type = "Error: Timeout"
        except Exception as e:
            logger.error(f"Unexpected error in FileInfoRecon: {e}")
            report.file_type = f"Error: {str(e)}"

        return report

    def _detect_architecture(self, file_output: str) -> str:
        """Detect architecture from file command output.

        Args:
            file_output: Output from the 'file' command

        Returns:
            Detected architecture name or "Unknown"
        """
        file_lower = file_output.lower()

        for pattern, arch in ARCH_PATTERNS.items():
            if pattern.lower() in file_lower:
                return arch

        logger.warning(f"Could not detect architecture from: {file_output}")
        return "Unknown"
