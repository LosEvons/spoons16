"""Main entry point for the Caspoon reverse engineering toolkit."""

import json
import logging
import os
import sys

from caspoon.core.runner import ReconRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_file_path(path: str) -> bool:
    """Validate that the provided path is a valid file.
    
    Args:
        path: File path to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    if not path:
        logger.error("Empty path provided")
        return False
        
    # Resolve to absolute path
    abs_path = os.path.abspath(path)
    
    # Check if file exists
    if not os.path.exists(abs_path):
        logger.error(f"File does not exist: {abs_path}")
        return False
        
    # Check if it's a file (not a directory)
    if not os.path.isfile(abs_path):
        logger.error(f"Path is not a file: {abs_path}")
        return False
        
    # Check if file is readable
    if not os.access(abs_path, os.R_OK):
        logger.error(f"File is not readable: {abs_path}")
        return False
        
    return True


def main() -> None:
    """Main entry point for the application."""
    if "--ui" in sys.argv:
        from caspoon.ui.app import CaspoonApp
        try:
            CaspoonApp().run()
        except Exception as e:
            logger.error(f"Error running UI: {e}")
            sys.exit(1)
        return

    if len(sys.argv) < 2:
        print("Usage: python -m caspoon <binary>  or  python -m caspoon --ui")
        sys.exit(1)

    path = sys.argv[1]
    
    # Validate the file path
    if not validate_file_path(path):
        sys.exit(1)
    
    # Use absolute path for consistency
    abs_path = os.path.abspath(path)
    
    try:
        logger.info(f"Analyzing binary: {abs_path}")
        runner = ReconRunner()
        report = runner.run(abs_path)
        
        # Output the report
        output = report.raw_backend_data.get("r2", {})
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)