"""Imports / Exports view — two tables side by side."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)


def _build_table(model: QStandardItemModel) -> QTableView:
    table = QTableView()
    table.setModel(model)
    table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    return table


class ImportsExportsView(QWidget):
    """Two side-by-side tables: Imports (left) and Exports (right)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Imports pane
        imports_widget = QWidget()
        imp_layout = QVBoxLayout(imports_widget)
        imp_layout.setContentsMargins(0, 0, 0, 0)
        imp_layout.addWidget(QLabel("<b>Imports</b>"))
        self._imports_model = QStandardItemModel()
        self._imports_model.setHorizontalHeaderLabels(["#", "Name"])
        self._imports_table = _build_table(self._imports_model)
        imp_layout.addWidget(self._imports_table)
        splitter.addWidget(imports_widget)

        # Exports pane
        exports_widget = QWidget()
        exp_layout = QVBoxLayout(exports_widget)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        exp_layout.addWidget(QLabel("<b>Exports</b>"))
        self._exports_model = QStandardItemModel()
        self._exports_model.setHorizontalHeaderLabels(["#", "Name"])
        self._exports_table = _build_table(self._exports_model)
        exp_layout.addWidget(self._exports_table)
        splitter.addWidget(exports_widget)

        layout.addWidget(splitter)

    @staticmethod
    def _fill_model(model: QStandardItemModel, items: list[str]) -> None:
        model.removeRows(0, model.rowCount())
        for i, name in enumerate(items, 1):
            idx_item = QStandardItem(str(i))
            idx_item.setEditable(False)
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            name_item = QStandardItem(name)
            name_item.setEditable(False)
            model.appendRow([idx_item, name_item])

    def update_from_results(self, imports: list[str], exports: list[str]) -> None:
        """Populate both tables.

        Args:
            imports: List of imported symbol names.
            exports: List of exported symbol names.
        """
        self._fill_model(self._imports_model, imports or [])
        self._fill_model(self._exports_model, exports or [])
        self._imports_table.resizeColumnToContents(0)
        self._exports_table.resizeColumnToContents(0)

    def clear(self) -> None:
        """Clear both tables."""
        self._imports_model.removeRows(0, self._imports_model.rowCount())
        self._exports_model.removeRows(0, self._exports_model.rowCount())
