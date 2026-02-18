"""Main entry point for the Caspoon reverse engineering toolkit."""

import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


def _check_dependencies() -> None:
    """Check if required dependencies are installed."""
    missing_deps = []
    try:
        import elftools  # noqa: F401
    except ImportError:
        missing_deps.append("pyelftools")
    try:
        import rich  # noqa: F401
    except ImportError:
        missing_deps.append("rich")
    if missing_deps:
        print("\nError: Missing required dependencies:", file=sys.stderr)
        print(f"  {', '.join(missing_deps)}", file=sys.stderr)
        print("\nPlease install caspoon with:", file=sys.stderr)
        print("    pip install caspoon", file=sys.stderr)
        print("\nOr with development dependencies:", file=sys.stderr)
        print('    pip install "caspoon[dev]"', file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)


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
    # Check dependencies early to provide helpful error messages
    _check_dependencies()

    # Import after dependency check to avoid confusing errors
    from caspoon.core.runner import ReconRunner

    # Handle special flags first
    if "--capabilities" in sys.argv:
        # Configure logging for CLI mode
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        from caspoon.utils.capabilities import get_capabilities

        try:
            caps = get_capabilities()
            caps.print_summary()
        except Exception as e:
            logger.error(f"Error checking capabilities: {e}")
            sys.exit(1)
        return

    if "--gui" in sys.argv:
        # Qt GUI — logging to stderr is fine (doesn't conflict with Qt)
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        try:
            from caspoon.gui.app import run_gui  # noqa: PLC0415
        except ImportError:
            print(
                "\nError: PySide6 is not installed. Install the GUI extra:\n"
                '    pip install "caspoon[gui]"',
                file=sys.stderr,
            )
            sys.exit(1)

        run_gui()
        return

    # Configure logging for CLI mode
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m caspoon <binary>         # Analyze a binary (CLI/JSON output)")
        print("  python -m caspoon --gui            # Launch Qt GUI interface")
        print("  python -m caspoon --capabilities   # Show available optional features")
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
