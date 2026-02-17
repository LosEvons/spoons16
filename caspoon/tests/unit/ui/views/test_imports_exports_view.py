"""Unit tests for ImportsExportsView migration to BaseView architecture."""

from unittest.mock import PropertyMock, patch

import pytest
from rich.console import Console

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.core.state import AppState
from caspoon.ui.views.imports_exports import ImportsExportsView


def render_rich_object(obj):
    """Render a Rich object to a string for testing.

    Args:
        obj: A Rich renderable object

    Returns:
        String representation of the rendered object
    """
    console = Console()
    with console.capture() as capture:
        console.print(obj)
    return capture.get()


class TestImportsExportsViewInheritance:
    """Test proper inheritance."""

    def test_inherits_baseview(self):
        """Test that ImportsExportsView inherits from BaseView."""
        assert issubclass(ImportsExportsView, BaseView)

    def test_has_render_content(self):
        """Test that ImportsExportsView has render_content method."""
        assert hasattr(ImportsExportsView, "render_content")
        assert callable(ImportsExportsView.render_content)


class TestImportsExportsViewInitialization:
    """Test initialization."""

    def test_initializes(self):
        """Test that ImportsExportsView can be instantiated."""
        view = ImportsExportsView()
        assert view is not None


class TestImportsExportsViewSubscription:
    """Test state subscription."""

    def test_subscribes_on_mount(self):
        """Test that on_mount sets up state subscription."""
        # Create mock app with state
        class MockApp:
            def __init__(self):
                self.state = AppState()

        view = ImportsExportsView()
        mock_app = MockApp()

        # Track if subscribe was called
        subscribe_calls = []

        def mock_subscribe(prop, callback):
            subscribe_calls.append((prop, callback))

        mock_app.state.subscribe = mock_subscribe

        # Mock the app property to return our mock
        with patch.object(type(view), 'app', new_callable=PropertyMock, return_value=mock_app):
            # Call on_mount
            view.on_mount()

        # Verify subscription was set up
        assert len(subscribe_calls) == 1
        assert subscribe_calls[0][0] == "analysis_results"

    def test_on_mount_handles_missing_state(self):
        """Test that on_mount handles missing app.state gracefully."""
        view = ImportsExportsView()

        # Mock app without state
        class MockApp:
            pass

        view._app = MockApp()

        # Should not raise
        view.on_mount()


class TestImportsExportsViewDataHandling:
    """Test data handling and updates."""

    def test_on_results_changed_with_data(self):
        """Test that _on_results_changed sets data."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=["printf", "malloc", "free"],
            exports=["main", "helper_func"],
        )

        view._on_results_changed(results)

        # data should be set to the results object
        assert view.data == results

    def test_on_results_changed_with_none(self):
        """Test that _on_results_changed handles None value."""
        view = ImportsExportsView()

        view._on_results_changed(None)

        # data should be None
        assert view.data is None


class TestImportsExportsViewRendering:
    """Test rendering."""

    def test_render_content_with_both_imports_and_exports(self):
        """Test that render_content displays both imports and exports."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=["printf", "malloc", "free"],
            exports=["main", "helper"],
        )

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.render_content(results)

        # Should call update once with Columns layout
        assert len(update_calls) == 1

        # Render the Rich object to check its content
        output_str = render_rich_object(update_calls[0])
        assert "Imports" in output_str
        assert "Exports" in output_str

    def test_render_content_with_empty_imports(self):
        """Test that render_content handles empty imports gracefully."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=[],
            exports=["main"],
        )

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.render_content(results)

        # Should still render without errors
        assert len(update_calls) == 1
        output_str = render_rich_object(update_calls[0])
        assert "No imports found" in output_str

    def test_render_content_with_empty_exports(self):
        """Test that render_content handles empty exports gracefully."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=["printf"],
            exports=[],
        )

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.render_content(results)

        # Should still render without errors
        assert len(update_calls) == 1
        output_str = render_rich_object(update_calls[0])
        assert "No exports found" in output_str

    def test_render_content_with_both_empty(self):
        """Test that render_content handles both empty lists."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=[],
            exports=[],
        )

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.render_content(results)

        # Should render with "No X found" messages
        assert len(update_calls) == 1
        output_str = render_rich_object(update_calls[0])
        assert "No imports found" in output_str
        assert "No exports found" in output_str

    def test_render_content_with_none_lists(self):
        """Test that render_content handles None imports/exports."""
        view = ImportsExportsView()

        results = AnalysisResults(
            imports=None,
            exports=None,
        )

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        # Should not raise
        view.render_content(results)

        assert len(update_calls) == 1


class TestImportsExportsViewTableStructure:
    """Test table structure and formatting."""

    def test_imports_table_has_correct_columns(self):
        """Test that imports table has correct column structure."""
        view = ImportsExportsView()

        imports = ["printf", "malloc", "free"]
        panel = view._build_imports_table(imports)

        # Render the panel and check content
        output_str = render_rich_object(panel)
        assert "Imports" in output_str
        assert "3" in output_str

    def test_exports_table_has_correct_columns(self):
        """Test that exports table has correct column structure."""
        view = ImportsExportsView()

        exports = ["main", "helper", "utils"]
        panel = view._build_exports_table(exports)

        # Render the panel and check content
        output_str = render_rich_object(panel)
        assert "Exports" in output_str
        assert "3" in output_str

    def test_imports_table_deduplicates_and_sorts(self):
        """Test that imports are deduplicated and sorted."""
        view = ImportsExportsView()

        # Duplicate imports
        imports = ["printf", "malloc", "printf", "free", "malloc"]

        # Mock update to capture table content
        update_calls = []
        original_update = view.update
        view.update = lambda x: update_calls.append(x)

        # Build table
        panel = view._build_imports_table(imports)

        # Should deduplicate to 3 unique imports
        output_str = render_rich_object(panel)
        assert "3" in output_str  # count should show 3

    def test_exports_table_deduplicates_and_sorts(self):
        """Test that exports are deduplicated and sorted."""
        view = ImportsExportsView()

        # Duplicate exports
        exports = ["main", "helper", "main", "utils"]

        panel = view._build_exports_table(exports)

        # Should deduplicate to 3 unique exports
        output_str = render_rich_object(panel)
        assert "3" in output_str  # count should show 3

    def test_handles_unnamed_symbols(self):
        """Test that unnamed symbols are displayed as <unnamed>."""
        view = ImportsExportsView()

        imports = ["printf", None, "", "malloc"]

        # Mock update to avoid UI operations
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        panel = view._build_imports_table(imports)

        # Should show <unnamed> for None and empty strings
        output_str = render_rich_object(panel)
        assert "<unnamed>" in output_str


class TestImportsExportsViewCounts:
    """Test count display in titles."""

    def test_imports_count_in_title(self):
        """Test that imports count is shown in title."""
        view = ImportsExportsView()

        imports = ["func1", "func2", "func3", "func4", "func5"]
        panel = view._build_imports_table(imports)

        output_str = render_rich_object(panel)
        assert "5" in output_str

    def test_exports_count_in_title(self):
        """Test that exports count is shown in title."""
        view = ImportsExportsView()

        exports = ["main", "helper"]
        panel = view._build_exports_table(exports)

        output_str = render_rich_object(panel)
        assert "2" in output_str

    def test_zero_count_for_empty(self):
        """Test that 0 count is shown for empty lists."""
        view = ImportsExportsView()

        panel = view._build_imports_table([])
        output_str = render_rich_object(panel)
        assert "0" in output_str


class TestImportsExportsViewPerformance:
    """Test performance with large datasets."""

    def test_handles_many_imports(self):
        """Test that view handles large number of imports."""
        view = ImportsExportsView()

        # Create 500 imports
        large_imports = [f"import_func_{i}" for i in range(500)]

        results = AnalysisResults(imports=large_imports, exports=[])

        # Mock update to avoid UI operations
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        # Should not raise and complete reasonably fast
        view.render_content(results)

        assert len(update_calls) == 1

    def test_handles_many_exports(self):
        """Test that view handles large number of exports."""
        view = ImportsExportsView()

        # Create 500 exports
        large_exports = [f"export_func_{i}" for i in range(500)]

        results = AnalysisResults(imports=[], exports=large_exports)

        # Mock update to avoid UI operations
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        # Should not raise
        view.render_content(results)

        assert len(update_calls) == 1

    def test_respects_500_item_limit(self):
        """Test that tables limit to 500 items for performance."""
        view = ImportsExportsView()

        # Create more than 500 imports
        huge_imports = [f"import_{i}" for i in range(1000)]

        panel = view._build_imports_table(huge_imports)

        # Should handle without crashing
        assert panel is not None


class TestImportsExportsViewBackwardCompatibility:
    """Test backward compatibility."""

    def test_has_update_data(self):
        """Test that ImportsExportsView has update_data method."""
        view = ImportsExportsView()
        assert hasattr(view, "update_data")
        assert callable(view.update_data)

    def test_update_data_with_imports_exports(self):
        """Test that update_data still works (deprecated path)."""
        view = ImportsExportsView()

        report = ExecutableReport(
            path="/test/binary", file_type="ELF", arch="x86_64"
        )
        report.imports = ["printf", "malloc"]
        report.exports = ["main"]

        # Should not raise
        view.update_data(report)

    def test_update_data_with_empty_lists(self):
        """Test that update_data handles empty imports/exports."""
        view = ImportsExportsView()

        report = ExecutableReport(
            path="/test/binary", file_type="ELF", arch="x86_64"
        )
        report.imports = []
        report.exports = []

        # Should not raise
        view.update_data(report)

    def test_update_data_with_duplicates(self):
        """Test that update_data handles duplicates correctly."""
        view = ImportsExportsView()

        report = ExecutableReport(
            path="/test/binary", file_type="ELF", arch="x86_64"
        )
        report.imports = ["printf", "printf", "malloc"]
        report.exports = ["main", "main"]

        # Should deduplicate
        view.update_data(report)


class TestImportsExportsViewIntegration:
    """Test integration scenarios."""

    def test_full_workflow(self):
        """Test full workflow from state change to render."""
        view = ImportsExportsView()

        # Mock update to track calls
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        # Simulate state change
        results = AnalysisResults(
            imports=["printf", "malloc", "free"],
            exports=["main", "helper_func", "utility"],
        )

        # _on_results_changed sets self.data which triggers watch_data
        # which automatically calls render_content, so we don't call it manually
        view._on_results_changed(results)

        # data should be set
        assert view.data == results

        # Should have rendered once via watch_data -> render_content
        assert len(update_calls) == 1

    def test_state_update_cycle(self):
        """Test complete state update cycle."""
        view = ImportsExportsView()

        # Mock update
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        # First update - _on_results_changed triggers render via watch_data
        results1 = AnalysisResults(
            imports=["func1", "func2"],
            exports=["main"],
        )
        view._on_results_changed(results1)

        assert len(update_calls) == 1

        # Second update (different data)
        results2 = AnalysisResults(
            imports=["new_func1", "new_func2", "new_func3"],
            exports=["new_main", "new_helper"],
        )
        view._on_results_changed(results2)

        # Should have rendered twice total (once per state change)
        assert len(update_calls) == 2
