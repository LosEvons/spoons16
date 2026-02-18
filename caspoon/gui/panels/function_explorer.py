"""Function explorer dock panel."""

from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDockWidget,
    QLineEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class FunctionExplorerPanel(QDockWidget):
    """Left-dock tree view of functions grouped by section.

    Signals:
        function_selected: Emitted when the user activates a function row.
            Arguments are the function name (str) and address (int).
    """

    function_selected = Signal(str, int)

    def __init__(self, parent=None) -> None:
        super().__init__("Functions", parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter functions…")
        layout.addWidget(self._filter)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Function", "Address"])

        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(0)
        self._proxy.setRecursiveFilteringEnabled(True)
        self._filter.textChanged.connect(self._proxy.setFilterWildcard)

        self._tree = QTreeView()
        self._tree.setModel(self._proxy)
        self._tree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self._tree.setRootIsDecorated(True)
        self._tree.setAlternatingRowColors(True)
        self._tree.activated.connect(self._on_activated)
        layout.addWidget(self._tree)

        self.setWidget(container)

    def populate(self, functions_by_section: dict) -> None:
        """Populate the tree from a section → function list mapping.

        Args:
            functions_by_section: Dict mapping section name to a list of dicts
                with keys ``name`` (str) and ``addr`` (int).
        """
        self._model.removeRows(0, self._model.rowCount())
        for section, funcs in functions_by_section.items():
            section_item = QStandardItem(section)
            section_item.setEditable(False)
            self._model.appendRow(section_item)
            for fn in funcs:
                name_item = QStandardItem(fn["name"])
                name_item.setEditable(False)
                name_item.setData(fn["addr"], Qt.ItemDataRole.UserRole)
                addr_item = QStandardItem(f"0x{fn['addr']:x}")
                addr_item.setEditable(False)
                section_item.appendRow([name_item, addr_item])
        self._tree.expandAll()
        self._tree.resizeColumnToContents(0)

    def clear(self) -> None:
        """Remove all items from the tree."""
        self._model.removeRows(0, self._model.rowCount())

    def _on_activated(self, index) -> None:
        source = self._proxy.mapToSource(index)
        item = self._model.itemFromIndex(source)
        if item is None:
            return
        addr = item.data(Qt.ItemDataRole.UserRole)
        if addr is not None:
            self.function_selected.emit(item.text(), int(addr))
