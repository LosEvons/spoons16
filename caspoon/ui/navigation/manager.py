"""Navigation manager for handling interactive navigation through disassembly."""

from typing import Any


class NavigationManager:
    """Manage navigation history and address resolution.

    Provides browser-like navigation history with back/forward functionality,
    allowing users to navigate through addresses in disassembly and return to
    previous locations.
    """

    def __init__(self) -> None:
        """Initialize the navigation manager with empty history."""
        self.history: list[str] = []
        self.current_index: int = -1
        self.address_map: dict[str, Any] = {}

    def navigate_to(self, address: str) -> None:
        """Navigate to an address, adding it to history.

        If currently viewing a position in the middle of history,
        this truncates forward history and adds the new address.

        Args:
            address: The address to navigate to
        """
        # Truncate forward history if we're not at the end
        if self.current_index < len(self.history) - 1:
            self.history = self.history[: self.current_index + 1]

        # Add new address to history
        self.history.append(address)
        self.current_index += 1

    def go_back(self) -> str | None:
        """Navigate back in history.

        Returns:
            The previous address if available, None if already at the start
        """
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None

    def go_forward(self) -> str | None:
        """Navigate forward in history.

        Returns:
            The next address if available, None if already at the end
        """
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None

    def can_go_back(self) -> bool:
        """Check if back navigation is possible.

        Returns:
            True if there is history to go back to, False otherwise
        """
        return self.current_index > 0

    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible.

        Returns:
            True if there is forward history available, False otherwise
        """
        return self.current_index < len(self.history) - 1

    def current_address(self) -> str | None:
        """Get the current address.

        Returns:
            The current address if history exists, None otherwise
        """
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None

    def clear_history(self) -> None:
        """Clear all navigation history."""
        self.history.clear()
        self.current_index = -1
        self.address_map.clear()

    def set_address_map(self, address_map: dict[str, Any]) -> None:
        """Set the address map from analysis results.

        The address map provides metadata about addresses, such as
        function information, for enhanced navigation.

        Args:
            address_map: Dictionary mapping addresses to their metadata
        """
        self.address_map = address_map
