"""Action registry for command and keybinding management.

This module provides a central registry for all application actions/commands.
Actions can be registered with keybindings, categories, and descriptions for
use in the command palette and keyboard shortcut system.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """Registered action/command.

    Attributes:
        action_id: Unique identifier for the action
        name: Human-readable action name
        handler: Callable to execute when action is triggered
        description: Detailed description for command palette
        keybinding: Optional keyboard shortcut (e.g., "ctrl+o", "f1")
        category: Category for grouping (e.g., "File", "View", "Navigation")
        enabled: Whether the action is currently enabled
    """

    action_id: str
    name: str
    handler: Callable[..., Any]
    description: str = ""
    keybinding: str | None = None
    category: str = "General"
    enabled: bool = True


class ActionRegistry:
    """Central registry for all application actions.

    Manages registration, lookup, and execution of actions. Supports:
    - Action registration with validation
    - Keybinding to action mapping
    - Category-based grouping
    - Fuzzy search for command palette
    - Enable/disable actions dynamically

    Example:
        >>> registry = ActionRegistry()
        >>> registry.register(
        ...     action_id="file.open",
        ...     name="Open Binary",
        ...     handler=open_file_handler,
        ...     description="Open a binary file for analysis",
        ...     keybinding="ctrl+o",
        ...     category="File"
        ... )
        >>> registry.execute("file.open", "/path/to/binary")
    """

    def __init__(self) -> None:
        """Initialize empty action registry."""
        self._actions: dict[str, Action] = {}
        self._keybindings: dict[str, str] = {}  # key -> action_id
        self._categories: dict[str, list[str]] = {}  # category -> [action_ids]

    def register(
        self,
        action_id: str,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
        keybinding: str | None = None,
        category: str = "General",
        enabled: bool = True,
    ) -> None:
        """Register a new action.

        Args:
            action_id: Unique identifier (e.g., "file.open")
            name: Display name for UI (e.g., "Open Binary")
            handler: Callable to execute when action is triggered
            description: Detailed description for command palette
            keybinding: Optional keyboard shortcut (e.g., "ctrl+o")
            category: Category for grouping (e.g., "File", "View")
            enabled: Whether action is enabled by default

        Raises:
            ValueError: If action_id already registered or keybinding conflicts
        """
        # Check for duplicate action_id
        if action_id in self._actions:
            logger.warning(f"Action {action_id} already registered, overwriting")

        # Check for keybinding conflict
        if keybinding and keybinding in self._keybindings:
            existing_action_id = self._keybindings[keybinding]
            if existing_action_id != action_id:
                logger.warning(
                    f"Keybinding {keybinding} already bound to {existing_action_id}, "
                    f"rebinding to {action_id}"
                )

        # Create action
        action = Action(
            action_id=action_id,
            name=name,
            handler=handler,
            description=description,
            keybinding=keybinding,
            category=category,
            enabled=enabled,
        )

        # Store action
        self._actions[action_id] = action

        # Store keybinding mapping
        if keybinding:
            self._keybindings[keybinding] = action_id

        # Store category mapping
        if category not in self._categories:
            self._categories[category] = []
        if action_id not in self._categories[category]:
            self._categories[category].append(action_id)

        logger.debug(f"Registered action: {action_id} ({category})")

    def execute(self, action_id: str, *args: Any, **kwargs: Any) -> bool:
        """Execute an action by ID.

        Args:
            action_id: ID of action to execute
            args: Positional arguments to pass to handler
            kwargs: Keyword arguments to pass to handler

        Returns:
            True if action executed successfully, False otherwise
        """
        action = self._actions.get(action_id)

        if not action:
            logger.error(f"Action {action_id} not found")
            return False

        if not action.enabled:
            logger.debug(f"Action {action_id} is disabled")
            return False

        try:
            logger.debug(f"Executing action: {action_id}")
            action.handler(*args, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Error executing action {action_id}: {e}", exc_info=True)
            return False

    def get_action(self, action_id: str) -> Action | None:
        """Get action by ID.

        Args:
            action_id: ID of action to retrieve

        Returns:
            Action object or None if not found
        """
        return self._actions.get(action_id)

    def get_by_keybinding(self, key: str) -> Action | None:
        """Get action associated with keybinding.

        Args:
            key: Keyboard shortcut (e.g., "ctrl+o")

        Returns:
            Action object or None if no action bound to key
        """
        action_id = self._keybindings.get(key)
        return self._actions.get(action_id) if action_id else None

    def get_by_category(self, category: str) -> list[Action]:
        """Get all actions in a category.

        Args:
            category: Category name (e.g., "File", "View")

        Returns:
            List of Action objects in category (empty list if none)
        """
        action_ids = self._categories.get(category, [])
        return [self._actions[aid] for aid in action_ids if aid in self._actions]

    def get_all_categories(self) -> list[str]:
        """Get list of all registered categories.

        Returns:
            List of category names
        """
        return sorted(self._categories.keys())

    def get_all_actions(self) -> list[Action]:
        """Get all registered actions.

        Returns:
            List of all Action objects
        """
        return list(self._actions.values())

    def search(self, query: str) -> list[Action]:
        """Search actions by name or description.

        Performs case-insensitive substring matching on action names and descriptions.
        Future versions may implement fuzzy matching.

        Args:
            query: Search query string

        Returns:
            List of matching Action objects, sorted by relevance
        """
        if not query:
            return self.get_all_actions()

        query_lower = query.lower()
        matches: list[tuple[int, Action]] = []

        for action in self._actions.values():
            # Score based on where match appears
            score = 0

            name_lower = action.name.lower()
            desc_lower = action.description.lower()

            # Exact name match
            if query_lower == name_lower:
                score = 100
            # Name starts with query
            elif name_lower.startswith(query_lower):
                score = 90
            # Query in name
            elif query_lower in name_lower:
                score = 80
            # Query in description
            elif query_lower in desc_lower:
                score = 50
            # Query in action_id
            elif query_lower in action.action_id.lower():
                score = 40

            if score > 0:
                matches.append((score, action))

        # Sort by score descending, then by name
        matches.sort(key=lambda x: (-x[0], x[1].name))

        return [action for _, action in matches]

    def set_enabled(self, action_id: str, enabled: bool) -> bool:
        """Enable or disable an action.

        Args:
            action_id: ID of action to modify
            enabled: True to enable, False to disable

        Returns:
            True if action was found and modified, False otherwise
        """
        action = self._actions.get(action_id)
        if action:
            action.enabled = enabled
            logger.debug(f"Action {action_id} {'enabled' if enabled else 'disabled'}")
            return True
        return False

    def unregister(self, action_id: str) -> bool:
        """Unregister an action.

        Args:
            action_id: ID of action to remove

        Returns:
            True if action was found and removed, False otherwise
        """
        action = self._actions.get(action_id)
        if not action:
            return False

        # Remove from actions
        del self._actions[action_id]

        # Remove keybinding
        if action.keybinding and action.keybinding in self._keybindings:
            del self._keybindings[action.keybinding]

        # Remove from category
        if action.category in self._categories:
            category_list = self._categories[action.category]
            if action_id in category_list:
                category_list.remove(action_id)
            # Clean up empty categories
            if not category_list:
                del self._categories[action.category]

        logger.debug(f"Unregistered action: {action_id}")
        return True
