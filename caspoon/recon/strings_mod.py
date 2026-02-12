"""String extraction reconnaissance module."""

import logging
import subprocess
from typing import List

from ..core.models import ExecutableReport

logger = logging.getLogger(__name__)

# Configuration
MIN_STRING_LENGTH = 4
MAX_STRINGS = 10000  # Limit to prevent memory issues


class StringsRecon:
    """Extracts printable strings from the executable.
    
    Uses the 'strings' command to extract human-readable strings
    from the binary file.
    """
    
    name = "strings"

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        """Run string extraction reconnaissance.
        
        Args:
            path: Path to the executable file
            report: ExecutableReport to enrich with extracted strings
            
        Returns:
            Updated ExecutableReport with strings list
        """
        try:
            result = subprocess.run(
                ["strings", "-n", str(MIN_STRING_LENGTH), path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"'strings' command returned non-zero exit code: {result.returncode}")
                return report
                
            strings_list = result.stdout.splitlines()
            
            # Limit the number of strings to prevent memory issues
            if len(strings_list) > MAX_STRINGS:
                logger.warning(f"String count ({len(strings_list)}) exceeds limit. Truncating to {MAX_STRINGS}")
                strings_list = strings_list[:MAX_STRINGS]
            
            report.strings = strings_list
            
        except FileNotFoundError:
            logger.error("'strings' command not found. Please install it.")
            report.strings = []
        except subprocess.TimeoutExpired:
            logger.error(f"'strings' command timed out on {path}")
            report.strings = []
        except Exception as e:
            logger.error(f"Unexpected error in StringsRecon: {e}")
            report.strings = []
            
        return report
