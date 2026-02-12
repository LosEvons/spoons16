"""Radare2 analysis view component."""

from textual.widgets import Static
from rich.pretty import Pretty
from rich.console import Group
from rich.text import Text

from caspoon.core.models import ExecutableReport

# Display limits to prevent UI slowdown
MAX_FUNCTIONS = 50
MAX_DISASM_OPS = 100
MAX_STRINGS = 50


class R2View(Static):
    """Display radare2 analysis results.
    
    Shows functions, disassembly of main, and strings discovered
    by radare2's analysis engine, with limits to prevent UI slowdown.
    """
    
    def update_data(self, report: ExecutableReport) -> None:
        """Update the view with new report data.
        
        Args:
            report: ExecutableReport containing analysis results
        """
        r2 = report.raw_backend_data.get("r2", {})
        if not r2:
            r2_error = report.raw_backend_data.get("r2_error")
            if r2_error:
                self.update(f"Radare2 analysis unavailable: {r2_error}")
            else:
                self.update("No radare2 data found.")
            return

        parts = []

        # Functions
        funcs = r2.get("functions", [])
        parts.append(Text("Functions:", style="bold cyan"))
        displayed_funcs = funcs[:MAX_FUNCTIONS]
        for fn in displayed_funcs:
            name = fn.get("name", "<unknown>")
            offset = hex(fn.get("offset", 0))
            parts.append(Text(f"  {offset}  {name}"))
        
        if len(funcs) > MAX_FUNCTIONS:
            parts.append(Text(f"  ... {len(funcs) - MAX_FUNCTIONS} more functions (truncated)"))

        # Main disassembly
        main_ops = r2.get("main_ops", [])
        parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))
        displayed_ops = main_ops[:MAX_DISASM_OPS]
        for op in displayed_ops:
            offset = hex(op.get("offset", 0))
            opcode = op.get("opcode", "")
            parts.append(Text(f"  {offset}: {opcode}"))
        
        if len(main_ops) > MAX_DISASM_OPS:
            parts.append(Text(f"  ... {len(main_ops) - MAX_DISASM_OPS} more instructions (truncated)"))

        # Strings
        rz_strings = r2.get("strings", [])
        parts.append(Text("\nStrings (r2):", style="bold green"))
        displayed_strings = rz_strings[:MAX_STRINGS]
        for s in displayed_strings:
            val = s.get("string", "")
            parts.append(Text(f"  {val}"))
        
        if len(rz_strings) > MAX_STRINGS:
            parts.append(Text(f"  ... {len(rz_strings) - MAX_STRINGS} more strings (truncated)"))

        group = Group(*parts)
        self.update(group)
