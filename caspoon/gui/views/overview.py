"""Overview view — binary metadata table."""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget


class OverviewView(QWidget):
    """Displays basic binary metadata as a two-column (Field / Value) table."""

    _FIELDS = [
        "Path",
        "Architecture",
        "Bits",
        "File Type",
        "File Size",
        "Stripped",
        "Entry Point",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Field", "Value"])
        self._populate_empty()

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.resizeColumnToContents(0)
        layout.addWidget(self._table)

    def _populate_empty(self) -> None:
        self._model.removeRows(0, self._model.rowCount())
        for field in self._FIELDS:
            self._model.appendRow([
                self._make_item(field, bold=True),
                self._make_item("—"),
            ])

    @staticmethod
    def _make_item(text: str, bold: bool = False) -> QStandardItem:
        item = QStandardItem(text)
        item.setEditable(False)
        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        return item

    def update_from_binary_info(self, binary_info) -> None:
        """Populate the table from a BinaryInfo object.

        Args:
            binary_info: BinaryInfo dataclass instance (or None to clear).
        """
        if binary_info is None:
            self._populate_empty()
            return

        size_str = (
            f"{binary_info.file_size:,} bytes"
            if binary_info.file_size
            else "—"
        )
        values = [
            binary_info.path,
            binary_info.architecture,
            str(binary_info.bits) if binary_info.bits else "—",
            binary_info.file_type,
            size_str,
            "Yes" if binary_info.stripped else "No",
            binary_info.entry_point or "—",
        ]

        self._model.removeRows(0, self._model.rowCount())
        for field, value in zip(self._FIELDS, values):
            self._model.appendRow([
                self._make_item(field, bold=True),
                self._make_item(str(value)),
            ])
        self._table.resizeColumnToContents(0)

    def clear(self) -> None:
        """Reset to empty state."""
        self._populate_empty()
