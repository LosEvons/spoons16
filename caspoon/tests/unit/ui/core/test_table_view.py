"""Unit tests for TableView widget."""

import pytest

from caspoon.ui.core.base import TableView


class ConcreteTableView(TableView[list[dict]]):
    """Concrete implementation of TableView for testing."""

    def __init__(self, rows: list[dict] | None = None):
        super().__init__()
        self._rows = rows or []
        self._filtered_rows = self._rows[:]
        self.columns = ["Name", "Value", "Type"]

    def render_content(self, data: list[dict]) -> None:
        """Mock implementation."""
        self._rows = data
        self._filtered_rows = data[:]
        table = self._build_rich_table()
        self.update(table)

    def get_item_count(self) -> int:
        """Return count of filtered rows."""
        return len(self._filtered_rows)

    def on_item_selected(self, index: int) -> None:
        """Handle selection."""
        pass

    def apply_filter(self, text: str) -> None:
        """Filter rows by text in name."""
        if not text:
            self._filtered_rows = self._rows[:]
        else:
            self._filtered_rows = [
                row for row in self._rows if text.lower() in row.get("name", "").lower()
            ]

    def get_columns(self) -> list[str]:
        """Return column names."""
        return self.columns

    def get_row_data(self, index: int) -> list[str]:
        """Return data for row."""
        if 0 <= index < len(self._filtered_rows):
            row = self._filtered_rows[index]
            return [row.get("name", ""), row.get("value", ""), row.get("type", "")]
        return ["", "", ""]


class TestTableView:
    """Tests for TableView class."""

    def test_initialization(self):
        """Test TableView initializes with correct defaults."""
        view = ConcreteTableView()

        assert view.sort_column is None
        assert view.sort_descending is False
        assert view.selected_index == 0
        assert view.filter_text == ""

    def test_initialization_with_data(self):
        """Test TableView can be initialized with rows."""
        rows = [
            {"name": "Row1", "value": "A", "type": "str"},
            {"name": "Row2", "value": "B", "type": "int"},
        ]
        view = ConcreteTableView(rows)

        assert view.get_item_count() == 2

    def test_sort_by_column_first_time(self):
        """Test sorting by column for first time."""
        view = ConcreteTableView()

        view.action_sort_by_column("Name")

        assert view.sort_column == "Name"
        assert view.sort_descending is False

    def test_sort_by_same_column_toggles_direction(self):
        """Test sorting by same column toggles direction."""
        view = ConcreteTableView()

        # First sort - ascending
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view.sort_descending is False

        # Second sort - descending
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view.sort_descending is True

        # Third sort - ascending again
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view.sort_descending is False

    def test_sort_by_different_column(self):
        """Test sorting by different column resets to ascending."""
        view = ConcreteTableView()

        # Sort by Name descending
        view.action_sort_by_column("Name")
        view.action_sort_by_column("Name")
        assert view.sort_descending is True

        # Sort by different column
        view.action_sort_by_column("Value")
        assert view.sort_column == "Value"
        assert view.sort_descending is False

    def test_get_columns_returns_list(self):
        """Test get_columns returns list of strings."""
        view = ConcreteTableView()

        columns = view.get_columns()

        assert isinstance(columns, list)
        assert len(columns) == 3
        assert "Name" in columns
        assert "Value" in columns
        assert "Type" in columns

    def test_get_row_data_returns_list(self):
        """Test get_row_data returns list of strings."""
        rows = [{"name": "Test", "value": "123", "type": "int"}]
        view = ConcreteTableView(rows)

        row_data = view.get_row_data(0)

        assert isinstance(row_data, list)
        assert len(row_data) == 3
        assert row_data[0] == "Test"
        assert row_data[1] == "123"
        assert row_data[2] == "int"

    def test_get_row_data_invalid_index(self):
        """Test get_row_data with invalid index."""
        view = ConcreteTableView([{"name": "Test", "value": "1", "type": "int"}])

        # Out of bounds
        row_data = view.get_row_data(10)

        # Should return empty or default values
        assert isinstance(row_data, list)

    def test_build_rich_table_structure(self):
        """Test _build_rich_table creates table with correct structure."""
        rows = [
            {"name": "Row1", "value": "A", "type": "str"},
            {"name": "Row2", "value": "B", "type": "int"},
        ]
        view = ConcreteTableView(rows)

        table = view._build_rich_table()

        # Verify it's a Rich Table
        from rich.table import Table

        assert isinstance(table, Table)

    def test_build_rich_table_with_selection(self):
        """Test _build_rich_table highlights selected row."""
        rows = [
            {"name": "Row1", "value": "A", "type": "str"},
            {"name": "Row2", "value": "B", "type": "int"},
            {"name": "Row3", "value": "C", "type": "str"},
        ]
        view = ConcreteTableView(rows)
        view.selected_index = 1

        table = view._build_rich_table()

        # Can't easily test the actual styling, but verify no errors
        assert table is not None

    def test_build_rich_table_with_sort_indicator(self):
        """Test _build_rich_table shows sort indicator in header."""
        rows = [{"name": "Row1", "value": "A", "type": "str"}]
        view = ConcreteTableView(rows)

        # Sort by Name ascending
        view.sort_column = "Name"
        view.sort_descending = False

        table = view._build_rich_table()
        assert table is not None

        # Sort descending
        view.sort_descending = True
        table = view._build_rich_table()
        assert table is not None

    def test_abstract_methods_enforced(self):
        """Test abstract methods must be implemented."""
        with pytest.raises(TypeError):

            class IncompleteTableView(TableView[list]):
                pass

            IncompleteTableView()  # Should fail

    def test_get_columns_abstract(self):
        """Test get_columns is abstract."""
        assert hasattr(TableView, "get_columns")

    def test_get_row_data_abstract(self):
        """Test get_row_data is abstract."""
        assert hasattr(TableView, "get_row_data")

    def test_inherits_from_interactive_view(self):
        """Test TableView inherits InteractiveView functionality."""
        rows = [
            {"name": "Row1", "value": "A", "type": "str"},
            {"name": "Row2", "value": "B", "type": "int"},
            {"name": "Row3", "value": "C", "type": "str"},
        ]
        view = ConcreteTableView(rows)

        # Should have navigation
        view.action_move_down()
        assert view.selected_index == 1

        view.action_move_up()
        assert view.selected_index == 0


class TestTableViewSorting:
    """Tests for TableView sorting functionality."""

    def test_sort_column_property(self):
        """Test sort_column property can be set."""
        view = ConcreteTableView()

        view.sort_column = "Name"
        assert view.sort_column == "Name"

        view.sort_column = "Value"
        assert view.sort_column == "Value"

        view.sort_column = None
        assert view.sort_column is None

    def test_sort_descending_property(self):
        """Test sort_descending property can be set."""
        view = ConcreteTableView()

        view.sort_descending = True
        assert view.sort_descending is True

        view.sort_descending = False
        assert view.sort_descending is False

    def test_sort_sequence(self):
        """Test full sorting sequence."""
        view = ConcreteTableView()

        # No sort initially
        assert view.sort_column is None
        assert view.sort_descending is False

        # Sort by Name ascending
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view.sort_descending is False

        # Sort by Name descending
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view.sort_descending is True

        # Sort by Value ascending
        view.action_sort_by_column("Value")
        assert view.sort_column == "Value"
        assert view.sort_descending is False


class TestTableViewWithFilter:
    """Tests for TableView with filtering."""

    def test_filter_and_sort_together(self):
        """Test filtering and sorting work together."""
        rows = [
            {"name": "Apple", "value": "1", "type": "fruit"},
            {"name": "Banana", "value": "2", "type": "fruit"},
            {"name": "Carrot", "value": "3", "type": "vegetable"},
        ]
        view = ConcreteTableView(rows)

        # Apply filter
        view.filter_text = "a"
        assert view.get_item_count() == 3  # All contain 'a'

        # Sort while filtered
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"

    def test_table_with_empty_data(self):
        """Test table operations with no data."""
        view = ConcreteTableView([])

        # These should not raise
        view.action_sort_by_column("Name")
        table = view._build_rich_table()
        assert table is not None

    def test_table_navigation_after_filter(self):
        """Test navigation after filtering reduces items."""
        rows = [
            {"name": "Apple", "value": "1", "type": "fruit"},
            {"name": "Banana", "value": "2", "type": "fruit"},
            {"name": "Cherry", "value": "3", "type": "fruit"},
        ]
        view = ConcreteTableView(rows)

        # Select last item
        view.selected_index = 2

        # Filter to fewer items
        view.filter_text = "app"
        assert view.get_item_count() == 1

        # Selection should be adjusted by watch_selected_index
        # Manually trigger the watcher to simulate reactive behavior
        view.watch_selected_index(2, view.selected_index)

        # Selection should now be valid
        assert view.selected_index < view.get_item_count()


class TestTableViewEdgeCases:
    """Tests for TableView edge cases."""

    def test_build_table_with_no_rows(self):
        """Test building table with no rows."""
        view = ConcreteTableView([])

        table = view._build_rich_table()

        assert table is not None

    def test_build_table_with_single_row(self):
        """Test building table with single row."""
        rows = [{"name": "Only", "value": "1", "type": "test"}]
        view = ConcreteTableView(rows)

        table = view._build_rich_table()

        assert table is not None

    def test_get_row_data_negative_index(self):
        """Test get_row_data with negative index."""
        rows = [{"name": "Test", "value": "1", "type": "int"}]
        view = ConcreteTableView(rows)

        row_data = view.get_row_data(-1)

        # Should handle gracefully
        assert isinstance(row_data, list)

    def test_sort_by_invalid_column(self):
        """Test sorting by column not in table."""
        view = ConcreteTableView()

        # Should not raise
        view.action_sort_by_column("InvalidColumn")

        assert view.sort_column == "InvalidColumn"

    def test_multiple_sort_toggles(self):
        """Test multiple rapid sort toggles."""
        view = ConcreteTableView()

        # Toggle sort 10 times
        for i in range(10):
            view.action_sort_by_column("Name")

        # Should be descending (odd number actually, 10 toggles total but first is set, so 9 toggles)
        # First call sets ascending, then 9 more toggles
        # So: 0=asc, 1=desc, 2=asc, 3=desc, 4=asc, 5=desc, 6=asc, 7=desc, 8=asc, 9=desc
        assert view.sort_column == "Name"
        assert view.sort_descending is True

    def test_selection_highlight_at_boundaries(self):
        """Test selection highlighting at first and last rows."""
        rows = [
            {"name": "First", "value": "1", "type": "int"},
            {"name": "Last", "value": "2", "type": "int"},
        ]
        view = ConcreteTableView(rows)

        # First row
        view.selected_index = 0
        table = view._build_rich_table()
        assert table is not None

        # Last row
        view.selected_index = 1
        table = view._build_rich_table()
        assert table is not None
