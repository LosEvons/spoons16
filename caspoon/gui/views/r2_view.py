"""R2 Analysis view — disassembly pane with search/filter and syntax highlighting."""

import re

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPlainTextEdit,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

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
        # 1. Highlight hex addresses (lower priority)
        for m in self._ADDRESS_PAT.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self._fmt("#b5cea8"))

        # 2. Classify and highlight the mnemonic
        tokens = text.strip().split()
        if not tokens:
            return
        # Skip a leading address token and byte-string token
        idx = 0
        if tokens[idx].startswith("0x"):
            idx += 1
        if idx < len(tokens) and re.fullmatch(r'[0-9a-fA-F]+', tokens[idx]):
            idx += 1
        if idx >= len(tokens):
            return

        mnemonic = tokens[idx].rstrip(":").lower()
        instr_type = get_instruction_type(mnemonic)
        color = self._INSTR_COLOR.get(instr_type, "#d4d4d4")

        start = text.lower().find(mnemonic, text.find(tokens[0]))
        if start >= 0:
            self.setFormat(start, len(mnemonic), self._fmt(color, bold=True))


class _DisasmEdit(QPlainTextEdit):
    """QPlainTextEdit with a custom right-click context menu."""

    _ADDR_PAT = re.compile(r'0x[0-9a-fA-F]+')

    def contextMenuEvent(self, event) -> None:
        menu: QMenu = self.createStandardContextMenu()

        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        line = cursor.selectedText()

        sep = menu.insertSeparator(menu.actions()[0])

        copy_addr = menu.addAction("Copy Address")
        copy_line = menu.addAction("Copy Line")
        menu.insertAction(sep, copy_addr)
        menu.insertAction(sep, copy_line)

        action = menu.exec(event.globalPos())

        if action == copy_addr:
            m = self._ADDR_PAT.search(line)
            if m:
                QApplication.clipboard().setText(m.group())
        elif action == copy_line:
            QApplication.clipboard().setText(line)


class R2View(QWidget):
    """Disassembly viewer with search/filter toolbar and syntax highlighting."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._instructions: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Toolbar ---
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(4, 4, 4, 4)
        toolbar_layout.setSpacing(6)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search disassembly…")
        toolbar_layout.addWidget(self._search)

        self._type_combo = QComboBox()
        self._type_combo.addItem("All Types",   None)
        self._type_combo.addItem("Call",        InstructionType.CALL)
        self._type_combo.addItem("Jump",        InstructionType.JUMP)
        self._type_combo.addItem("Return",      InstructionType.RETURN)
        self._type_combo.addItem("Move",        InstructionType.MOVE)
        self._type_combo.addItem("Arithmetic",  InstructionType.ARITHMETIC)
        self._type_combo.addItem("Logic",       InstructionType.LOGIC)
        self._type_combo.addItem("Stack",       InstructionType.STACK)
        self._type_combo.addItem("Compare",     InstructionType.COMPARE)
        toolbar_layout.addWidget(self._type_combo)

        self._count_label = QLabel("0 / 0 instructions")
        toolbar_layout.addWidget(self._count_label)

        layout.addWidget(toolbar)

        # --- Disassembly editor ---
        self._disasm = _DisasmEdit()
        self._disasm.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self._disasm.setFont(font)
        self._highlighter = AsmQHighlighter(self._disasm.document())

        layout.addWidget(self._disasm)

        # --- Connections ---
        self._search.textChanged.connect(self._apply_filter)
        self._type_combo.currentIndexChanged.connect(self._apply_filter)

        # Ctrl+F focuses the search box
        QShortcut(QKeySequence("Ctrl+F"), self, self._search.setFocus)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_data(self, raw_backend_data: dict | None) -> None:
        """Populate the disassembly pane from backend data.

        Args:
            raw_backend_data: The ``raw_backend_data`` dict from
                ``ExecutableReport`` (may be None).
        """
        if not raw_backend_data:
            self._instructions = []
            self._disasm.setPlainText("No R2 data available.")
            self._update_count(0)
            return

        disasm = raw_backend_data.get("disassembly")
        if not disasm:
            self._instructions = []
            self._disasm.setPlainText("No disassembly data available.")
            self._update_count(0)
            return

        if isinstance(disasm, list):
            self._instructions = [op for op in disasm if isinstance(op, dict)]
        elif isinstance(disasm, str):
            # Plain-text fallback — no structured filtering possible
            self._instructions = []
            self._disasm.setPlainText(disasm)
            self._update_count(0)
            return
        else:
            self._instructions = []
            self._disasm.setPlainText(str(disasm))
            self._update_count(0)
            return

        self._apply_filter()

    def clear(self) -> None:
        """Clear the disassembly pane and reset filters."""
        self._instructions = []
        self._disasm.clear()
        self._update_count(0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fmt_op(op: dict) -> str:
        """Format one instruction dict as a display line."""
        addr = op.get("offset", 0)
        raw_bytes = op.get("bytes", "")
        disasm = op.get("disasm", "")
        return f"0x{addr:08x}  {raw_bytes:<12}  {disasm}"

    def _matches(self, op: dict, text: str, type_filter: InstructionType | None) -> bool:
        """Return True if *op* passes both the text and type filters."""
        if type_filter is not None:
            mnemonic = op.get("disasm", "").split()[0] if op.get("disasm") else ""
            if get_instruction_type(mnemonic.lower()) != type_filter:
                return False
        if text:
            line = self._fmt_op(op).lower()
            if text not in line:
                return False
        return True

    def _apply_filter(self) -> None:
        text = self._search.text().lower()
        type_filter = self._type_combo.currentData()
        filtered = [op for op in self._instructions if self._matches(op, text, type_filter)]
        self._disasm.setPlainText("\n".join(self._fmt_op(op) for op in filtered))
        self._update_count(len(filtered))

    def _update_count(self, visible: int) -> None:
        total = len(self._instructions)
        self._count_label.setText(f"{visible:,} / {total:,} instructions")
