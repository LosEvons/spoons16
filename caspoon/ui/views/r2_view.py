
from textual.widgets import Static
from rich.pretty import Pretty
from rich.console import Group
from rich.text import Text


class R2View(Static):
    def update_data(self, report):
        r2 = report.raw_backend_data.get("r2", {})
        if not r2:
            self.update("No radare2 data found.")
            return

        parts = []

        # Functions
        funcs = r2.get("functions", [])
        parts.append(Text("Functions:", style="bold cyan"))
        for fn in funcs[:50]:  # avoid huge output
            name = fn.get("name", "<unknown>")
            offset = hex(fn.get("offset", 0))
            parts.append(Text(f"  {offset}  {name}"))

        # Main disassembly
        main_ops = r2.get("main_ops", [])
        parts.append(Text("\nMain Function Disassembly:", style="bold magenta"))
        for op in main_ops[:100]:
            offset = hex(op.get("offset", 0))
            opcode = op.get("opcode", "")
            parts.append(Text(f"  {offset}: {opcode}"))

        # Strings
        rz_strings = r2.get("strings", [])
        parts.append(Text("\nStrings (r2):", style="bold green"))
        for s in rz_strings[:50]:
            val = s.get("string", "")
            parts.append(Text(f"  {val}"))

        group = Group(*parts)
        self.update(group)
