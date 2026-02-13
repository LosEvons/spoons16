"""Shared test fixtures and configuration.

This module provides pytest configuration and shared fixtures for all tests.
"""

from collections.abc import Generator
from pathlib import Path

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden test files with current output",
    )


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to fixtures directory.

    Returns:
        Path to the test fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_binaries_dir(fixtures_dir: Path) -> Path:
    """Return path to test binaries directory.

    Args:
        fixtures_dir: Path to fixtures directory.

    Returns:
        Path to the test binaries directory.
    """
    return fixtures_dir / "binaries"


@pytest.fixture
def sample_binary(test_binaries_dir: Path) -> str:
    """Return path to a sample test binary for testing.

    Uses system 'ls' binary if available, otherwise falls back to
    test_hello_x64 from test fixtures.

    Args:
        test_binaries_dir: Path to test binaries directory.

    Returns:
        String path to a usable test binary.

    Raises:
        pytest.skip: If no suitable binary is available.
    """
    from shutil import which

    ls_path = which("ls")
    if ls_path:
        return ls_path

    # Fallback to test binary once created
    test_bin = test_binaries_dir / "test_hello_x64"
    if test_bin.exists():
        return str(test_bin)

    pytest.skip("No test binary available")
