"""VS Code-style dark QSS stylesheet."""

DARK_STYLESHEET = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QDockWidget { color: #d4d4d4; }
QDockWidget::title { background-color: #252526; padding: 4px; border-bottom: 1px solid #3e3e42; }
QPlainTextEdit, QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #3e3e42; font-family: Consolas, monospace; }
QLineEdit { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #3e3e42; padding: 3px; border-radius: 2px; }
QLineEdit:focus { border: 1px solid #0e639c; }
QTableView, QTreeView, QListView { background-color: #1e1e1e; color: #d4d4d4; gridline-color: #3e3e42; border: 1px solid #3e3e42; alternate-background-color: #252526; }
QTableView::item:selected, QTreeView::item:selected { background-color: #0e639c; color: #ffffff; }
QHeaderView::section { background-color: #252526; color: #d4d4d4; border: none; border-right: 1px solid #3e3e42; padding: 4px; }
QTabWidget::pane { border: 1px solid #3e3e42; }
QTabBar::tab { background-color: #2d2d2d; color: #d4d4d4; padding: 6px 14px; border: 1px solid #3e3e42; }
QTabBar::tab:selected { background-color: #1e1e1e; border-bottom: 2px solid #0e639c; }
QScrollBar:vertical { background-color: #1e1e1e; width: 10px; }
QScrollBar::handle:vertical { background-color: #464647; border-radius: 5px; min-height: 20px; }
QScrollBar:horizontal { background-color: #1e1e1e; height: 10px; }
QScrollBar::handle:horizontal { background-color: #464647; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; }
QStatusBar { background-color: #007acc; color: white; }
QPushButton { background-color: #0e639c; color: white; border: none; padding: 5px 10px; border-radius: 3px; }
QPushButton:hover { background-color: #1177bb; }
QPushButton:pressed { background-color: #0a4f7e; }
QMenuBar { background-color: #252526; color: #d4d4d4; }
QMenuBar::item:selected { background-color: #3e3e42; }
QMenu { background-color: #252526; color: #d4d4d4; border: 1px solid #3e3e42; }
QMenu::item:selected { background-color: #0e639c; }
QSplitter::handle { background-color: #3e3e42; }
QProgressBar { background-color: #3c3c3c; border: none; color: white; }
QProgressBar::chunk { background-color: #0e639c; }
QDialog { background-color: #1e1e1e; color: #d4d4d4; }
QLabel { color: #d4d4d4; }
QToolBar { background-color: #252526; border: none; spacing: 3px; }
QToolBar::separator { background-color: #3e3e42; width: 1px; height: 1px; margin: 3px; }
"""
