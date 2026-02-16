"""Integration tests for base widget classes."""

from unittest.mock import Mock

import pytest

from caspoon.ui.core.base import BaseView, InteractiveView, TableView, TreeNode, TreeView
from caspoon.ui.core.models import BinaryInfo
from caspoon.ui.core.state import AppState


class BinaryInfoView(BaseView[BinaryInfo]):
    """Example view that displays BinaryInfo from AppState."""

    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.render_count = 0

    def on_mount(self):
        """Subscribe to state changes."""
        self.state.subscribe("binary_info", self._on_binary_info_changed)

    def _on_binary_info_changed(self, new):
        """Update data when state changes."""
        self.data = new

    def render_content(self, data: BinaryInfo) -> None:
        """Render binary info."""
        self.render_count += 1
        self.update(f"Path: {data.path}")


class FunctionListView(InteractiveView[list[dict]]):
    """Example list view with selection."""

    def __init__(self):
        super().__init__()
        self._items = []
        self._filtered_items = []
        self.selected_function = None

    def render_content(self, data: list[dict]) -> None:
        """Render function list."""
        self._items = data
        self._filtered_items = data[:]
        self.update(f"Functions: {len(data)}")

    def get_item_count(self) -> int:
        """Return filtered item count."""
        return len(self._filtered_items)

    def on_item_selected(self, index: int) -> None:
        """Handle function selection."""
        if 0 <= index < len(self._filtered_items):
            self.selected_function = self._filtered_items[index]

    def apply_filter(self, text: str) -> None:
        """Filter functions by name."""
        if not text:
            self._filtered_items = self._items[:]
        else:
            self._filtered_items = [
                f for f in self._items if text.lower() in f.get("name", "").lower()
            ]


class SymbolTableView(TableView[list[dict]]):
    """Example table view with sorting."""

    def __init__(self):
        super().__init__()
        self._items = []
        self._filtered_items = []

    def render_content(self, data: list[dict]) -> None:
        """Render symbol table."""
        self._items = data
        self._filtered_items = data[:]
        self._apply_sort()
        table = self._build_rich_table()
        self.update(table)

    def get_item_count(self) -> int:
        """Return filtered item count."""
        return len(self._filtered_items)

    def on_item_selected(self, index: int) -> None:
        """Handle symbol selection."""
        pass

    def apply_filter(self, text: str) -> None:
        """Filter symbols."""
        if not text:
            self._filtered_items = self._items[:]
        else:
            self._filtered_items = [
                s for s in self._items if text.lower() in s.get("name", "").lower()
            ]
        self._apply_sort()

    def get_columns(self) -> list[str]:
        """Return column names."""
        return ["Address", "Name", "Size"]

    def get_row_data(self, index: int) -> list[str]:
        """Return row data."""
        if 0 <= index < len(self._filtered_items):
            item = self._filtered_items[index]
            return [item.get("addr", ""), item.get("name", ""), str(item.get("size", 0))]
        return ["", "", ""]

    def _apply_sort(self):
        """Apply current sort to filtered items."""
        if self.sort_column:
            reverse = self.sort_descending
            if self.sort_column == "Address":
                self._filtered_items.sort(key=lambda x: x.get("addr", ""), reverse=reverse)
            elif self.sort_column == "Name":
                self._filtered_items.sort(key=lambda x: x.get("name", ""), reverse=reverse)
            elif self.sort_column == "Size":
                self._filtered_items.sort(key=lambda x: x.get("size", 0), reverse=reverse)

    def watch_sort_column(self, old, new):
        """Re-sort when column changes."""
        if self.data:
            self._apply_sort()
            if self.data:
                table = self._build_rich_table()
                self.update(table)

    def watch_sort_descending(self, old, new):
        """Re-sort when direction changes."""
        if self.data:
            self._apply_sort()
            if self.data:
                table = self._build_rich_table()
                self.update(table)


class CallGraphTreeView(TreeView[dict]):
    """Example tree view for call graph."""

    def __init__(self):
        super().__init__()
        self._graph = {}

    def render_content(self, data: dict) -> None:
        """Render call graph."""
        self._graph = data
        self.update(f"Functions: {len(data.get('nodes', {}))}")

    def get_item_count(self) -> int:
        """Return visible node count."""
        return len(self._flatten_tree())

    def on_item_selected(self, index: int) -> None:
        """Handle node selection."""
        pass

    def apply_filter(self, text: str) -> None:
        """Filter not implemented."""
        pass

    def get_root_nodes(self) -> list[TreeNode]:
        """Return root functions."""
        roots = self._graph.get("roots", [])
        return [
            TreeNode(
                node_id=node["id"],
                label=node["name"],
                has_children=len(node.get("calls", [])) > 0,
                data=node,
            )
            for node in roots
        ]

    def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        """Return called functions."""
        nodes = self._graph.get("nodes", {})
        node = nodes.get(node_id, {})
        calls = node.get("calls", [])
        return [
            TreeNode(
                node_id=call["id"],
                label=call["name"],
                has_children=len(call.get("calls", [])) > 0,
                data=call,
            )
            for call in calls
        ]


class TestBaseViewIntegration:
    """Integration tests for BaseView with AppState."""

    def test_baseview_subscribes_to_state(self):
        """Test BaseView can subscribe to AppState changes."""
        state = AppState()
        view = BinaryInfoView(state)

        # Simulate mount
        view.on_mount()

        # Change state
        binary_info = BinaryInfo(path="/test/binary")
        state.binary_info = binary_info

        # View should receive update
        assert view.data == binary_info

    def test_baseview_renders_on_state_change(self):
        """Test BaseView renders when state changes."""
        state = AppState()
        view = BinaryInfoView(state)
        view.on_mount()

        initial_count = view.render_count

        # Change state
        state.binary_info = BinaryInfo(path="/test/binary")

        # Should have rendered
        assert view.render_count > initial_count

    def test_baseview_multiple_state_changes(self):
        """Test BaseView handles multiple state changes."""
        state = AppState()
        view = BinaryInfoView(state)
        view.on_mount()

        # Multiple changes
        state.binary_info = BinaryInfo(path="/test/bin1")
        assert view.data.path == "/test/bin1"

        state.binary_info = BinaryInfo(path="/test/bin2")
        assert view.data.path == "/test/bin2"

        state.binary_info = BinaryInfo(path="/test/bin3")
        assert view.data.path == "/test/bin3"


class TestInteractiveViewIntegration:
    """Integration tests for InteractiveView selection flow."""

    def test_interactiveview_selection_flow(self):
        """Test complete selection flow."""
        functions = [
            {"name": "main", "addr": "0x1000"},
            {"name": "foo", "addr": "0x2000"},
            {"name": "bar", "addr": "0x3000"},
        ]
        view = FunctionListView()
        view.data = functions

        # Navigate and select
        view.action_move_down()
        assert view.selected_index == 1

        view.action_select_item()
        assert view.selected_function == functions[1]
        assert view.selected_function["name"] == "foo"

    def test_interactiveview_filter_and_select(self):
        """Test filtering then selecting."""
        functions = [
            {"name": "test_one", "addr": "0x1000"},
            {"name": "test_two", "addr": "0x2000"},
            {"name": "other", "addr": "0x3000"},
        ]
        view = FunctionListView()
        view.data = functions

        # Filter
        view.filter_text = "test"
        assert view.get_item_count() == 2

        # Select from filtered list
        view.selected_index = 0
        view.action_select_item()
        assert view.selected_function["name"] == "test_one"

    def test_interactiveview_navigation_boundaries(self):
        """Test navigation respects boundaries."""
        functions = [{"name": f"func_{i}", "addr": f"0x{i}000"} for i in range(5)]
        view = FunctionListView()
        view.data = functions

        # Try to go past bottom
        view.action_move_to_bottom()
        assert view.selected_index == 4
        view.action_move_down()  # Should stay at 4
        assert view.selected_index == 4

        # Try to go past top
        view.action_move_to_top()
        assert view.selected_index == 0
        view.action_move_up()  # Should stay at 0
        assert view.selected_index == 0


class TestTableViewIntegration:
    """Integration tests for TableView with sorting and filtering."""

    def test_tableview_sort_and_filter(self):
        """Test sorting and filtering work together."""
        symbols = [
            {"name": "zzz", "addr": "0x3000", "size": 10},
            {"name": "aaa", "addr": "0x1000", "size": 30},
            {"name": "mmm", "addr": "0x2000", "size": 20},
        ]
        view = SymbolTableView()
        view.data = symbols

        # Sort by name ascending
        view.action_sort_by_column("Name")
        assert view.sort_column == "Name"
        assert view._filtered_items[0]["name"] == "aaa"
        assert view._filtered_items[2]["name"] == "zzz"

        # Filter
        view.filter_text = "mm"
        assert view.get_item_count() == 1
        assert view._filtered_items[0]["name"] == "mmm"

    def test_tableview_sort_toggle(self):
        """Test sort direction toggle."""
        symbols = [
            {"name": "b", "addr": "0x2000", "size": 20},
            {"name": "a", "addr": "0x1000", "size": 10},
            {"name": "c", "addr": "0x3000", "size": 30},
        ]
        view = SymbolTableView()
        view.data = symbols

        # Sort ascending
        view.action_sort_by_column("Name")
        assert view._filtered_items[0]["name"] == "a"
        assert view._filtered_items[2]["name"] == "c"

        # Toggle to descending
        view.action_sort_by_column("Name")
        assert view._filtered_items[0]["name"] == "c"
        assert view._filtered_items[2]["name"] == "a"

    def test_tableview_selection_with_sort(self):
        """Test selection is maintained across sorts."""
        symbols = [
            {"name": "z", "addr": "0x3000", "size": 30},
            {"name": "a", "addr": "0x1000", "size": 10},
            {"name": "m", "addr": "0x2000", "size": 20},
        ]
        view = SymbolTableView()
        view.data = symbols

        # Select first (unsorted)
        view.selected_index = 0
        assert view.selected_index == 0

        # Sort - selection stays valid
        view.action_sort_by_column("Name")
        assert view.selected_index == 0  # Still at 0, but different item now

    def test_tableview_render_with_highlights(self):
        """Test table renders with selection highlighting."""
        symbols = [
            {"name": "sym1", "addr": "0x1000", "size": 10},
            {"name": "sym2", "addr": "0x2000", "size": 20},
        ]
        view = SymbolTableView()
        view.data = symbols

        view.selected_index = 1
        table = view._build_rich_table()

        # Verify table was built (can't easily check styling)
        from rich.table import Table

        assert isinstance(table, Table)


class TestTreeViewIntegration:
    """Integration tests for TreeView navigation and expansion."""

    def test_treeview_expand_and_navigate(self):
        """Test expanding nodes and navigating."""
        graph = {
            "roots": [{"id": "main", "name": "main", "calls": [{"id": "foo", "name": "foo"}]}],
            "nodes": {
                "main": {
                    "calls": [
                        {"id": "foo", "name": "foo", "calls": []},
                        {"id": "bar", "name": "bar", "calls": []},
                    ]
                },
                "foo": {"calls": []},
                "bar": {"calls": []},
            },
        }
        view = CallGraphTreeView()
        view.data = graph

        # Initially collapsed
        assert view.get_item_count() == 1

        # Expand root
        view.action_toggle_node()
        assert "main" in view.expanded_nodes

        # Now can see children
        count = view.get_item_count()
        assert count > 1

        # Navigate to child
        view.action_move_down()
        assert view.selected_index == 1

    def test_treeview_collapse_hides_children(self):
        """Test collapsing node hides children."""
        graph = {
            "roots": [{"id": "root", "name": "root", "calls": [{"id": "child", "name": "child"}]}],
            "nodes": {"root": {"calls": [{"id": "child", "name": "child", "calls": []}]}},
        }
        view = CallGraphTreeView()
        view.data = graph

        # Expand
        view.expanded_nodes = {"root"}
        expanded_count = view.get_item_count()
        assert expanded_count == 2

        # Collapse
        view.action_toggle_node()
        collapsed_count = view.get_item_count()
        assert collapsed_count == 1

    def test_treeview_expand_all_flow(self):
        """Test expand all then collapse all."""
        graph = {
            "roots": [{"id": "r1", "name": "r1", "calls": [{"id": "c1", "name": "c1"}]}],
            "nodes": {
                "r1": {"calls": [{"id": "c1", "name": "c1", "calls": []}]},
                "c1": {"calls": []},
            },
        }
        view = CallGraphTreeView()
        view.data = graph

        # Expand all
        view.action_expand_all()
        expanded = view.get_item_count()

        # Collapse all
        view.action_collapse_all()
        collapsed = view.get_item_count()

        assert collapsed < expanded

    def test_treeview_navigation_respects_expansion(self):
        """Test navigation only sees visible nodes."""
        graph = {
            "roots": [
                {"id": "r1", "name": "r1", "calls": [{"id": "c1", "name": "c1"}]},
                {"id": "r2", "name": "r2", "calls": []},
            ],
            "nodes": {
                "r1": {"calls": [{"id": "c1", "name": "c1", "calls": []}]},
                "c1": {"calls": []},
                "r2": {"calls": []},
            },
        }
        view = CallGraphTreeView()
        view.data = graph

        # Collapsed - 2 roots visible
        assert view.get_item_count() == 2

        # Navigate to bottom
        view.action_move_to_bottom()
        assert view.selected_index == 1  # r2

        # Expand first root
        view.selected_index = 0
        view.action_toggle_node()

        # Now 3 visible: r1, c1, r2
        assert view.get_item_count() == 3

        # Navigate to bottom again
        view.action_move_to_bottom()
        assert view.selected_index == 2  # r2


class TestCrossWidgetIntegration:
    """Tests for multiple widgets working together."""

    def test_state_updates_multiple_views(self):
        """Test AppState change updates multiple views."""
        state = AppState()
        view1 = BinaryInfoView(state)
        view2 = BinaryInfoView(state)

        view1.on_mount()
        view2.on_mount()

        # Change state once
        binary = BinaryInfo(path="/test/file")
        state.binary_info = binary

        # Both views should update
        assert view1.data == binary
        assert view2.data == binary

    def test_filter_synchronization(self):
        """Test two views can share filter state."""
        data = [
            {"name": "apple", "value": "1"},
            {"name": "banana", "value": "2"},
            {"name": "apricot", "value": "3"},
        ]

        view1 = FunctionListView()
        view2 = FunctionListView()

        view1.data = data
        view2.data = data

        # Apply same filter
        view1.filter_text = "ap"
        view2.filter_text = "ap"

        # Both should show same count
        assert view1.get_item_count() == view2.get_item_count()

    def test_independent_selections(self):
        """Test two views maintain independent selections."""
        data = [{"name": f"item{i}", "addr": f"0x{i}000"} for i in range(5)]

        view1 = FunctionListView()
        view2 = FunctionListView()

        view1.data = data
        view2.data = data

        # Different selections
        view1.selected_index = 1
        view2.selected_index = 3

        assert view1.selected_index != view2.selected_index
