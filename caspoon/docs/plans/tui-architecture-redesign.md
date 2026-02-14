# IDE-Like TUI Architecture Design for Caspoon

**Version**: 1.0  
**Author**: CLI/Reporting Agent  
**Date**: 2024  
**Status**: Design Proposal

---

## Executive Summary

This document proposes a comprehensive redesign of Caspoon's TUI from a simple tabbed interface to a professional, IDE-like experience leveraging Textual's advanced features. The architecture emphasizes:

- **Async-first design** with workers and reactive properties
- **Event-driven architecture** with centralized state management
- **Extensible plugin system** for views and analyzers
- **Complete keyboard control** with command palette
- **Professional multi-panel layout** with docking
- **Full testability** without rendering

---

## 1. High-Level Architecture

### 1.1 Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CaspoonApp (App)                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     AppState (Reactive Store)                      │ │
│  │  • BinaryInfo    • AnalysisResults   • UIState   • UserPrefs      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  ▲                                       │
│                                  │ Reactive Watchers                    │
│                                  │                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      ScreenManager                                 │ │
│  │  [MainScreen] [SettingsScreen] [ComparisonScreen] [HelpScreen]    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

                    MainScreen Composition
┌──────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    StatusBar (Top)                                │  │
│  │  File: /bin/ls | Arch: x86_64 | Analysis: ✓ | Worker: Idle       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌────────────┬──────────────────────────────────┬──────────────────┐  │
│  │            │                                  │                  │  │
│  │  Sidebar   │      ContentPanel (Tabs)         │   DetailsPanel   │  │
│  │            │  ┌──────────────────────────┐    │                  │  │
│  │  • Tree    │  │ [Overview] [Functions]   │    │  Properties:     │  │
│  │  • Funcs   │  │ [Strings] [Imports]      │    │  • Address       │  │
│  │  • Sects   │  │ [Disasm]  [Hex]          │    │  • Size          │  │
│  │  • Search  │  │                          │    │  • Refs          │  │
│  │            │  │  ActiveView Widget       │    │                  │  │
│  │            │  │  (Reactive Content)      │    │                  │  │
│  │  Filter:   │  │                          │    │  Context:        │  │
│  │  [_____]   │  │                          │    │  • Jump to       │  │
│  │            │  │                          │    │  • Copy          │  │
│  │            │  └──────────────────────────┘    │  • Export        │  │
│  │            │                                  │                  │  │
│  └────────────┴──────────────────────────────────┴──────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                  BottomPanel (Toggleable)                         │  │
│  │  [Console] [Worker Logs] [Search Results]                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    CommandBar (Ctrl+P)                            │  │
│  │  > analyze binary_____________  [fuzzy search results]            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Hierarchy

```
CaspoonApp (App)
├── AppState (Reactive[dict])
│   ├── binary_info: BinaryInfo
│   ├── analysis_results: AnalysisResults
│   ├── ui_state: UIState
│   └── user_prefs: UserPreferences
│
├── ScreenManager (manages screen stack)
│   ├── MainScreen
│   │   ├── StatusBar
│   │   ├── MainLayout (Horizontal)
│   │   │   ├── Sidebar (Vertical, collapsible)
│   │   │   │   ├── NavigationTree
│   │   │   │   ├── FilterInput
│   │   │   │   └── QuickActions
│   │   │   ├── ContentPanel (Vertical)
│   │   │   │   ├── ContentTabs
│   │   │   │   │   ├── OverviewView
│   │   │   │   │   ├── FunctionsView
│   │   │   │   │   ├── StringsView
│   │   │   │   │   ├── ImportsExportsView
│   │   │   │   │   ├── DisassemblyView
│   │   │   │   │   └── HexView
│   │   │   │   └── ViewContainer
│   │   │   └── DetailsPanel (Vertical, collapsible)
│   │   │       ├── PropertiesView
│   │   │       └── ContextActions
│   │   ├── BottomPanel (collapsible)
│   │   │   ├── ConsoleTab
│   │   │   ├── WorkerLogsTab
│   │   │   └── SearchResultsTab
│   │   └── CommandPalette (modal overlay)
│   │
│   ├── SettingsScreen
│   │   ├── ThemeSettings
│   │   ├── KeybindingSettings
│   │   └── AnalysisSettings
│   │
│   ├── ComparisonScreen
│   │   ├── SplitView (Side by side)
│   │   └── DiffView
│   │
│   └── HelpScreen
│       ├── KeybindingsHelp
│       └── QuickStartGuide
│
├── WorkerPool
│   ├── AnalysisWorker
│   ├── SearchWorker
│   └── ExportWorker
│
├── ActionRegistry (commands and keybindings)
└── PluginManager (extensibility)
```

### 1.3 Data Flow

```
┌─────────────┐
│ User Input  │ (Keyboard/Mouse)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Widget    │ (captures event)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Action     │ (dispatch to ActionRegistry)
└──────┬──────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────┐          ┌──────────────┐
│  UI Action  │          │ Async Worker │ (long operations)
│  (instant)  │          └──────┬───────┘
└──────┬──────┘                 │
       │                        │ (emit progress messages)
       │                        │
       ▼                        ▼
┌─────────────────────────────────────┐
│      AppState (Reactive Store)      │
│  (single source of truth)           │
└──────────────┬──────────────────────┘
               │
               │ (reactive watchers trigger)
               │
       ┌───────┴────────────────┐
       │                        │
       ▼                        ▼
┌─────────────┐          ┌─────────────┐
│   View A    │          │   View B    │
│  (watches   │          │  (watches   │
│   state)    │          │   state)    │
└─────────────┘          └─────────────┘
       │                        │
       ▼                        ▼
┌─────────────────────────────────────┐
│         UI Update (render)          │
└─────────────────────────────────────┘
```

### 1.4 Message/Event Flow

```
Event Types:
-----------

1. User Events (input)
   ├── KeyboardEvent → ActionRegistry
   ├── MouseEvent → Widget
   └── CommandPaletteEvent → ActionRegistry

2. System Events
   ├── WorkerStarted
   ├── WorkerProgress(percent, message)
   ├── WorkerComplete(result)
   └── WorkerError(error)

3. State Events (reactive)
   ├── StateChanged[BinaryInfo]
   ├── StateChanged[AnalysisResults]
   └── StateChanged[UIState]

4. Navigation Events
   ├── ScreenPush(screen)
   ├── ScreenPop()
   ├── TabChanged(tab_id)
   └── PanelToggled(panel_id)

5. Plugin Events
   ├── PluginLoaded(plugin)
   └── PluginCommand(command, args)

Message Flow Example (Load Binary):
──────────────────────────────────

User → "analyze /bin/ls" → CommandPalette
  │
  └→ ActionRegistry.execute("analyze_binary", path="/bin/ls")
       │
       └→ post_message(StartAnalysis(path="/bin/ls"))
            │
            └→ CaspoonApp.on_start_analysis()
                 │
                 ├→ AppState.ui_state.analyzing = True
                 │    │
                 │    └→ StatusBar watches analyzing → updates UI "Analyzing..."
                 │
                 └→ run_worker(AnalysisWorker, path="/bin/ls")
                      │
                      ├→ WorkerProgress(25%, "Parsing ELF...")
                      │    └→ StatusBar updates progress
                      │
                      ├→ WorkerProgress(50%, "Running r2...")
                      │
                      ├→ WorkerProgress(75%, "Extracting strings...")
                      │
                      └→ WorkerComplete(report)
                           │
                           └→ CaspoonApp.on_analysis_complete(report)
                                │
                                ├→ AppState.binary_info = report.info
                                │    └→ OverviewView watches binary_info → updates
                                │
                                ├→ AppState.analysis_results = report.results
                                │    └→ All views watch → update reactively
                                │
                                └→ AppState.ui_state.analyzing = False
                                     └→ StatusBar → "Analysis complete ✓"
```

---

## 2. Widget Component Design

### 2.1 Base Widget Classes

```python
# caspoon/ui/core/base.py

from abc import ABC, abstractmethod
from textual.reactive import reactive
from textual.widgets import Static
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class BaseView(Static, ABC, Generic[T]):
    """Base class for all Caspoon views.
    
    Features:
    - Automatic state subscription via reactive properties
    - Lifecycle hooks (on_mount, on_show, on_hide)
    - Standard interface for data updates
    - Built-in error handling
    """
    
    # Reactive property that auto-updates when state changes
    data: reactive[Optional[T]] = reactive(None)
    is_loading: reactive[bool] = reactive(False)
    error: reactive[Optional[str]] = reactive(None)
    
    def watch_data(self, old_data: Optional[T], new_data: Optional[T]) -> None:
        """Called automatically when data changes."""
        if new_data is not None:
            self.render_content(new_data)
    
    def watch_is_loading(self, loading: bool) -> None:
        """Show/hide loading indicator."""
        if loading:
            self.show_loading()
        else:
            self.hide_loading()
    
    def watch_error(self, error: Optional[str]) -> None:
        """Display error state."""
        if error:
            self.show_error(error)
    
    @abstractmethod
    def render_content(self, data: T) -> None:
        """Render the view content. Implemented by subclasses."""
        pass
    
    def show_loading(self) -> None:
        """Show loading indicator."""
        self.update("[dim]Loading...[/]")
    
    def hide_loading(self) -> None:
        """Hide loading indicator."""
        pass
    
    def show_error(self, error: str) -> None:
        """Show error message."""
        self.update(f"[red]Error:[/] {error}")
    
    # Lifecycle hooks
    def on_show(self) -> None:
        """Called when view becomes visible."""
        pass
    
    def on_hide(self) -> None:
        """Called when view becomes hidden."""
        pass


class InteractiveView(BaseView[T], ABC):
    """Base class for views with keyboard/mouse interaction.
    
    Features:
    - Selection state management
    - Keyboard navigation (up/down/enter)
    - Search/filter support
    - Context menu integration
    """
    
    selected_index: reactive[int] = reactive(0)
    filter_text: reactive[str] = reactive("")
    
    def action_move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
    
    def action_move_down(self) -> None:
        """Move selection down."""
        max_index = self.get_item_count() - 1
        if self.selected_index < max_index:
            self.selected_index += 1
    
    def action_select_item(self) -> None:
        """Activate selected item."""
        self.on_item_selected(self.selected_index)
    
    @abstractmethod
    def get_item_count(self) -> int:
        """Return number of items in view."""
        pass
    
    @abstractmethod
    def on_item_selected(self, index: int) -> None:
        """Handle item selection."""
        pass
    
    def watch_filter_text(self, text: str) -> None:
        """Re-filter items when filter text changes."""
        self.apply_filter(text)
    
    @abstractmethod
    def apply_filter(self, text: str) -> None:
        """Filter displayed items."""
        pass


class TreeView(InteractiveView[T]):
    """Base class for hierarchical tree views.
    
    Features:
    - Expand/collapse nodes
    - Hierarchical navigation
    - Lazy loading of children
    """
    
    expanded_nodes: reactive[set[str]] = reactive(set, init=set)
    
    def action_toggle_expand(self) -> None:
        """Expand/collapse current node."""
        node_id = self.get_selected_node_id()
        if node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)
        else:
            self.expanded_nodes.add(node_id)
    
    @abstractmethod
    def get_selected_node_id(self) -> str:
        """Get ID of currently selected node."""
        pass


class TableView(InteractiveView[T]):
    """Base class for table-based views.
    
    Features:
    - Column sorting
    - Row selection
    - Column resizing
    - Cell formatting
    """
    
    sort_column: reactive[Optional[str]] = reactive(None)
    sort_descending: reactive[bool] = reactive(False)
    
    def action_sort_by_column(self, column: str) -> None:
        """Sort table by column."""
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
    
    @abstractmethod
    def get_columns(self) -> list[str]:
        """Return list of column names."""
        pass
```

### 2.2 Standard Widget Types

```python
# caspoon/ui/widgets/standard.py

from rich.table import Table
from textual.widgets import DataTable
from typing import Callable, Any


class FilterableTable(TableView[list[dict]]):
    """A table with built-in filtering and sorting.
    
    Usage:
        table = FilterableTable(columns=["Name", "Address", "Size"])
        table.data = [
            {"Name": "main", "Address": "0x1234", "Size": "100"},
            {"Name": "init", "Address": "0x5678", "Size": "50"},
        ]
    """
    
    def __init__(self, columns: list[str], **kwargs):
        super().__init__(**kwargs)
        self._columns = columns
        self._rows: list[dict] = []
        self._filtered_rows: list[dict] = []
    
    def render_content(self, data: list[dict]) -> None:
        """Render table data."""
        self._rows = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter rows by text."""
        if not text:
            self._filtered_rows = self._rows
        else:
            text_lower = text.lower()
            self._filtered_rows = [
                row for row in self._rows
                if any(text_lower in str(v).lower() for v in row.values())
            ]
        self._render_table()
    
    def _render_table(self) -> None:
        """Render the filtered and sorted table."""
        table = Table()
        for col in self._columns:
            table.add_column(col)
        
        rows = self._get_sorted_rows()
        for i, row in enumerate(rows):
            style = "bold" if i == self.selected_index else ""
            table.add_row(*[str(row.get(col, "")) for col in self._columns], style=style)
        
        self.update(table)
    
    def _get_sorted_rows(self) -> list[dict]:
        """Get rows sorted by current sort column."""
        if not self.sort_column:
            return self._filtered_rows
        
        return sorted(
            self._filtered_rows,
            key=lambda r: r.get(self.sort_column, ""),
            reverse=self.sort_descending
        )
    
    def get_item_count(self) -> int:
        return len(self._filtered_rows)
    
    def get_columns(self) -> list[str]:
        return self._columns
    
    def on_item_selected(self, index: int) -> None:
        """Handle row selection."""
        if 0 <= index < len(self._filtered_rows):
            row = self._filtered_rows[index]
            self.post_message(self.RowSelected(row))
    
    class RowSelected(Static.Selected):
        """Message emitted when a row is selected."""
        def __init__(self, row: dict) -> None:
            super().__init__()
            self.row = row


class SearchableList(InteractiveView[list[str]]):
    """A filterable, searchable list with keyboard navigation.
    
    Usage:
        lst = SearchableList()
        lst.data = ["item1", "item2", "item3"]
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items: list[str] = []
        self._filtered_items: list[str] = []
    
    def render_content(self, data: list[str]) -> None:
        """Render list items."""
        self._items = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter items by text."""
        if not text:
            self._filtered_items = self._items
        else:
            text_lower = text.lower()
            self._filtered_items = [
                item for item in self._items
                if text_lower in item.lower()
            ]
        self._render_list()
    
    def _render_list(self) -> None:
        """Render the filtered list."""
        lines = []
        for i, item in enumerate(self._filtered_items):
            prefix = "▶ " if i == self.selected_index else "  "
            style = "bold" if i == self.selected_index else ""
            lines.append(f"[{style}]{prefix}{item}[/]")
        
        self.update("\n".join(lines) or "[dim]No items[/]")
    
    def get_item_count(self) -> int:
        return len(self._filtered_items)
    
    def on_item_selected(self, index: int) -> None:
        """Handle item selection."""
        if 0 <= index < len(self._filtered_items):
            item = self._filtered_items[index]
            self.post_message(self.ItemSelected(item))
    
    class ItemSelected(Static.Selected):
        """Message emitted when an item is selected."""
        def __init__(self, item: str) -> None:
            super().__init__()
            self.item = item


class ProgressView(BaseView[dict]):
    """Display progress for long-running operations.
    
    Usage:
        progress = ProgressView()
        progress.data = {"percent": 50, "message": "Processing..."}
    """
    
    def render_content(self, data: dict) -> None:
        """Render progress bar."""
        percent = data.get("percent", 0)
        message = data.get("message", "Working...")
        
        bar_width = 40
        filled = int(bar_width * percent / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        self.update(f"{message}\n[{bar}] {percent}%")
```

### 2.3 Custom Widgets for Caspoon

```python
# caspoon/ui/widgets/custom.py

from textual.containers import Container
from textual.widgets import Tree
from rich.syntax import Syntax
from caspoon.core.models import Function, Section


class FunctionExplorer(TreeView[list[Function]]):
    """Hierarchical view of functions organized by section/module.
    
    Features:
    - Group by section, module, or alphabetically
    - Show function size, complexity
    - Jump to disassembly on selection
    """
    
    def render_content(self, data: list[Function]) -> None:
        """Render function tree."""
        # Group functions by section
        by_section: dict[str, list[Function]] = {}
        for func in data:
            section = func.section or "Unknown"
            by_section.setdefault(section, []).append(func)
        
        # Build tree
        lines = []
        for section, funcs in sorted(by_section.items()):
            node_id = f"section:{section}"
            expanded = node_id in self.expanded_nodes
            
            icon = "▼" if expanded else "▶"
            lines.append(f"{icon} [bold]{section}[/] ({len(funcs)} functions)")
            
            if expanded:
                for func in sorted(funcs, key=lambda f: f.name):
                    lines.append(f"  • {func.name} @ {func.address:08x} ({func.size} bytes)")
        
        self.update("\n".join(lines))
    
    def get_selected_node_id(self) -> str:
        """Get ID of selected node."""
        # Implementation would track current selection
        return ""
    
    def get_item_count(self) -> int:
        # Count all visible items
        return 0


class HexViewer(BaseView[bytes]):
    """Hexadecimal viewer with ASCII sidebar.
    
    Features:
    - Scrollable hex dump
    - Address column
    - ASCII representation
    - Byte highlighting
    - Jump to address
    """
    
    current_address: reactive[int] = reactive(0)
    bytes_per_row: int = 16
    
    def render_content(self, data: bytes) -> None:
        """Render hex dump."""
        lines = []
        offset = self.current_address
        
        for i in range(0, len(data), self.bytes_per_row):
            chunk = data[i:i + self.bytes_per_row]
            
            # Address column
            addr = f"{offset + i:08x}"
            
            # Hex bytes
            hex_parts = []
            for b in chunk:
                hex_parts.append(f"{b:02x}")
            hex_str = " ".join(hex_parts).ljust(self.bytes_per_row * 3)
            
            # ASCII representation
            ascii_parts = []
            for b in chunk:
                ascii_parts.append(chr(b) if 32 <= b < 127 else ".")
            ascii_str = "".join(ascii_parts)
            
            lines.append(f"[dim]{addr}[/]  {hex_str}  [dim]|{ascii_str}|[/]")
        
        self.update("\n".join(lines))
    
    def action_jump_to_address(self, address: int) -> None:
        """Jump to specific address."""
        self.current_address = address


class DisassemblyView(BaseView[list[dict]]):
    """Syntax-highlighted disassembly view.
    
    Features:
    - Assembly syntax highlighting (reuse existing system)
    - Address labels
    - Jump target highlighting
    - Cross-references
    - Inline comments
    """
    
    current_function: reactive[Optional[str]] = reactive(None)
    show_addresses: reactive[bool] = reactive(True)
    show_bytes: reactive[bool] = reactive(False)
    
    def render_content(self, data: list[dict]) -> None:
        """Render disassembly with syntax highlighting."""
        from caspoon.ui.syntax.highlighter import AssemblyHighlighter
        
        lines = []
        for instr in data:
            parts = []
            
            if self.show_addresses:
                parts.append(f"[dim]{instr['address']:08x}[/]")
            
            if self.show_bytes:
                parts.append(f"[dim]{instr.get('bytes', ''):16}[/]")
            
            # Use existing syntax highlighter
            highlighted = self._highlight_instruction(instr)
            parts.append(highlighted)
            
            lines.append("  ".join(parts))
        
        self.update("\n".join(lines))
    
    def _highlight_instruction(self, instr: dict) -> str:
        """Apply syntax highlighting to instruction."""
        # Delegate to existing AssemblyHighlighter system
        from caspoon.ui.syntax.highlighter import AssemblyHighlighter
        highlighter = AssemblyHighlighter(arch=instr.get("arch", "x86"))
        return highlighter.highlight_line(instr.get("disasm", ""))


class SectionExplorer(TreeView[list[Section]]):
    """Explore binary sections hierarchically.
    
    Features:
    - Show section properties (address, size, permissions)
    - Color-coded by type (code/data/bss)
    - Jump to hex view on selection
    """
    
    def render_content(self, data: list[Section]) -> None:
        """Render section tree."""
        lines = []
        for section in data:
            icon = self._get_section_icon(section)
            perms = self._format_permissions(section)
            lines.append(
                f"{icon} [bold]{section.name}[/] "
                f"@ {section.address:08x} "
                f"({section.size} bytes) "
                f"[dim]{perms}[/]"
            )
        
        self.update("\n".join(lines))
    
    def _get_section_icon(self, section: Section) -> str:
        """Get icon based on section type."""
        if section.executable:
            return "⚡"
        elif section.writable:
            return "✎"
        else:
            return "📄"
    
    def _format_permissions(self, section: Section) -> str:
        """Format permission string (rwx)."""
        r = "r" if section.readable else "-"
        w = "w" if section.writable else "-"
        x = "x" if section.executable else "-"
        return f"{r}{w}{x}"
```

---

## 3. State Management Design

### 3.1 State Structure

```python
# caspoon/ui/core/state.py

from dataclasses import dataclass, field
from typing import Optional, Any
from textual.reactive import Reactive


@dataclass
class BinaryInfo:
    """Information about the loaded binary."""
    path: str = ""
    architecture: str = ""
    bits: int = 0
    endianness: str = ""
    file_type: str = ""
    stripped: bool = False
    file_size: int = 0


@dataclass
class AnalysisResults:
    """Results from binary analysis."""
    functions: list[dict] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)
    strings: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    protections: dict[str, bool] = field(default_factory=dict)
    disassembly: list[dict] = field(default_factory=list)
    raw_report: Optional[Any] = None


@dataclass
class UIState:
    """UI state (not persisted)."""
    current_screen: str = "main"
    current_tab: str = "overview"
    sidebar_collapsed: bool = False
    details_panel_collapsed: bool = False
    bottom_panel_collapsed: bool = True
    bottom_panel_tab: str = "console"
    
    # Analysis state
    is_analyzing: bool = False
    analysis_progress: float = 0.0
    analysis_message: str = ""
    
    # Selection state
    selected_function: Optional[str] = None
    selected_address: Optional[int] = None
    
    # Search state
    search_query: str = ""
    search_results: list[dict] = field(default_factory=list)


@dataclass
class UserPreferences:
    """User preferences (persisted)."""
    theme: str = "monokai"
    font_size: int = 12
    
    # Keybindings
    keybindings: dict[str, str] = field(default_factory=dict)
    
    # View preferences
    show_addresses: bool = True
    show_bytes: bool = False
    bytes_per_row: int = 16
    max_strings: int = 1000
    max_functions: int = 1000
    
    # Analysis preferences
    auto_analyze: bool = False
    deep_analysis: bool = False


class AppState:
    """Central application state (reactive).
    
    Single source of truth for all application data.
    Views watch relevant parts of state and update reactively.
    """
    
    def __init__(self):
        self.binary_info = Reactive(BinaryInfo())
        self.analysis_results = Reactive(AnalysisResults())
        self.ui_state = Reactive(UIState())
        self.user_prefs = Reactive(UserPreferences())
    
    def reset(self) -> None:
        """Reset to initial state."""
        self.binary_info = BinaryInfo()
        self.analysis_results = AnalysisResults()
        self.ui_state = UIState()
    
    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "binary_info": self.binary_info.__dict__,
            "analysis_results": {
                k: v for k, v in self.analysis_results.__dict__.items()
                if k != "raw_report"  # Don't serialize raw report
            },
            "ui_state": self.ui_state.__dict__,
            "user_prefs": self.user_prefs.__dict__,
        }
    
    def from_dict(self, data: dict) -> None:
        """Deserialize state from dictionary."""
        if "binary_info" in data:
            self.binary_info = BinaryInfo(**data["binary_info"])
        if "analysis_results" in data:
            self.analysis_results = AnalysisResults(**data["analysis_results"])
        if "ui_state" in data:
            self.ui_state = UIState(**data["ui_state"])
        if "user_prefs" in data:
            self.user_prefs = UserPreferences(**data["user_prefs"])
```

### 3.2 State Update Patterns

```python
# caspoon/ui/core/actions.py

from typing import Protocol, Callable, Any
from textual.message import Message


class Action(Message):
    """Base class for all actions that mutate state."""
    pass


class LoadBinary(Action):
    """Action to load and analyze a binary."""
    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path


class AnalysisProgress(Action):
    """Action to update analysis progress."""
    def __init__(self, percent: float, message: str) -> None:
        super().__init__()
        self.percent = percent
        self.message = message


class AnalysisComplete(Action):
    """Action dispatched when analysis completes."""
    def __init__(self, results: AnalysisResults) -> None:
        super().__init__()
        self.results = results


class AnalysisError(Action):
    """Action dispatched when analysis fails."""
    def __init__(self, error: str) -> None:
        super().__init__()
        self.error = error


class SelectFunction(Action):
    """Action to select a function."""
    def __init__(self, function_name: str) -> None:
        super().__init__()
        self.function_name = function_name


class JumpToAddress(Action):
    """Action to jump to an address."""
    def __init__(self, address: int) -> None:
        super().__init__()
        self.address = address


class UpdateFilter(Action):
    """Action to update filter text."""
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class TogglePanel(Action):
    """Action to toggle panel visibility."""
    def __init__(self, panel: str) -> None:
        super().__init__()
        self.panel = panel


# Action Handlers (reducers)
# These are methods on CaspoonApp that handle actions

class CaspoonApp:
    """Main app with action handlers."""
    
    def on_load_binary(self, action: LoadBinary) -> None:
        """Handle binary loading action."""
        # Validate path
        if not os.path.exists(action.path):
            self.post_message(AnalysisError(f"File not found: {action.path}"))
            return
        
        # Update state to show loading
        self.state.ui_state.is_analyzing = True
        self.state.ui_state.analysis_progress = 0.0
        self.state.binary_info.path = action.path
        
        # Start async worker
        self.run_worker(
            self._analyze_binary(action.path),
            name="analysis",
            description="Analyzing binary"
        )
    
    async def _analyze_binary(self, path: str) -> None:
        """Async worker for binary analysis."""
        try:
            # Progress updates
            self.post_message(AnalysisProgress(10, "Parsing file format..."))
            runner = ReconRunner()
            
            self.post_message(AnalysisProgress(30, "Extracting metadata..."))
            # ... analysis steps ...
            
            self.post_message(AnalysisProgress(60, "Running disassembly..."))
            report = runner.run(path)
            
            self.post_message(AnalysisProgress(90, "Finalizing..."))
            
            # Convert report to state
            results = AnalysisResults(
                functions=report.functions,
                sections=report.sections,
                strings=report.strings,
                imports=report.imports,
                exports=report.exports,
                protections=report.protections,
                disassembly=report.disassembly,
                raw_report=report
            )
            
            self.post_message(AnalysisComplete(results))
            
        except Exception as e:
            self.post_message(AnalysisError(str(e)))
    
    def on_analysis_progress(self, action: AnalysisProgress) -> None:
        """Handle analysis progress updates."""
        self.state.ui_state.analysis_progress = action.percent
        self.state.ui_state.analysis_message = action.message
    
    def on_analysis_complete(self, action: AnalysisComplete) -> None:
        """Handle analysis completion."""
        self.state.analysis_results = action.results
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_progress = 100.0
        self.state.ui_state.analysis_message = "Complete"
    
    def on_analysis_error(self, action: AnalysisError) -> None:
        """Handle analysis errors."""
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_message = f"Error: {action.error}"
        # Show error dialog
        self.push_screen(ErrorDialog(action.error))
    
    def on_select_function(self, action: SelectFunction) -> None:
        """Handle function selection."""
        self.state.ui_state.selected_function = action.function_name
        # Automatically switch to disassembly tab
        self.state.ui_state.current_tab = "disassembly"
    
    def on_jump_to_address(self, action: JumpToAddress) -> None:
        """Handle address jump."""
        self.state.ui_state.selected_address = action.address
        self.state.ui_state.current_tab = "hex"
    
    def on_toggle_panel(self, action: TogglePanel) -> None:
        """Handle panel toggle."""
        ui = self.state.ui_state
        if action.panel == "sidebar":
            ui.sidebar_collapsed = not ui.sidebar_collapsed
        elif action.panel == "details":
            ui.details_panel_collapsed = not ui.details_panel_collapsed
        elif action.panel == "bottom":
            ui.bottom_panel_collapsed = not ui.bottom_panel_collapsed
```

### 3.3 View State Subscription

```python
# caspoon/ui/views/overview.py

from caspoon.ui.core.base import BaseView
from caspoon.ui.core.state import BinaryInfo, AppState
from textual.app import App


class OverviewView(BaseView[BinaryInfo]):
    """Overview view that watches binary_info state."""
    
    def on_mount(self) -> None:
        """Subscribe to state when mounted."""
        app: CaspoonApp = self.app
        
        # Watch binary_info changes
        app.state.binary_info.watch(self, "_on_binary_info_changed")
    
    def _on_binary_info_changed(self, old_value: BinaryInfo, new_value: BinaryInfo) -> None:
        """Called automatically when binary_info changes."""
        self.data = new_value
    
    def render_content(self, data: BinaryInfo) -> None:
        """Render overview table."""
        from rich.table import Table
        
        table = Table(title="Executable Overview")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        
        table.add_row("Path", data.path)
        table.add_row("Architecture", data.architecture)
        table.add_row("Bits", str(data.bits))
        table.add_row("Endianness", data.endianness)
        table.add_row("File Type", data.file_type)
        table.add_row("Stripped", "Yes" if data.stripped else "No")
        table.add_row("Size", f"{data.file_size:,} bytes")
        
        self.update(table)


# Alternative: Use reactive directly in App
class CaspoonApp(App):
    """App with reactive state."""
    
    def __init__(self):
        super().__init__()
        self.state = AppState()
    
    def watch_state_binary_info(self, old: BinaryInfo, new: BinaryInfo) -> None:
        """Automatically called when state.binary_info changes."""
        # Could dispatch to views here, or let views watch directly
        pass
```

---

## 4. Screen Architecture

### 4.1 Screen Types

```python
# caspoon/ui/screens/main.py

from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer


class MainScreen(Screen):
    """Primary analysis screen with multi-panel layout."""
    
    BINDINGS = [
        ("ctrl+p", "command_palette", "Command Palette"),
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+j", "toggle_bottom", "Toggle Bottom Panel"),
        ("ctrl+k", "toggle_details", "Toggle Details"),
        ("f1", "show_help", "Help"),
        ("ctrl+s", "show_settings", "Settings"),
        ("ctrl+q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose main screen layout."""
        yield StatusBar(id="status_bar")
        
        with Horizontal(id="main_layout"):
            # Sidebar (collapsible)
            yield Sidebar(id="sidebar")
            
            # Main content area
            with Vertical(id="content_panel"):
                yield ContentTabs(id="content_tabs")
            
            # Details panel (collapsible)
            yield DetailsPanel(id="details_panel")
        
        # Bottom panel (collapsible)
        yield BottomPanel(id="bottom_panel")
        
        # Command palette (modal overlay, hidden by default)
        yield CommandPalette(id="command_palette")
    
    def on_mount(self) -> None:
        """Initialize screen state."""
        # Subscribe to UI state for panel visibility
        app: CaspoonApp = self.app
        app.state.ui_state.watch(self, "_on_ui_state_changed")
    
    def _on_ui_state_changed(self, old_state, new_state) -> None:
        """Update panel visibility based on state."""
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.display = not new_state.sidebar_collapsed
        
        details = self.query_one("#details_panel", DetailsPanel)
        details.display = not new_state.details_panel_collapsed
        
        bottom = self.query_one("#bottom_panel", BottomPanel)
        bottom.display = not new_state.bottom_panel_collapsed
    
    def action_command_palette(self) -> None:
        """Show command palette."""
        palette = self.query_one("#command_palette", CommandPalette)
        palette.show()
    
    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self.app.post_message(TogglePanel("sidebar"))
    
    def action_toggle_bottom(self) -> None:
        """Toggle bottom panel."""
        self.app.post_message(TogglePanel("bottom"))
    
    def action_toggle_details(self) -> None:
        """Toggle details panel."""
        self.app.post_message(TogglePanel("details"))
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen(HelpScreen())
    
    def action_show_settings(self) -> None:
        """Show settings screen."""
        self.app.push_screen(SettingsScreen())


class SettingsScreen(Screen):
    """Settings and preferences screen."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+s", "save_settings", "Save"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose settings UI."""
        yield Header(title="Settings")
        
        with Vertical():
            yield ThemeSettings()
            yield KeybindingSettings()
            yield AnalysisSettings()
        
        yield Footer()
    
    def action_save_settings(self) -> None:
        """Save settings to disk."""
        # Serialize user_prefs and save
        self.app.state.user_prefs.save()
        self.app.pop_screen()


class ComparisonScreen(Screen):
    """Side-by-side binary comparison screen."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+o", "open_second_binary", "Open Second Binary"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose comparison UI."""
        yield Header(title="Binary Comparison")
        
        with Horizontal():
            with Vertical(id="left_panel"):
                yield Label("Binary 1")
                yield OverviewView(id="overview_left")
            
            with Vertical(id="right_panel"):
                yield Label("Binary 2")
                yield OverviewView(id="overview_right")
        
        yield DiffView(id="diff_view")
        yield Footer()


class HelpScreen(Screen):
    """Help and keybindings screen."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose help UI."""
        yield Header(title="Help")
        
        with TabbedContent():
            with TabPane("Keybindings"):
                yield KeybindingsHelp()
            with TabPane("Quick Start"):
                yield QuickStartGuide()
            with TabPane("About"):
                yield AboutView()
        
        yield Footer()
```

### 4.2 Screen Navigation

```python
# Navigation patterns

class CaspoonApp(App):
    """App with screen management."""
    
    SCREENS = {
        "main": MainScreen,
        "settings": SettingsScreen,
        "comparison": ComparisonScreen,
        "help": HelpScreen,
    }
    
    def on_mount(self) -> None:
        """Start with main screen."""
        self.push_screen("main")
    
    # Screen stack operations
    def show_settings(self) -> None:
        """Push settings screen onto stack."""
        self.push_screen("settings")
    
    def show_comparison(self, binary1: str, binary2: str) -> None:
        """Show comparison screen with two binaries."""
        screen = ComparisonScreen()
        screen.load_binaries(binary1, binary2)
        self.push_screen(screen)
    
    def go_back(self) -> None:
        """Pop current screen."""
        self.pop_screen()
```

### 4.3 Modal Dialogs

```python
# caspoon/ui/dialogs/common.py

from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Input


class ConfirmDialog(ModalScreen[bool]):
    """Modal confirmation dialog."""
    
    def __init__(self, message: str, title: str = "Confirm"):
        super().__init__()
        self.message = message
        self.title = title
    
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title, id="dialog_title")
            yield Label(self.message, id="dialog_message")
            
            with Horizontal(id="dialog_buttons"):
                yield Button("OK", variant="primary", id="ok")
                yield Button("Cancel", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "ok":
            self.dismiss(True)
        else:
            self.dismiss(False)


class InputDialog(ModalScreen[Optional[str]]):
    """Modal input dialog."""
    
    def __init__(self, message: str, title: str = "Input", default: str = ""):
        super().__init__()
        self.message = message
        self.title = title
        self.default = default
    
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title, id="dialog_title")
            yield Label(self.message, id="dialog_message")
            yield Input(value=self.default, id="input")
            
            with Horizontal(id="dialog_buttons"):
                yield Button("OK", variant="primary", id="ok")
                yield Button("Cancel", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "ok":
            input_widget = self.query_one("#input", Input)
            self.dismiss(input_widget.value)
        else:
            self.dismiss(None)


class ErrorDialog(ModalScreen[None]):
    """Modal error dialog."""
    
    def __init__(self, error: str, title: str = "Error"):
        super().__init__()
        self.error = error
        self.title = title
    
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title, id="dialog_title")
            yield Label(f"[red]{self.error}[/]", id="dialog_message")
            yield Button("OK", variant="primary", id="ok")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click."""
        self.dismiss()


# Usage
async def delete_function():
    """Example of using confirmation dialog."""
    result = await app.push_screen_wait(
        ConfirmDialog("Are you sure you want to delete this function?")
    )
    
    if result:
        # User confirmed
        perform_delete()


async def rename_function():
    """Example of using input dialog."""
    new_name = await app.push_screen_wait(
        InputDialog("Enter new function name:", default=current_name)
    )
    
    if new_name:
        # User provided a name
        perform_rename(new_name)
```

---

## 5. Command System Design

### 5.1 Command Palette Implementation

```python
# caspoon/ui/widgets/command_palette.py

from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical
from typing import Callable, Optional
import re


class Command:
    """Represents an executable command."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        handler: Callable,
        keybinding: Optional[str] = None,
        category: str = "General"
    ):
        self.id = id
        self.name = name
        self.description = description
        self.handler = handler
        self.keybinding = keybinding
        self.category = category
    
    def matches(self, query: str) -> int:
        """Return match score for query (0 = no match)."""
        query_lower = query.lower()
        name_lower = self.name.lower()
        desc_lower = self.description.lower()
        
        # Exact match
        if query_lower == name_lower:
            return 100
        
        # Starts with
        if name_lower.startswith(query_lower):
            return 90
        
        # Word boundary match
        if re.search(r'\b' + re.escape(query_lower), name_lower):
            return 80
        
        # Contains in name
        if query_lower in name_lower:
            return 70
        
        # Contains in description
        if query_lower in desc_lower:
            return 60
        
        # Fuzzy match (initials)
        if self._fuzzy_match(query_lower, name_lower):
            return 50
        
        return 0
    
    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Check if query matches initials of words in text."""
        words = text.split()
        initials = "".join(w[0] for w in words if w)
        return query in initials


class CommandPalette(Vertical):
    """Fuzzy-searchable command palette (Ctrl+P style)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._commands: list[Command] = []
        self._filtered_commands: list[Command] = []
        self.display = False
    
    def compose(self) -> ComposeResult:
        """Compose command palette UI."""
        yield Input(placeholder="Type command...", id="command_input")
        yield ListView(id="command_list")
    
    def on_mount(self) -> None:
        """Focus input when shown."""
        self.query_one("#command_input", Input).focus()
    
    def show(self) -> None:
        """Show command palette."""
        self.display = True
        self._filtered_commands = self._commands.copy()
        self._update_list()
        self.query_one("#command_input", Input).focus()
    
    def hide(self) -> None:
        """Hide command palette."""
        self.display = False
        self.query_one("#command_input", Input).value = ""
    
    def register_command(self, command: Command) -> None:
        """Register a command."""
        self._commands.append(command)
    
    def unregister_command(self, command_id: str) -> None:
        """Unregister a command."""
        self._commands = [c for c in self._commands if c.id != command_id]
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types."""
        query = event.value.strip()
        
        if not query:
            self._filtered_commands = self._commands.copy()
        else:
            # Score and sort commands
            scored = [
                (cmd, cmd.matches(query))
                for cmd in self._commands
            ]
            scored = [(cmd, score) for cmd, score in scored if score > 0]
            scored.sort(key=lambda x: x[1], reverse=True)
            self._filtered_commands = [cmd for cmd, _ in scored]
        
        self._update_list()
    
    def _update_list(self) -> None:
        """Update command list display."""
        list_view = self.query_one("#command_list", ListView)
        list_view.clear()
        
        for cmd in self._filtered_commands[:20]:  # Limit to 20 results
            keybinding = f" [{cmd.keybinding}]" if cmd.keybinding else ""
            list_view.append(
                ListItem(
                    Label(f"{cmd.name}{keybinding} - {cmd.description}")
                )
            )
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Execute selected command."""
        index = event.list_view.index
        if 0 <= index < len(self._filtered_commands):
            cmd = self._filtered_commands[index]
            self.hide()
            cmd.handler()
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.hide()
            event.prevent_default()
        elif event.key == "enter":
            # Execute first command
            if self._filtered_commands:
                self.hide()
                self._filtered_commands[0].handler()
                event.prevent_default()
```

### 5.2 Action Registry Pattern

```python
# caspoon/ui/core/actions_registry.py

from typing import Callable, Optional
from .command_palette import Command, CommandPalette


class ActionRegistry:
    """Central registry for all application actions.
    
    Features:
    - Register actions with keybindings
    - Automatic command palette integration
    - Keybinding conflict detection
    - Context-aware action availability
    """
    
    def __init__(self, app):
        self.app = app
        self._actions: dict[str, Command] = {}
        self._keybindings: dict[str, str] = {}  # key -> action_id
    
    def register(
        self,
        action_id: str,
        name: str,
        handler: Callable,
        description: str = "",
        keybinding: Optional[str] = None,
        category: str = "General",
        context: Optional[str] = None
    ) -> None:
        """Register an action.
        
        Args:
            action_id: Unique identifier for action
            name: Display name
            handler: Function to execute
            description: Help text
            keybinding: Keyboard shortcut (e.g., "ctrl+p")
            category: Category for grouping
            context: Context where action is available (None = always)
        """
        if action_id in self._actions:
            raise ValueError(f"Action {action_id} already registered")
        
        if keybinding and keybinding in self._keybindings:
            existing = self._keybindings[keybinding]
            raise ValueError(
                f"Keybinding {keybinding} already assigned to {existing}"
            )
        
        cmd = Command(
            id=action_id,
            name=name,
            description=description,
            handler=handler,
            keybinding=keybinding,
            category=category
        )
        
        self._actions[action_id] = cmd
        
        if keybinding:
            self._keybindings[keybinding] = action_id
    
    def unregister(self, action_id: str) -> None:
        """Unregister an action."""
        if action_id not in self._actions:
            return
        
        cmd = self._actions[action_id]
        if cmd.keybinding:
            del self._keybindings[cmd.keybinding]
        
        del self._actions[action_id]
    
    def execute(self, action_id: str, *args, **kwargs) -> None:
        """Execute an action by ID."""
        if action_id not in self._actions:
            raise ValueError(f"Unknown action: {action_id}")
        
        cmd = self._actions[action_id]
        cmd.handler(*args, **kwargs)
    
    def get_action(self, action_id: str) -> Optional[Command]:
        """Get action by ID."""
        return self._actions.get(action_id)
    
    def get_actions_by_category(self, category: str) -> list[Command]:
        """Get all actions in a category."""
        return [cmd for cmd in self._actions.values() if cmd.category == category]
    
    def get_all_actions(self) -> list[Command]:
        """Get all registered actions."""
        return list(self._actions.values())
    
    def handle_keybinding(self, key: str) -> bool:
        """Handle a keybinding. Returns True if handled."""
        if key in self._keybindings:
            action_id = self._keybindings[key]
            self.execute(action_id)
            return True
        return False
    
    def update_command_palette(self, palette: CommandPalette) -> None:
        """Update command palette with all registered actions."""
        for cmd in self._actions.values():
            palette.register_command(cmd)


# Example: Register default actions
def register_default_actions(app: CaspoonApp) -> None:
    """Register all default application actions."""
    registry = app.action_registry
    
    # File actions
    registry.register(
        "analyze_binary",
        "Analyze Binary",
        lambda: app.show_file_dialog(),
        description="Open and analyze a binary file",
        keybinding="ctrl+o",
        category="File"
    )
    
    registry.register(
        "reload_binary",
        "Reload Current Binary",
        lambda: app.reload_binary(),
        description="Reload and re-analyze current binary",
        keybinding="ctrl+r",
        category="File"
    )
    
    # View actions
    registry.register(
        "goto_overview",
        "Go to Overview",
        lambda: app.switch_tab("overview"),
        description="Switch to Overview tab",
        keybinding="alt+1",
        category="View"
    )
    
    registry.register(
        "goto_functions",
        "Go to Functions",
        lambda: app.switch_tab("functions"),
        description="Switch to Functions tab",
        keybinding="alt+2",
        category="View"
    )
    
    registry.register(
        "goto_strings",
        "Go to Strings",
        lambda: app.switch_tab("strings"),
        description="Switch to Strings tab",
        keybinding="alt+3",
        category="View"
    )
    
    # Panel actions
    registry.register(
        "toggle_sidebar",
        "Toggle Sidebar",
        lambda: app.post_message(TogglePanel("sidebar")),
        description="Show/hide sidebar",
        keybinding="ctrl+b",
        category="View"
    )
    
    registry.register(
        "toggle_details",
        "Toggle Details Panel",
        lambda: app.post_message(TogglePanel("details")),
        description="Show/hide details panel",
        keybinding="ctrl+d",
        category="View"
    )
    
    # Navigation actions
    registry.register(
        "jump_to_address",
        "Jump to Address",
        lambda: app.show_jump_dialog(),
        description="Jump to specific address",
        keybinding="ctrl+g",
        category="Navigation"
    )
    
    registry.register(
        "search_global",
        "Global Search",
        lambda: app.show_search_dialog(),
        description="Search across all views",
        keybinding="ctrl+f",
        category="Search"
    )
    
    # Help actions
    registry.register(
        "show_help",
        "Show Help",
        lambda: app.push_screen(HelpScreen()),
        description="Show help and keybindings",
        keybinding="f1",
        category="Help"
    )
    
    registry.register(
        "show_settings",
        "Show Settings",
        lambda: app.push_screen(SettingsScreen()),
        description="Open settings",
        keybinding="ctrl+comma",
        category="Settings"
    )
```

### 5.3 Keybinding System

```python
# caspoon/ui/core/keybindings.py

from typing import Optional
import json
from pathlib import Path


class KeybindingManager:
    """Manage user-customizable keybindings."""
    
    DEFAULT_KEYBINDINGS = {
        "analyze_binary": "ctrl+o",
        "reload_binary": "ctrl+r",
        "save_report": "ctrl+s",
        "quit": "ctrl+q",
        "command_palette": "ctrl+p",
        "goto_overview": "alt+1",
        "goto_functions": "alt+2",
        "goto_strings": "alt+3",
        "goto_imports": "alt+4",
        "goto_disassembly": "alt+5",
        "goto_hex": "alt+6",
        "toggle_sidebar": "ctrl+b",
        "toggle_details": "ctrl+d",
        "toggle_bottom": "ctrl+j",
        "jump_to_address": "ctrl+g",
        "search_global": "ctrl+f",
        "search_in_view": "ctrl+shift+f",
        "show_help": "f1",
        "show_settings": "ctrl+comma",
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".caspoon" / "keybindings.json"
        self.keybindings = self.DEFAULT_KEYBINDINGS.copy()
        self.load()
    
    def load(self) -> None:
        """Load keybindings from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    custom = json.load(f)
                self.keybindings.update(custom)
            except Exception:
                pass  # Use defaults on error
    
    def save(self) -> None:
        """Save keybindings to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.keybindings, f, indent=2)
    
    def set_keybinding(self, action_id: str, key: str) -> None:
        """Set keybinding for an action."""
        # Check for conflicts
        for action, existing_key in self.keybindings.items():
            if existing_key == key and action != action_id:
                raise ValueError(f"Key {key} already bound to {action}")
        
        self.keybindings[action_id] = key
    
    def get_keybinding(self, action_id: str) -> Optional[str]:
        """Get keybinding for an action."""
        return self.keybindings.get(action_id)
    
    def reset_to_defaults(self) -> None:
        """Reset all keybindings to defaults."""
        self.keybindings = self.DEFAULT_KEYBINDINGS.copy()
    
    def get_conflicts(self) -> dict[str, list[str]]:
        """Find conflicting keybindings."""
        conflicts = {}
        for action, key in self.keybindings.items():
            if key not in conflicts:
                conflicts[key] = []
            conflicts[key].append(action)
        
        return {k: v for k, v in conflicts.items() if len(v) > 1}
```

---

## 6. Testing Strategy

### 6.1 Unit Testing Widgets

```python
# tests/ui/test_widgets.py

import pytest
from textual.app import App
from caspoon.ui.widgets.standard import FilterableTable, SearchableList
from caspoon.ui.core.base import BaseView


class TestFilterableTable:
    """Test FilterableTable widget."""
    
    def test_init(self):
        """Test widget initialization."""
        table = FilterableTable(columns=["Name", "Value"])
        assert table._columns == ["Name", "Value"]
        assert table._rows == []
    
    def test_render_content(self):
        """Test rendering table data."""
        table = FilterableTable(columns=["Name", "Value"])
        data = [
            {"Name": "foo", "Value": "123"},
            {"Name": "bar", "Value": "456"},
        ]
        table.render_content(data)
        
        assert len(table._rows) == 2
        assert table._filtered_rows == data
    
    def test_filter(self):
        """Test filtering rows."""
        table = FilterableTable(columns=["Name", "Value"])
        data = [
            {"Name": "foo", "Value": "123"},
            {"Name": "bar", "Value": "456"},
            {"Name": "baz", "Value": "789"},
        ]
        table.render_content(data)
        
        table.apply_filter("ba")
        assert len(table._filtered_rows) == 2
        assert all("ba" in row["Name"] for row in table._filtered_rows)
    
    def test_sorting(self):
        """Test column sorting."""
        table = FilterableTable(columns=["Name", "Value"])
        data = [
            {"Name": "charlie", "Value": "3"},
            {"Name": "alice", "Value": "1"},
            {"Name": "bob", "Value": "2"},
        ]
        table.render_content(data)
        
        table.action_sort_by_column("Name")
        sorted_rows = table._get_sorted_rows()
        
        assert sorted_rows[0]["Name"] == "alice"
        assert sorted_rows[1]["Name"] == "bob"
        assert sorted_rows[2]["Name"] == "charlie"


class TestSearchableList:
    """Test SearchableList widget."""
    
    def test_filter(self):
        """Test filtering list items."""
        lst = SearchableList()
        lst.render_content(["apple", "banana", "cherry", "apricot"])
        
        lst.apply_filter("ap")
        assert len(lst._filtered_items) == 2
        assert "apple" in lst._filtered_items
        assert "apricot" in lst._filtered_items
    
    def test_selection(self):
        """Test item selection."""
        lst = SearchableList()
        lst.render_content(["item1", "item2", "item3"])
        
        lst.selected_index = 1
        assert lst.selected_index == 1
        
        lst.action_move_down()
        assert lst.selected_index == 2
        
        lst.action_move_down()
        assert lst.selected_index == 2  # Can't go past end
        
        lst.action_move_up()
        assert lst.selected_index == 1


class TestBaseView:
    """Test BaseView functionality."""
    
    def test_reactive_data_update(self):
        """Test that data changes trigger render."""
        class TestView(BaseView[str]):
            def __init__(self):
                super().__init__()
                self.render_called = False
                self.rendered_data = None
            
            def render_content(self, data: str) -> None:
                self.render_called = True
                self.rendered_data = data
        
        view = TestView()
        view.data = "test data"
        
        assert view.render_called
        assert view.rendered_data == "test data"
    
    def test_loading_state(self):
        """Test loading state management."""
        class TestView(BaseView[str]):
            def render_content(self, data: str) -> None:
                pass
        
        view = TestView()
        
        view.is_loading = True
        # Would assert on rendered content here
        
        view.is_loading = False
        # Would assert loading indicator is hidden
    
    def test_error_state(self):
        """Test error state display."""
        class TestView(BaseView[str]):
            def render_content(self, data: str) -> None:
                pass
        
        view = TestView()
        view.error = "Test error message"
        
        # Would assert error is displayed
```

### 6.2 Integration Testing Screen Flows

```python
# tests/ui/test_screens.py

import pytest
from textual.pilot import Pilot
from caspoon.ui.app import CaspoonApp
from caspoon.ui.screens.main import MainScreen


@pytest.mark.asyncio
async def test_main_screen_layout():
    """Test main screen components are rendered."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Assert main components exist
        assert pilot.app.screen is not None
        assert pilot.app.query_one("#sidebar") is not None
        assert pilot.app.query_one("#content_tabs") is not None


@pytest.mark.asyncio
async def test_command_palette():
    """Test command palette interaction."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Press Ctrl+P to open command palette
        await pilot.press("ctrl+p")
        
        palette = pilot.app.query_one("#command_palette")
        assert palette.display is True
        
        # Type a command
        await pilot.press("a", "n", "a")
        
        # Should show filtered commands
        # (would need to inspect palette._filtered_commands)
        
        # Press Enter to execute
        await pilot.press("enter")
        
        # Palette should be hidden
        assert palette.display is False


@pytest.mark.asyncio
async def test_tab_navigation():
    """Test navigating between tabs."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Initially on overview tab
        assert pilot.app.state.ui_state.current_tab == "overview"
        
        # Press Alt+2 to go to functions
        await pilot.press("alt+2")
        assert pilot.app.state.ui_state.current_tab == "functions"
        
        # Press Alt+3 to go to strings
        await pilot.press("alt+3")
        assert pilot.app.state.ui_state.current_tab == "strings"


@pytest.mark.asyncio
async def test_panel_toggle():
    """Test toggling panels."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Sidebar starts visible
        assert not pilot.app.state.ui_state.sidebar_collapsed
        
        # Press Ctrl+B to toggle
        await pilot.press("ctrl+b")
        assert pilot.app.state.ui_state.sidebar_collapsed
        
        # Press again to show
        await pilot.press("ctrl+b")
        assert not pilot.app.state.ui_state.sidebar_collapsed


@pytest.mark.asyncio
async def test_screen_navigation():
    """Test navigating between screens."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Start on main screen
        assert isinstance(pilot.app.screen, MainScreen)
        
        # Open settings
        await pilot.press("ctrl+comma")
        
        # Should be on settings screen
        # (would check screen type)
        
        # Press Escape to go back
        await pilot.press("escape")
        assert isinstance(pilot.app.screen, MainScreen)
```

### 6.3 Mocking Async Workers

```python
# tests/ui/test_workers.py

import pytest
from unittest.mock import Mock, AsyncMock, patch
from caspoon.ui.app import CaspoonApp
from caspoon.core.models import ExecutableReport


@pytest.mark.asyncio
async def test_binary_analysis_worker():
    """Test binary analysis with mocked worker."""
    app = CaspoonApp()
    
    # Mock the ReconRunner
    mock_report = ExecutableReport(
        path="/test/binary",
        arch="x86_64",
        bits=64,
        stripped=False,
        file_type="ELF",
        functions=[],
        sections=[],
        strings=[],
        imports=[],
        exports=[]
    )
    
    with patch('caspoon.ui.app.ReconRunner') as mock_runner:
        mock_runner.return_value.run = AsyncMock(return_value=mock_report)
        
        async with app.run_test() as pilot:
            # Trigger analysis
            app.post_message(LoadBinary("/test/binary"))
            
            # Wait for worker to complete
            await pilot.pause()
            
            # Assert state was updated
            assert app.state.binary_info.path == "/test/binary"
            assert app.state.binary_info.architecture == "x86_64"
            assert not app.state.ui_state.is_analyzing


@pytest.mark.asyncio
async def test_worker_progress_updates():
    """Test worker progress reporting."""
    app = CaspoonApp()
    
    progress_updates = []
    
    def on_progress(action):
        progress_updates.append((action.percent, action.message))
    
    app.on_analysis_progress = on_progress
    
    async with app.run_test() as pilot:
        # Simulate progress updates
        app.post_message(AnalysisProgress(25, "Parsing..."))
        await pilot.pause()
        
        app.post_message(AnalysisProgress(50, "Analyzing..."))
        await pilot.pause()
        
        app.post_message(AnalysisProgress(100, "Complete"))
        await pilot.pause()
        
        # Assert progress was tracked
        assert len(progress_updates) == 3
        assert progress_updates[0] == (25, "Parsing...")
        assert progress_updates[2] == (100, "Complete")


@pytest.mark.asyncio
async def test_worker_error_handling():
    """Test worker error handling."""
    app = CaspoonApp()
    
    with patch('caspoon.ui.app.ReconRunner') as mock_runner:
        mock_runner.return_value.run = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        async with app.run_test() as pilot:
            # Trigger analysis
            app.post_message(LoadBinary("/test/binary"))
            
            # Wait for worker to fail
            await pilot.pause()
            
            # Assert error state
            assert not app.state.ui_state.is_analyzing
            assert "Test error" in app.state.ui_state.analysis_message


# Fixture for common test setup
@pytest.fixture
def mock_app():
    """Create app with mocked dependencies."""
    app = CaspoonApp()
    
    # Mock ReconRunner
    app._runner = Mock()
    app._runner.run = AsyncMock(return_value=Mock())
    
    return app
```

### 6.4 Snapshot Testing for UI

```python
# tests/ui/test_snapshots.py

import pytest
from textual.pilot import Pilot
from syrupy.assertion import SnapshotAssertion


@pytest.mark.asyncio
async def test_overview_snapshot(snapshot: SnapshotAssertion):
    """Test overview view renders correctly."""
    from caspoon.ui.views.overview import OverviewView
    from caspoon.core.models import BinaryInfo
    
    view = OverviewView()
    
    data = BinaryInfo(
        path="/bin/ls",
        architecture="x86_64",
        bits=64,
        stripped=False,
        file_type="ELF"
    )
    
    view.render_content(data)
    
    # Compare rendered output to snapshot
    assert view.renderable == snapshot


@pytest.mark.asyncio
async def test_full_screen_snapshot(snapshot: SnapshotAssertion):
    """Test complete screen layout."""
    from caspoon.ui.app import CaspoonApp
    
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Load test data
        # ...
        
        # Capture screen rendering
        screenshot = pilot.app.export_screenshot()
        assert screenshot == snapshot
```

---

## 7. Migration Strategy

### 7.1 Phase 1: Foundation (Week 1-2)

**Goal**: Establish new architecture without breaking existing functionality.

1. **Create new structure alongside old**:
   ```
   caspoon/ui/
   ├── app.py                 # Existing (keep as-is initially)
   ├── core/                  # NEW: Core architecture
   │   ├── base.py           # BaseView, InteractiveView, etc.
   │   ├── state.py          # AppState, reactive store
   │   ├── actions.py        # Action messages
   │   └── actions_registry.py
   ├── widgets/               # NEW: Reusable widgets
   │   ├── standard.py       # FilterableTable, SearchableList
   │   └── custom.py         # FunctionExplorer, HexViewer
   ├── screens/               # NEW: Screen management
   │   └── main.py           # MainScreen
   └── views/                 # EXISTING: Migrate one by one
       ├── overview.py       # ← Migrate first
       ├── protections.py
       └── ...
   ```

2. **Implement base classes**:
   - Create `BaseView`, `InteractiveView`, `TreeView`, `TableView`
   - Create `AppState` with reactive properties
   - Create `ActionRegistry`

3. **Add tests for base classes**:
   - Test reactive properties work
   - Test message passing
   - Test widget isolation

**Success Criteria**: New base classes exist, have tests, and don't break existing UI.

---

### 7.2 Phase 2: Migrate First View (Week 3)

**Goal**: Prove the migration path works with one complete view.

1. **Choose simplest view**: `OverviewView`
   
2. **Refactor OverviewView**:
   ```python
   # OLD (caspoon/ui/views/overview.py)
   class OverviewView(Static):
       def update_data(self, report: ExecutableReport) -> None:
           # Direct imperative update
           table = Table(...)
           self.update(table)
   
   # NEW
   class OverviewView(BaseView[BinaryInfo]):
       def render_content(self, data: BinaryInfo) -> None:
           # Reactive update
           table = Table(...)
           self.update(table)
       
       def on_mount(self) -> None:
           # Subscribe to state
           app.state.binary_info.watch(self, "_on_binary_info_changed")
   ```

3. **Update CaspoonApp**:
   ```python
   class CaspoonApp(App):
       def __init__(self):
           super().__init__()
           self.state = AppState()  # NEW: Central state
       
       def on_input_submitted(self, message: Input.Submitted) -> None:
           # OLD: Direct view updates
           # NEW: Update state, let views react
           self.run_worker(self._analyze_binary(path))
       
       async def _analyze_binary(self, path: str) -> None:
           # Update state instead of calling view methods
           self.state.binary_info = BinaryInfo(path=path, ...)
   ```

4. **Add compatibility shim**:
   ```python
   # For views not yet migrated
   def display_report(self, report: ExecutableReport) -> None:
       # Update new state
       self.state.binary_info = BinaryInfo.from_report(report)
       
       # Call old-style views
       self.query_one("#protections").update_data(report)
       self.query_one("#strings_view").update_data(report)
   ```

**Success Criteria**: OverviewView uses new architecture, still works, and coexists with old views.

---

### 7.3 Phase 3: Migrate Remaining Views (Week 4-5)

**Goal**: Convert all views to new architecture.

**Migration Order** (easiest to hardest):
1. ✅ OverviewView (done in Phase 2)
2. ProtectionsView (simple table)
3. ImportsExportsView (two tables)
4. StringsView (list with filtering)
5. R2View (complex, syntax highlighting)

**For each view**:
1. Identify what state it needs
2. Create reactive data type if needed
3. Refactor to extend `BaseView` or appropriate subclass
4. Subscribe to state changes
5. Update tests
6. Remove old `update_data()` interface

**Success Criteria**: All views use new architecture, no more direct `update_data()` calls.

---

### 7.4 Phase 4: Add Advanced Features (Week 6-7)

**Goal**: Layer on IDE-like features now that foundation is solid.

1. **Implement CommandPalette**:
   - Create `CommandPalette` widget
   - Integrate with `ActionRegistry`
   - Add Ctrl+P keybinding
   - Register all default commands

2. **Implement multi-panel layout**:
   - Create `Sidebar`, `DetailsPanel`, `BottomPanel`
   - Make panels collapsible
   - Wire up toggle actions

3. **Add custom widgets**:
   - `FunctionExplorer` (tree view)
   - `HexViewer`
   - `SectionExplorer`

4. **Implement worker pool**:
   - Convert analysis to async worker
   - Add progress reporting
   - Update StatusBar to show progress

**Success Criteria**: Command palette works, panels toggle, analysis is async.

---

### 7.5 Phase 5: Testing & Polish (Week 8)

**Goal**: Comprehensive testing and UX refinement.

1. **Add integration tests**:
   - Test complete user workflows
   - Test all keybindings
   - Test error handling

2. **Add snapshot tests**:
   - Capture rendering of each view
   - Detect unintended UI changes

3. **Performance testing**:
   - Test with large binaries (10k+ functions)
   - Optimize rendering if needed
   - Add virtual scrolling if needed

4. **Documentation**:
   - Document new architecture
   - Create widget development guide
   - Update user documentation

**Success Criteria**: >90% test coverage, no regressions, performance is acceptable.

---

### 7.6 Compatibility & Rollback Plan

**Backward Compatibility**:

```python
# Compatibility shim for old-style views
class LegacyViewAdapter(BaseView[ExecutableReport]):
    """Adapter to make old views work with new architecture."""
    
    def __init__(self, legacy_view):
        super().__init__()
        self.legacy_view = legacy_view
    
    def render_content(self, data: ExecutableReport) -> None:
        """Delegate to old update_data() method."""
        self.legacy_view.update_data(data)
```

**Feature Flags**:

```python
# caspoon/ui/config.py
class UIConfig:
    # Feature flags for gradual rollout
    USE_NEW_STATE_MANAGEMENT = True
    USE_COMMAND_PALETTE = True
    USE_ASYNC_WORKERS = True
    USE_MULTI_PANEL_LAYOUT = False  # Not ready yet
```

**Rollback Plan**:
- Keep old code in `views_legacy/` directory
- Add `--legacy-ui` CLI flag to use old interface
- If critical bug found, disable feature flag
- Can rollback individual features without full revert

---

## 8. Example: Complete Widget Lifecycle

Here's a complete example showing how a widget works in the new architecture:

```python
# caspoon/ui/views/functions.py

from caspoon.ui.core.base import TableView
from caspoon.ui.core.actions import SelectFunction, JumpToAddress
from caspoon.core.models import Function


class FunctionsView(TableView[list[Function]]):
    """View showing all functions in the binary.
    
    Features:
    - Sortable by name, address, size
    - Filterable by name
    - Double-click to jump to disassembly
    - Context menu for actions
    """
    
    BINDINGS = [
        ("enter", "select_function", "View Function"),
        ("d", "jump_to_disassembly", "Disassembly"),
        ("h", "jump_to_hex", "Hex View"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._functions: list[Function] = []
    
    def on_mount(self) -> None:
        """Subscribe to state when widget is added to DOM."""
        app: CaspoonApp = self.app
        
        # Watch for function list changes
        app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_results, new_results) -> None:
        """Reactively update when analysis results change."""
        self.data = new_results.functions
    
    def render_content(self, data: list[Function]) -> None:
        """Render function table."""
        self._functions = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter functions by name."""
        if not text:
            filtered = self._functions
        else:
            text_lower = text.lower()
            filtered = [
                f for f in self._functions
                if text_lower in f.name.lower()
            ]
        
        self._render_table(filtered)
    
    def _render_table(self, functions: list[Function]) -> None:
        """Render the function table."""
        from rich.table import Table
        
        table = Table(title=f"Functions ({len(functions)})")
        table.add_column("Name", style="bold")
        table.add_column("Address")
        table.add_column("Size")
        table.add_column("Type")
        
        # Apply sorting
        functions = self._sort_functions(functions)
        
        for i, func in enumerate(functions):
            style = "reverse" if i == self.selected_index else ""
            table.add_row(
                func.name,
                f"{func.address:08x}",
                f"{func.size} bytes",
                func.type or "unknown",
                style=style
            )
        
        self.update(table)
    
    def _sort_functions(self, functions: list[Function]) -> list[Function]:
        """Sort functions by current sort column."""
        if not self.sort_column:
            return functions
        
        key_map = {
            "Name": lambda f: f.name,
            "Address": lambda f: f.address,
            "Size": lambda f: f.size,
        }
        
        key_func = key_map.get(self.sort_column, lambda f: f.name)
        return sorted(functions, key=key_func, reverse=self.sort_descending)
    
    def get_columns(self) -> list[str]:
        """Return column names for sorting."""
        return ["Name", "Address", "Size", "Type"]
    
    def get_item_count(self) -> int:
        """Return number of functions."""
        return len(self._functions)
    
    def on_item_selected(self, index: int) -> None:
        """Handle function selection."""
        if 0 <= index < len(self._functions):
            func = self._functions[index]
            # Post message to select function
            self.post_message(SelectFunction(func.name))
    
    def action_select_function(self) -> None:
        """View selected function details."""
        if 0 <= self.selected_index < len(self._functions):
            func = self._functions[self.selected_index]
            self.post_message(SelectFunction(func.name))
    
    def action_jump_to_disassembly(self) -> None:
        """Jump to disassembly of selected function."""
        if 0 <= self.selected_index < len(self._functions):
            func = self._functions[self.selected_index]
            # Post message to jump to address in disassembly view
            self.post_message(JumpToAddress(func.address))
            # Switch to disassembly tab
            app = self.app
            app.state.ui_state.current_tab = "disassembly"
    
    def action_jump_to_hex(self) -> None:
        """Jump to hex view of selected function."""
        if 0 <= self.selected_index < len(self._functions):
            func = self._functions[self.selected_index]
            self.post_message(JumpToAddress(func.address))
            app = self.app
            app.state.ui_state.current_tab = "hex"
```

**How it works**:

1. **Mount**: Widget subscribes to `app.state.analysis_results`
2. **State Change**: Analysis completes → `analysis_results.functions` updates
3. **Watch Callback**: `_on_results_changed()` called automatically
4. **Data Update**: `self.data = new_results.functions` triggers `watch_data()`
5. **Render**: `render_content()` called with new data
6. **User Interaction**: User presses Enter → `action_select_function()`
7. **Message**: `SelectFunction` message posted to app
8. **App Handler**: `CaspoonApp.on_select_function()` updates state
9. **State Update**: `selected_function` changes
10. **Other Views React**: Disassembly view watches `selected_function`, updates

**Testing**:

```python
# tests/ui/views/test_functions.py

def test_functions_view_filtering():
    """Test function name filtering."""
    view = FunctionsView()
    
    functions = [
        Function(name="main", address=0x1000, size=100),
        Function(name="init", address=0x2000, size=50),
        Function(name="main_loop", address=0x3000, size=200),
    ]
    
    view.render_content(functions)
    
    # Filter by "main"
    view.filter_text = "main"
    
    # Should show 2 functions
    assert len(view._filtered_functions) == 2


def test_functions_view_selection():
    """Test function selection."""
    view = FunctionsView()
    
    functions = [Function(name="test", address=0x1000, size=100)]
    view.render_content(functions)
    
    messages = []
    view.post_message = lambda msg: messages.append(msg)
    
    view.selected_index = 0
    view.action_select_function()
    
    assert len(messages) == 1
    assert isinstance(messages[0], SelectFunction)
    assert messages[0].function_name == "test"
```

---

## 9. Summary & Next Steps

### Key Design Decisions

1. **Reactive state management**: Single source of truth, views auto-update
2. **Event-driven architecture**: Messages for all actions, loose coupling
3. **Async workers**: Non-blocking analysis with progress reporting
4. **Component hierarchy**: Base classes → Standard widgets → Custom widgets
5. **Screen system**: Multiple screens with navigation stack
6. **Command palette**: Universal action invocation
7. **Testability first**: Every component can be unit tested

### Benefits Over Current Implementation

| Current | New Architecture |
|---------|-----------------|
| Blocking analysis | Async workers with progress |
| Manual view updates | Reactive state propagation |
| No keyboard shortcuts | Complete command palette |
| Static layout | Collapsible multi-panel layout |
| Hard to extend | Plugin-ready architecture |
| Hard to test | Fully testable components |
| No user preferences | Persistent configuration |

### Timeline (8 weeks)

- **Week 1-2**: Build foundation (base classes, state, tests)
- **Week 3**: Migrate first view, prove pattern
- **Week 4-5**: Migrate all remaining views
- **Week 6-7**: Add advanced features (palette, panels, workers)
- **Week 8**: Testing, polish, documentation

### Immediate Next Steps

1. **Create feature branch**: `git checkout -b feature/tui-redesign`
2. **Set up new structure**: Create `ui/core/`, `ui/widgets/`, `ui/screens/`
3. **Implement base classes**: Start with `BaseView`, `AppState`
4. **Write tests first**: TDD approach for base classes
5. **Migrate OverviewView**: Prove the pattern works

### Risk Mitigation

- **Incremental migration**: New coexists with old
- **Feature flags**: Can disable features if needed
- **Compatibility shims**: Old views still work
- **Rollback plan**: Keep old code, add CLI flag
- **Testing**: High coverage before shipping

---

## Appendix: File Structure

```
caspoon/
├── ui/
│   ├── __init__.py
│   ├── app.py                      # Main CaspoonApp (refactored)
│   ├── config.py                   # Feature flags, config
│   │
│   ├── core/                       # NEW: Core architecture
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseView, InteractiveView, TreeView, TableView
│   │   ├── state.py                # AppState, BinaryInfo, AnalysisResults, UIState
│   │   ├── actions.py              # Action messages
│   │   └── actions_registry.py     # ActionRegistry, Command
│   │
│   ├── widgets/                    # NEW: Reusable widgets
│   │   ├── __init__.py
│   │   ├── standard.py             # FilterableTable, SearchableList, ProgressView
│   │   ├── custom.py               # FunctionExplorer, HexViewer, DisassemblyView
│   │   └── command_palette.py      # CommandPalette
│   │
│   ├── screens/                    # NEW: Screen management
│   │   ├── __init__.py
│   │   ├── main.py                 # MainScreen, Sidebar, BottomPanel, StatusBar
│   │   ├── settings.py             # SettingsScreen
│   │   ├── comparison.py           # ComparisonScreen
│   │   └── help.py                 # HelpScreen
│   │
│   ├── dialogs/                    # NEW: Modal dialogs
│   │   ├── __init__.py
│   │   └── common.py               # ConfirmDialog, InputDialog, ErrorDialog
│   │
│   ├── views/                      # REFACTORED: Analysis views
│   │   ├── __init__.py
│   │   ├── overview.py             # OverviewView (uses BaseView)
│   │   ├── protections.py          # ProtectionsView
│   │   ├── strings_view.py         # StringsView (uses SearchableList)
│   │   ├── imports_exports.py      # ImportsExportsView (uses FilterableTable)
│   │   ├── functions.py            # NEW: FunctionsView
│   │   ├── disassembly.py          # NEW: Disassembly with navigation
│   │   └── hex.py                  # NEW: HexViewer
│   │
│   └── syntax/                     # EXISTING: Keep as-is
│       ├── highlighter.py
│       ├── arch_manager.py
│       └── ...
│
└── docs/
    └── plans/
        ├── tui-architecture-redesign.md    # This document
        └── tui-widget-development-guide.md # To be created

tests/
└── ui/
    ├── core/
    │   ├── test_base.py
    │   ├── test_state.py
    │   └── test_actions_registry.py
    ├── widgets/
    │   ├── test_standard.py
    │   └── test_custom.py
    ├── views/
    │   ├── test_overview.py
    │   ├── test_functions.py
    │   └── ...
    └── integration/
        ├── test_screens.py
        ├── test_workflows.py
        └── test_snapshots.py
```

---

**End of Design Document**

This architecture provides a solid, professional foundation for Caspoon's TUI that can scale with the project's growth. The design emphasizes modularity, testability, and user experience while maintaining compatibility with existing code.

Questions or feedback on this design should be directed to the architect or discussed in a design review session.
