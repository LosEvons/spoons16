"""R2 Analysis view — disassembly pane with syntax highlighting."""

import re

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Reuse classification logic from the existing syntax module
from caspoon.ui.syntax.instructions import get_instruction_type
from caspoon.ui.syntax.schemes import InstructionType


class AsmQHighlighter(QSyntaxHighlighter):
    """Qt syntax highlighter for assembly disassembly text.

    Reuses the existing :func:`get_instruction_type` classifier from
    ``caspoon.ui.syntax`` and maps its results to Qt text formats.
    """

    _INSTR_COLOR: dict[InstructionType, str] = {
        InstructionType.JUMP:       "#569cd6",  # blue
        InstructionType.CALL:       "#dcdcaa",  # yellow
        InstructionType.MOVE:       "#9cdcfe",  # light blue
        InstructionType.ARITHMETIC: "#ce9178",  # orange
        InstructionType.LOGIC:      "#c586c0",  # purple
        InstructionType.STACK:      "#4ec9b0",  # teal
        InstructionType.COMPARE:    "#d7ba7d",  # gold
        InstructionType.RETURN:     "#f44747",  # red
        InstructionType.OTHER:      "#d4d4d4",  # default
    }

    _ADDRESS_PAT = re.compile(r'0x[0-9a-fA-F]+')
    # Match the leading mnemonic token on a line (optionally preceded by an address)
    _MNEMONIC_PAT = re.compile(r'^\s*(?:0x[0-9a-fA-F]+\s+)?\S+\s+(\w+)')

    def __init__(self, document=None) -> None:
        super().__init__(document)

    @staticmethod
    def _fmt(color_hex: str, bold: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def highlightBlock(self, text: str) -> None:
        # 1. Highlight hex addresses first (lower priority)
        for m in self._ADDRESS_PAT.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self._fmt("#b5cea8"))

        # 2. Classify and highlight the first mnemonic on the line
        tokens = text.strip().split()
        if not tokens:
            return
        # Skip a leading address token like "0x1234:" or "0x1234"
        idx = 0
        if tokens[0].startswith("0x") or tokens[0].rstrip(":").startswith("0x"):
            idx = 1
        if idx >= len(tokens):
            return

        mnemonic = tokens[idx].rstrip(":").lower()
        instr_type = get_instruction_type(mnemonic)
        color = self._INSTR_COLOR.get(instr_type, "#d4d4d4")

        # Find the mnemonic's position in the raw text
        start = text.lower().find(mnemonic, text.find(tokens[0]))
        if start >= 0:
            self.setFormat(start, len(mnemonic), self._fmt(color, bold=True))


class R2View(QWidget):
    """Disassembly viewer backed by QPlainTextEdit + AsmQHighlighter."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._disasm = QPlainTextEdit()
        self._disasm.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self._disasm.setFont(font)
        self._highlighter = AsmQHighlighter(self._disasm.document())

        layout.addWidget(self._disasm)

    def set_data(self, raw_backend_data: dict | None) -> None:
        """Populate the disassembly pane from backend data.

        Args:
            raw_backend_data: The ``raw_backend_data`` dict from
                ``ExecutableReport`` (may be None).
        """
        if not raw_backend_data:
            self._disasm.setPlainText("No R2 data available.")
            return

        disasm = raw_backend_data.get("disassembly")
        if not disasm:
            self._disasm.setPlainText("No disassembly data available.")
            return

        if isinstance(disasm, list):
            lines = disasm[:500]
            self._disasm.setPlainText("\n".join(str(l) for l in lines))
        elif isinstance(disasm, str):
            self._disasm.setPlainText(disasm)
        else:
            self._disasm.setPlainText(str(disasm))

    def clear(self) -> None:
        """Clear the disassembly pane."""
        self._disasm.clear()
