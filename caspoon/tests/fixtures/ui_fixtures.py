"""Reusable fixtures for UI testing.

This module provides pytest fixtures for testing TUI components:
- Mock data models (BinaryInfo, AnalysisResults, ExecutableReport)
- Mock AppState instances
- Test app instances
"""

import pytest

from caspoon.core.models import ExecutableReport, ProtectionInfo
from caspoon.ui.core.models import AnalysisResults, BinaryInfo
from caspoon.ui.core.state import AppState


@pytest.fixture
def mock_binary_info() -> BinaryInfo:
    """Create a realistic BinaryInfo for testing.

    Returns:
        BinaryInfo with typical values for a Linux ELF binary
    """
    return BinaryInfo(
        path="/usr/bin/test_binary",
        architecture="x86_64",
        bits=64,
        file_type="ELF 64-bit LSB executable, x86-64, version 1 (SYSV)",
        stripped=False,
        file_size=23456,
        entry_point="0x401000",
    )


@pytest.fixture
def mock_binary_info_stripped() -> BinaryInfo:
    """Create a BinaryInfo for a stripped binary.

    Returns:
        BinaryInfo for a stripped executable
    """
    return BinaryInfo(
        path="/bin/stripped_binary",
        architecture="ARM",
        bits=32,
        file_type="ELF 32-bit LSB executable, ARM",
        stripped=True,
        file_size=12345,
        entry_point=None,
    )


@pytest.fixture
def mock_analysis_results() -> AnalysisResults:
    """Create realistic AnalysisResults for testing.

    Returns:
        AnalysisResults with typical protection values
    """
    return AnalysisResults(
        functions=["main", "init", "fini"],
        strings=["Hello, World!", "/lib/ld-linux.so.2", "Usage: %s"],
        imports=["printf", "malloc", "free", "exit"],
        exports=["main"],
        sections=[".text", ".data", ".bss", ".rodata"],
        protections={
            "pie": True,
            "nx": True,
            "canary": True,
            "relro": "full",
        },
        disassembly=None,
    )


@pytest.fixture
def mock_analysis_results_no_protections() -> AnalysisResults:
    """Create AnalysisResults with no protections enabled.

    Returns:
        AnalysisResults with all protections disabled
    """
    return AnalysisResults(
        functions=["main"],
        strings=["test"],
        imports=["printf"],
        exports=[],
        sections=[".text"],
        protections={
            "pie": False,
            "nx": False,
            "canary": False,
            "relro": "none",
        },
        disassembly=None,
    )


@pytest.fixture
def mock_executable_report() -> ExecutableReport:
    """Create a complete ExecutableReport for testing.

    Returns:
        ExecutableReport with full structure
    """
    return ExecutableReport(
        path="/usr/bin/test_binary",
        arch="x86_64",
        bits=64,
        file_type="ELF 64-bit LSB executable, x86-64, version 1 (SYSV)",
        stripped=False,
        protections=ProtectionInfo(
            pie=True,
            nx=True,
            canary=True,
            relro="full",
        ),
        strings=["Hello, World!", "/lib/ld-linux.so.2", "Usage: %s"],
        imports=["printf", "malloc", "free", "exit"],
        exports=["main"],
        raw_backend_data={},
    )


@pytest.fixture
def mock_executable_report_stripped() -> ExecutableReport:
    """Create an ExecutableReport for a stripped binary.

    Returns:
        ExecutableReport for a stripped, unprotected binary
    """
    return ExecutableReport(
        path="/bin/stripped_binary",
        arch="ARM",
        bits=32,
        file_type="ELF 32-bit LSB executable, ARM",
        stripped=True,
        protections=ProtectionInfo(
            pie=False,
            nx=False,
            canary=False,
            relro="none",
        ),
        strings=["test"],
        imports=["printf"],
        exports=[],
        raw_backend_data={},
    )


@pytest.fixture
def mock_app_state() -> AppState:
    """Create a fresh AppState instance for testing.

    Returns:
        Empty AppState ready for use
    """
    return AppState()


@pytest.fixture
def mock_app_state_loaded(
    mock_binary_info: BinaryInfo, mock_analysis_results: AnalysisResults
) -> AppState:
    """Create an AppState with data already loaded.

    Args:
        mock_binary_info: Binary info fixture
        mock_analysis_results: Analysis results fixture

    Returns:
        AppState with binary and analysis data populated
    """
    state = AppState()
    state.binary_info = mock_binary_info
    state.analysis_results = mock_analysis_results
    return state


@pytest.fixture
def empty_protections_dict() -> dict:
    """Create an empty protections dictionary.

    Returns:
        Empty dict (for testing empty state handling)
    """
    return {}


@pytest.fixture
def full_protections_dict() -> dict:
    """Create a protections dict with all protections enabled.

    Returns:
        Dict with all protections set to True/"full"
    """
    return {
        "pie": True,
        "nx": True,
        "canary": True,
        "relro": "full",
    }


@pytest.fixture
def no_protections_dict() -> dict:
    """Create a protections dict with all protections disabled.

    Returns:
        Dict with all protections set to False/"none"
    """
    return {
        "pie": False,
        "nx": False,
        "canary": False,
        "relro": "none",
    }


@pytest.fixture
def partial_protections_dict() -> dict:
    """Create a protections dict with mixed protection levels.

    Returns:
        Dict with some protections enabled, some disabled
    """
    return {
        "pie": True,
        "nx": True,
        "canary": False,
        "relro": "partial",
    }
