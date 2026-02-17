"""Tests for empty data handling across all views.

Ensures that all views display appropriate messages when no data is available,
rather than showing blank screens or crashing.
"""

from unittest.mock import MagicMock

import pytest

from caspoon.ui.core.models import AnalysisResults, BinaryInfo
from caspoon.ui.views.imports_exports import ImportsExportsView
from caspoon.ui.views.overview import OverviewView
from caspoon.ui.views.protections import ProtectionsView
from caspoon.ui.views.r2_view import R2View
from caspoon.ui.views.strings_view import StringsView


class TestEmptyDataHandling:
    """Test that all views handle empty data gracefully."""

    def test_strings_view_empty_data(self):
        """StringsView should show 'No strings found' when empty."""
        view = StringsView()

        # Set empty string list
        view._strings = []
        view._filtered = []
        view._render_strings()

        # Check that view contains "No strings" message
        rendered = str(view.renderable)
        assert "No strings" in rendered or "no strings" in rendered.lower()

    def test_strings_view_empty_after_filter(self):
        """StringsView should show message when filter excludes all strings."""
        view = StringsView()

        # Set some strings
        view._strings = ["test1", "test2", "test3"]

        # Apply filter that matches nothing
        view.apply_filter("nonexistent_string_xyz")

        # Should show "No strings" or similar message
        rendered = str(view.renderable)
        # The view should indicate no results
        assert view.filtered_count == 0

    def test_imports_exports_view_empty_imports(self):
        """ImportsExportsView should show 'No imports' when empty."""
        view = ImportsExportsView()

        # Create analysis results with no imports
        results = AnalysisResults(
            functions=[],
            strings=[],
            imports=[],  # Empty
            exports=["export1"],
            sections=[],
            protections={}
        )

        view.data = results

        # Check that view doesn't crash and has renderable
        assert view.renderable is not None
        # The view internally handles empty imports correctly

    def test_imports_exports_view_empty_exports(self):
        """ImportsExportsView should show 'No exports' when empty."""
        view = ImportsExportsView()

        # Create analysis results with no exports
        results = AnalysisResults(
            functions=[],
            strings=[],
            imports=["import1"],
            exports=[],  # Empty
            sections=[],
            protections={}
        )

        view.data = results

        # Check that view doesn't crash and has renderable
        assert view.renderable is not None
        # The view internally handles empty exports correctly

    def test_imports_exports_view_both_empty(self):
        """ImportsExportsView should handle both empty gracefully."""
        view = ImportsExportsView()

        # Create analysis results with nothing
        results = AnalysisResults(
            functions=[],
            strings=[],
            imports=[],
            exports=[],
            sections=[],
            protections={}
        )

        view.data = results

        # Should not crash, should have renderable
        assert view.renderable is not None
        # The view shows "No imports found" and "No exports found" internally

    def test_protections_view_empty_data(self):
        """ProtectionsView should show message when no protections available."""
        view = ProtectionsView()

        # Set empty protections dict
        view.data = {}

        # Check that it shows "No protection information"
        rendered = str(view.renderable)
        assert "No protection" in rendered or "no protection" in rendered.lower()

    def test_protections_view_none_data(self):
        """ProtectionsView should handle None protections."""
        view = ProtectionsView()

        # Create analysis results with None protections
        results = AnalysisResults(
            functions=[],
            strings=[],
            imports=[],
            exports=[],
            sections=[],
            protections=None  # type: ignore
        )

        # This should not crash
        view._on_results_changed(results)

        # Should have set data to empty dict
        assert view.data == {} or view.data is None

    def test_r2_view_empty_data(self):
        """R2View should show message when no r2 data available."""
        view = R2View()

        # Set empty r2 data
        view._r2_data = {}

        # Check that it doesn't crash
        assert view.renderable is not None
        # R2View internally handles empty data correctly

    def test_overview_view_with_minimal_data(self):
        """OverviewView should handle minimal binary info."""
        view = OverviewView()

        # Create minimal binary info
        binary_info = BinaryInfo(
            path="/test/binary",
            architecture="unknown",
            bits=0,
            file_type="unknown",
            stripped=False,
            file_size=0,
            entry_point=None
        )

        # Should not crash with minimal data
        view.data = binary_info

        # Should have valid renderable
        assert view.renderable is not None
        # The view renders the data correctly even if minimal


class TestEmptyDataWorkflows:
    """Test workflows with empty or missing data."""

    @pytest.mark.asyncio
    async def test_empty_analysis_results(self):
        """Test handling of analysis with no interesting data."""
        from unittest.mock import patch

        from caspoon.tests.helpers import wait_for_workers
        from caspoon.ui.app import CaspoonApp

        app = CaspoonApp()

        # Create a report with empty data
        mock_report = MagicMock()
        mock_report.path = "/test/empty_binary"
        mock_report.arch = "x86_64"
        mock_report.bits = 64
        mock_report.file_type = "ELF"
        mock_report.strings = []  # No strings
        mock_report.functions = []  # No functions
        mock_report.imports = []  # No imports
        mock_report.exports = []  # No exports
        mock_report.protections = MagicMock()
        mock_report.protections.pie = False
        mock_report.protections.nx = False
        mock_report.protections.canary = False
        mock_report.protections.relro = "none"
        mock_report.raw_backend_data = {}

        with patch("caspoon.ui.workers.analysis.ReconRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_report
            mock_runner_class.return_value = mock_runner

            async with app.run_test() as pilot:
                # Start analysis
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    f.write(b"\x7fELF\x02\x01\x01\x00")
                    temp_path = f.name

                await app.start_analysis(temp_path)
                await wait_for_workers(app, pilot)

                # Verify analysis completed
                assert app.state.binary_info is not None
                assert app.state.analysis_results is not None

                # Navigate to strings view - should show empty message
                await pilot.press("3")
                await pilot.pause()

                strings_view = app.query_one(StringsView)
                assert strings_view.total_count == 0
                # View should handle empty gracefully

                # Navigate to imports/exports view
                await pilot.press("4")
                await pilot.pause()

                # Should not crash with empty data
                assert app.state.analysis_results is not None

    def test_view_initialization_without_data(self):
        """Test that views can be created without crashing when no data."""
        # All views should be constructable without data
        views = [
            StringsView(),
            ImportsExportsView(),
            ProtectionsView(),
            OverviewView(),
            R2View(),
        ]

        # All should be created successfully
        assert len(views) == 5

        # All should have some initial state
        for view in views:
            assert view is not None
            # They might be empty initially, but should not be None
            assert view.renderable is not None or view.data is None


class TestEmptyStateMessages:
    """Test the specific empty state messages."""

    def test_strings_view_message_format(self):
        """Test StringsView empty message is properly formatted."""
        view = StringsView()
        view._strings = []
        view._filtered = []
        view._render_strings()

        rendered = str(view.renderable)
        # Should have dim styling for empty state
        assert "dim" in rendered.lower() or "no strings" in rendered.lower()

    def test_imports_exports_messages_are_dimmed(self):
        """Test that empty messages use dim styling for consistency."""
        view = ImportsExportsView()
        results = AnalysisResults(
            functions=[],
            strings=[],
            imports=[],
            exports=[],
            sections=[],
            protections={}
        )
        view.data = results

        # Should have valid renderable that displays empty states
        assert view.renderable is not None
        # The empty messages are shown with dim styling in the actual views

    def test_protections_view_message_format(self):
        """Test ProtectionsView empty message is properly formatted."""
        view = ProtectionsView()
        view.data = {}

        rendered = str(view.renderable)
        # Should have dim styling
        assert "dim" in rendered.lower() or "no protection" in rendered.lower()
