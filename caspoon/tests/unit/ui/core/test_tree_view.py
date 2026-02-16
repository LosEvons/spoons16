"""Unit tests for TreeView widget."""

import pytest

from caspoon.ui.core.base import TreeNode, TreeView


class ConcreteTreeView(TreeView[dict]):
    """Concrete implementation of TreeView for testing."""

    def __init__(self, tree_data: dict | None = None):
        super().__init__()
        self._tree_data = tree_data or {}

    def render_content(self, data: dict) -> None:
        """Mock implementation."""
        self._tree_data = data
        # Build flat list for display
        flat = self._flatten_tree()
        self.update(f"Tree nodes: {len(flat)}")

    def get_item_count(self) -> int:
        """Return count of visible nodes."""
        return len(self._flatten_tree())

    def on_item_selected(self, index: int) -> None:
        """Handle selection."""
        pass

    def apply_filter(self, text: str) -> None:
        """Filter not implemented for basic tree."""
        pass

    def get_root_nodes(self) -> list[TreeNode]:
        """Return root nodes."""
        if not self._tree_data:
            return []

        roots = self._tree_data.get("roots", [])
        return [
            TreeNode(
                node_id=node["id"],
                label=node["label"],
                has_children=node.get("has_children", False),
                data=node,
            )
            for node in roots
        ]

    def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        """Return children of node."""
        # Find node in tree_data
        all_nodes = self._tree_data.get("all_nodes", {})
        node_data = all_nodes.get(node_id, {})
        children = node_data.get("children", [])

        return [
            TreeNode(
                node_id=child["id"],
                label=child["label"],
                has_children=child.get("has_children", False),
                data=child,
            )
            for child in children
        ]


class TestTreeNode:
    """Tests for TreeNode dataclass."""

    def test_treenode_creation(self):
        """Test TreeNode can be created."""
        node = TreeNode(node_id="n1", label="Node 1", has_children=True)

        assert node.node_id == "n1"
        assert node.label == "Node 1"
        assert node.has_children is True
        assert node.data is None

    def test_treenode_with_data(self):
        """Test TreeNode with data."""
        data = {"key": "value"}
        node = TreeNode(node_id="n1", label="Node", has_children=False, data=data)

        assert node.data == data

    def test_treenode_equality(self):
        """Test TreeNode equality."""
        node1 = TreeNode("n1", "Node", True, {"a": 1})
        node2 = TreeNode("n1", "Node", True, {"a": 1})

        assert node1 == node2


class TestTreeView:
    """Tests for TreeView class."""

    def test_initialization(self):
        """Test TreeView initializes with correct defaults."""
        view = ConcreteTreeView()

        assert view.selected_index == 0
        assert view.filter_text == ""
        assert len(view.expanded_nodes) == 0

    def test_initialization_with_data(self):
        """Test TreeView can be initialized with tree data."""
        tree_data = {
            "roots": [
                {"id": "root1", "label": "Root 1", "has_children": False},
                {"id": "root2", "label": "Root 2", "has_children": False},
            ],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)

        assert view.get_item_count() == 2

    def test_toggle_node_expands(self):
        """Test toggling node expands it."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {
                    "children": [
                        {"id": "child1", "label": "Child 1", "has_children": False}
                    ]
                }
            },
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Initially collapsed
        assert "root" not in view.expanded_nodes
        assert view.get_item_count() == 1

        # Toggle to expand
        view.action_toggle_node()

        # Should be expanded
        assert "root" in view.expanded_nodes

    def test_toggle_node_collapses(self):
        """Test toggling expanded node collapses it."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {
                    "children": [
                        {"id": "child1", "label": "Child 1", "has_children": False}
                    ]
                }
            },
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Expand first
        view.expanded_nodes = {"root"}
        assert view.get_item_count() == 2

        # Toggle to collapse
        view.action_toggle_node()

        # Should be collapsed
        assert "root" not in view.expanded_nodes

    def test_flatten_tree_root_only(self):
        """Test _flatten_tree with no expanded nodes."""
        tree_data = {
            "roots": [
                {"id": "root1", "label": "Root 1", "has_children": False},
                {"id": "root2", "label": "Root 2", "has_children": True},
            ],
            "all_nodes": {
                "root2": {"children": [{"id": "child", "label": "Child", "has_children": False}]}
            },
        }
        view = ConcreteTreeView(tree_data)

        flat = view._flatten_tree()

        # Should only have roots
        assert len(flat) == 2
        assert flat[0][0].node_id == "root1"
        assert flat[1][0].node_id == "root2"
        assert flat[0][1] == 0  # indent level
        assert flat[1][1] == 0  # indent level

    def test_flatten_tree_with_expanded_children(self):
        """Test _flatten_tree with expanded nodes."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {
                    "children": [
                        {"id": "child1", "label": "Child 1", "has_children": False},
                        {"id": "child2", "label": "Child 2", "has_children": False},
                    ]
                }
            },
        }
        view = ConcreteTreeView(tree_data)
        view.expanded_nodes = {"root"}

        flat = view._flatten_tree()

        # Should have root + 2 children
        assert len(flat) == 3
        assert flat[0][0].node_id == "root"
        assert flat[0][1] == 0  # root at level 0
        assert flat[1][0].node_id == "child1"
        assert flat[1][1] == 1  # children at level 1
        assert flat[2][0].node_id == "child2"
        assert flat[2][1] == 1

    def test_flatten_tree_nested_expansion(self):
        """Test _flatten_tree with nested expansion."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {
                    "children": [{"id": "child", "label": "Child", "has_children": True}]
                },
                "child": {
                    "children": [
                        {"id": "grandchild", "label": "Grandchild", "has_children": False}
                    ]
                },
            },
        }
        view = ConcreteTreeView(tree_data)
        view.expanded_nodes = {"root", "child"}

        flat = view._flatten_tree()

        # Should have root + child + grandchild
        assert len(flat) == 3
        assert flat[0][1] == 0  # root
        assert flat[1][1] == 1  # child
        assert flat[2][1] == 2  # grandchild

    def test_expand_all(self):
        """Test action_expand_all expands all nodes."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {
                    "children": [{"id": "child", "label": "Child", "has_children": True}]
                },
                "child": {
                    "children": [
                        {"id": "grandchild", "label": "Grandchild", "has_children": False}
                    ]
                },
            },
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Initially collapsed
        assert len(view.expanded_nodes) == 0

        # Expand all
        view.action_expand_all()

        # All nodes with children should be expanded
        assert "root" in view.expanded_nodes
        assert "child" in view.expanded_nodes
        assert len(view.expanded_nodes) == 2

    def test_collapse_all(self):
        """Test action_collapse_all collapses all nodes."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {"root": {"children": []}},
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Expand first
        view.expanded_nodes = {"root"}
        assert len(view.expanded_nodes) == 1

        # Collapse all
        view.action_collapse_all()

        # Should be empty
        assert len(view.expanded_nodes) == 0

    def test_navigation_in_tree(self):
        """Test navigation through tree."""
        tree_data = {
            "roots": [
                {"id": "root1", "label": "Root 1", "has_children": False},
                {"id": "root2", "label": "Root 2", "has_children": False},
                {"id": "root3", "label": "Root 3", "has_children": False},
            ],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)

        # Start at first
        assert view.selected_index == 0

        # Move down
        view.action_move_down()
        assert view.selected_index == 1

        # Move to bottom
        view.action_move_to_bottom()
        assert view.selected_index == 2

    def test_build_rich_tree(self):
        """Test _build_rich_tree creates Rich Tree."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": False}],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)

        tree = view._build_rich_tree()

        from rich.tree import Tree

        assert isinstance(tree, Tree)

    def test_abstract_methods_enforced(self):
        """Test abstract methods must be implemented."""
        with pytest.raises(TypeError):

            class IncompleteTreeView(TreeView[dict]):
                pass

            IncompleteTreeView()  # Should fail

    def test_get_root_nodes_abstract(self):
        """Test get_root_nodes is abstract."""
        assert hasattr(TreeView, "get_root_nodes")

    def test_get_child_nodes_abstract(self):
        """Test get_child_nodes is abstract."""
        assert hasattr(TreeView, "get_child_nodes")

    def test_inherits_from_interactive_view(self):
        """Test TreeView inherits InteractiveView functionality."""
        tree_data = {
            "roots": [
                {"id": "r1", "label": "R1", "has_children": False},
                {"id": "r2", "label": "R2", "has_children": False},
            ],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)

        # Should have navigation
        view.action_move_down()
        assert view.selected_index == 1

    def test_bindings_include_tree_specific(self):
        """Test TreeView has tree-specific bindings."""
        view = ConcreteTreeView()

        binding_keys = [str(b.key) for b in view.BINDINGS]

        # Check for tree-specific bindings
        assert any("right" in k or "l" in k for k in binding_keys)
        assert any("left" in k or "h" in k for k in binding_keys)
        assert any("+" in k for k in binding_keys)
        assert any("-" in k for k in binding_keys)


class TestTreeViewEdgeCases:
    """Tests for TreeView edge cases."""

    def test_empty_tree(self):
        """Test operations on empty tree."""
        view = ConcreteTreeView({})

        flat = view._flatten_tree()
        assert len(flat) == 0

        # Navigation should not raise
        view.action_move_down()
        view.action_toggle_node()

    def test_single_root_node(self):
        """Test tree with single root node."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": False}],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)

        flat = view._flatten_tree()
        assert len(flat) == 1
        assert flat[0][0].node_id == "root"

    def test_toggle_node_without_children(self):
        """Test toggling node without children does nothing."""
        tree_data = {
            "roots": [{"id": "leaf", "label": "Leaf", "has_children": False}],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Try to toggle leaf node
        view.action_toggle_node()

        # Should not be in expanded set
        assert "leaf" not in view.expanded_nodes

    def test_toggle_node_with_invalid_index(self):
        """Test toggling with invalid selected_index."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {"root": {"children": []}},
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        # Set invalid index
        view.selected_index = 999

        # Should not raise
        view.action_toggle_node()

    def test_expand_all_with_no_expandable_nodes(self):
        """Test expand_all with no nodes that have children."""
        tree_data = {
            "roots": [
                {"id": "leaf1", "label": "Leaf 1", "has_children": False},
                {"id": "leaf2", "label": "Leaf 2", "has_children": False},
            ],
            "all_nodes": {},
        }
        view = ConcreteTreeView(tree_data)
        view.data = tree_data

        view.action_expand_all()

        # No nodes should be expanded
        assert len(view.expanded_nodes) == 0

    def test_deep_nested_tree(self):
        """Test tree with deep nesting."""
        tree_data = {
            "roots": [{"id": "l0", "label": "Level 0", "has_children": True}],
            "all_nodes": {
                "l0": {"children": [{"id": "l1", "label": "Level 1", "has_children": True}]},
                "l1": {"children": [{"id": "l2", "label": "Level 2", "has_children": True}]},
                "l2": {"children": [{"id": "l3", "label": "Level 3", "has_children": False}]},
            },
        }
        view = ConcreteTreeView(tree_data)
        view.expanded_nodes = {"l0", "l1", "l2"}

        flat = view._flatten_tree()

        # Should have all 4 levels
        assert len(flat) == 4
        assert flat[0][1] == 0  # level 0
        assert flat[1][1] == 1  # level 1
        assert flat[2][1] == 2  # level 2
        assert flat[3][1] == 3  # level 3

    def test_partial_expansion(self):
        """Test tree with some nodes expanded, some collapsed."""
        tree_data = {
            "roots": [
                {"id": "r1", "label": "Root 1", "has_children": True},
                {"id": "r2", "label": "Root 2", "has_children": True},
            ],
            "all_nodes": {
                "r1": {"children": [{"id": "c1", "label": "Child 1", "has_children": False}]},
                "r2": {"children": [{"id": "c2", "label": "Child 2", "has_children": False}]},
            },
        }
        view = ConcreteTreeView(tree_data)
        view.expanded_nodes = {"r1"}  # Only expand first root

        flat = view._flatten_tree()

        # Should have: r1, c1 (expanded), r2 (collapsed)
        assert len(flat) == 3
        assert flat[0][0].node_id == "r1"
        assert flat[1][0].node_id == "c1"
        assert flat[2][0].node_id == "r2"

    def test_navigation_respects_expansion(self):
        """Test navigation index respects expanded state."""
        tree_data = {
            "roots": [{"id": "root", "label": "Root", "has_children": True}],
            "all_nodes": {
                "root": {"children": [{"id": "child", "label": "Child", "has_children": False}]}
            },
        }
        view = ConcreteTreeView(tree_data)

        # Collapsed - only 1 item
        assert view.get_item_count() == 1

        # Expand
        view.expanded_nodes = {"root"}

        # Now 2 items
        assert view.get_item_count() == 2

        # Can navigate to child
        view.action_move_to_bottom()
        assert view.selected_index == 1
