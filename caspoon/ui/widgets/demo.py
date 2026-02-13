"""
Demo script for InteractiveDisasmView widget.

This script demonstrates the interactive disassembly widget with sample data.
Run with: python -m caspoon.ui.widgets.demo
"""

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header

from caspoon.ui.widgets import GotoDialog, InteractiveDisasmView


class DisasmDemo(App):
    """Demo application for interactive disassembly widget."""

    TITLE = "Interactive Disassembly Widget Demo"
    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        with ScrollableContainer():
            yield InteractiveDisasmView(id="disasm")
        yield Footer()

    def on_mount(self) -> None:
        """Load sample disassembly on mount."""
        # Sample disassembly data (typical x86-64 function)
        sample_disasm = [
            {"offset": 0x401000, "opcode": "push rbp"},
            {"offset": 0x401001, "opcode": "mov rbp, rsp"},
            {"offset": 0x401004, "opcode": "sub rsp, 0x20"},
            {"offset": 0x401008, "opcode": "mov dword [rbp-0x4], 0x0"},
            {"offset": 0x40100F, "opcode": "lea rdi, [rip+0x100]"},
            {"offset": 0x401016, "opcode": "call 0x401100"},  # Navigable
            {"offset": 0x40101B, "opcode": "mov eax, dword [rbp-0x4]"},
            {"offset": 0x40101E, "opcode": "cmp eax, 0xa"},
            {"offset": 0x401021, "opcode": "jge 0x401040"},  # Navigable
            {"offset": 0x401023, "opcode": "mov eax, dword [rbp-0x4]"},
            {"offset": 0x401026, "opcode": "add eax, 0x1"},
            {"offset": 0x401029, "opcode": "mov dword [rbp-0x4], eax"},
            {"offset": 0x40102C, "opcode": "jmp 0x40101B"},  # Navigable
            {"offset": 0x40102E, "opcode": "nop"},
            {"offset": 0x40102F, "opcode": "leave"},
            {"offset": 0x401030, "opcode": "ret"},
        ]

        # Load into widget
        widget = self.query_one("#disasm", InteractiveDisasmView)
        widget.update_disassembly(sample_disasm, "sample_function")

        # Focus the widget so it receives keyboard input
        widget.focus()

    def on_interactive_disasm_view_navigate_to(
        self, message: InteractiveDisasmView.NavigateTo
    ) -> None:
        """Handle navigation request."""
        self.notify(f"Navigate to: {message.address}", title="Navigation")

    def on_interactive_disasm_view_show_xrefs(
        self, message: InteractiveDisasmView.ShowXrefs
    ) -> None:
        """Handle xref display request."""
        self.notify(
            f"Cross-references for: {message.address}",
            title="XRefs",
            severity="information",
        )

    def on_interactive_disasm_view_open_goto_dialog(
        self, message: InteractiveDisasmView.OpenGotoDialog
    ) -> None:
        """Handle goto dialog request."""

        def handle_goto(address: str | None) -> None:
            if address:
                self.notify(f"Go to: {address}", title="Goto Address")
                widget = self.query_one("#disasm", InteractiveDisasmView)
                widget.jump_to_address(address)

        self.push_screen(GotoDialog(), callback=handle_goto)


def main():
    """Run the demo app."""
    app = DisasmDemo()
    app.run()


if __name__ == "__main__":
    main()
