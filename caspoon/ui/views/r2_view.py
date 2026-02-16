"""Radare2 analysis view component."""

import logging

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.syntax import AsmHighlighter
from caspoon.ui.syntax.arch_detector import detect_architecture
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax.schemes import get_default_scheme

logger = logging.getLogger(__name__)

# Display limits to prevent UI slowdown
MAX_FUNCTIONS = 50
MAX_DISASM_OPS = 100
MAX_STRINGS = 50


class R2View(BaseView[dict | None]):
    """Display radare2 analysis results.

    Shows functions, disassembly of main, and strings discovered
    by radare2's analysis engine, with limits to prevent UI slowdown.
    Automatically detects architecture and uses appropriate syntax highlighting.

    Automatically updates when AppState.analysis_results changes (extracts r2 data).
    """

    def __init__(self, *args, **kwargs):
        """Initialize R2View with default syntax highlighter."""
        super().__init__(*args, **kwargs)
        # Default highlighter for x86_64, will be updated per report
        self._highlighter = AsmHighlighter()
        # Store current architecture for highlighter updates
        self._current_arch = None

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
        """Render r2 analysis data with syntax highlighting.

        Args:
            data: Dictionary containing r2 analysis data (functions, main_ops, strings)
                  or None if no data available
        """
        if not data:
            self.update("[dim]No radare2 data available.[/dim]")
            return

        # Check for r2 errors
        if "r2_error" in data:
            error_msg = data["r2_error"]
            self.update(f"[red]Radare2 analysis unavailable: {error_msg}[/]")
            return

        parts = []

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

        # Wrap in panel for visual consistency
        group = Group(*parts)
        panel = Panel(
            group, title="[bold]Radare2 Analysis[/bold]", border_style="magenta", padding=(1, 2)
        )
        self.update(panel)

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
