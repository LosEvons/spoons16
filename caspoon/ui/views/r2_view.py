"""Radare2 analysis view component - SIMPLIFIED VERSION."""

from typing import Any

from rich.console import Group
from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Static

from caspoon.core.models import ExecutableReport
from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.syntax.arch_detector import detect_architecture
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax.schemes import get_default_scheme

# Display limits to prevent UI slowdown
MAX_FUNCTIONS = 50
MAX_DISASM_OPS = 100
MAX_STRINGS = 50


class R2View(VerticalScroll):
    """Display radare2 analysis results - SIMPLIFIED VERSION.

    Shows functions, disassembly of main, and strings discovered
    by radare2's analysis engine, with limits to prevent UI slowdown.
    Automatically detects architecture and uses appropriate syntax highlighting.
    
    This is a simplified version that uses VerticalScroll to handle scrolling
    without complex custom widget interactions.
    """

    def __init__(self, *args, **kwargs):
        """Initialize R2View with basic rendering."""
        super().__init__(*args, **kwargs)
        # Default highlighter for x86_64, will be updated per report
        self._highlighter = AsmHighlighter()

        # Store current report for dynamic loading
        self._current_report: ExecutableReport | None = None

        # Single content widget for all rendered output
        self._content_widget = Static()

    def compose(self):
        """Compose the R2View with single content widget."""
        yield self._content_widget

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

        r2 = report.raw_backend_data.get("r2", {})
        if not r2:
            r2_error = report.raw_backend_data.get("r2_error")
            if r2_error:
                self._content_widget.update(f"Radare2 analysis unavailable: {r2_error}")
            else:
                self._content_widget.update("No radare2 data found.")
            return

        # Render all content as a single Rich Group
        content = self._render_all_content(r2)
        self._content_widget.update(content)


    def _render_all_content(self, r2_data: dict[str, Any]) -> Group:
        """Render all content as a single Rich Group.

        Args:
            r2_data: Radare2 analysis data

        Returns:
            Rich Group containing all rendered content
        """
        parts = []

        # === FUNCTIONS SECTION ===
        funcs = r2_data.get("functions", [])
        parts.append(Text("Functions:", style="bold cyan"))
        displayed_funcs = funcs[:MAX_FUNCTIONS]
        for fn in displayed_funcs:
            name = fn.get("name", "<unknown>")
            offset = hex(fn.get("offset", 0))
            parts.append(Text(f"  {offset}  {name}"))

        if len(funcs) > MAX_FUNCTIONS:
            parts.append(Text(f"  ... {len(funcs) - MAX_FUNCTIONS} more functions (truncated)"))

        # === DISASSEMBLY SECTION ===
        parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))

        # Add the color legend
        parts.append(self._create_legend())
        parts.append(Text())  # Blank line

        # Disassemble main function with syntax highlighting
        main_ops = r2_data.get("main_ops", [])
        if main_ops:
            displayed_ops = main_ops[:MAX_DISASM_OPS]
            for op in displayed_ops:
                offset = op.get("offset", 0)
                opcode = op.get("opcode", "")
                
                # Apply syntax highlighting
                highlighted = self._highlighter.highlight_instruction(opcode)
                
                # Format as "  address  opcode"
                line = Text(f"  {hex(offset).ljust(12)}  ")
                line.append(highlighted)
                parts.append(line)

            if len(main_ops) > MAX_DISASM_OPS:
                parts.append(Text(f"  ... {len(main_ops) - MAX_DISASM_OPS} more instructions (truncated)"))

        # === STRINGS SECTION ===
        rz_strings = r2_data.get("strings", [])
        if rz_strings:
            parts.append(Text("\nStrings (r2):", style="bold green"))
            displayed_strings = rz_strings[:MAX_STRINGS]
            for s in displayed_strings:
                val = s.get("string", "")
                parts.append(Text(f"  {val}"))

            if len(rz_strings) > MAX_STRINGS:
                parts.append(Text(f"  ... {len(rz_strings) - MAX_STRINGS} more strings (truncated)"))

        return Group(*parts)
