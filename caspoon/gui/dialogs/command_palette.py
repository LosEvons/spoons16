"""Command palette dialog (Ctrl+P)."""

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListView,
    QVBoxLayout,
)


class CommandPalette(QDialog):
    """Fuzzy-search command palette accessible via Ctrl+P.

    Commands are registered as (label, callable) pairs. The user can
    type to filter and press Enter / double-click to execute a command.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Command Palette")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Type a command…")
        self._search.textChanged.connect(self._on_filter)
        layout.addWidget(self._search)

        self._model = QStandardItemModel()
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._list = QListView()
        self._list.setModel(self._proxy)
        self._list.activated.connect(self._on_activated)
        layout.addWidget(self._list)

        self._commands: dict[str, callable] = {}
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register built-in commands provided by the main window."""
        main = self.parent()
        if main is None:
            return

        builtins = {
            "File: Open Binary…": lambda: main._open_binary_dialog(),
            "View: Toggle Function Explorer": lambda: main._func_explorer.toggleViewAction().trigger(),
            "View: Toggle Details Panel": lambda: main._details.toggleViewAction().trigger(),
            "View: Toggle Console": lambda: main._console.toggleViewAction().trigger(),
            "File: Quit": lambda: main.close(),
        }
        for label, fn in builtins.items():
            self.add_command(label, fn)

    def add_command(self, label: str, fn) -> None:
        """Register a new command.

        Args:
            label: Human-readable command name shown in the list.
            fn: Callable to invoke when the command is selected.
        """
        self._commands[label] = fn
        item = QStandardItem(label)
        item.setEditable(False)
        item.setData(label, Qt.ItemDataRole.UserRole)
        self._model.appendRow(item)

    def _on_filter(self, text: str) -> None:
        self._proxy.setFilterWildcard(f"*{text}*")

    def _on_activated(self, index) -> None:
        source = self._proxy.mapToSource(index)
        item = self._model.itemFromIndex(source)
        if item is None:
            return
        label = item.data(Qt.ItemDataRole.UserRole)
        fn = self._commands.get(label)
        self.accept()
        if fn:
            fn()
