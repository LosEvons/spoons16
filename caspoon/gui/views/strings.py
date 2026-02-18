"""Strings view — filterable table of extracted strings."""

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class StringsView(QWidget):
    """QTableView of extracted strings with a live-filter input."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Filter bar
        bar = QWidget()
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(4, 4, 4, 0)
        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter strings…")
        self._count_label = QLabel("0 strings")
        bar_layout.addWidget(self._filter)
        bar_layout.addWidget(self._count_label)
        layout.addWidget(bar)

        # Model
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["#", "String"])

        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(1)
        self._filter.textChanged.connect(self._proxy.setFilterWildcard)
        self._proxy.rowsInserted.connect(self._update_count)
        self._proxy.rowsRemoved.connect(self._update_count)
        self._proxy.layoutChanged.connect(self._update_count)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def update_from_strings(self, strings: list[str]) -> None:
        """Populate the table from a list of strings.

        Args:
            strings: List of extracted string values.
        """
        self._model.removeRows(0, self._model.rowCount())
        for i, s in enumerate(strings, 1):
            idx_item = QStandardItem(str(i))
            idx_item.setEditable(False)
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            str_item = QStandardItem(s)
            str_item.setEditable(False)
            self._model.appendRow([idx_item, str_item])
        self._table.resizeColumnToContents(0)
        self._update_count()

    def _update_count(self) -> None:
        total = self._model.rowCount()
        visible = self._proxy.rowCount()
        if total == visible:
            self._count_label.setText(f"{total:,} strings")
        else:
            self._count_label.setText(f"{visible:,} / {total:,} strings")

    def clear(self) -> None:
        """Remove all strings."""
        self._model.removeRows(0, self._model.rowCount())
        self._update_count()
