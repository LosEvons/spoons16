"""Command-line entry point for Caspoon."""

import sys

try:
    from .main import main
except ImportError as e:
    print("\nError: Failed to import required modules.", file=sys.stderr)
    print(f"  {e}", file=sys.stderr)
    print("\nPlease install caspoon with:", file=sys.stderr)
    print("    pip install -e .", file=sys.stderr)
    print("\nOr with development dependencies:", file=sys.stderr)
    print('    pip install -e ".[dev]"', file=sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
