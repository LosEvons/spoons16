"""Protections view — security feature status table."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget

_COLOR_ENABLED  = QColor("#4ec9b0")   # teal — protection active (good)
_COLOR_DISABLED = QColor("#f44747")   # red  — protection missing
_COLOR_PARTIAL  = QColor("#dcdcaa")   # yellow — partial (e.g. RELRO partial)
_COLOR_UNKNOWN  = QColor("#808080")   # grey  — not determined


def _relro_color(value: str) -> QColor:
    v = (value or "").lower()
    if v == "full":
        return _COLOR_ENABLED
    if v in ("partial", "now"):
        return _COLOR_PARTIAL
    if v in ("none", "no", "disabled"):
        return _COLOR_DISABLED
    return _COLOR_UNKNOWN


class ProtectionsView(QWidget):
    """Displays PIE / NX / Canary / RELRO with colored status labels."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Protection", "Status", "Description"])
        self._populate_empty()

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    _ROWS = [
        ("PIE",    "Position-Independent Executable — randomises base address"),
        ("NX",     "Non-Executable stack/heap — prevents shellcode execution"),
        ("Canary", "Stack canary — detects stack buffer overflows"),
        ("RELRO",  "Relocation Read-Only — hardens GOT/PLT against overwrites"),
    ]

    def _populate_empty(self) -> None:
        self._model.removeRows(0, self._model.rowCount())
        for name, desc in self._ROWS:
            self._model.appendRow([
                self._label_item(name),
                self._status_item("Unknown", _COLOR_UNKNOWN),
                self._label_item(desc),
            ])

    @staticmethod
    def _label_item(text: str) -> QStandardItem:
        item = QStandardItem(text)
        item.setEditable(False)
        return item

    @staticmethod
    def _status_item(text: str, color: QColor) -> QStandardItem:
        item = QStandardItem(text)
        item.setEditable(False)
        item.setForeground(color)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def update_from_protections(self, protections: dict | None) -> None:
        """Populate the table from a protections dictionary.

        Args:
            protections: Dict with keys pie, nx, canary, relro (from AppState).
                         Pass None to reset to unknown state.
        """
        if not protections:
            self._populate_empty()
            return

        def bool_status(val) -> tuple[str, QColor]:
            if val is True:
                return "Enabled", _COLOR_ENABLED
            if val is False:
                return "Disabled", _COLOR_DISABLED
            return "Unknown", _COLOR_UNKNOWN

        pie_text, pie_color     = bool_status(protections.get("pie"))
        nx_text, nx_color       = bool_status(protections.get("nx"))
        canary_text, can_color  = bool_status(protections.get("canary"))
        relro_val               = str(protections.get("relro", "Unknown"))
        relro_color             = _relro_color(relro_val)
        relro_text              = relro_val if relro_val else "Unknown"

        rows = [
            (pie_text,    pie_color),
            (nx_text,     nx_color),
            (canary_text, can_color),
            (relro_text,  relro_color),
        ]

        self._model.removeRows(0, self._model.rowCount())
        for (name, desc), (status, color) in zip(self._ROWS, rows):
            self._model.appendRow([
                self._label_item(name),
                self._status_item(status, color),
                self._label_item(desc),
            ])
        self._table.resizeColumnToContents(0)
        self._table.resizeColumnToContents(1)

    def clear(self) -> None:
        """Reset to unknown state."""
        self._populate_empty()
