"""Radare2 analysis view component."""

import logging
import re

from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.binding import Binding

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.messages import JumpToAddress
from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.syntax.arch_detector import detect_architecture
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax.schemes import get_default_scheme

logger = logging.getLogger(__name__)

# Display limits to prevent UI slowdown
MAX_FUNCTIONS = 50
MAX_DISASM_OPS = 100
MAX_STRINGS = 50


class R2View(InteractiveView[dict | None]):
    """Display radare2 analysis results with interactive navigation.

    Shows functions, disassembly of main, and strings discovered
    by radare2's analysis engine, with limits to prevent UI slowdown.
    Automatically detects architecture and uses appropriate syntax highlighting.

    Interactive Features:
    - Arrow keys / j/k: Navigate between lines
    - Enter: Jump to address on selected line
    - x: Show cross-references for selected address (future)

    Automatically updates when AppState.analysis_results changes (extracts r2 data).
    """

    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("home", "move_to_top", "First", show=False),
        Binding("end", "move_to_bottom", "Last", show=False),
        Binding("enter", "select_item", "Jump to Address", show=True),
        Binding("x", "show_xrefs", "Show Xrefs", show=True),
    ]

    def __init__(self, *args, **kwargs):
        """Initialize R2View with default syntax highlighter."""
        super().__init__(*args, **kwargs)
        # Default highlighter for x86_64, will be updated per report
        self._highlighter = AsmHighlighter()
        # Store current architecture for highlighter updates
        self._current_arch = None
        # Map line numbers to addresses for navigation
        self._address_map: dict[int, str] = {}
        # Store all lines for rendering with selection highlighting
        self._all_lines: list[Text] = []

    def on_mount(self) -> None:
        """Subscribe to analysis results updates from AppState.

        This is called when the view is added to the app. It sets up
        the reactive subscription to get r2 data from raw_backend_data.
        """
        try:
            app = self.app
            if hasattr(app, "state"):
                # We need to watch for report updates to get raw_backend_data
                # For now, we'll keep backward compatibility and rely on update_data()
                # In a full migration, we'd need to add raw_backend_data to AppState
                logger.debug("R2View mounted (using legacy update path)")
        except Exception as e:
            # Handle case where app is not available (e.g., in tests)
            logger.debug(f"Could not initialize in on_mount: {e}")

    # ========================================================================
    # InteractiveView Required Methods
    # ========================================================================

    def get_item_count(self) -> int:
        """Return number of navigable lines in the view.

        Returns:
            Total number of lines available for selection
        """
        return len(self._all_lines)

    def on_item_selected(self, index: int) -> None:
        """Handle selection of a line (Enter key pressed).

        If the selected line has an associated address, posts a JumpToAddress
        message to navigate to that address.

        Args:
            index: Index of selected line (0-based)
        """
        # Check if this line has an address
        address = self._address_map.get(index)
        if address:
            logger.debug(f"R2View: Jumping to address {address} from line {index}")
            # Post message to app to handle navigation
            self.post_message(JumpToAddress(address))
            # Update navigation history in app state
            try:
                if hasattr(self.app, "state"):
                    self.app.state.navigate_to(address)
            except Exception as e:
                logger.debug(f"Could not update navigation history: {e}")
        else:
            logger.debug(f"R2View: Line {index} has no associated address")

    def apply_filter(self, text: str) -> None:
        """Apply filter to disassembly view.

        Currently not implemented for R2View as filtering disassembly
        is complex and might break address mapping. Future enhancement
        could filter to show only lines matching certain instructions.

        Args:
            text: Filter text (currently ignored)
        """
        # For now, filtering is not supported in R2View
        # We could implement instruction filtering in the future
        pass

    def action_show_xrefs(self) -> None:
        """Show cross-references for the currently selected address.

        Bound to: x key

        If the selected line has an address, shows cross-references to/from
        that address. This will be implemented in future steps.
        """
        address = self._address_map.get(self.selected_index)
        if address:
            logger.info(f"R2View: Show xrefs for address {address} (not yet implemented)")
            # TODO: Implement xref display (Step 4)
            # For now, just log the request
        else:
            logger.debug(f"R2View: No address at line {self.selected_index}")

    # ========================================================================
    # Address Parsing and Mapping
    # ========================================================================

    def _parse_address_from_line(self, text: str) -> str | None:
        """Extract address from a disassembly line.

        Looks for hex addresses in the format 0x[hex] at the start of the line.

        Args:
            text: Line of text to parse

        Returns:
            Address as hex string (e.g., "0x401000") or None if no address found
        """
        # Match hex address at start of line: 0x followed by hex digits
        match = re.match(r"^\s*(0x[0-9a-fA-F]+)", text)
        if match:
            return match.group(1)
        return None

    def _build_address_map(self, lines: list[Text]) -> dict[int, str]:
        """Build mapping from line numbers to addresses.

        Args:
            lines: List of Text objects representing disassembly lines

        Returns:
            Dictionary mapping line index to address string
        """
        address_map: dict[int, str] = {}
        for i, line in enumerate(lines):
            # Extract plain text from Rich Text object
            line_text = line.plain
            address = self._parse_address_from_line(line_text)
            if address:
                address_map[i] = address
        return address_map

    # ========================================================================
    # Rendering
    # ========================================================================


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

    def render_content(self, data: dict | None) -> None:
        """Render r2 analysis data with syntax highlighting and selection support.

        Args:
            data: Dictionary containing r2 analysis data (functions, main_ops, strings)
                  or None if no data available
        """
        if not data:
            self._all_lines = [Text("[dim]No radare2 data available.[/dim]")]
            self._address_map = {}
            self.update(self._all_lines[0])
            return

        # Check for r2 errors
        if "r2_error" in data:
            error_msg = data["r2_error"]
            self._all_lines = [Text(f"[red]Radare2 analysis unavailable: {error_msg}[/]")]
            self._address_map = {}
            self.update(self._all_lines[0])
            return

        parts: list[Text] = []

        # Functions
        funcs = data.get("functions", [])
        parts.append(Text("Functions:", style="bold cyan"))
        displayed_funcs = funcs[:MAX_FUNCTIONS]
        for fn in displayed_funcs:
            name = fn.get("name", "<unknown>")
            offset = hex(fn.get("offset", 0))
            parts.append(Text(f"  {offset}  {name}"))

        if len(funcs) > MAX_FUNCTIONS:
            parts.append(Text(f"  ... {len(funcs) - MAX_FUNCTIONS} more functions (truncated)"))

        # Main disassembly
        main_ops = data.get("main_ops", [])
        parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))

        # Add the color legend right before the disassembly
        parts.append(self._create_legend())
        parts.append(Text())  # Add a blank line for spacing

        displayed_ops = main_ops[:MAX_DISASM_OPS]
        for op in displayed_ops:
            offset = hex(op.get("offset", 0))
            opcode = op.get("opcode", "")
            # Apply syntax highlighting to disassembly
            highlighted = self._highlighter.highlight_instruction(opcode, offset)
            # Add indentation
            indented = Text("  ")
            indented.append_text(highlighted)
            parts.append(indented)

        if len(main_ops) > MAX_DISASM_OPS:
            parts.append(
                Text(f"  ... {len(main_ops) - MAX_DISASM_OPS} more instructions (truncated)")
            )

        # Strings
        rz_strings = data.get("strings", [])
        parts.append(Text("\nStrings (r2):", style="bold green"))
        displayed_strings = rz_strings[:MAX_STRINGS]
        for s in displayed_strings:
            val = s.get("string", "")
            parts.append(Text(f"  {val}"))

        if len(rz_strings) > MAX_STRINGS:
            parts.append(Text(f"  ... {len(rz_strings) - MAX_STRINGS} more strings (truncated)"))

        # Store all lines for navigation
        self._all_lines = parts

        # Build address map for navigation
        self._address_map = self._build_address_map(parts)

        # Apply selection highlighting to current line
        display_parts = self._apply_selection_highlighting(parts)

        # Wrap in panel for visual consistency
        group = Group(*display_parts)
        panel = Panel(
            group, title="[bold]Radare2 Analysis[/bold]", border_style="magenta", padding=(1, 2)
        )
        self.update(panel)

    def _apply_selection_highlighting(self, lines: list[Text]) -> list[Text]:
        """Apply selection highlighting to the currently selected line.

        Args:
            lines: List of Text objects to potentially highlight

        Returns:
            New list of Text objects with selection highlighting applied
        """
        highlighted_lines: list[Text] = []
        for i, line in enumerate(lines):
            if i == self.selected_index:
                # Create a copy with reverse style for selection
                selected_line = Text()
                selected_line.append_text(line)
                selected_line.stylize("reverse")
                highlighted_lines.append(selected_line)
            else:
                highlighted_lines.append(line)
        return highlighted_lines

    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """Re-render when selection changes to update highlighting.

        Args:
            old_value: Previous selected index
            new_value: New selected index
        """
        # Call parent to ensure bounds checking
        super().watch_selected_index(old_value, new_value)
        
        # Re-render with updated selection if we have data
        # Only re-render if values actually changed to avoid infinite loops
        if self.data is not None and old_value != new_value:
            try:
                self.render_content(self.data)
            except Exception as e:
                # Handle case where app context is not available (e.g., in tests)
                logger.debug(f"Could not re-render on selection change: {e}")

    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.

        This method handles both legacy compatibility and architecture detection
        for syntax highlighting.

        Args:
            report: ExecutableReport containing analysis results
        """
        # Detect architecture and create appropriate highlighter
        arch = detect_architecture(report)
        if arch != self._current_arch:
            classifier = get_instruction_classifier(arch)
            self._highlighter = AsmHighlighter(instruction_classifier=classifier)
            self._current_arch = arch
            logger.debug(f"R2View: Updated highlighter for architecture: {arch}")

        r2 = report.raw_backend_data.get("r2", {})
        if not r2:
            r2_error = report.raw_backend_data.get("r2_error")
            if r2_error:
                self.update(f"Radare2 analysis unavailable: {r2_error}")
            else:
                self.update("No radare2 data found.")
            return

        # Use render_content for consistency (sets self.data internally)
        self.render_content(
            r2 | {"r2_error": report.raw_backend_data.get("r2_error")}
            if "r2_error" in report.raw_backend_data
            else r2
        )
