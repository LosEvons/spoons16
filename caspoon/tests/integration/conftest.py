"""Shared fixtures for integration tests."""

import pytest
from textual.app import App

from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.core.state import AppState


@pytest.fixture
def app_with_state():
    """Create a test app with AppState.

    Returns:
        App instance with initialized AppState
    """

    class TestApp(App):
        """Test application with AppState."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.state = AppState()

    return TestApp()


@pytest.fixture
def mock_analysis_results():
    """Create mock analysis results for testing.

    Returns:
        AnalysisResults with sample data including xrefs
    """
    return AnalysisResults(
        functions=[
            {"name": "main", "address": 0x401000, "size": 256, "section": ".text"},
            {"name": "sub_401100", "address": 0x401100, "size": 128, "section": ".text"},
            {"name": "printf", "address": 0x402000, "size": 64, "section": ".plt"},
        ],
        strings=["Hello, World!", "Error: %s", "Success"],
        imports=["printf", "malloc", "free"],
        exports=["main"],
        sections=[".text", ".data", ".bss", ".plt"],
        protections={"PIE": True, "NX": True, "Canary": False, "RELRO": "Partial"},
    )
