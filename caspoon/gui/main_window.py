"""Main application window."""

from PySide6.QtCore import Qt, QSettings, QThreadPool
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QProgressBar,
    QTabWidget,
)

from caspoon.gui.panels.console import ConsolePanel
from caspoon.gui.panels.details import DetailsPanel
from caspoon.gui.panels.function_explorer import FunctionExplorerPanel
from caspoon.gui.views.imports_exports import ImportsExportsView
from caspoon.gui.views.overview import OverviewView
from caspoon.gui.views.protections import ProtectionsView
from caspoon.gui.views.r2_view import R2View
from caspoon.gui.views.strings import StringsView

# Tab indices (must match insertion order in _build_central_tabs)
_TAB_OVERVIEW    = 0
_TAB_PROTECTIONS = 1
_TAB_STRINGS     = 2
_TAB_IMPORTS     = 3
_TAB_R2          = 4


class CaspoonMainWindow(QMainWindow):
    """Top-level window: menus, toolbar, central tabs, dock panels."""

    def __init__(self, state) -> None:
        super().__init__()
        self.state = state
        self.threadpool = QThreadPool()
        self.setWindowTitle("Caspoon — Binary Analysis")
        self.setDockNestingEnabled(True)
        self.resize(1400, 900)

        self._build_central_tabs()
        self._build_docks()
        self._build_menus()
        self._build_shortcuts()
        self._build_status_bar()

        # Restore previous dock/geometry layout
        settings = QSettings("Caspoon", "GUI")
        geom = settings.value("geometry")
        state_data = settings.value("windowState")
        if geom:
            self.restoreGeometry(geom)
        if state_data:
            self.restoreState(state_data)

        # Subscribe to AppState updates
        self.state.subscribe("binary_info",      self._on_binary_info)
        self.state.subscribe("analysis_results", self._on_analysis_results)

    # ------------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------------

    def _build_central_tabs(self) -> None:
        self._overview    = OverviewView()
        self._protections = ProtectionsView()
        self._strings     = StringsView()
        self._imports     = ImportsExportsView()
        self._r2          = R2View()

        self._tabs = QTabWidget()
        self._tabs.addTab(self._overview,    "Overview")
        self._tabs.addTab(self._protections, "Protections")
        self._tabs.addTab(self._strings,     "Strings")
        self._tabs.addTab(self._imports,     "Imports / Exports")
        self._tabs.addTab(self._r2,          "R2 Analysis")
        self.setCentralWidget(self._tabs)

    def _build_docks(self) -> None:
        self._func_explorer = FunctionExplorerPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._func_explorer)

        self._details = DetailsPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._details)

        self._console = ConsolePanel(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._console)

        self._func_explorer.function_selected.connect(self._on_function_selected)

    def _build_menus(self) -> None:
        # File menu
        file_menu = self.menuBar().addMenu("&File")

        open_act = QAction("&Open Binary…", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self._open_binary_dialog)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        quit_act = QAction("&Quit", self)
        quit_act.setShortcut("Ctrl+Q")
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        # View menu — dock toggle actions
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self._func_explorer.toggleViewAction())
        view_menu.addAction(self._details.toggleViewAction())
        view_menu.addAction(self._console.toggleViewAction())

    def _build_shortcuts(self) -> None:
        # Number keys 1–5 switch tabs
        for i in range(5):
            QShortcut(str(i + 1), self, lambda idx=i: self._tabs.setCurrentIndex(idx))

        # Command palette
        QShortcut("Ctrl+P", self, self._show_command_palette)

    def _build_status_bar(self) -> None:
        self._status_label = QLabel("Ready")
        self._progress = QProgressBar()
        self._progress.setMaximumWidth(200)
        self._progress.setRange(0, 100)
        self._progress.setVisible(False)
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._progress)

    # ------------------------------------------------------------------
    # Slots / handlers
    # ------------------------------------------------------------------

    def _open_binary_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Binary",
            "",
            "Executables (*.elf *.exe *.so *.dylib *.bin);;All Files (*)",
        )
        if path:
            self._run_analysis(path)

    def _run_analysis(self, path: str) -> None:
        from caspoon.core.runner import ReconRunner
        from caspoon.gui.worker import AnalysisWorker

        self._console.log(f"Starting analysis: {path}", "info")
        self._clear_views()

        worker = AnalysisWorker(path, ReconRunner())
        worker.signals.progress.connect(self._on_progress)
        worker.signals.result.connect(self._on_analysis_done)
        worker.signals.error.connect(self._on_analysis_error)

        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._status_label.setText(f"Analysing: {path}")
        self.threadpool.start(worker)

    def _on_progress(self, pct: int, msg: str) -> None:
        self._progress.setValue(pct)
        self._status_label.setText(msg)
        self._console.log(msg, "info")

    def _on_analysis_done(self, report) -> None:
        self._progress.setVisible(False)
        self._status_label.setText("Analysis complete")
        self._console.log("Analysis complete.", "success")
        self.state.update_from_report(report)

    def _on_analysis_error(self, err: str) -> None:
        self._progress.setVisible(False)
        self._status_label.setText("Analysis failed")
        self._console.log(f"Error: {err}", "error")

    def _on_binary_info(self, binary_info) -> None:
        self._overview.update_from_binary_info(binary_info)

    def _on_analysis_results(self, results) -> None:
        if results is None:
            self._clear_views()
            return

        self._protections.update_from_protections(results.protections)
        self._strings.update_from_strings(results.strings or [])
        self._imports.update_from_results(results.imports or [], results.exports or [])

        # Populate function explorer from disassembly data if available
        functions_section: dict = {}
        disasm = results.disassembly
        if isinstance(disasm, dict):
            # r2 disassembly may have function-keyed entries
            for fn_name, ops in disasm.items():
                if isinstance(ops, list):
                    functions_section.setdefault("functions", []).append(
                        {"name": fn_name, "addr": 0}
                    )
        if functions_section:
            self._func_explorer.populate(functions_section)

        # R2 raw data
        # The disassembly is passed via raw_backend_data in update_from_report,
        # but AnalysisResults.disassembly holds the extracted value.  We wrap it
        # back into a minimal dict so R2View.set_data() works unchanged.
        self._r2.set_data({"disassembly": disasm})

    def _on_function_selected(self, name: str, addr: int) -> None:
        self._details.show_function(name, addr)
        self._console.log(f"Selected function: {name} @ 0x{addr:x}", "debug")

    def _show_command_palette(self) -> None:
        from caspoon.gui.dialogs.command_palette import CommandPalette
        palette = CommandPalette(self)
        palette.exec()

    def _clear_views(self) -> None:
        self._overview.clear()
        self._protections.clear()
        self._strings.clear()
        self._imports.clear()
        self._r2.clear()
        self._func_explorer.clear()
        self._details.clear()

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        settings = QSettings("Caspoon", "GUI")
        settings.setValue("geometry",    self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        super().closeEvent(event)
