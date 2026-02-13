"""Interactive disassembly widget with keyboard navigation."""

import re
from typing import Any

from rich.console import Group
from rich.text import Text
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

from caspoon.ui.navigation.manager import NavigationManager
from caspoon.ui.syntax import AsmHighlighter


class InteractiveDisasmView(Static):
    """Interactive disassembly view with keyboard navigation.

    Features:
    - Keyboard-driven navigation (arrow keys for selection)
    - Visual indicators for navigable addresses
    - Jump to target addresses (Enter key)
    - Back/forward history (Alt+Left/Right)
    - Go to address dialog (g key)
    - Cross-reference display (x key)

    The widget uses a keyboard-first approach for navigation, as this is
    more reliable and efficient than mouse-based navigation in Textual.
    """

    # Reactive properties
    selected_line = reactive(0)

    # Visual indicators
    INDICATOR_NAVIGABLE = "▸"
    INDICATOR_SELECTED = ">"

    # Regex patterns for address extraction
    # Matches hex addresses in various formats:
    # - 0x401234
    # - call 0x401234
    # - jmp sym.main
    # - lea rax, [0x401234]
    ADDRESS_PATTERN = re.compile(
        r'\b(?:'
        r'(?:0x[0-9a-fA-F]+)|'  # Hex addresses
        r'(?:sym\.[a-zA-Z_][a-zA-Z0-9_.]*)|'  # Symbols
        r'(?:fcn\.[0-9a-fA-F]+)'  # Function addresses
        r')\b'
    )

    # Navigation-related instructions (calls, jumps)
    NAVIGABLE_INSTRUCTIONS = {
        'call', 'jmp', 'je', 'jne', 'jz', 'jnz', 'jg', 'jge', 'jl', 'jle',
        'ja', 'jae', 'jb', 'jbe', 'jo', 'jno', 'js', 'jns', 'jp', 'jnp',
        'jcxz', 'jecxz', 'jrcxz',
        'b', 'bl', 'beq', 'bne', 'blt', 'bgt', 'ble', 'bge',  # ARM branches
    }

    class NavigateTo(Message):
        """Message sent when user wants to navigate to an address."""

        def __init__(self, address: str) -> None:
            """Initialize navigation message.

            Args:
                address: Target address to navigate to
            """
            super().__init__()
            self.address = address

    class ShowXrefs(Message):
        """Message sent when user wants to see cross-references."""

        def __init__(self, address: str) -> None:
            """Initialize xref message.

            Args:
                address: Address to show cross-references for
            """
            super().__init__()
            self.address = address

    class OpenGotoDialog(Message):
        """Message sent when user wants to open the goto dialog."""

        pass

    def __init__(
        self,
        *args,
        navigation_manager: NavigationManager | None = None,
        highlighter: AsmHighlighter | None = None,
        **kwargs
    ):
        """Initialize the interactive disassembly view.

        Args:
            navigation_manager: Optional navigation manager for history tracking
            highlighter: Optional syntax highlighter for assembly code
            *args: Additional positional arguments for Static
            **kwargs: Additional keyword arguments for Static
        """
        super().__init__(*args, **kwargs)
        self.nav_manager = navigation_manager or NavigationManager()
        self.highlighter = highlighter or AsmHighlighter()

        # Store disassembly data
        self.disasm_lines: list[dict[str, Any]] = []
        self.current_function: str = ""

    def update_disassembly(
        self,
        disasm_ops: list[dict[str, Any]],
        function_name: str = "",
        current_address: str | None = None
    ) -> None:
        """Update the disassembly display with new data.

        Args:
            disasm_ops: List of disassembly operations from r2/other analyzer
            function_name: Name of the function being displayed
            current_address: Optional address to highlight/select
        """
        self.disasm_lines = disasm_ops
        self.current_function = function_name

        # If a specific address is provided, select that line
        if current_address:
            for i, op in enumerate(disasm_ops):
                addr = hex(op.get("offset", 0))
                if addr == current_address:
                    self.selected_line = i
                    break

        self._render_disassembly()

    def _render_disassembly(self) -> None:
        """Render the disassembly with visual indicators and highlighting."""
        if not self.disasm_lines:
            self.update("No disassembly data available.")
            return

        parts = []

        # Add function header if available
        if self.current_function:
            header = Text(f"Function: {self.current_function}", style="bold cyan")
            parts.append(header)
            parts.append(Text())  # Blank line

        # Add navigation hints
        hints = Text("Navigation: ", style="dim")
        hints.append("↑↓", style="bold")
        hints.append(" Select | ", style="dim")
        hints.append("Enter", style="bold")
        hints.append(" Jump | ", style="dim")
        hints.append("Alt+←→", style="bold")
        hints.append(" History | ", style="dim")
        hints.append("g", style="bold")
        hints.append(" Go to | ", style="dim")
        hints.append("x", style="bold")
        hints.append(" Xrefs", style="dim")
        parts.append(hints)
        parts.append(Text())  # Blank line

        # Render each line with indicators
        for i, op in enumerate(self.disasm_lines):
            line = self._render_line(op, i == self.selected_line)
            parts.append(line)

        # Add history status if available
        if self.nav_manager.history:
            status = Text("\n", style="dim")
            status.append(f"History: {self.nav_manager.current_index + 1}/{len(self.nav_manager.history)}", style="dim")
            if self.nav_manager.can_go_back():
                status.append(" [can go back]", style="dim green")
            if self.nav_manager.can_go_forward():
                status.append(" [can go forward]", style="dim blue")
            parts.append(status)

        group = Group(*parts)
        self.update(group)

    def _render_line(self, op: dict[str, Any], is_selected: bool) -> Text:
        """Render a single disassembly line with indicators.

        Args:
            op: Disassembly operation dictionary
            is_selected: Whether this line is currently selected

        Returns:
            Formatted Text object for the line
        """
        line = Text()

        # Selection indicator (left margin)
        if is_selected:
            line.append(f"{self.INDICATOR_SELECTED} ", style="bold yellow")
        else:
            line.append("  ")

        # Address
        offset = op.get("offset", 0)
        addr_str = f"{offset:#010x}"  # Format as 0x00401234 for display
        line.append(addr_str, style="cyan")
        line.append("  ")

        # Navigation indicator (for lines with navigable addresses)
        opcode = op.get("opcode", "")
        if self._is_navigable_instruction(opcode):
            line.append(f"{self.INDICATOR_NAVIGABLE} ", style="green")
        else:
            line.append("  ")

        # Highlighted instruction (without address, we display it separately)
        # Don't pass address to highlighter to avoid duplication
        highlighted = self.highlighter.highlight_instruction(opcode, address="")
        line.append_text(highlighted)

        # Add background highlight for selected line
        if is_selected:
            # Apply a subtle background to the entire line
            line.stylize("reverse")

        return line

    def _is_navigable_instruction(self, opcode: str) -> bool:
        """Check if an instruction contains a navigable address.

        Args:
            opcode: The instruction opcode and operands

        Returns:
            True if the instruction can be navigated (contains an address)
        """
        if not opcode:
            return False

        # Check if the mnemonic is a navigable instruction
        mnemonic = opcode.strip().split()[0].lower()
        if mnemonic not in self.NAVIGABLE_INSTRUCTIONS:
            return False

        # Check if there's actually an address in the operands
        return bool(self.ADDRESS_PATTERN.search(opcode))

    def _extract_target_address(self, opcode: str) -> str | None:
        """Extract the target address from an instruction.

        Args:
            opcode: The instruction opcode and operands

        Returns:
            The target address as a string, or None if not found
        """
        match = self.ADDRESS_PATTERN.search(opcode)
        if match:
            return match.group(0)
        return None

    def _get_current_line_address(self) -> str | None:
        """Get the address of the currently selected line.

        Returns:
            The address as a hex string, or None if invalid
        """
        if 0 <= self.selected_line < len(self.disasm_lines):
            op = self.disasm_lines[self.selected_line]
            offset = op.get("offset", 0)
            return f"{offset:#x}"
        return None

    # Keyboard event handlers

    def on_key(self, event) -> None:
        """Handle keyboard input for navigation.

        Args:
            event: The key event
        """
        key = event.key

        # Arrow key navigation
        if key == "up":
            self._move_selection(-1)
            event.prevent_default()
        elif key == "down":
            self._move_selection(1)
            event.prevent_default()

        # Jump to address on current line
        elif key == "enter":
            self._navigate_to_current_line()
            event.prevent_default()

        # History navigation
        elif key == "alt+left" or key == "ctrl+h":
            self._go_back()
            event.prevent_default()
        elif key == "alt+right" or key == "ctrl+l":
            self._go_forward()
            event.prevent_default()

        # Go to address dialog
        elif key == "g":
            self.post_message(self.OpenGotoDialog())
            event.prevent_default()

        # Show cross-references
        elif key == "x":
            self._show_xrefs()
            event.prevent_default()

    def _move_selection(self, delta: int) -> None:
        """Move the selection up or down.

        Args:
            delta: Number of lines to move (-1 for up, +1 for down)
        """
        new_selection = self.selected_line + delta
        # Clamp to valid range
        new_selection = max(0, min(new_selection, len(self.disasm_lines) - 1))

        if new_selection != self.selected_line:
            self.selected_line = new_selection
            self._render_disassembly()

    def _navigate_to_current_line(self) -> None:
        """Navigate to the target address of the currently selected line."""
        if not (0 <= self.selected_line < len(self.disasm_lines)):
            return

        op = self.disasm_lines[self.selected_line]
        opcode = op.get("opcode", "")

        target = self._extract_target_address(opcode)
        if target:
            # Add current location to history before navigating
            current_addr = self._get_current_line_address()
            if current_addr:
                self.nav_manager.navigate_to(current_addr)

            # Post message to parent to handle navigation
            self.post_message(self.NavigateTo(target))

    def _go_back(self) -> None:
        """Navigate back in history."""
        prev_addr = self.nav_manager.go_back()
        if prev_addr:
            self.post_message(self.NavigateTo(prev_addr))
            self._render_disassembly()

    def _go_forward(self) -> None:
        """Navigate forward in history."""
        next_addr = self.nav_manager.go_forward()
        if next_addr:
            self.post_message(self.NavigateTo(next_addr))
            self._render_disassembly()

    def _show_xrefs(self) -> None:
        """Show cross-references for the currently selected line."""
        addr = self._get_current_line_address()
        if addr:
            self.post_message(self.ShowXrefs(addr))

    def watch_selected_line(self, old_value: int, new_value: int) -> None:
        """React to changes in selected line.

        Args:
            old_value: Previous selected line index
            new_value: New selected line index
        """
        # Re-render when selection changes
        if old_value != new_value:
            self._render_disassembly()

    def jump_to_address(self, address: str) -> None:
        """Jump to a specific address in the disassembly.

        Args:
            address: Target address to jump to
        """
        # Find the line with this address
        for i, op in enumerate(self.disasm_lines):
            offset = op.get("offset", 0)
            addr_str = f"{offset:#x}"

            if addr_str == address or hex(offset) == address:
                # Add current location to history
                current_addr = self._get_current_line_address()
                if current_addr:
                    self.nav_manager.navigate_to(current_addr)

                # Update selection
                self.selected_line = i
                self._render_disassembly()

                # Emit navigation message
                self.post_message(self.NavigateTo(address))
                return

    def can_take_focus(self) -> bool:
        """Allow this widget to receive keyboard focus.

        Returns:
            True to enable keyboard focus
        """
        # Widget should be focusable to receive keyboard input for navigation
        # The parent ScrollableContainer will still handle scroll events
        return True
