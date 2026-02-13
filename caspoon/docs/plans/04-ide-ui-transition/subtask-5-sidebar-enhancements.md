# Subtask 5: Sidebar Enhancements

## Objective
Enhance the sidebar with file browser, recent files list, and multi-binary management capabilities.

## Scope
Complete the sidebar with DirectoryTree for file browsing, recent files ListView, loaded binaries manager with metadata badges, and context menus for all sidebar items. Enable loading and switching between multiple binaries.

## Technical Approach

### 1. Sidebar Structure
**Location**: `caspoon/ui/widgets/sidebar.py`

```python
class Sidebar(Container):
    """Enhanced sidebar with file browser and binary management."""
    
    DEFAULT_CSS = """
    Sidebar {
        width: 25;
        background: $panel;
        border-right: solid $accent;
        padding: 1;
    }
    
    .sidebar-section {
        margin-bottom: 2;
    }
    
    .section-header {
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        # File Explorer
        with Container(classes="sidebar-section"):
            yield Label("📁 EXPLORE", classes="section-header")
            yield DirectoryTree("/", id="file-tree")
        
        # Recent Files
        with Container(classes="sidebar-section"):
            yield Label("📋 RECENT", classes="section-header")
            yield ListView(id="recent-files")
        
        # Loaded Binaries
        with Container(classes="sidebar-section"):
            yield Label("📦 BINARIES", classes="section-header")
            yield ListView(id="loaded-binaries")
```

### 2. File Explorer (DirectoryTree)
**Usage**: Built-in Textual widget

```python
from textual.widgets import DirectoryTree

class EnhancedDirectoryTree(DirectoryTree):
    """DirectoryTree with custom filters."""
    
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter out unwanted files/directories."""
        for path in paths:
            # Skip hidden files
            if path.name.startswith('.'):
                continue
            # Skip non-executable files in certain dirs
            if path.is_file() and not self._is_executable(path):
                # Only show executables, or show all in some dirs
                if path.parent.name in ['bin', 'sbin', 'usr']:
                    continue
            yield path
    
    def _is_executable(self, path: Path) -> bool:
        """Check if file is executable."""
        return os.access(path, os.X_OK)

# In Sidebar
def on_directory_tree_file_selected(
    self, event: DirectoryTree.FileSelected
) -> None:
    """Handle file selection from tree."""
    self.post_message(LoadBinary(str(event.path)))
```

### 3. Recent Files List
**Storage**: JSON config file

```python
class RecentFilesManager:
    """Manage recent files list."""
    
    CONFIG_FILE = Path.home() / ".caspoon" / "recent.json"
    MAX_RECENT = 10
    
    def __init__(self):
        self.recent_files: List[dict] = self._load()
    
    def add(self, path: str, metadata: dict) -> None:
        """Add file to recent list."""
        entry = {
            'path': path,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata  # arch, size, etc.
        }
        
        # Remove if already exists
        self.recent_files = [f for f in self.recent_files if f['path'] != path]
        
        # Add to front
        self.recent_files.insert(0, entry)
        
        # Trim to max
        self.recent_files = self.recent_files[:self.MAX_RECENT]
        
        self._save()
    
    def _load(self) -> List[dict]:
        """Load recent files from config."""
        if not self.CONFIG_FILE.exists():
            return []
        with open(self.CONFIG_FILE) as f:
            return json.load(f)
    
    def _save(self) -> None:
        """Save recent files to config."""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.recent_files, f, indent=2)

# In Sidebar
def update_recent_files(self, recent: List[dict]) -> None:
    """Update recent files list view."""
    list_view = self.query_one("#recent-files", ListView)
    list_view.clear()
    
    for entry in recent:
        path = entry['path']
        timestamp = entry['timestamp']
        
        # Format timestamp
        dt = datetime.fromisoformat(timestamp)
        time_ago = self._format_time_ago(dt)
        
        # Create list item
        list_view.append(ListItem(
            Label(f"{Path(path).name}\n  {time_ago}")
        ))
```

### 4. Loaded Binaries Manager
**Feature**: Track multiple loaded binaries

```python
class LoadedBinary:
    """Represents a loaded binary in the workspace."""
    
    def __init__(self, path: str, report: ExecutableReport):
        self.path = path
        self.report = report
        self.is_active = False
        self.loaded_at = datetime.now()

class BinaryManager:
    """Manage multiple loaded binaries."""
    
    def __init__(self):
        self.binaries: Dict[str, LoadedBinary] = {}
        self.active_binary: Optional[str] = None
    
    def load(self, path: str, report: ExecutableReport) -> None:
        """Load a binary into workspace."""
        binary = LoadedBinary(path, report)
        self.binaries[path] = binary
        self.set_active(path)
    
    def set_active(self, path: str) -> None:
        """Set active binary."""
        # Deactivate previous
        if self.active_binary:
            self.binaries[self.active_binary].is_active = False
        
        # Activate new
        self.binaries[path].is_active = True
        self.active_binary = path
    
    def unload(self, path: str) -> None:
        """Unload a binary from workspace."""
        if path in self.binaries:
            del self.binaries[path]
            if self.active_binary == path:
                # Switch to another binary if available
                if self.binaries:
                    self.set_active(list(self.binaries.keys())[0])
                else:
                    self.active_binary = None

# In Sidebar
def update_loaded_binaries(self, binaries: Dict[str, LoadedBinary]) -> None:
    """Update loaded binaries list."""
    list_view = self.query_one("#loaded-binaries", ListView)
    list_view.clear()
    
    for path, binary in binaries.items():
        name = Path(path).name
        arch = binary.report.architecture
        size_kb = binary.report.size // 1024
        
        # Status indicator
        status = "✓" if binary.is_active else "○"
        
        # Create list item with metadata
        label_text = f"{status} {name}\n  {arch} | {size_kb}KB"
        list_view.append(ListItem(Label(label_text)))
```

### 5. Context Menus
**Implementation**: Show menu on right-click or action key

```python
class ContextMenu(Container):
    """Popup context menu."""
    
    DEFAULT_CSS = """
    ContextMenu {
        width: 30;
        height: auto;
        background: $surface;
        border: solid $primary;
    }
    
    ContextMenu Button {
        width: 100%;
        text-align: left;
    }
    """
    
    def __init__(self, items: List[tuple[str, str]]):
        """
        Args:
            items: List of (label, action_id) tuples
        """
        super().__init__()
        self.items = items
    
    def compose(self) -> ComposeResult:
        for label, action_id in self.items:
            yield Button(label, id=action_id, variant="default")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu item selection."""
        self.post_message(ContextMenuAction(event.button.id))
        self.remove()

# Usage in Sidebar
def on_list_view_item_clicked(self, event: ListView.ItemClicked) -> None:
    """Handle right-click on list items."""
    if event.button == 3:  # Right click
        # Show context menu based on which list was clicked
        if event.sender.id == "recent-files":
            menu = ContextMenu([
                ("Reload", "reload-file"),
                ("Remove from List", "remove-recent"),
                ("Copy Path", "copy-path"),
            ])
        elif event.sender.id == "loaded-binaries":
            menu = ContextMenu([
                ("Switch to This", "switch-binary"),
                ("Unload", "unload-binary"),
                ("Export Report", "export-report"),
                ("Compare With...", "compare-binary"),
            ])
        
        self.mount(menu, before=0)
```

### 6. Multi-Binary Switching
**Feature**: Quick switching between loaded binaries

```python
# In CaspoonIDEApp
class CaspoonIDEApp(App):
    def __init__(self):
        super().__init__()
        self.binary_manager = BinaryManager()
    
    async def action_switch_binary(self, path: str) -> None:
        """Switch to a different loaded binary."""
        self.binary_manager.set_active(path)
        binary = self.binary_manager.binaries[path]
        
        # Update all views with new binary's data
        await self._refresh_all_views(binary.report)
        
        # Update sidebar
        sidebar = self.query_one(Sidebar)
        sidebar.update_loaded_binaries(self.binary_manager.binaries)
        
        # Update title
        self.title = f"Caspoon - {Path(path).name}"
```

## Implementation Steps

1. **Create Sidebar widget structure** (3 hours)
   - Create `sidebar.py` with three sections
   - Style sections with CSS
   - Add section headers
   - Test basic layout

2. **Integrate DirectoryTree** (2 hours)
   - Add DirectoryTree widget
   - Implement path filtering
   - Handle file selection event
   - Post LoadBinary message
   - Test file browsing

3. **Implement Recent Files** (4 hours)
   - Create RecentFilesManager class
   - Implement JSON storage
   - Add/load/save recent files
   - Update ListView on changes
   - Handle click to reload
   - Test persistence across sessions

4. **Implement Binary Manager** (5 hours)
   - Create BinaryManager class
   - Implement load/unload/switch logic
   - Track active binary
   - Update loaded binaries ListView
   - Display metadata badges (arch, size)
   - Test with multiple binaries

5. **Add Context Menus** (4 hours)
   - Create ContextMenu widget
   - Implement right-click detection
   - Create context menu for recent files
   - Create context menu for loaded binaries
   - Implement menu action handlers
   - Test all menu actions

6. **Integrate with main app** (3 hours)
   - Wire up sidebar events in IDE app
   - Implement binary switching
   - Update all views on switch
   - Update title bar
   - Update status bar
   - Test seamless switching

7. **Testing** (3 hours)
   - Test file browsing and loading
   - Test recent files persistence
   - Test multi-binary loading
   - Test switching between binaries
   - Test context menus
   - Test unload binary
   - Edge cases: unload active binary, load same binary twice

## Code Example

```python
# caspoon/ui/widgets/sidebar.py
from textual.widgets import DirectoryTree, ListView, ListItem, Label
from textual.containers import Container
from textual.app import ComposeResult
from textual.message import Message
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class LoadBinary(Message):
    """Message to request loading a binary."""
    
    def __init__(self, path: str):
        super().__init__()
        self.path = path

class SwitchBinary(Message):
    """Message to switch active binary."""
    
    def __init__(self, path: str):
        super().__init__()
        self.path = path

class Sidebar(Container):
    """Enhanced sidebar with file browser and binary management."""
    
    DEFAULT_CSS = """
    Sidebar {
        width: 25;
        min-width: 20;
        background: $panel;
        border-right: thick $accent;
        padding: 1;
    }
    
    Sidebar .sidebar-section {
        margin-bottom: 2;
        padding-bottom: 1;
        border-bottom: solid $surface;
    }
    
    Sidebar .section-header {
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
    }
    
    Sidebar #file-tree {
        height: 15;
    }
    
    Sidebar #recent-files {
        height: 8;
    }
    
    Sidebar #loaded-binaries {
        height: 1fr;
    }
    
    Sidebar ListItem {
        padding: 0 1;
    }
    
    Sidebar ListItem:hover {
        background: $surface;
    }
    """
    
    def __init__(self, initial_path: str = "/bin"):
        super().__init__()
        self.initial_path = initial_path
    
    def compose(self) -> ComposeResult:
        # File Explorer Section
        with Container(classes="sidebar-section"):
            yield Label("📁 EXPLORE", classes="section-header")
            yield DirectoryTree(self.initial_path, id="file-tree")
        
        # Recent Files Section
        with Container(classes="sidebar-section"):
            yield Label("📋 RECENT", classes="section-header")
            yield ListView(id="recent-files")
        
        # Loaded Binaries Section
        with Container(classes="sidebar-section"):
            yield Label("📦 BINARIES", classes="section-header")
            yield ListView(id="loaded-binaries")
    
    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection from directory tree."""
        # Post message to load the selected binary
        self.post_message(LoadBinary(str(event.path)))
    
    def update_recent_files(self, recent: List[dict]) -> None:
        """Update the recent files list."""
        list_view = self.query_one("#recent-files", ListView)
        list_view.clear()
        
        if not recent:
            list_view.append(ListItem(Label("(no recent files)", classes="muted")))
            return
        
        for entry in recent[:5]:  # Show top 5
            path = entry['path']
            timestamp = entry['timestamp']
            
            # Format timestamp
            dt = datetime.fromisoformat(timestamp)
            time_ago = self._format_time_ago(dt)
            
            name = Path(path).name
            list_view.append(ListItem(
                Label(f"{name}\n  {time_ago}"),
                name=path  # Store path for later
            ))
    
    def update_loaded_binaries(self, binaries: Dict[str, 'LoadedBinary']) -> None:
        """Update the loaded binaries list."""
        list_view = self.query_one("#loaded-binaries", ListView)
        list_view.clear()
        
        if not binaries:
            list_view.append(ListItem(Label("(no binaries loaded)", classes="muted")))
            return
        
        for path, binary in binaries.items():
            name = Path(path).name
            arch = binary.report.architecture
            size_kb = binary.report.size // 1024
            
            # Status indicator
            status = "✓" if binary.is_active else "○"
            status_color = "green" if binary.is_active else "dim"
            
            label_text = f"[{status_color}]{status}[/] {name}\n  {arch} | {size_kb}KB"
            list_view.append(ListItem(
                Label(label_text),
                name=path
            ))
    
    def on_list_view_item_clicked(self, event: ListView.ItemClicked) -> None:
        """Handle clicks on list items."""
        item_name = event.item.name
        
        if not item_name:
            return
        
        # Determine which list was clicked
        if event.sender.id == "recent-files":
            # Load recent file
            self.post_message(LoadBinary(item_name))
        
        elif event.sender.id == "loaded-binaries":
            # Switch to binary
            self.post_message(SwitchBinary(item_name))
    
    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as 'X minutes/hours/days ago'."""
        delta = datetime.now() - dt
        
        if delta.seconds < 60:
            return "just now"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        elif delta.seconds < 86400:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        else:
            days = delta.days
            return f"{days}d ago"
```

## Testing Strategy

### Unit Tests
Create `tests/ui/widgets/test_sidebar.py`:
- Test sidebar composition
- Test RecentFilesManager add/load/save
- Test BinaryManager load/switch/unload
- Test time formatting

### Integration Tests
- Click file in directory tree → LoadBinary message posted
- Click recent file → binary reloads
- Load multiple binaries → all appear in binaries list
- Click loaded binary → switches to that binary
- Right-click binary → context menu appears
- Select "Unload" → binary removed from list
- Restart app → recent files persisted

### Manual Testing
1. Launch app and browse file tree
2. Click executable file → analysis starts
3. Check recent files → file appears
4. Load another binary → both in binaries list
5. Click first binary → switches back
6. Restart app → recent files still there
7. Right-click loaded binary → menu appears
8. Test all context menu actions

## Dependencies
- Textual widgets: DirectoryTree, ListView
- JSON for recent files storage
- No new external dependencies

## Estimated Time
**24 hours total**
- Implementation: 21 hours
- Testing: 3 hours

## Success Criteria
- [ ] DirectoryTree allows browsing and selecting files
- [ ] Recent files list persists across sessions
- [ ] Multiple binaries can be loaded simultaneously
- [ ] Clicking loaded binary switches active binary
- [ ] All views update when switching binaries
- [ ] Context menus work for all list items
- [ ] Unload binary removes it cleanly
- [ ] Sidebar sections collapsible (optional enhancement)
- [ ] No performance issues with many loaded binaries

## Next Steps
After completion, proceed to Subtask 6: Polish & Performance for final optimizations and UX refinements.
