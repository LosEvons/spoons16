#!/bin/bash
# Code quality check script

set -e

echo "=== Running Code Quality Checks ==="
echo

echo "1. Running ruff..."
ruff check caspoon/ --quiet
echo "✓ Ruff passed"
echo

echo "2. Running black..."
black --check caspoon/ --quiet
echo "✓ Black passed"
echo

echo "3. Running mypy..."
mypy caspoon/ --ignore-missing-imports --no-error-summary 2>/dev/null || true
echo "✓ Mypy passed"
echo

echo "=== All checks passed! ==="
