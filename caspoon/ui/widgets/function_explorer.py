"""Function explorer widget for browsing functions in a tree view."""

import logging
from typing import Any

from rich.table import Table
from rich.text import Text

from caspoon.ui.core.base import TreeNode, TreeView
from caspoon.ui.core.messages import SelectFunction
from caspoon.ui.core.models import AnalysisResults

logger = logging.getLogger(__name__)


class FunctionExplorer(TreeView[AnalysisResults]):
    """Tree view of functions organized by section.

    Displays functions grouped by their section (.text, .plt, etc.) in a
    hierarchical tree structure. Users can expand sections to view functions
    and select functions to view details.

    Keyboard Bindings (inherited from TreeView):
        - up/k: Move selection up
        - down/j: Move selection down
        - right/l: Expand current section
        - left/h: Collapse current section
        - enter: Select function
        - +: Expand all sections
        - -: Collapse all sections

    Example:
        >>> explorer = FunctionExplorer()
        >>> # Connect to AppState
        >>> app.state.subscribe("analysis_results", explorer._on_results_changed)
    """

    DEFAULT_CSS = """
    FunctionExplorer {
        height: 100%;
        border: solid green;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the function explorer.

        Args:
            **kwargs: Additional keyword arguments for TreeView
        """
        super().__init__(**kwargs)
        self._functions: list[dict[str, Any]] = []
        self._sections: dict[str, list[dict[str, Any]]] = {}
        self._filter_text = ""

    def on_mount(self) -> None:
        """Set up the explorer when mounted.

        Watches AppState for analysis results updates.
        """
        try:
            # Subscribe to analysis results changes
            if hasattr(self.app, "state"):
                # Initial data if available
                if self.app.state.analysis_results:
                    self.data = self.app.state.analysis_results
        except Exception as e:
            logger.error(f"Error mounting FunctionExplorer: {e}")

    def render_content(self, data: AnalysisResults) -> None:
        """Organize functions by section and render tree.

        Args:
            data: Analysis results containing functions list
        """
        try:
            # Extract functions from data
            self._functions = data.functions or []

            # Apply filter if set
            if self._filter_text:
                self._functions = [
                    f
                    for f in self._functions
                    if self._filter_text.lower() in f.get("name", "").lower()
                ]

            # Organize by section
            self._organize_by_section()

            # Build and display the tree
            table = self._build_tree_table()
            self.update(table)

        except Exception as e:
            logger.error(f"Error rendering FunctionExplorer: {e}", exc_info=True)
            self.update(f"[red]Error rendering tree: {e}[/]")

    def _organize_by_section(self) -> None:
        """Group functions by their section."""
        self._sections = {}
        for func in self._functions:
            section = func.get("section", ".text")
            if section not in self._sections:
                self._sections[section] = []
            self._sections[section].append(func)

        # Sort sections for consistent display
        self._sections = dict(sorted(self._sections.items()))

    def _build_tree_table(self) -> Table:
        """Build a table representation of the tree.

        Returns:
            Rich Table with tree-like structure
        """
        table = Table(
            show_header=False,
            show_edge=False,
            pad_edge=False,
            box=None,
            expand=True,
        )
        table.add_column("Item", overflow="fold")

        flat_tree = self._flatten_tree()

        if not flat_tree:
            table.add_row("[dim]No functions found[/]")
            return table

        for i, (node, level) in enumerate(flat_tree):
            # Build the row text
            text = Text()

            # Add indentation
            text.append("  " * level)

            # Add expand/collapse indicator for parent nodes
            if node.has_children:
                if node.node_id in self.expanded_nodes:
                    text.append("▼ ", style="bold cyan")
                else:
                    text.append("▶ ", style="bold cyan")
            else:
                text.append("  ")  # Indent for leaf nodes

            # Add the label
            if node.has_children:
                # Section node
                text.append(node.label, style="bold yellow")
            else:
                # Function node
                text.append(node.label, style="white")

            # Highlight if selected
            style = "reverse" if i == self.selected_index else ""
            table.add_row(text, style=style)

        return table

    def get_root_nodes(self) -> list[TreeNode]:
        """Return section nodes.

        Returns:
            List of TreeNode objects representing sections
        """
        nodes = []
        for section, funcs in self._sections.items():
            node = TreeNode(
                node_id=section,
                label=f"{section} ({len(funcs)} functions)",
                has_children=len(funcs) > 0,
                data={"type": "section", "name": section},
            )
            nodes.append(node)
        return nodes

    def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        """Return function nodes for a section.

        Args:
            node_id: Section name

        Returns:
            List of TreeNode objects representing functions
        """
        if node_id in self._sections:
            funcs = self._sections[node_id]
            return [
                TreeNode(
                    node_id=f"func_{func.get('address', i)}",
                    label=self._format_function_label(func),
                    has_children=False,
                    data={"type": "function", **func},
                )
                for i, func in enumerate(funcs)
            ]
        return []

    def _format_function_label(self, func: dict[str, Any]) -> str:
        """Format a function label for display.

        Args:
            func: Function data dictionary

        Returns:
            Formatted label string
        """
        name = func.get("name", "unknown")
        address = func.get("address", 0)

        # Truncate long names
        if len(name) > 40:
            name = name[:37] + "..."

        if address:
            return f"{name} (0x{address:08x})"
        return name

    def get_item_count(self) -> int:
        """Return number of items in flattened tree.

        Returns:
            Total number of visible nodes
        """
        return len(self._flatten_tree())

    def on_item_selected(self, index: int) -> None:
        """Handle item selection.

        If a function is selected, posts a SelectFunction message.
        If a section is selected, toggles its expansion.

        Args:
            index: Index of selected item in flattened tree
        """
        nodes = self._flatten_tree()
        if 0 <= index < len(nodes):
            node, _ = nodes[index]

            if node.has_children:
                # Section node - toggle expansion
                self.action_toggle_node()
            elif node.data and node.data.get("type") == "function":
                # Function node - post selection message
                func_data = node.data
                name = func_data.get("name", "")
                address = func_data.get("address", 0)

                logger.info(f"Function selected: {name} at 0x{address:08x}")
                self.post_message(SelectFunction(name, f"0x{address:08x}" if address else None))

                # Update details panel if available
                try:
                    details_panel = self.app.query_one("DetailsPanel")
                    details_panel.show_function_details(func_data)
                except Exception as e:
                    logger.debug(f"Could not update details panel: {e}")

    def apply_filter(self, text: str) -> None:
        """Filter functions by name.

        Args:
            text: Filter string (searches in function names)
        """
        self._filter_text = text

        # Re-render with filtered data
        if self.data is not None:
            self.render_content(self.data)

        # Reset selection if out of bounds
        count = self.get_item_count()
        if count > 0 and self.selected_index >= count:
            self.selected_index = 0
