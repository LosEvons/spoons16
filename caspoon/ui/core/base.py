"""Base widget classes for the Caspoon TUI.

This module provides reusable base widget classes that implement standard patterns
for reactive data binding, keyboard interaction, and content rendering:

- BaseView: Foundation for all views with reactive data binding
- InteractiveView: Adds keyboard navigation and selection
- TableView: Specialized for tabular data with sorting
- TreeView: For hierarchical data display

All views should inherit from one of these base classes to ensure consistent
behavior and reduce code duplication.
"""

import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from rich.table import Table
from rich.tree import Tree
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Create a compatible metaclass that combines Textual's metaclass with ABCMeta
class WidgetMeta(type(Static), ABCMeta):  # type: ignore
    """Metaclass that combines Textual's widget metaclass with ABCMeta."""

    pass


class BaseView(Static, Generic[T], metaclass=WidgetMeta):
    """Base class for all Caspoon views with reactive data binding.

    Provides automatic re-rendering when data changes, lifecycle hooks,
    and error handling for render failures. All views should inherit from
    this class to ensure consistent behavior.

    Type Parameters:
        T: The type of data this view displays (e.g., BinaryInfo, list[dict])

    Attributes:
        data: Reactive property that triggers render_content() when changed

    Subclasses must implement:
        - render_content(data: T) -> None: Render the view content

    Example:
        >>> class FileInfoView(BaseView[BinaryInfo]):
        ...     def on_mount(self):
        ...         # Subscribe to state changes
        ...         self.app.state.subscribe("binary_info", self._on_data_changed)
        ...
        ...     def _on_data_changed(self, old, new):
        ...         self.data = new  # Triggers render_content()
        ...
        ...     def render_content(self, data: BinaryInfo) -> None:
        ...         # Build and display content
        ...         table = self._build_table(data)
        ...         self.update(table)
    """

    # Reactive data - triggers render_content() when changed
    data: reactive[T | None] = reactive(None)

    def watch_data(self, old_value: T | None, new_value: T | None) -> None:
        """Called automatically when data changes.

        Triggers render_content() with the new data. If render_content()
        raises an exception, it's caught and displayed as an error message.

        Args:
            old_value: Previous data value
            new_value: New data value (triggers render if not None)
        """
        if new_value is not None:
            try:
                self.render_content(new_value)
            except Exception as e:
                logger.error(f"Error rendering {self.__class__.__name__}: {e}", exc_info=True)
                self.update(f"[red]Error rendering view: {e}[/]")

    @abstractmethod
    def render_content(self, data: T) -> None:
        """Render the view content with the given data.

        Must call self.update() with a Rich renderable object (Table, Tree,
        Panel, etc.) to update the display.

        Args:
            data: The data to render

        Example:
            >>> def render_content(self, data: BinaryInfo):
            ...     table = Table(title="Binary Info")
            ...     table.add_column("Property")
            ...     table.add_column("Value")
            ...     table.add_row("Path", data.path)
            ...     self.update(table)
        """
        pass

    def on_show(self) -> None:
        """Called when view becomes visible.

        Override this for view-specific logic when shown (e.g., refresh data,
        resume updates). Default implementation does nothing.
        """
        pass

    def on_hide(self) -> None:
        """Called when view becomes hidden.

        Override this for cleanup when hidden (e.g., pause updates, clear
        resources). Default implementation does nothing.
        """
        pass


class InteractiveView(BaseView[T], metaclass=WidgetMeta):
    """Base class for views with keyboard/mouse interaction.

    Extends BaseView with selection state, keyboard navigation, and filtering
    capabilities. Ideal for list views, tables, and any view with selectable items.

    Additional Attributes:
        selected_index: Currently selected item index (0-based)
        filter_text: Current filter string (triggers apply_filter when changed)

    Keyboard Bindings:
        - up/k: Move selection up
        - down/j: Move selection down
        - home: Move to first item
        - end: Move to last item
        - enter: Select current item

    Subclasses must implement (in addition to render_content):
        - get_item_count() -> int: Return number of items (after filtering)
        - on_item_selected(index: int) -> None: Handle item selection
        - apply_filter(text: str) -> None: Apply filter and re-render

    Example:
        >>> class FunctionListView(InteractiveView[list[Function]]):
        ...     BINDINGS = [
        ...         Binding("enter", "select_item", "Select Function"),
        ...     ]
        ...
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._filtered_items = []
        ...
        ...     def get_item_count(self) -> int:
        ...         return len(self._filtered_items)
        ...
        ...     def on_item_selected(self, index: int) -> None:
        ...         func = self._filtered_items[index]
        ...         self.post_message(SelectFunction(func.name))
        ...
        ...     def apply_filter(self, text: str) -> None:
        ...         if not self.data:
        ...             self._filtered_items = []
        ...             return
        ...         self._filtered_items = [
        ...             f for f in self.data
        ...             if text.lower() in f.name.lower()
        ...         ]
        ...         self.render_content(self.data)
        ...
        ...     def render_content(self, data: list[Function]) -> None:
        ...         table = Table()
        ...         for i, func in enumerate(self._filtered_items):
        ...             style = "reverse" if i == self.selected_index else ""
        ...             table.add_row(func.name, style=style)
        ...         self.update(table)
    """

    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("home", "move_to_top", "First", show=False),
        Binding("end", "move_to_bottom", "Last", show=False),
        Binding("enter", "select_item", "Select", show=True),
    ]

    # Current selection index (0-based)
    selected_index: reactive[int] = reactive(0)

    # Current filter text
    filter_text: reactive[str] = reactive("")

    @abstractmethod
    def get_item_count(self) -> int:
        """Return number of items available (after filtering).

        Returns:
            Number of items that can be selected. Return 0 if no items.

        Example:
            >>> def get_item_count(self) -> int:
            ...     return len(self._filtered_items)
        """
        pass

    @abstractmethod
    def on_item_selected(self, index: int) -> None:
        """Handle item selection at the given index.

        Called when user presses Enter. Typically posts a message or updates
        state to notify other components of the selection.

        Args:
            index: Index of selected item (guaranteed to be valid)

        Example:
            >>> def on_item_selected(self, index: int) -> None:
            ...     item = self._filtered_items[index]
            ...     self.post_message(ItemSelected(item.id))
        """
        pass

    @abstractmethod
    def apply_filter(self, text: str) -> None:
        """Apply filter to items and re-render the view.

        Called automatically when filter_text changes. Should update internal
        filtered item list and call render_content() to refresh display.

        Args:
            text: Filter string (may be empty for no filter)

        Example:
            >>> def apply_filter(self, text: str) -> None:
            ...     if not self.data:
            ...         self._filtered_items = []
            ...         return
            ...     self._filtered_items = [
            ...         item for item in self.data
            ...         if text.lower() in item.name.lower()
            ...     ]
            ...     # Reset selection if filter changed item count
            ...     if self.selected_index >= len(self._filtered_items):
            ...         self.selected_index = 0
            ...     self.render_content(self.data)
        """
        pass

    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """Ensure selected_index stays within valid range.

        Called automatically when selected_index changes. Clamps the value
        to [0, get_item_count()-1].

        Args:
            old_value: Previous index
            new_value: New index (may be out of bounds)
        """
        count = self.get_item_count()
        if count == 0:
            # No items - set to 0
            if new_value != 0:
                self.selected_index = 0
        elif new_value < 0:
            # Below minimum - clamp to 0
            self.selected_index = 0
        elif new_value >= count:
            # Above maximum - clamp to last item
            self.selected_index = count - 1

    def watch_filter_text(self, old_value: str, new_value: str) -> None:
        """Apply filter when filter_text changes.

        Called automatically when filter_text is modified. Delegates to
        apply_filter() for the actual filtering logic.

        Args:
            old_value: Previous filter text
            new_value: New filter text
        """
        self.apply_filter(new_value)

    def action_move_up(self) -> None:
        """Move selection up by one item.

        Bound to: up arrow, k (vim-style)
        """
        if self.selected_index > 0:
            self.selected_index -= 1

    def action_move_down(self) -> None:
        """Move selection down by one item.

        Bound to: down arrow, j (vim-style)
        """
        count = self.get_item_count()
        if count > 0 and self.selected_index < count - 1:
            self.selected_index += 1

    def action_move_to_top(self) -> None:
        """Move to the first item.

        Bound to: home
        """
        if self.get_item_count() > 0:
            self.selected_index = 0

    def action_move_to_bottom(self) -> None:
        """Move to the last item.

        Bound to: end
        """
        count = self.get_item_count()
        if count > 0:
            self.selected_index = count - 1

    def action_select_item(self) -> None:
        """Select the current item.

        Bound to: enter

        Calls on_item_selected() with the current selected_index.
        """
        if self.get_item_count() > 0:
            self.on_item_selected(self.selected_index)


class TableView(InteractiveView[T], metaclass=WidgetMeta):
    """Base class for table views with column sorting.

    Extends InteractiveView with column sorting capabilities. Ideal for
    displaying tabular data where users can sort by different columns.

    Additional Attributes:
        sort_column: Name of currently sorted column (None if not sorted)
        sort_descending: Whether sort is descending (True) or ascending (False)

    Subclasses must implement (in addition to InteractiveView methods):
        - get_columns() -> list[str]: Return list of column names
        - get_row_data(index: int) -> list[str]: Return data for row at index

    Subclasses should:
        - Implement sorting logic in their data management
        - Call action_sort_by_column(column) to trigger sorting
        - Use _build_rich_table() helper to build table with highlighting

    Example:
        >>> class SymbolTableView(TableView[list[Symbol]]):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._filtered_items = []
        ...
        ...     def get_columns(self) -> list[str]:
        ...         return ["Address", "Name", "Type", "Size"]
        ...
        ...     def get_row_data(self, index: int) -> list[str]:
        ...         sym = self._filtered_items[index]
        ...         return [sym.address, sym.name, sym.type, str(sym.size)]
        ...
        ...     def render_content(self, data: list[Symbol]) -> None:
        ...         table = self._build_rich_table()
        ...         self.update(table)
    """

    # Currently sorted column name (None if no sort)
    sort_column: reactive[str | None] = reactive(None)

    # Sort direction (False = ascending, True = descending)
    sort_descending: reactive[bool] = reactive(False)

    @abstractmethod
    def get_columns(self) -> list[str]:
        """Return list of column names for the table.

        Returns:
            List of column names in display order

        Example:
            >>> def get_columns(self) -> list[str]:
            ...     return ["Address", "Name", "Type", "Size"]
        """
        pass

    @abstractmethod
    def get_row_data(self, index: int) -> list[str]:
        """Return data for the row at the given index.

        Args:
            index: Row index (0-based, after filtering/sorting)

        Returns:
            List of strings, one per column (must match get_columns() length)

        Example:
            >>> def get_row_data(self, index: int) -> list[str]:
            ...     item = self._filtered_items[index]
            ...     return [item.addr, item.name, item.type, str(item.size)]
        """
        pass

    def action_sort_by_column(self, column: str) -> None:
        """Sort by the specified column.

        If already sorting by this column, toggles sort direction.
        If different column, sorts ascending by new column.

        Args:
            column: Name of column to sort by (must be in get_columns())

        Note:
            This method only updates the sort state. Subclasses must implement
            the actual sorting logic by watching sort_column/sort_descending
            or by calling this as part of their sort implementation.

        Example:
            >>> def watch_sort_column(self, old, new):
            ...     if new:
            ...         self._sort_items()
            ...         self.render_content(self.data)
        """
        if self.sort_column == column:
            # Same column - toggle direction
            self.sort_descending = not self.sort_descending
        else:
            # New column - sort ascending
            self.sort_column = column
            self.sort_descending = False

    def _build_rich_table(self) -> Table:
        """Build a Rich Table with current data and highlighting.

        Helper method that creates a table with:
        - Columns from get_columns()
        - Rows from get_row_data()
        - Selection highlighting on selected_index
        - Sort indicators in column headers

        Returns:
            Rich Table ready to pass to self.update()

        Example:
            >>> def render_content(self, data):
            ...     table = self._build_rich_table()
            ...     self.update(table)
        """
        table = Table(show_header=True, header_style="bold cyan")

        # Add columns with sort indicators
        for col_name in self.get_columns():
            header = col_name
            if self.sort_column == col_name:
                indicator = "↓" if self.sort_descending else "↑"
                header = f"{col_name} {indicator}"
            table.add_column(header)

        # Add rows with selection highlighting
        count = self.get_item_count()
        for i in range(count):
            row_data = self.get_row_data(i)
            style = "reverse" if i == self.selected_index else ""
            table.add_row(*row_data, style=style)

        return table


@dataclass
class TreeNode:
    """Node in a tree structure.

    Attributes:
        node_id: Unique identifier for this node
        label: Display label for the node
        has_children: Whether this node has children (for expand/collapse)
        data: Optional arbitrary data associated with node
    """

    node_id: str
    label: str
    has_children: bool
    data: Any = None


class TreeView(InteractiveView[T], metaclass=WidgetMeta):
    """Base class for tree/hierarchical views.

    Extends InteractiveView with node expansion/collapse capabilities.
    Ideal for displaying hierarchical data like file trees, call graphs, etc.

    Additional Attributes:
        expanded_nodes: Set of expanded node IDs

    Additional Keyboard Bindings:
        - right/l: Expand current node
        - left/h: Collapse current node
        - +: Expand all nodes
        - -: Collapse all nodes

    Subclasses must implement (in addition to InteractiveView methods):
        - get_root_nodes() -> list[TreeNode]: Return top-level nodes
        - get_child_nodes(node_id: str) -> list[TreeNode]: Return children

    The tree is rendered as a flat list where expanded nodes show their children.
    Navigation works on this flattened view.

    Example:
        >>> class FileTreeView(TreeView[FileSystem]):
        ...     def get_root_nodes(self) -> list[TreeNode]:
        ...         if not self.data:
        ...             return []
        ...         return [
        ...             TreeNode(
        ...                 node_id=f.path,
        ...                 label=f.name,
        ...                 has_children=f.is_dir,
        ...                 data=f
        ...             )
        ...             for f in self.data.root_files
        ...         ]
        ...
        ...     def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        ...         dir_obj = self.data.get_dir(node_id)
        ...         return [
        ...             TreeNode(
        ...                 node_id=f.path,
        ...                 label=f.name,
        ...                 has_children=f.is_dir,
        ...                 data=f
        ...             )
        ...             for f in dir_obj.children
        ...         ]
        ...
        ...     def render_content(self, data: FileSystem) -> None:
        ...         flat_tree = self._flatten_tree()
        ...         table = Table(show_header=False)
        ...         table.add_column("Item")
        ...         for node, indent in flat_tree:
        ...             prefix = "  " * indent
        ...             icon = "▼" if node.node_id in self.expanded_nodes else "▶"
        ...             label = f"{prefix}{icon} {node.label}"
        ...             table.add_row(label)
        ...         self.update(table)
    """

    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("home", "move_to_top", "First", show=False),
        Binding("end", "move_to_bottom", "Last", show=False),
        Binding("enter", "select_item", "Select", show=True),
        Binding("right,l", "toggle_node", "Expand/Collapse", show=False),
        Binding("left,h", "toggle_node", "Expand/Collapse", show=False),
        Binding("+", "expand_all", "Expand All", show=False),
        Binding("-", "collapse_all", "Collapse All", show=False),
    ]

    # Set of expanded node IDs
    expanded_nodes: reactive[set[str]] = reactive(set, init=False)

    def __init__(self, **kwargs) -> None:
        """Initialize TreeView with empty expansion state."""
        super().__init__(**kwargs)
        self.expanded_nodes = set()

    @abstractmethod
    def get_root_nodes(self) -> list[TreeNode]:
        """Return top-level tree nodes.

        Returns:
            List of root nodes (nodes with no parent)

        Example:
            >>> def get_root_nodes(self) -> list[TreeNode]:
            ...     return [
            ...         TreeNode("root", "Root", True, self.data.root)
            ...     ]
        """
        pass

    @abstractmethod
    def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        """Return children of the specified node.

        Args:
            node_id: ID of parent node

        Returns:
            List of child nodes (empty list if no children)

        Example:
            >>> def get_child_nodes(self, node_id: str) -> list[TreeNode]:
            ...     parent = self.data.get_node(node_id)
            ...     return [
            ...         TreeNode(child.id, child.name, child.has_children)
            ...         for child in parent.children
            ...     ]
        """
        pass

    def action_toggle_node(self) -> None:
        """Expand or collapse the current node.

        Bound to: right/l (expand), left/h (collapse), enter

        If node is collapsed, expands it. If expanded, collapses it.
        Only works on nodes with has_children=True.
        """
        nodes = self._flatten_tree()
        if 0 <= self.selected_index < len(nodes):
            node, _ = nodes[self.selected_index]
            if node.has_children:
                if node.node_id in self.expanded_nodes:
                    # Collapse
                    self.expanded_nodes = self.expanded_nodes - {node.node_id}
                else:
                    # Expand
                    self.expanded_nodes = self.expanded_nodes | {node.node_id}
                # Trigger re-render by updating data watcher
                if self.data is not None:
                    self.render_content(self.data)

    def action_expand_all(self) -> None:
        """Expand all nodes in the tree.

        Bound to: +

        Note: May be slow for very large trees.
        """
        # Collect all nodes with children
        all_expandable = set()

        def collect_expandable(nodes: list[TreeNode]) -> None:
            for node in nodes:
                if node.has_children:
                    all_expandable.add(node.node_id)
                    children = self.get_child_nodes(node.node_id)
                    collect_expandable(children)

        collect_expandable(self.get_root_nodes())
        self.expanded_nodes = all_expandable
        if self.data is not None:
            self.render_content(self.data)

    def action_collapse_all(self) -> None:
        """Collapse all nodes in the tree.

        Bound to: -
        """
        self.expanded_nodes = set()
        if self.data is not None:
            self.render_content(self.data)

    def _flatten_tree(self) -> list[tuple[TreeNode, int]]:
        """Flatten tree into a list for rendering.

        Walks the tree depth-first, including only expanded nodes' children.
        Returns a list of (node, indent_level) tuples suitable for rendering
        as a flat list with indentation.

        Returns:
            List of (TreeNode, indent_level) tuples

        Example:
            >>> flat = self._flatten_tree()
            >>> for node, level in flat:
            ...     print("  " * level + node.label)
        """
        result: list[tuple[TreeNode, int]] = []

        def walk(nodes: list[TreeNode], level: int) -> None:
            for node in nodes:
                result.append((node, level))
                if node.has_children and node.node_id in self.expanded_nodes:
                    children = self.get_child_nodes(node.node_id)
                    walk(children, level + 1)

        walk(self.get_root_nodes(), 0)
        return result

    def _build_rich_tree(self) -> Tree:
        """Build a Rich Tree with current data.

        Helper method that creates a Rich Tree object suitable for display.
        Respects expanded_nodes state.

        Returns:
            Rich Tree ready to pass to self.update()

        Example:
            >>> def render_content(self, data):
            ...     tree = self._build_rich_tree()
            ...     self.update(tree)
        """
        tree = Tree("Root")

        def build_branch(parent_tree: Tree, nodes: list[TreeNode]) -> None:
            for node in nodes:
                branch = parent_tree.add(node.label)
                if node.has_children and node.node_id in self.expanded_nodes:
                    children = self.get_child_nodes(node.node_id)
                    build_branch(branch, children)

        build_branch(tree, self.get_root_nodes())
        return tree
