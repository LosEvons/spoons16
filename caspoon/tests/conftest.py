"""Shared test fixtures and configuration."""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_binaries_dir(fixtures_dir):
    """Return path to test binaries directory."""
    return fixtures_dir / "binaries"


@pytest.fixture
def sample_binary(test_binaries_dir):
    """Return path to a sample test binary."""
    # Will use system binary initially, then custom test binary
    from shutil import which
    ls_path = which("ls")
    if ls_path:
        return ls_path
    # Fallback to test binary once created
    test_bin = test_binaries_dir / "test_hello_x64"
    if test_bin.exists():
        return str(test_bin)
    pytest.skip("No test binary available")
