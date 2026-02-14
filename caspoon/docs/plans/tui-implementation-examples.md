# TUI Implementation Examples

**Companion to**: [TUI Architecture Redesign](./tui-architecture-redesign.md)

This document provides concrete, copy-paste-ready code examples for common TUI patterns.

---

## Example 1: Simple Read-Only View

**Use Case**: Display static information that updates when analysis completes.

```python
# caspoon/ui/views/file_info.py

from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static

from caspoon.ui.core.base import BaseView
from caspoon.ui.core.state import BinaryInfo


class FileInfoView(BaseView[BinaryInfo]):
    """Display file metadata in a formatted panel."""
    
    def on_mount(self) -> None:
        """Subscribe to binary info changes."""
        app = self.app
        app.state.binary_info.watch(self, "_on_binary_info_changed")
    
    def _on_binary_info_changed(self, old_value, new_value):
        """Update view when binary info changes."""
        self.data = new_value
    
    def render_content(self, data: BinaryInfo) -> None:
        """Render file information."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan")
        table.add_column()
        
        table.add_row("File:", data.path)
        table.add_row("Architecture:", data.architecture)
        table.add_row("Bits:", str(data.bits))
        table.add_row("Type:", data.file_type)
        table.add_row("Size:", f"{data.file_size:,} bytes")
        
        panel = Panel(
            table,
            title="[bold]File Information[/]",
            border_style="blue"
        )
        
        self.update(panel)
```

**Usage in Screen**:

```python
from textual.containers import Container

class MainScreen(Screen):
    def compose(self):
        with Container():
            yield FileInfoView(id="file_info")
```

---

## Example 2: Interactive List with Selection

**Use Case**: List of items user can navigate and select.

```python
# caspoon/ui/views/function_list.py

from rich.table import Table
from textual.binding import Binding

from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.actions import SelectFunction


class FunctionListView(InteractiveView[list[dict]]):
    """Interactive list of functions with keyboard navigation."""
    
    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("enter", "select_item", "Select", show=True),
        Binding("d", "view_disassembly", "Disassembly", show=True),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._functions = []
        self._filtered = []
    
    def on_mount(self) -> None:
        """Subscribe to analysis results."""
        app = self.app
        app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value):
        """Update when functions change."""
        self.data = new_value.functions
    
    def render_content(self, data: list[dict]) -> None:
        """Render function list."""
        self._functions = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter functions by name."""
        if not text:
            self._filtered = self._functions
        else:
            text_lower = text.lower()
            self._filtered = [
                f for f in self._functions
                if text_lower in f.get("name", "").lower()
            ]
        
        self._render_list()
    
    def _render_list(self) -> None:
        """Render the filtered list."""
        table = Table(show_header=True, show_edge=False)
        table.add_column("Name", style="cyan")
        table.add_column("Address", style="yellow")
        table.add_column("Size", justify="right")
        
        for i, func in enumerate(self._filtered):
            name = func.get("name", "unknown")
            address = f"{func.get('address', 0):08x}"
            size = f"{func.get('size', 0)} bytes"
            
            # Highlight selected row
            style = "reverse bold" if i == self.selected_index else ""
            
            table.add_row(name, address, size, style=style)
        
        # Show count
        title = f"Functions ({len(self._filtered)})"
        if len(self._filtered) < len(self._functions):
            title += f" [dim](filtered from {len(self._functions)})[/]"
        
        self.update(table)
    
    def get_item_count(self) -> int:
        """Return number of filtered items."""
        return len(self._filtered)
    
    def on_item_selected(self, index: int) -> None:
        """Handle selection."""
        if 0 <= index < len(self._filtered):
            func = self._filtered[index]
            self.post_message(SelectFunction(func["name"]))
    
    def action_view_disassembly(self) -> None:
        """Jump to disassembly of selected function."""
        if 0 <= self.selected_index < len(self._filtered):
            func = self._filtered[self.selected_index]
            from caspoon.ui.core.actions import JumpToAddress
            self.post_message(JumpToAddress(func["address"]))
            self.app.state.ui_state.current_tab = "disassembly"
    
    def watch_selected_index(self, old_index: int, new_index: int) -> None:
        """Re-render when selection changes."""
        self._render_list()
```

---

## Example 3: Filterable Table with Sorting

**Use Case**: Table that can be filtered and sorted by columns.

```python
# caspoon/ui/views/imports_table.py

from rich.table import Table
from textual.binding import Binding

from caspoon.ui.core.base import TableView


class ImportsTableView(TableView[list[dict]]):
    """Filterable, sortable table of imports."""
    
    BINDINGS = [
        Binding("n", "sort_by_name", "Sort by Name"),
        Binding("a", "sort_by_address", "Sort by Address"),
        Binding("t", "sort_by_type", "Sort by Type"),
        Binding("/", "focus_filter", "Filter"),
    ]
    
    COLUMNS = ["Name", "Address", "Type", "Library"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._imports = []
        self._filtered = []
    
    def on_mount(self) -> None:
        """Subscribe to imports data."""
        app = self.app
        app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value):
        """Update when imports change."""
        self.data = new_value.imports
    
    def render_content(self, data: list[dict]) -> None:
        """Render imports table."""
        self._imports = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter imports by text."""
        if not text:
            self._filtered = self._imports
        else:
            text_lower = text.lower()
            self._filtered = [
                imp for imp in self._imports
                if any(
                    text_lower in str(imp.get(col, "")).lower()
                    for col in ["Name", "Library"]
                )
            ]
        
        self._render_table()
    
    def _render_table(self) -> None:
        """Render the table with current filter and sort."""
        table = Table(title=f"Imports ({len(self._filtered)})")
        
        # Add columns with sort indicator
        for col in self.COLUMNS:
            header = col
            if self.sort_column == col:
                header += " ↓" if self.sort_descending else " ↑"
            table.add_column(header, style=self._column_style(col))
        
        # Sort and render rows
        rows = self._get_sorted_rows()
        for i, imp in enumerate(rows):
            style = "reverse" if i == self.selected_index else ""
            table.add_row(
                imp.get("Name", ""),
                f"{imp.get('Address', 0):08x}",
                imp.get("Type", ""),
                imp.get("Library", ""),
                style=style
            )
        
        self.update(table)
    
    def _get_sorted_rows(self) -> list[dict]:
        """Get sorted rows."""
        if not self.sort_column:
            return self._filtered
        
        return sorted(
            self._filtered,
            key=lambda r: r.get(self.sort_column, ""),
            reverse=self.sort_descending
        )
    
    def _column_style(self, column: str) -> str:
        """Get style for column."""
        styles = {
            "Name": "cyan",
            "Address": "yellow",
            "Type": "green",
            "Library": "magenta",
        }
        return styles.get(column, "")
    
    def get_columns(self) -> list[str]:
        """Return column names."""
        return self.COLUMNS
    
    def get_item_count(self) -> int:
        """Return row count."""
        return len(self._filtered)
    
    def on_item_selected(self, index: int) -> None:
        """Handle row selection."""
        if 0 <= index < len(self._filtered):
            imp = self._filtered[index]
            # Could post message here to show details
            self.app.log(f"Selected import: {imp['Name']}")
    
    def action_sort_by_name(self) -> None:
        """Sort by name column."""
        self.action_sort_by_column("Name")
    
    def action_sort_by_address(self) -> None:
        """Sort by address column."""
        self.action_sort_by_column("Address")
    
    def action_sort_by_type(self) -> None:
        """Sort by type column."""
        self.action_sort_by_column("Type")
    
    def action_focus_filter(self) -> None:
        """Focus filter input."""
        # Post message to parent to focus filter input
        from caspoon.ui.core.actions import FocusFilter
        self.post_message(FocusFilter())
```

---

## Example 4: Tree View with Expand/Collapse

**Use Case**: Hierarchical view like function explorer or section navigator.

```python
# caspoon/ui/widgets/section_tree.py

from rich.tree import Tree as RichTree
from textual.binding import Binding

from caspoon.ui.core.base import TreeView


class SectionTreeView(TreeView[list[dict]]):
    """Hierarchical view of binary sections."""
    
    BINDINGS = [
        Binding("space,enter", "toggle_expand", "Expand/Collapse"),
        Binding("right", "expand", "Expand"),
        Binding("left", "collapse", "Collapse"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sections = []
    
    def on_mount(self) -> None:
        """Subscribe to sections data."""
        app = self.app
        app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value):
        """Update when sections change."""
        self.data = new_value.sections
    
    def render_content(self, data: list[dict]) -> None:
        """Render section tree."""
        self._sections = data
        self._render_tree()
    
    def _render_tree(self) -> None:
        """Render the tree structure."""
        tree = RichTree("[bold]Sections[/]")
        
        for i, section in enumerate(self._sections):
            node_id = f"section:{i}"
            is_expanded = node_id in self.expanded_nodes
            is_selected = i == self.selected_index
            
            # Section node
            name = section.get("name", "unknown")
            size = section.get("size", 0)
            address = section.get("address", 0)
            perms = self._format_perms(section)
            
            style = "reverse bold" if is_selected else "bold"
            label = f"[{style}]{name}[/] ({size} bytes) [{perms}]"
            
            section_node = tree.add(label)
            
            # Add details if expanded
            if is_expanded:
                section_node.add(f"Address: [yellow]{address:08x}[/]")
                section_node.add(f"Size: {size:,} bytes")
                section_node.add(f"Permissions: {perms}")
                
                if section.get("type"):
                    section_node.add(f"Type: {section['type']}")
        
        self.update(tree)
    
    def _format_perms(self, section: dict) -> str:
        """Format permission string."""
        r = "r" if section.get("readable", False) else "-"
        w = "w" if section.get("writable", False) else "-"
        x = "x" if section.get("executable", False) else "-"
        return f"{r}{w}{x}"
    
    def get_selected_node_id(self) -> str:
        """Get ID of selected node."""
        if 0 <= self.selected_index < len(self._sections):
            return f"section:{self.selected_index}"
        return ""
    
    def get_item_count(self) -> int:
        """Return number of sections."""
        return len(self._sections)
    
    def on_item_selected(self, index: int) -> None:
        """Handle section selection."""
        if 0 <= index < len(self._sections):
            section = self._sections[index]
            # Jump to section address
            from caspoon.ui.core.actions import JumpToAddress
            self.post_message(JumpToAddress(section["address"]))
    
    def action_expand(self) -> None:
        """Expand selected node."""
        node_id = self.get_selected_node_id()
        if node_id:
            self.expanded_nodes.add(node_id)
            self._render_tree()
    
    def action_collapse(self) -> None:
        """Collapse selected node."""
        node_id = self.get_selected_node_id()
        if node_id and node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)
            self._render_tree()
```

---

## Example 5: Multi-Panel Layout

**Use Case**: Main screen with collapsible sidebar, content, and details panel.

```python
# caspoon/ui/screens/main_screen.py

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, TabbedContent, TabPane

from caspoon.ui.widgets.sidebar import Sidebar
from caspoon.ui.widgets.details_panel import DetailsPanel
from caspoon.ui.widgets.bottom_panel import BottomPanel
from caspoon.ui.widgets.status_bar import StatusBar


class MainScreen(Screen):
    """Main analysis screen with multi-panel layout."""
    
    BINDINGS = [
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+d", "toggle_details", "Toggle Details"),
        Binding("ctrl+j", "toggle_bottom", "Toggle Bottom"),
        Binding("ctrl+p", "command_palette", "Command Palette"),
    ]
    
    CSS = """
    MainScreen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: auto 1fr auto;
    }
    
    #status_bar {
        height: 1;
        dock: top;
    }
    
    #main_layout {
        height: 1fr;
    }
    
    #sidebar {
        width: 30;
        height: 1fr;
    }
    
    #sidebar.collapsed {
        display: none;
    }
    
    #content_panel {
        width: 1fr;
        height: 1fr;
    }
    
    #details_panel {
        width: 25;
        height: 1fr;
    }
    
    #details_panel.collapsed {
        display: none;
    }
    
    #bottom_panel {
        height: 10;
        dock: bottom;
    }
    
    #bottom_panel.collapsed {
        display: none;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Compose main screen layout."""
        yield StatusBar(id="status_bar")
        
        with Horizontal(id="main_layout"):
            yield Sidebar(id="sidebar")
            
            with Vertical(id="content_panel"):
                with TabbedContent():
                    with TabPane("Overview"):
                        yield OverviewView(id="overview")
                    
                    with TabPane("Functions"):
                        yield FunctionListView(id="functions")
                    
                    with TabPane("Strings"):
                        yield StringsView(id="strings")
                    
                    with TabPane("Imports"):
                        yield ImportsTableView(id="imports")
            
            yield DetailsPanel(id="details_panel")
        
        yield BottomPanel(id="bottom_panel", classes="collapsed")
        yield Footer()
    
    def on_mount(self) -> None:
        """Watch UI state for panel visibility."""
        app = self.app
        app.state.ui_state.watch(self, "_on_ui_state_changed")
    
    def _on_ui_state_changed(self, old_state, new_state):
        """Update panel visibility based on state."""
        sidebar = self.query_one("#sidebar", Sidebar)
        if new_state.sidebar_collapsed:
            sidebar.add_class("collapsed")
        else:
            sidebar.remove_class("collapsed")
        
        details = self.query_one("#details_panel", DetailsPanel)
        if new_state.details_panel_collapsed:
            details.add_class("collapsed")
        else:
            details.remove_class("collapsed")
        
        bottom = self.query_one("#bottom_panel", BottomPanel)
        if new_state.bottom_panel_collapsed:
            bottom.add_class("collapsed")
        else:
            bottom.remove_class("collapsed")
    
    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        from caspoon.ui.core.actions import TogglePanel
        self.app.post_message(TogglePanel("sidebar"))
    
    def action_toggle_details(self) -> None:
        """Toggle details panel visibility."""
        from caspoon.ui.core.actions import TogglePanel
        self.app.post_message(TogglePanel("details"))
    
    def action_toggle_bottom(self) -> None:
        """Toggle bottom panel visibility."""
        from caspoon.ui.core.actions import TogglePanel
        self.app.post_message(TogglePanel("bottom"))
    
    def action_command_palette(self) -> None:
        """Show command palette."""
        palette = self.query_one("#command_palette")
        palette.show()
```

---

## Example 6: Async Worker with Progress

**Use Case**: Long-running analysis that reports progress.

```python
# caspoon/ui/app.py

from textual.app import App
from textual.worker import Worker, WorkerState

from caspoon.core.runner import ReconRunner
from caspoon.ui.core.state import AppState, BinaryInfo, AnalysisResults
from caspoon.ui.core.actions import (
    LoadBinary,
    AnalysisProgress,
    AnalysisComplete,
    AnalysisError,
)


class CaspoonApp(App):
    """Main application with async workers."""
    
    def __init__(self):
        super().__init__()
        self.state = AppState()
        self._analysis_worker: Optional[Worker] = None
    
    def on_load_binary(self, action: LoadBinary) -> None:
        """Handle binary load request."""
        # Cancel existing analysis if running
        if self._analysis_worker and self._analysis_worker.is_running:
            self._analysis_worker.cancel()
        
        # Update state
        self.state.ui_state.is_analyzing = True
        self.state.ui_state.analysis_progress = 0.0
        self.state.ui_state.analysis_message = "Starting analysis..."
        
        # Start worker
        self._analysis_worker = self.run_worker(
            self._analyze_binary(action.path),
            name="binary_analysis",
            description=f"Analyzing {action.path}",
            group="analysis"
        )
    
    async def _analyze_binary(self, path: str) -> None:
        """Async worker for binary analysis."""
        try:
            runner = ReconRunner()
            
            # Step 1: Parse file format
            self.post_message(AnalysisProgress(10, "Parsing file format..."))
            # Simulate async work
            await asyncio.sleep(0.1)
            
            # Step 2: Extract metadata
            self.post_message(AnalysisProgress(30, "Extracting metadata..."))
            await asyncio.sleep(0.1)
            
            # Step 3: Run r2 analysis
            self.post_message(AnalysisProgress(50, "Running radare2 analysis..."))
            # Run blocking operation in thread pool
            report = await asyncio.to_thread(runner.run, path)
            
            # Step 4: Process results
            self.post_message(AnalysisProgress(80, "Processing results..."))
            await asyncio.sleep(0.1)
            
            # Convert to state
            binary_info = BinaryInfo(
                path=report.path,
                architecture=report.arch,
                bits=report.bits,
                file_type=report.file_type,
                stripped=report.stripped,
                file_size=os.path.getsize(path)
            )
            
            results = AnalysisResults(
                functions=report.functions or [],
                sections=report.sections or [],
                strings=report.strings or [],
                imports=report.imports or [],
                exports=report.exports or [],
                protections=report.protections or {},
                disassembly=report.disassembly or [],
                raw_report=report
            )
            
            # Complete
            self.post_message(AnalysisProgress(100, "Complete"))
            self.post_message(AnalysisComplete(binary_info, results))
            
        except Exception as e:
            self.log.error(f"Analysis failed: {e}")
            self.post_message(AnalysisError(str(e)))
    
    def on_analysis_progress(self, action: AnalysisProgress) -> None:
        """Update progress state."""
        self.state.ui_state.analysis_progress = action.percent
        self.state.ui_state.analysis_message = action.message
    
    def on_analysis_complete(self, action: AnalysisComplete) -> None:
        """Handle analysis completion."""
        self.state.binary_info = action.binary_info
        self.state.analysis_results = action.results
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_message = "Analysis complete ✓"
    
    def on_analysis_error(self, action: AnalysisError) -> None:
        """Handle analysis error."""
        self.state.ui_state.is_analyzing = False
        self.state.ui_state.analysis_message = f"Error: {action.error}"
        
        # Show error dialog
        from caspoon.ui.dialogs.common import ErrorDialog
        self.push_screen(ErrorDialog(action.error))
```

---

## Example 7: Command Palette Integration

**Use Case**: Register commands that appear in command palette.

```python
# caspoon/ui/app.py (continued)

def on_mount(self) -> None:
    """Initialize app on mount."""
    # Register default commands
    self._register_commands()
    
    # Update command palette
    palette = self.query_one("#command_palette")
    self.action_registry.update_command_palette(palette)

def _register_commands(self) -> None:
    """Register all application commands."""
    reg = self.action_registry
    
    # File commands
    reg.register(
        "analyze_binary",
        "Analyze Binary",
        self._prompt_analyze,
        description="Open and analyze a binary file",
        keybinding="ctrl+o",
        category="File"
    )
    
    reg.register(
        "reload_binary",
        "Reload Current Binary",
        self._reload_binary,
        description="Reload and re-analyze current binary",
        keybinding="ctrl+r",
        category="File"
    )
    
    reg.register(
        "export_report",
        "Export Report",
        self._export_report,
        description="Export analysis report to file",
        keybinding="ctrl+s",
        category="File"
    )
    
    # View commands
    for i, (tab_name, tab_id) in enumerate([
        ("Overview", "overview"),
        ("Functions", "functions"),
        ("Strings", "strings"),
        ("Imports", "imports"),
        ("Disassembly", "disassembly"),
        ("Hex", "hex"),
    ], 1):
        reg.register(
            f"goto_{tab_id}",
            f"Go to {tab_name}",
            lambda tid=tab_id: self._switch_tab(tid),
            description=f"Switch to {tab_name} tab",
            keybinding=f"alt+{i}",
            category="View"
        )
    
    # Panel commands
    for panel_name, panel_id in [
        ("Sidebar", "sidebar"),
        ("Details", "details"),
        ("Bottom Panel", "bottom"),
    ]:
        reg.register(
            f"toggle_{panel_id}",
            f"Toggle {panel_name}",
            lambda pid=panel_id: self.post_message(TogglePanel(pid)),
            description=f"Show/hide {panel_name}",
            category="View"
        )
    
    # Navigation commands
    reg.register(
        "jump_to_address",
        "Jump to Address",
        self._prompt_jump_address,
        description="Jump to specific address in hex/disassembly",
        keybinding="ctrl+g",
        category="Navigation"
    )
    
    reg.register(
        "search_global",
        "Global Search",
        self._prompt_global_search,
        description="Search across all views",
        keybinding="ctrl+f",
        category="Search"
    )
    
    # Help commands
    reg.register(
        "show_help",
        "Show Help",
        lambda: self.push_screen(HelpScreen()),
        description="Show help and keybindings",
        keybinding="f1",
        category="Help"
    )

async def _prompt_analyze(self) -> None:
    """Prompt for binary path and analyze."""
    from caspoon.ui.dialogs.common import FileDialog
    
    path = await self.push_screen_wait(FileDialog("Select binary to analyze"))
    if path:
        self.post_message(LoadBinary(path))

async def _prompt_jump_address(self) -> None:
    """Prompt for address to jump to."""
    from caspoon.ui.dialogs.common import InputDialog
    
    address_str = await self.push_screen_wait(
        InputDialog("Enter address (hex):", "Jump to Address", "0x")
    )
    
    if address_str:
        try:
            address = int(address_str, 16)
            self.post_message(JumpToAddress(address))
        except ValueError:
            self.notify("Invalid address format", severity="error")

def _switch_tab(self, tab_id: str) -> None:
    """Switch to specified tab."""
    self.state.ui_state.current_tab = tab_id
    
    # Focus the tab (implementation depends on tab widget used)
    tabs = self.query_one(TabbedContent)
    tabs.active = tab_id
```

---

## Example 8: Modal Dialog

**Use Case**: Show confirmation or input dialog.

```python
# caspoon/ui/dialogs/confirm.py

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmDialog(ModalScreen[bool]):
    """Modal confirmation dialog."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "OK"),
    ]
    
    CSS = """
    ConfirmDialog {
        align: center middle;
    }
    
    #dialog {
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
    }
    
    #message {
        width: 100%;
        height: 3;
        content-align: center middle;
        margin: 1 0;
    }
    
    #buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(
        self,
        message: str,
        title: str = "Confirm",
        ok_label: str = "OK",
        cancel_label: str = "Cancel"
    ):
        super().__init__()
        self.message = message
        self.title = title
        self.ok_label = ok_label
        self.cancel_label = cancel_label
    
    def compose(self) -> ComposeResult:
        """Compose dialog."""
        with Grid(id="dialog"):
            yield Label(self.title, id="title")
            yield Label(self.message, id="message")
            
            with Grid(id="buttons"):
                yield Button(self.ok_label, variant="primary", id="ok")
                yield Button(self.cancel_label, id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm(self) -> None:
        """Confirm action."""
        self.dismiss(True)
    
    def action_cancel(self) -> None:
        """Cancel action."""
        self.dismiss(False)


# Usage:
async def delete_function():
    """Delete function after confirmation."""
    confirmed = await app.push_screen_wait(
        ConfirmDialog(
            "Are you sure you want to delete this function?",
            title="Delete Function",
            ok_label="Delete",
            cancel_label="Cancel"
        )
    )
    
    if confirmed:
        # Proceed with deletion
        pass
```

---

## Example 9: Custom Message Passing

**Use Case**: Widgets communicate via custom messages.

```python
# caspoon/ui/core/actions.py

from textual.message import Message


class FunctionSelected(Message):
    """Posted when a function is selected."""
    
    def __init__(self, function_name: str, address: int):
        super().__init__()
        self.function_name = function_name
        self.address = address


class AddressJumped(Message):
    """Posted when jumping to an address."""
    
    def __init__(self, address: int, view: str = "hex"):
        super().__init__()
        self.address = address
        self.view = view  # "hex" or "disassembly"


# Widget A posts message
class FunctionListView(InteractiveView):
    def on_item_selected(self, index: int):
        func = self._functions[index]
        self.post_message(
            FunctionSelected(func["name"], func["address"])
        )


# Widget B handles message
class DisassemblyView(BaseView):
    def on_function_selected(self, msg: FunctionSelected) -> None:
        """Handle function selection."""
        self.jump_to_function(msg.function_name)
        self.highlight_address(msg.address)


# App can also handle
class CaspoonApp(App):
    def on_function_selected(self, msg: FunctionSelected) -> None:
        """Update state when function selected."""
        self.state.ui_state.selected_function = msg.function_name
        self.state.ui_state.selected_address = msg.address
```

---

## Example 10: Testing a View

**Use Case**: Unit test a view component.

```python
# tests/ui/views/test_function_list.py

import pytest
from unittest.mock import Mock

from caspoon.ui.views.function_list import FunctionListView
from caspoon.ui.core.actions import SelectFunction


def test_render_empty_list():
    """Test rendering empty function list."""
    view = FunctionListView()
    view.render_content([])
    
    assert view._functions == []
    assert view._filtered == []


def test_render_functions():
    """Test rendering function list."""
    view = FunctionListView()
    
    functions = [
        {"name": "main", "address": 0x1000, "size": 100},
        {"name": "init", "address": 0x2000, "size": 50},
    ]
    
    view.render_content(functions)
    
    assert len(view._functions) == 2
    assert len(view._filtered) == 2


def test_filter_functions():
    """Test filtering functions by name."""
    view = FunctionListView()
    
    functions = [
        {"name": "main", "address": 0x1000, "size": 100},
        {"name": "init", "address": 0x2000, "size": 50},
        {"name": "main_loop", "address": 0x3000, "size": 200},
    ]
    
    view.render_content(functions)
    view.apply_filter("main")
    
    assert len(view._filtered) == 2
    assert all("main" in f["name"] for f in view._filtered)


def test_selection():
    """Test item selection."""
    view = FunctionListView()
    
    functions = [
        {"name": "test_func", "address": 0x1000, "size": 100},
    ]
    
    view.render_content(functions)
    
    # Mock post_message
    messages = []
    view.post_message = lambda msg: messages.append(msg)
    
    # Select item
    view.selected_index = 0
    view.on_item_selected(0)
    
    # Assert message was posted
    assert len(messages) == 1
    assert isinstance(messages[0], SelectFunction)
    assert messages[0].function_name == "test_func"


def test_navigation():
    """Test keyboard navigation."""
    view = FunctionListView()
    
    functions = [
        {"name": f"func{i}", "address": 0x1000 + i * 0x100, "size": 100}
        for i in range(5)
    ]
    
    view.render_content(functions)
    
    # Initial position
    assert view.selected_index == 0
    
    # Move down
    view.action_move_down()
    assert view.selected_index == 1
    
    view.action_move_down()
    assert view.selected_index == 2
    
    # Move up
    view.action_move_up()
    assert view.selected_index == 1
    
    # Can't go below 0
    view.selected_index = 0
    view.action_move_up()
    assert view.selected_index == 0
    
    # Can't go above max
    view.selected_index = 4
    view.action_move_down()
    assert view.selected_index == 4
```

---

These examples provide concrete, working patterns for building IDE-like TUI components in Caspoon. Each example is self-contained and demonstrates a specific aspect of the architecture.
