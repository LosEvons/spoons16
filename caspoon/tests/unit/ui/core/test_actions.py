"""Unit tests for ActionRegistry."""

from unittest.mock import Mock

import pytest

from caspoon.ui.core.actions import Action, ActionRegistry


class TestAction:
    """Tests for Action dataclass."""

    def test_action_creation(self):
        """Test creating an Action with all fields."""
        handler = Mock()

        action = Action(
            action_id="file.open",
            name="Open Binary",
            handler=handler,
            description="Open a binary file",
            keybinding="ctrl+o",
            category="File",
            enabled=True,
        )

        assert action.action_id == "file.open"
        assert action.name == "Open Binary"
        assert action.handler == handler
        assert action.description == "Open a binary file"
        assert action.keybinding == "ctrl+o"
        assert action.category == "File"
        assert action.enabled is True

    def test_action_defaults(self):
        """Test Action with default values."""
        handler = Mock()

        action = Action(
            action_id="test.action",
            name="Test Action",
            handler=handler,
        )

        assert action.action_id == "test.action"
        assert action.name == "Test Action"
        assert action.handler == handler
        assert action.description == ""
        assert action.keybinding is None
        assert action.category == "General"
        assert action.enabled is True


class TestActionRegistry:
    """Tests for ActionRegistry class."""

    def test_registry_initialization(self):
        """Test ActionRegistry initializes empty."""
        registry = ActionRegistry()

        assert registry.get_all_actions() == []
        assert registry.get_all_categories() == []

    def test_register_action(self):
        """Test registering a single action."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register(
            action_id="file.open",
            name="Open Binary",
            handler=handler,
            description="Open a binary file",
            keybinding="ctrl+o",
            category="File",
        )

        action = registry.get_action("file.open")
        assert action is not None
        assert action.action_id == "file.open"
        assert action.name == "Open Binary"
        assert action.handler == handler

    def test_register_multiple_actions(self):
        """Test registering multiple actions."""
        registry = ActionRegistry()

        registry.register("file.open", "Open", Mock(), category="File")
        registry.register("file.close", "Close", Mock(), category="File")
        registry.register("edit.copy", "Copy", Mock(), category="Edit")

        all_actions = registry.get_all_actions()
        assert len(all_actions) == 3

        categories = registry.get_all_categories()
        assert set(categories) == {"File", "Edit"}

    def test_register_duplicate_warns(self):
        """Test registering duplicate action_id warns but overwrites."""
        registry = ActionRegistry()
        handler1 = Mock()
        handler2 = Mock()

        registry.register("test.action", "First", handler1)
        registry.register("test.action", "Second", handler2)  # Duplicate

        action = registry.get_action("test.action")
        assert action.name == "Second"
        assert action.handler == handler2

    def test_execute_action(self):
        """Test executing an action."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("test.action", "Test", handler)

        result = registry.execute("test.action")

        assert result is True
        handler.assert_called_once()

    def test_execute_action_with_args(self):
        """Test executing action with arguments."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("test.action", "Test", handler)

        result = registry.execute("test.action", "arg1", "arg2", kwarg1="value1")

        assert result is True
        handler.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_execute_disabled_action(self):
        """Test executing a disabled action fails."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("test.action", "Test", handler, enabled=False)

        result = registry.execute("test.action")

        assert result is False
        handler.assert_not_called()

    def test_execute_nonexistent_action(self):
        """Test executing nonexistent action returns False."""
        registry = ActionRegistry()

        result = registry.execute("nonexistent.action")

        assert result is False

    def test_execute_action_with_exception(self):
        """Test executing action that raises exception returns False."""
        registry = ActionRegistry()
        handler = Mock(side_effect=Exception("Test error"))

        registry.register("test.action", "Test", handler)

        result = registry.execute("test.action")

        assert result is False

    def test_get_action_not_found(self):
        """Test getting nonexistent action returns None."""
        registry = ActionRegistry()

        action = registry.get_action("nonexistent")

        assert action is None

    def test_get_by_keybinding(self):
        """Test getting action by keybinding."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register(
            "file.open",
            "Open",
            handler,
            keybinding="ctrl+o",
        )

        action = registry.get_by_keybinding("ctrl+o")
        assert action is not None
        assert action.action_id == "file.open"

    def test_get_by_keybinding_not_found(self):
        """Test getting action by nonexistent keybinding."""
        registry = ActionRegistry()

        action = registry.get_by_keybinding("ctrl+x")

        assert action is None

    def test_keybinding_conflict_warns(self):
        """Test registering conflicting keybinding warns and rebinds."""
        registry = ActionRegistry()

        registry.register("action1", "Action 1", Mock(), keybinding="ctrl+o")
        registry.register("action2", "Action 2", Mock(), keybinding="ctrl+o")

        # Second action should have the keybinding now
        action = registry.get_by_keybinding("ctrl+o")
        assert action.action_id == "action2"

    def test_get_by_category(self):
        """Test getting actions by category."""
        registry = ActionRegistry()

        registry.register("file.open", "Open", Mock(), category="File")
        registry.register("file.close", "Close", Mock(), category="File")
        registry.register("edit.copy", "Copy", Mock(), category="Edit")

        file_actions = registry.get_by_category("File")
        assert len(file_actions) == 2
        assert {a.action_id for a in file_actions} == {"file.open", "file.close"}

    def test_get_by_category_empty(self):
        """Test getting actions from nonexistent category."""
        registry = ActionRegistry()

        actions = registry.get_by_category("Nonexistent")

        assert actions == []

    def test_search_actions_empty_query(self):
        """Test search with empty query returns all actions."""
        registry = ActionRegistry()

        registry.register("action1", "Test 1", Mock())
        registry.register("action2", "Test 2", Mock())

        results = registry.search("")

        assert len(results) == 2

    def test_search_actions_by_name(self):
        """Test searching actions by name."""
        registry = ActionRegistry()

        registry.register("file.open", "Open Binary", Mock())
        registry.register("file.close", "Close Binary", Mock())
        registry.register("edit.copy", "Copy Text", Mock())

        results = registry.search("Binary")

        assert len(results) == 2
        assert {a.action_id for a in results} == {"file.open", "file.close"}

    def test_search_actions_by_description(self):
        """Test searching actions by description."""
        registry = ActionRegistry()

        registry.register("action1", "Test", Mock(), description="search this text")
        registry.register("action2", "Test", Mock(), description="other content")

        results = registry.search("search")

        assert len(results) == 1
        assert results[0].action_id == "action1"

    def test_search_actions_case_insensitive(self):
        """Test search is case insensitive."""
        registry = ActionRegistry()

        registry.register("file.open", "Open Binary", Mock())

        results = registry.search("BINARY")

        assert len(results) == 1
        assert results[0].action_id == "file.open"

    def test_search_actions_by_action_id(self):
        """Test searching by action_id."""
        registry = ActionRegistry()

        registry.register("file.open", "Open", Mock())
        registry.register("file.close", "Close", Mock())

        results = registry.search("file.open")

        assert len(results) >= 1
        assert any(a.action_id == "file.open" for a in results)

    def test_search_scoring(self):
        """Test search results are scored and sorted."""
        registry = ActionRegistry()

        # Exact match should score highest
        registry.register("open", "open", Mock())
        # Prefix match should score high
        registry.register("open.file", "open file", Mock())
        # Substring match should score lower
        registry.register("file.open", "File Open", Mock())
        # Description match should score even lower
        registry.register("action", "Test", Mock(), description="open a file")

        results = registry.search("open")

        # Exact match should be first
        assert results[0].action_id == "open"

    def test_set_enabled(self):
        """Test enabling/disabling actions."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("test.action", "Test", handler)

        # Disable action
        result = registry.set_enabled("test.action", False)
        assert result is True

        action = registry.get_action("test.action")
        assert action.enabled is False

        # Try to execute (should fail)
        exec_result = registry.execute("test.action")
        assert exec_result is False

        # Re-enable action
        registry.set_enabled("test.action", True)
        exec_result = registry.execute("test.action")
        assert exec_result is True

    def test_set_enabled_nonexistent(self):
        """Test set_enabled on nonexistent action returns False."""
        registry = ActionRegistry()

        result = registry.set_enabled("nonexistent", True)

        assert result is False

    def test_unregister_action(self):
        """Test unregistering an action."""
        registry = ActionRegistry()

        registry.register("test.action", "Test", Mock(), keybinding="ctrl+t", category="Test")

        # Unregister
        result = registry.unregister("test.action")
        assert result is True

        # Should not be findable anymore
        assert registry.get_action("test.action") is None
        assert registry.get_by_keybinding("ctrl+t") is None
        assert len(registry.get_by_category("Test")) == 0

    def test_unregister_nonexistent(self):
        """Test unregistering nonexistent action returns False."""
        registry = ActionRegistry()

        result = registry.unregister("nonexistent")

        assert result is False

    def test_unregister_cleans_empty_category(self):
        """Test unregistering last action in category removes category."""
        registry = ActionRegistry()

        registry.register("test.action", "Test", Mock(), category="TestCategory")

        assert "TestCategory" in registry.get_all_categories()

        registry.unregister("test.action")

        assert "TestCategory" not in registry.get_all_categories()

    def test_multiple_actions_same_category(self):
        """Test multiple actions can share a category."""
        registry = ActionRegistry()

        registry.register("file.open", "Open", Mock(), category="File")
        registry.register("file.close", "Close", Mock(), category="File")
        registry.register("file.save", "Save", Mock(), category="File")

        file_actions = registry.get_by_category("File")
        assert len(file_actions) == 3
