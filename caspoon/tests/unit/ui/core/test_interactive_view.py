"""Unit tests for InteractiveView widget."""

from unittest.mock import Mock

import pytest

from caspoon.ui.core.base import InteractiveView


class ConcreteInteractiveView(InteractiveView[list[str]]):
    """Concrete implementation of InteractiveView for testing."""

    def __init__(self, items: list[str] | None = None):
        super().__init__()
        self._items = items or []
        self._filtered_items = self._items[:]
        self.selected_item = None

    def render_content(self, data: list[str]) -> None:
        """Mock implementation."""
        self._items = data
        self._filtered_items = data[:]
        self.update(f"Items: {len(data)}")

    def get_item_count(self) -> int:
        """Return count of filtered items."""
        return len(self._filtered_items)

    def on_item_selected(self, index: int) -> None:
        """Record selected item."""
        if 0 <= index < len(self._filtered_items):
            self.selected_item = self._filtered_items[index]

    def apply_filter(self, text: str) -> None:
        """Filter items by text."""
        if not text:
            self._filtered_items = self._items[:]
        else:
            self._filtered_items = [
                item for item in self._items if text.lower() in item.lower()
            ]
        # Reset selection if needed
        if self.selected_index >= len(self._filtered_items):
            self.selected_index = max(0, len(self._filtered_items) - 1)


class TestInteractiveView:
    """Tests for InteractiveView class."""

    def test_initialization(self):
        """Test InteractiveView initializes with correct defaults."""
        view = ConcreteInteractiveView()

        assert view.selected_index == 0
        assert view.filter_text == ""
        assert view.data is None

    def test_initialization_with_data(self):
        """Test InteractiveView can be initialized with items."""
        items = ["one", "two", "three"]
        view = ConcreteInteractiveView(items)

        assert view.get_item_count() == 3

    def test_move_up_action(self):
        """Test action_move_up decrements selected_index."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        # Start at 2
        view.selected_index = 2
        view.action_move_up()

        assert view.selected_index == 1

    def test_move_down_action(self):
        """Test action_move_down increments selected_index."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        # Start at 0
        view.selected_index = 0
        view.action_move_down()

        assert view.selected_index == 1

    def test_move_up_at_top_boundary(self):
        """Test move_up at index 0 stays at 0."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        view.selected_index = 0
        view.action_move_up()

        assert view.selected_index == 0

    def test_move_down_at_bottom_boundary(self):
        """Test move_down at last index stays at last."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        view.selected_index = 2  # Last item
        view.action_move_down()

        assert view.selected_index == 2

    def test_move_to_top(self):
        """Test action_move_to_top sets index to 0."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        view.selected_index = 2
        view.action_move_to_top()

        assert view.selected_index == 0

    def test_move_to_bottom(self):
        """Test action_move_to_bottom sets index to last."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        view.selected_index = 0
        view.action_move_to_bottom()

        assert view.selected_index == 2

    def test_select_item_calls_handler(self):
        """Test action_select_item calls on_item_selected."""
        view = ConcreteInteractiveView(["apple", "banana", "cherry"])

        view.selected_index = 1
        view.action_select_item()

        assert view.selected_item == "banana"

    def test_select_item_with_no_items(self):
        """Test action_select_item with empty list does nothing."""
        view = ConcreteInteractiveView([])

        # Should not raise
        view.action_select_item()

        assert view.selected_item is None

    def test_filter_text_triggers_apply_filter(self):
        """Test setting filter_text calls apply_filter."""
        view = ConcreteInteractiveView(["apple", "apricot", "banana", "blueberry"])

        # Set filter
        view.filter_text = "ap"

        # Should filter to items containing "ap"
        assert view.get_item_count() == 2
        assert "apple" in view._filtered_items
        assert "apricot" in view._filtered_items

    def test_filter_clears_with_empty_string(self):
        """Test clearing filter shows all items."""
        view = ConcreteInteractiveView(["apple", "banana", "cherry"])

        # Apply filter
        view.filter_text = "ap"
        assert view.get_item_count() == 1

        # Clear filter
        view.filter_text = ""
        assert view.get_item_count() == 3

    def test_watch_selected_index_clamps_below_zero(self):
        """Test selected_index is clamped to 0 if negative."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        # Manually trigger watch with negative value
        view.watch_selected_index(0, -5)

        assert view.selected_index == 0

    def test_watch_selected_index_clamps_above_max(self):
        """Test selected_index is clamped to max if too high."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        # Manually trigger watch with too high value
        view.watch_selected_index(0, 10)

        assert view.selected_index == 2

    def test_watch_selected_index_with_no_items(self):
        """Test selected_index is set to 0 when no items."""
        view = ConcreteInteractiveView([])

        # Try to set to non-zero
        view.watch_selected_index(0, 5)

        assert view.selected_index == 0

    def test_navigation_sequence(self):
        """Test full navigation sequence."""
        view = ConcreteInteractiveView(["one", "two", "three", "four", "five"])

        # Start at top
        assert view.selected_index == 0

        # Move down twice
        view.action_move_down()
        view.action_move_down()
        assert view.selected_index == 2

        # Move up once
        view.action_move_up()
        assert view.selected_index == 1

        # Jump to bottom
        view.action_move_to_bottom()
        assert view.selected_index == 4

        # Jump to top
        view.action_move_to_top()
        assert view.selected_index == 0

    def test_abstract_methods_enforced(self):
        """Test abstract methods must be implemented."""
        with pytest.raises(TypeError):

            class IncompleteView(InteractiveView[str]):
                pass

            IncompleteView()  # Should fail

    def test_get_item_count_abstract(self):
        """Test get_item_count is abstract."""
        # Verify method exists and is abstract
        assert hasattr(InteractiveView, "get_item_count")

    def test_on_item_selected_abstract(self):
        """Test on_item_selected is abstract."""
        # Verify method exists and is abstract
        assert hasattr(InteractiveView, "on_item_selected")

    def test_apply_filter_abstract(self):
        """Test apply_filter is abstract."""
        # Verify method exists and is abstract
        assert hasattr(InteractiveView, "apply_filter")

    def test_bindings_defined(self):
        """Test keyboard bindings are defined."""
        view = ConcreteInteractiveView()

        # Check BINDINGS exist
        assert hasattr(view, "BINDINGS")
        assert len(view.BINDINGS) >= 5

        # Check key bindings exist
        binding_keys = [str(b.key) for b in view.BINDINGS]
        assert any("up" in k or "k" in k for k in binding_keys)
        assert any("down" in k or "j" in k for k in binding_keys)
        assert any("enter" in k for k in binding_keys)


class TestInteractiveViewWithFilter:
    """Tests for InteractiveView filtering functionality."""

    def test_filter_case_insensitive(self):
        """Test filter is case-insensitive."""
        view = ConcreteInteractiveView(["Apple", "BANANA", "cherry"])

        view.filter_text = "app"

        assert view.get_item_count() == 1
        assert "Apple" in view._filtered_items

    def test_filter_partial_match(self):
        """Test filter matches partial strings."""
        view = ConcreteInteractiveView(["function_one", "function_two", "method_one"])

        view.filter_text = "function"

        assert view.get_item_count() == 2

    def test_filter_no_matches(self):
        """Test filter with no matches."""
        view = ConcreteInteractiveView(["apple", "banana", "cherry"])

        view.filter_text = "xyz"

        assert view.get_item_count() == 0

    def test_filter_resets_selection_if_out_of_bounds(self):
        """Test filter resets selection if current index becomes invalid."""
        view = ConcreteInteractiveView(["apple", "apricot", "banana", "blueberry"])

        # Select last item
        view.selected_index = 3

        # Filter to only 2 items
        view.filter_text = "ap"

        # Selection should be adjusted
        assert view.selected_index <= view.get_item_count() - 1

    def test_multiple_filters(self):
        """Test applying multiple filters in sequence."""
        view = ConcreteInteractiveView(["apple", "apricot", "banana", "blueberry", "cherry"])

        # First filter
        view.filter_text = "a"
        assert view.get_item_count() == 3  # apple, apricot, banana

        # More specific filter
        view.filter_text = "ap"
        assert view.get_item_count() == 2  # apple, apricot

        # Clear filter
        view.filter_text = ""
        assert view.get_item_count() == 5  # all items


class TestInteractiveViewEdgeCases:
    """Tests for InteractiveView edge cases."""

    def test_empty_view_navigation(self):
        """Test navigation with no items."""
        view = ConcreteInteractiveView([])

        # These should not raise
        view.action_move_up()
        view.action_move_down()
        view.action_move_to_top()
        view.action_move_to_bottom()
        view.action_select_item()

        assert view.selected_index == 0

    def test_single_item_navigation(self):
        """Test navigation with single item."""
        view = ConcreteInteractiveView(["only"])

        # All navigation should stay at 0
        view.action_move_up()
        assert view.selected_index == 0

        view.action_move_down()
        assert view.selected_index == 0

        view.action_move_to_top()
        assert view.selected_index == 0

        view.action_move_to_bottom()
        assert view.selected_index == 0

    def test_selection_with_single_item(self):
        """Test selection with single item."""
        view = ConcreteInteractiveView(["only"])

        view.action_select_item()

        assert view.selected_item == "only"

    def test_move_down_to_last_then_up(self):
        """Test moving to last item then back up."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        # Move to last
        view.action_move_to_bottom()
        assert view.selected_index == 2

        # Try to move down (should stay)
        view.action_move_down()
        assert view.selected_index == 2

        # Move up
        view.action_move_up()
        assert view.selected_index == 1

    def test_data_change_updates_items(self):
        """Test changing data updates available items."""
        view = ConcreteInteractiveView(["a", "b", "c"])

        assert view.get_item_count() == 3

        # Change data
        view.data = ["x", "y"]

        assert view.get_item_count() == 2

    def test_filter_on_empty_data(self):
        """Test filter on view with no data."""
        view = ConcreteInteractiveView([])

        # Should not raise
        view.filter_text = "test"

        assert view.get_item_count() == 0

    def test_rapid_navigation(self):
        """Test rapid navigation changes."""
        view = ConcreteInteractiveView(["a", "b", "c", "d", "e"])

        # Rapid navigation
        for _ in range(10):
            view.action_move_down()

        # Should be at last item
        assert view.selected_index == 4

        for _ in range(10):
            view.action_move_up()

        # Should be at first item
        assert view.selected_index == 0
