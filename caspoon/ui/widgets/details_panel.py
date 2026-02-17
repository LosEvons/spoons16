"""Details panel widget for displaying contextual information."""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.containers import ScrollableContainer
from textual.widgets import Static

from caspoon.ui import widget_ids


class DetailsPanel(ScrollableContainer):
    """Context-sensitive information display panel.

    Shows detailed information about the currently selected item:
    - Function details (address, size, calls, etc.)
    - String details (offset, encoding, references)
    - Import/export details (library, type, etc.)
    - Help text when nothing is selected

    The panel updates automatically when the selection changes in AppState.

    Example:
        >>> panel = DetailsPanel()
        >>> # Panel automatically updates when app.state.ui_state.selected_function changes
    """

    DEFAULT_CSS = """
    DetailsPanel {
        border: solid blue;
    }

    DetailsPanel Static {
        padding: 1;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the details panel.

        Args:
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self._content_widget = Static(id=widget_ids.DETAILS_CONTENT)

    def compose(self):
        """Compose the details panel with content widget.

        Yields:
            Static widget for displaying details
        """
        yield self._content_widget

    def on_mount(self) -> None:
        """Set up the panel when mounted.

        Displays initial help text.
        """
        self._show_help()

    def show_function_details(self, function_data: dict) -> None:
        """Display details for a selected function.

        Args:
            function_data: Dictionary containing function information
                Expected keys: name, address, size, section, calls, refs, etc.
        """
        try:
            content = Text()
            content.append("Function Details\n\n", style="bold cyan")

            # Basic info
            name = function_data.get("name", "unknown")
            address = function_data.get("address", 0)
            size = function_data.get("size", 0)
            section = function_data.get("section", "unknown")

            content.append("Name: ", style="bold")
            content.append(f"{name}\n")
            content.append("Address: ", style="bold")
            content.append(f"0x{address:08x}\n", style="cyan")
            content.append("Size: ", style="bold")
            content.append(f"{size} bytes\n")
            content.append("Section: ", style="bold")
            content.append(f"{section}\n")

            # Optional: Call information
            calls = function_data.get("calls", [])
            if calls:
                content.append(f"\nCalls ({len(calls)}):\n", style="bold yellow")
                for call in calls[:5]:  # Show first 5
                    content.append(f"  → {call}\n", style="dim")
                if len(calls) > 5:
                    content.append(f"  ... and {len(calls) - 5} more\n", style="dim")

            # Optional: References
            refs = function_data.get("refs", [])
            if refs:
                content.append(f"\nCalled by ({len(refs)}):\n", style="bold yellow")
                for ref in refs[:5]:  # Show first 5
                    content.append(f"  ← {ref}\n", style="dim")
                if len(refs) > 5:
                    content.append(f"  ... and {len(refs) - 5} more\n", style="dim")

            panel = Panel(content, title="Function", border_style="blue")
            self._content_widget.update(panel)

        except Exception as e:
            self._show_error(f"Error displaying function details: {e}")

    def show_string_details(self, string_data: dict) -> None:
        """Display details for a selected string.

        Args:
            string_data: Dictionary containing string information
                Expected keys: value, offset, length, encoding, refs, etc.
        """
        try:
            content = Text()
            content.append("String Details\n\n", style="bold cyan")

            value = string_data.get("value", "")
            offset = string_data.get("offset", 0)
            length = string_data.get("length", len(value))
            encoding = string_data.get("encoding", "ascii")

            content.append("Value: ", style="bold")
            content.append(f'"{value}"\n')
            content.append("Offset: ", style="bold")
            content.append(f"0x{offset:08x}\n", style="cyan")
            content.append("Length: ", style="bold")
            content.append(f"{length} bytes\n")
            content.append("Encoding: ", style="bold")
            content.append(f"{encoding}\n")

            # Optional: References
            refs = string_data.get("refs", [])
            if refs:
                content.append(f"\nReferenced by ({len(refs)}):\n", style="bold yellow")
                for ref in refs[:5]:
                    content.append(f"  → {ref}\n", style="dim")
                if len(refs) > 5:
                    content.append(f"  ... and {len(refs) - 5} more\n", style="dim")

            panel = Panel(content, title="String", border_style="blue")
            self._content_widget.update(panel)

        except Exception as e:
            self._show_error(f"Error displaying string details: {e}")

    def show_import_details(self, import_data: dict) -> None:
        """Display details for a selected import.

        Args:
            import_data: Dictionary containing import information
                Expected keys: name, library, type, address, etc.
        """
        try:
            content = Text()
            content.append("Import Details\n\n", style="bold cyan")

            name = import_data.get("name", "unknown")
            library = import_data.get("library", "unknown")
            address = import_data.get("address", 0)

            content.append("Function: ", style="bold")
            content.append(f"{name}\n")
            content.append("Library: ", style="bold")
            content.append(f"{library}\n")
            if address:
                content.append("Address: ", style="bold")
                content.append(f"0x{address:08x}\n", style="cyan")

            panel = Panel(content, title="Import", border_style="blue")
            self._content_widget.update(panel)

        except Exception as e:
            self._show_error(f"Error displaying import details: {e}")

    def _show_help(self) -> None:
        """Display default help text when nothing is selected."""
        content = Text()
        content.append("Details Panel\n\n", style="bold cyan")
        content.append("Select an item to view details:\n\n", style="dim")
        content.append("• Functions: ", style="bold")
        content.append("address, size, calls\n", style="dim")
        content.append("• Strings: ", style="bold")
        content.append("offset, encoding, refs\n", style="dim")
        content.append("• Imports: ", style="bold")
        content.append("library, type\n", style="dim")
        content.append("\n")
        content.append("Navigate with arrow keys\n", style="dim")
        content.append("Press Enter to select\n", style="dim")

        panel = Panel(content, title="Help", border_style="blue")
        self._content_widget.update(panel)

    def _show_error(self, error_msg: str) -> None:
        """Display an error message.

        Args:
            error_msg: Error message to display
        """
        content = Text()
        content.append("Error\n\n", style="bold red")
        content.append(error_msg, style="red")

        panel = Panel(content, title="Error", border_style="red")
        self._content_widget.update(panel)

    def show_xrefs(self, address: str, xref_data: dict) -> None:
        """Display cross-references for a given address.

        Shows callers (who calls this address) and callees (what this calls)
        in a formatted table.

        Args:
            address: The hex address string (e.g., "0x401000")
            xref_data: Dictionary containing xref information:
                {
                    "callers": [{"from": int, "type": str, "fcn_name": str}, ...],
                    "callees": [{"to": int, "type": str, "fcn_name": str}, ...]
                }
        """
        try:
            # Extract callers and callees
            callers = xref_data.get("callers", [])
            callees = xref_data.get("callees", [])

            # If no xrefs, show a message
            if not callers and not callees:
                content = Text()
                content.append(f"No cross-references found for {address}\n\n", style="bold yellow")
                content.append("This address is not referenced by or from other code.\n", style="dim")
                panel = Panel(content, title="Cross-References", border_style="blue")
                self._content_widget.update(panel)
                return

            # Build the content with tables
            content_parts = []

            # Title
            title_text = Text()
            title_text.append(f"Cross-References for {address}\n", style="bold cyan")
            content_parts.append(title_text)

            # Callers section (who calls this address)
            if callers:
                callers_table = Table(show_header=True, header_style="bold magenta", box=None)
                callers_table.add_column("From Address", style="cyan")
                callers_table.add_column("Type", style="yellow")
                callers_table.add_column("Function", style="green")

                for caller in callers:
                    from_addr = caller.get("from", 0)
                    ref_type = caller.get("type", "UNKNOWN")
                    fcn_name = caller.get("fcn_name", "<unknown>")

                    callers_table.add_row(
                        f"0x{from_addr:x}",
                        ref_type,
                        fcn_name
                    )

                caller_title = Text(f"\n📥 Called From ({len(callers)}):\n", style="bold yellow")
                content_parts.append(caller_title)
                content_parts.append(callers_table)

            # Callees section (what this address calls)
            if callees:
                callees_table = Table(show_header=True, header_style="bold magenta", box=None)
                callees_table.add_column("To Address", style="cyan")
                callees_table.add_column("Type", style="yellow")
                callees_table.add_column("Function", style="green")

                for callee in callees:
                    to_addr = callee.get("to", 0)
                    ref_type = callee.get("type", "UNKNOWN")
                    fcn_name = callee.get("fcn_name", "<unknown>")

                    callees_table.add_row(
                        f"0x{to_addr:x}",
                        ref_type,
                        fcn_name
                    )

                callee_title = Text(f"\n📤 Calls To ({len(callees)}):\n", style="bold yellow")
                content_parts.append(callee_title)
                content_parts.append(callees_table)

            # Help text
            help_text = Text("\nTip: Press Enter on an address to navigate to it.\n", style="dim italic")
            content_parts.append(help_text)

            # Combine all parts and wrap in panel
            from rich.console import Group
            content_group = Group(*content_parts)
            panel = Panel(content_group, title="Cross-References", border_style="blue")
            self._content_widget.update(panel)

        except Exception as e:
            self._show_error(f"Error displaying cross-references: {e}")

    def clear(self) -> None:
        """Clear the details panel and show help text."""
        self._show_help()
