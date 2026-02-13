"""Radare2 analysis view component."""

from typing import Any

from rich.console import Group
from rich.text import Text
from textual import on
from textual.containers import Container
from textual.widgets import Static

from caspoon.core.models import ExecutableReport
from caspoon.ui.navigation.manager import NavigationManager
from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.syntax.arch_detector import detect_architecture
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax.schemes import get_default_scheme
from caspoon.ui.widgets.interactive_disasm import InteractiveDisasmView

# Display limits to prevent UI slowdown
MAX_FUNCTIONS = 50
MAX_DISASM_OPS = 100
MAX_STRINGS = 50


class R2View(Container):
    """Display radare2 analysis results.

    Shows functions, disassembly of main, and strings discovered
    by radare2's analysis engine, with limits to prevent UI slowdown.
    Automatically detects architecture and uses appropriate syntax highlighting.
    Features interactive navigation through disassembly.
    """

    def __init__(self, *args, **kwargs):
        """Initialize R2View with navigation and caching."""
        super().__init__(*args, **kwargs)
        # Default highlighter for x86_64, will be updated per report
        self._highlighter = AsmHighlighter()

        # Navigation manager for history tracking
        self._nav_manager = NavigationManager()

        # Cache for function disassembly to avoid re-querying r2
        self._disasm_cache: dict[str, list[dict[str, Any]]] = {}

        # Store current report for dynamic loading
        self._current_report: ExecutableReport | None = None

        # Widgets for display
        self._header_widget = Static()
        self._interactive_disasm = InteractiveDisasmView(
            navigation_manager=self._nav_manager,
            highlighter=self._highlighter
        )

        # Add widgets to container
        # Remove explicit height to allow proper scrolling
        # self._header_widget.styles.height = "auto"
        # self._interactive_disasm.styles.height = "auto"

    def compose(self):
        """Compose the R2View with header and interactive disassembly."""
        yield self._header_widget
        yield self._interactive_disasm

    def _create_legend(self) -> Text:
        """Create a color legend showing instruction type colors.

        Returns:
            A Rich Text object containing the formatted legend.
        """
        scheme = get_default_scheme()
        legend = Text("Color Legend: ", style="bold")

        # Define legend items with their colors
        items = [
            ("Jump", scheme.jump),
            ("Call", scheme.call),
            ("Move", scheme.move),
            ("Arithmetic", scheme.arithmetic),
            ("Logic", scheme.logic),
            ("Stack", scheme.stack),
            ("Compare", scheme.compare),
            ("Return", scheme.return_),
        ]

        # Add each item with its color
        for i, (label, color) in enumerate(items):
            if i > 0:
                legend.append(" | ", style="dim")
            legend.append(label, style=color)

        return legend

    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.

        Args:
            report: ExecutableReport containing analysis results
        """
        self._current_report = report

        # Detect architecture and create appropriate highlighter
        arch = detect_architecture(report)
        classifier = get_instruction_classifier(arch)
        self._highlighter = AsmHighlighter(instruction_classifier=classifier)

        # Update interactive widget's highlighter
        self._interactive_disasm.highlighter = self._highlighter

        # Clear caches and navigation
        self._disasm_cache.clear()
        self._nav_manager.clear_history()

        r2 = report.raw_backend_data.get("r2", {})
        if not r2:
            r2_error = report.raw_backend_data.get("r2_error")
            if r2_error:
                self._header_widget.update(f"Radare2 analysis unavailable: {r2_error}")
            else:
                self._header_widget.update("No radare2 data found.")
            self._interactive_disasm.update("")
            return

        # Build address map for navigation
        self._build_address_map(r2)

        # Display header information (functions, strings, legend)
        self._display_header(r2)

        # Display main function disassembly in interactive widget
        main_ops = r2.get("main_ops", [])
        if main_ops:
            # Cache main function disassembly
            self._disasm_cache["main"] = main_ops
            # Display in interactive widget
            self._display_disasm(main_ops, "main", None)

    def _build_address_map(self, r2_data: dict[str, Any]) -> None:
        """Build address map from r2 functions for navigation.

        Args:
            r2_data: Radare2 analysis data
        """
        address_map = {}
        funcs = r2_data.get("functions", [])

        for fn in funcs:
            offset = fn.get("offset")
            if offset is not None:
                # Store function metadata by address
                address_map[hex(offset)] = {
                    "name": fn.get("name", "<unknown>"),
                    "offset": offset,
                    "size": fn.get("size", 0),
                }

        self._nav_manager.set_address_map(address_map)

    def _display_header(self, r2_data: dict[str, Any]) -> None:
        """Display header with functions list, legend, and strings.

        Args:
            r2_data: Radare2 analysis data
        """
        parts = []

        # Functions
        funcs = r2_data.get("functions", [])
        parts.append(Text("Functions:", style="bold cyan"))
        displayed_funcs = funcs[:MAX_FUNCTIONS]
        for fn in displayed_funcs:
            name = fn.get("name", "<unknown>")
            offset = hex(fn.get("offset", 0))
            parts.append(Text(f"  {offset}  {name}"))

        if len(funcs) > MAX_FUNCTIONS:
            parts.append(Text(f"  ... {len(funcs) - MAX_FUNCTIONS} more functions (truncated)"))

        # Add spacing before disassembly section
        parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))

        # Add the color legend
        parts.append(self._create_legend())
        parts.append(Text())  # Add a blank line for spacing

        # Strings section
        rz_strings = r2_data.get("strings", [])
        if rz_strings:
            parts.append(Text("\nStrings (r2):", style="bold green"))
            displayed_strings = rz_strings[:MAX_STRINGS]
            for s in displayed_strings:
                val = s.get("string", "")
                parts.append(Text(f"  {val}"))

            if len(rz_strings) > MAX_STRINGS:
                parts.append(Text(f"  ... {len(rz_strings) - MAX_STRINGS} more strings (truncated)"))

        group = Group(*parts)
        self._header_widget.update(group)

    def _display_disasm(
        self,
        ops: list[dict[str, Any]],
        function_name: str,
        current_address: str | None
    ) -> None:
        """Display disassembly in the interactive widget.

        Args:
            ops: List of disassembly operations
            function_name: Name of the function being displayed
            current_address: Optional address to highlight
        """
        # Limit ops to prevent UI slowdown
        displayed_ops = ops[:MAX_DISASM_OPS]

        # Update interactive widget
        self._interactive_disasm.update_disassembly(
            disasm_ops=displayed_ops,
            function_name=function_name,
            current_address=current_address
        )

    def _get_function_disasm(self, address: str) -> tuple[list[dict[str, Any]], str] | None:
        """Get disassembly for a function at the given address.

        Args:
            address: Target address (hex string)

        Returns:
            Tuple of (disassembly ops, function name) or None if not found
        """
        if not self._current_report:
            return None

        # Check cache first
        if address in self._disasm_cache:
            func_info = self._nav_manager.address_map.get(address, {})
            func_name = func_info.get("name", address)
            return self._disasm_cache[address], func_name

        # Look up function in address map
        func_info = self._nav_manager.address_map.get(address)
        if not func_info:
            # Try to find by normalized address
            for addr, info in self._nav_manager.address_map.items():
                try:
                    if int(addr, 16) == int(address, 16):
                        func_info = info
                        address = addr
                        break
                except ValueError:
                    continue

        if not func_info:
            return None

        # For now, we only have main_ops cached
        # In a full implementation, we'd query r2 for other functions
        # For this MVP, return None for non-main functions
        if func_info.get("name") != "main":
            return None

        r2_data = self._current_report.raw_backend_data.get("r2", {})
        main_ops = r2_data.get("main_ops", [])

        if main_ops:
            self._disasm_cache["main"] = main_ops
            return main_ops, "main"

        return None

    @on(InteractiveDisasmView.NavigateTo)
    def _handle_navigate_to(self, message: InteractiveDisasmView.NavigateTo) -> None:
        """Handle navigation to a new address.

        Args:
            message: Navigation message with target address
        """
        # Try to get disassembly for the target address
        result = self._get_function_disasm(message.address)

        if result:
            ops, func_name = result
            self._display_disasm(ops, func_name, message.address)
        else:
            # Address not found - could show error or just ignore
            # For now, we'll just not navigate
            pass

    @on(InteractiveDisasmView.ShowXrefs)
    def _handle_show_xrefs(self, message: InteractiveDisasmView.ShowXrefs) -> None:
        """Handle request to show cross-references.

        Args:
            message: Xref message with target address
        """
        if not self._current_report:
            return

        # Get xrefs from report
        r2_data = self._current_report.raw_backend_data.get("r2", {})
        xrefs = r2_data.get("xrefs", {})

        # Find xrefs for this address
        addr_xrefs = xrefs.get(message.address, [])

        if addr_xrefs:
            # Display xrefs (for now, just show in header)
            xref_text = Text(f"\nCross-references for {message.address}:", style="bold yellow")
            for xref in addr_xrefs[:10]:  # Limit to 10 xrefs
                xref_text.append(f"\n  {xref}")

            # Append to current header
            current = self._header_widget.renderable
            if isinstance(current, Group):
                new_parts = list(current.renderables)
                new_parts.append(xref_text)
                self._header_widget.update(Group(*new_parts))
        else:
            # No xrefs found
            pass

    @on(InteractiveDisasmView.OpenGotoDialog)
    def _handle_open_goto(self, message: InteractiveDisasmView.OpenGotoDialog) -> None:
        """Handle request to open goto dialog.

        Args:
            message: Goto dialog request message
        """
        # TODO: Implement goto dialog
        # For now, this is a placeholder
        pass
