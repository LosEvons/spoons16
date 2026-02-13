"""Go-to address dialog for interactive navigation."""

import re

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class GotoDialog(ModalScreen[str | None]):
    """Modal dialog for entering an address to navigate to.

    This screen provides a simple input dialog where users can enter
    an address in various formats (hex, decimal, symbol name) to jump to
    in the disassembly view.

    Supported address formats:
    - Hexadecimal: 0x401234, 0x00401234, 401234
    - Decimal: 4198964
    - Symbol: sym.main, fcn.00401234
    """

    # CSS styling for the dialog
    CSS = """
    GotoDialog {
        align: center middle;
    }

    GotoDialog > Container {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    GotoDialog Label {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }

    GotoDialog Input {
        width: 100%;
        margin-bottom: 1;
    }

    GotoDialog #button-container {
        width: 100%;
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    GotoDialog Button {
        margin: 0 1;
    }
    
    #error-message {
        color: $error;
        text-style: bold;
        height: auto;
        margin-bottom: 1;
    }
    """

    # Regex patterns for address validation
    HEX_PATTERN = re.compile(r'^(?:0x)?([0-9a-fA-F]+)$')
    DEC_PATTERN = re.compile(r'^(\d+)$')
    SYMBOL_PATTERN = re.compile(r'^(sym\.|fcn\.)?[a-zA-Z_][a-zA-Z0-9_.]*$')

    def __init__(self, *args, **kwargs):
        """Initialize the goto dialog."""
        super().__init__(*args, **kwargs)
        self.error_message: str = ""

    def compose(self) -> ComposeResult:
        """Compose the dialog UI.

        Yields:
            UI components for the dialog
        """
        with Container():
            yield Label("Go to Address", id="title")
            yield Input(
                placeholder="Enter address (e.g., 0x401234, sym.main)",
                id="address-input"
            )
            yield Static("", id="error-message")
            with Vertical(id="button-container"):
                yield Button("Go", variant="primary", id="go-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus the input when dialog opens."""
        self.query_one("#address-input", Input).focus()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field.

        Args:
            event: Input submission event
        """
        self._validate_and_go()

    @on(Button.Pressed, "#go-button")
    def on_go_button_pressed(self) -> None:
        """Handle Go button press."""
        self._validate_and_go()

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_button_pressed(self) -> None:
        """Handle Cancel button press."""
        self.dismiss(None)

    def _validate_and_go(self) -> None:
        """Validate the input address and navigate if valid."""
        input_widget = self.query_one("#address-input", Input)
        address_str = input_widget.value.strip()

        if not address_str:
            self._show_error("Please enter an address")
            return

        # Normalize the address
        normalized = self._normalize_address(address_str)

        if normalized:
            self.dismiss(normalized)
        else:
            self._show_error("Invalid address format")

    def _normalize_address(self, address_str: str) -> str | None:
        """Normalize an address string to a standard format.

        Args:
            address_str: Raw address string from user input

        Returns:
            Normalized address string (hex format with 0x prefix), or None if invalid
        """
        # Try hex format
        hex_match = self.HEX_PATTERN.match(address_str)
        if hex_match:
            hex_digits = hex_match.group(1)
            try:
                # Convert to int and back to ensure valid hex
                addr_int = int(hex_digits, 16)
                return f"0x{addr_int:x}"
            except ValueError:
                pass

        # Try decimal format
        dec_match = self.DEC_PATTERN.match(address_str)
        if dec_match:
            try:
                addr_int = int(dec_match.group(1))
                return f"0x{addr_int:x}"
            except ValueError:
                pass

        # Try symbol format
        symbol_match = self.SYMBOL_PATTERN.match(address_str)
        if symbol_match:
            # Return symbol as-is (will be resolved by caller)
            return address_str

        return None

    def _show_error(self, message: str) -> None:
        """Display an error message in the dialog.

        Args:
            message: Error message to display
        """
        error_label = self.query_one("#error-message", Static)
        error_label.update(message)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts.

        Args:
            event: Key event
        """
        # ESC to close dialog
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
