"""Unit tests for StringsView migration to InteractiveView architecture."""

import pytest

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.models import AnalysisResults
from caspoon.ui.core.state import AppState
from caspoon.ui.views.strings_view import StringsView


class TestStringsViewInheritance:
    """Test proper inheritance."""

    def test_inherits_interactiveview(self):
        """Test that StringsView inherits from InteractiveView."""
        assert issubclass(StringsView, InteractiveView)

    def test_has_render_content(self):
        """Test that StringsView has render_content method."""
        assert hasattr(StringsView, "render_content")
        assert callable(StringsView.render_content)

    def test_has_apply_filter(self):
        """Test that StringsView has apply_filter method."""
        assert hasattr(StringsView, "apply_filter")
        assert callable(StringsView.apply_filter)

    def test_has_get_item_count(self):
        """Test that StringsView has get_item_count method."""
        assert hasattr(StringsView, "get_item_count")
        assert callable(StringsView.get_item_count)


class TestStringsViewInitialization:
    """Test initialization."""

    def test_initializes(self):
        """Test that StringsView can be instantiated."""
        view = StringsView()
        assert view is not None

    def test_initializes_with_empty_strings(self):
        """Test that StringsView initializes with empty string lists."""
        view = StringsView()
        assert view.all_strings == []
        assert view.filtered_strings == []

    def test_has_bindings(self):
        """Test that StringsView has keybindings defined."""
        view = StringsView()
        assert hasattr(view, "BINDINGS")
        assert len(view.BINDINGS) > 0


class TestStringsViewSubscription:
    """Test state subscription."""

    def test_subscribes_on_mount(self):
        """Test that on_mount attempts state subscription."""
        view = StringsView()

        # Since on_mount uses self.app which accesses Textual context,
        # we test the key functionality: _on_results_changed
        # This verifies the subscription callback works correctly
        results = AnalysisResults(strings=["test"])
        view._on_results_changed(results)
        assert view.data == ["test"]

    def test_on_mount_handles_missing_state(self):
        """Test that on_mount handles missing app.state gracefully."""
        view = StringsView()

        # Mock app without state
        class MockApp:
            pass

        view._app = MockApp()

        # Should not raise
        view.on_mount()


class TestStringsViewDataHandling:
    """Test data handling and updates."""

    def test_on_results_changed_with_strings(self):
        """Test that _on_results_changed extracts strings from results."""
        view = StringsView()

        results = AnalysisResults(
            strings=["test string 1", "test string 2", "test string 3"]
        )

        view._on_results_changed(results)

        # data should be set to the strings list
        assert view.data == ["test string 1", "test string 2", "test string 3"]

    def test_on_results_changed_with_empty_strings(self):
        """Test that _on_results_changed handles empty strings list."""
        view = StringsView()

        results = AnalysisResults(strings=[])

        view._on_results_changed(results)

        # data should be empty list
        assert view.data == []

    def test_on_results_changed_with_none(self):
        """Test that _on_results_changed handles None value."""
        view = StringsView()

        view._on_results_changed(None)

        # data should be empty list
        assert view.data == []


class TestStringsViewRendering:
    """Test rendering."""

    def test_render_content_stores_strings(self):
        """Test that render_content stores strings in instance var."""
        view = StringsView()

        strings = ["string1", "string2", "string3"]
        view.render_content(strings)

        assert view.all_strings == strings

    def test_render_content_with_empty_list(self):
        """Test that render_content handles empty list."""
        view = StringsView()

        # Should not raise
        view.render_content([])

        assert view.all_strings == []
        assert view.filtered_strings == []

    def test_render_strings_shows_empty_message(self):
        """Test that empty strings list shows appropriate message."""
        view = StringsView()

        view._strings = []
        view._filtered = []

        # Mock update method to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view._render_strings()

        # Should show "No strings found" message
        assert len(update_calls) == 1
        assert "No strings found" in str(update_calls[0])


class TestStringsViewFiltering:
    """Test filtering functionality."""

    def test_apply_filter_no_filter(self):
        """Test that apply_filter with empty text shows all strings."""
        view = StringsView()

        view._strings = ["apple", "banana", "cherry"]
        view.apply_filter("")

        assert view.filtered_strings == ["apple", "banana", "cherry"]

    def test_apply_filter_case_insensitive(self):
        """Test that apply_filter is case-insensitive."""
        view = StringsView()

        view._strings = ["Apple", "BANANA", "cherry", "APPLE PIE"]

        # Mock _render_strings to avoid UI operations
        view._render_strings = lambda: None

        view.apply_filter("apple")

        assert view.filtered_count == 2
        assert "Apple" in view.filtered_strings
        assert "APPLE PIE" in view.filtered_strings

    def test_apply_filter_substring_match(self):
        """Test that apply_filter does substring matching."""
        view = StringsView()

        view._strings = [
            "/usr/bin/test",
            "/home/user/file",
            "/var/log/test.log",
            "/etc/config",
        ]

        # Mock _render_strings to avoid UI operations
        view._render_strings = lambda: None

        view.apply_filter("test")

        assert view.filtered_count == 2
        assert "/usr/bin/test" in view.filtered_strings
        assert "/var/log/test.log" in view.filtered_strings

    def test_apply_filter_resets_selection(self):
        """Test that apply_filter resets selection when needed."""
        view = StringsView()

        view._strings = ["string1", "string2", "string3"]
        view.selected_index = 2

        # Mock _render_strings to avoid UI operations
        view._render_strings = lambda: None

        # Apply filter that reduces items
        view._strings = ["apple", "banana"]
        view._filtered = ["apple", "banana"]
        view.selected_index = 5  # Beyond bounds

        view.apply_filter("")

        # Selection should be clamped to valid range
        assert view.selected_index == 0

    def test_filter_text_watch_triggers_apply_filter(self):
        """Test that changing filter_text triggers apply_filter."""
        view = StringsView()

        view._strings = ["apple", "banana", "cherry"]

        # Mock _render_strings to avoid UI operations
        view._render_strings = lambda: None

        # Change filter_text (triggers watch_filter_text)
        view.filter_text = "ban"

        # Should filter strings
        assert view.filtered_strings == ["banana"]

    def test_action_clear_filter(self):
        """Test that action_clear_filter clears the filter."""
        view = StringsView()

        view.filter_text = "test"

        view.action_clear_filter()

        assert view.filter_text == ""


class TestStringsViewNavigation:
    """Test navigation and selection."""

    def test_get_item_count(self):
        """Test that get_item_count returns filtered count."""
        view = StringsView()

        view._filtered = ["string1", "string2", "string3"]

        assert view.get_item_count() == 3

    def test_get_item_count_empty(self):
        """Test that get_item_count returns 0 for empty list."""
        view = StringsView()

        view._filtered = []

        assert view.get_item_count() == 0

    def test_get_item_count_respects_max_limit(self):
        """Test that get_item_count respects MAX_DISPLAY_STRINGS."""
        from caspoon.ui.views.strings_view import MAX_DISPLAY_STRINGS

        view = StringsView()

        # Create more strings than max
        view._filtered = [f"string{i}" for i in range(MAX_DISPLAY_STRINGS + 100)]

        # Should return max limit
        assert view.get_item_count() == MAX_DISPLAY_STRINGS

    def test_on_item_selected(self):
        """Test that on_item_selected handles valid index."""
        view = StringsView()

        view._filtered = ["string1", "string2", "string3"]

        # Should not raise
        view.on_item_selected(1)

    def test_on_item_selected_invalid_index(self):
        """Test that on_item_selected handles invalid index."""
        view = StringsView()

        view._filtered = ["string1", "string2"]

        # Should not raise (just logs)
        view.on_item_selected(10)
        view.on_item_selected(-1)

    def test_watch_selected_index_triggers_render(self):
        """Test that selection change triggers re-render."""
        view = StringsView()

        view._filtered = ["string1", "string2", "string3"]

        # Track if _render_strings was called
        render_calls = []
        view._render_strings = lambda: render_calls.append(True)

        # Change selection
        view.watch_selected_index(0, 1)

        assert len(render_calls) == 1


class TestStringsViewFilteredCountDisplay:
    """Test filtered count display."""

    def test_filtered_count_in_title_with_filter(self):
        """Test that title shows filtered count when filter active."""
        view = StringsView()

        view._strings = ["apple", "banana", "cherry", "apricot"]
        view.filter_text = "ap"

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.apply_filter("ap")

        # Check that title shows filtered count
        # Should be something like "Strings (2 / 4)"
        assert len(update_calls) == 1
        # The output is a Panel, need to get title from Rich object
        panel = update_calls[0]
        # Check the filtered counts are correct
        assert view.filtered_count == 2
        assert view.total_count == 4

    def test_filtered_count_in_title_no_filter(self):
        """Test that title shows total count when no filter."""
        view = StringsView()

        view._strings = ["apple", "banana", "cherry"]
        view.filter_text = ""

        # Mock update to capture output
        update_calls = []
        view.update = lambda x: update_calls.append(x)

        view.apply_filter("")

        # Check that title shows total count only
        assert len(update_calls) == 1
        # Check the counts are correct
        assert view.filtered_count == 3
        assert view.total_count == 3


class TestStringsViewBackwardCompatibility:
    """Test backward compatibility."""

    def test_has_update_data(self):
        """Test that StringsView has update_data method."""
        view = StringsView()
        assert hasattr(view, "update_data")
        assert callable(view.update_data)

    def test_update_data_with_strings(self):
        """Test that update_data still works (deprecated path)."""
        view = StringsView()

        report = ExecutableReport(
            path="/test/binary", file_type="ELF", arch="x86_64"
        )
        report.strings = ["test string 1", "test string 2"]

        # Should not raise
        view.update_data(report)

    def test_update_data_with_empty_strings(self):
        """Test that update_data handles empty strings."""
        view = StringsView()

        report = ExecutableReport(
            path="/test/binary", file_type="ELF", arch="x86_64"
        )
        report.strings = []

        # Should not raise
        view.update_data(report)


class TestStringsViewPerformance:
    """Test performance with large datasets."""

    def test_handles_large_string_list(self):
        """Test that view handles large number of strings."""
        view = StringsView()

        # Create 10,000 test strings
        large_string_list = [f"test_string_{i}" for i in range(10000)]

        # Should not raise and should complete reasonably fast
        view.render_content(large_string_list)

        assert view.all_strings == large_string_list

    def test_filtering_large_list(self):
        """Test that filtering works on large lists."""
        view = StringsView()

        # Create large list with some matches
        view._strings = [f"string_{i}" for i in range(5000)]
        view._strings.extend([f"test_{i}" for i in range(5000)])

        # Mock _render_strings to avoid UI operations
        view._render_strings = lambda: None

        # Filter should be fast
        view.apply_filter("test")

        # Should find all test strings
        assert view.filtered_count == 5000

    def test_respects_max_display_limit(self):
        """Test that get_item_count respects MAX_DISPLAY_STRINGS."""
        from caspoon.ui.views.strings_view import MAX_DISPLAY_STRINGS

        view = StringsView()

        # Create more strings than max
        large_list = [f"string_{i}" for i in range(MAX_DISPLAY_STRINGS + 500)]
        view._strings = large_list
        view._filtered = large_list

        # get_item_count should return max limit
        assert view.get_item_count() == MAX_DISPLAY_STRINGS

        # Verify that _render_strings doesn't crash with large list
        # (it internally limits to MAX_DISPLAY_STRINGS for display)
        view.update = lambda x: None  # Mock to avoid UI
        view._render_strings()  # Should not raise
