# Subtask 4: Context-Aware Detail Panel

## Objective
Create a detail panel that displays context-specific information based on user selections in any view.

## Scope
Implement a detail panel widget that responds to selection events from DataTables and Trees, displays relevant metadata, cross-references, and quick actions for the selected item.

## Technical Approach

### 1. Message-Based Architecture
**Pattern**: Use Textual's message system for widget communication

```python
# Define custom messages
class SelectionChanged(Message):
    """Posted when a selection changes in any view."""
    
    def __init__(self, item_type: str, item_data: dict):
        super().__init__()
        self.item_type = item_type  # "string", "import", "function", etc.
        self.item_data = item_data  # Relevant data for the item
```

### 2. Detail Panel Widget
**Location**: `caspoon/ui/widgets/detail_panel.py`

```python
class DetailPanel(Container):
    """Context-aware detail panel."""
    
    DEFAULT_CSS = """
    DetailPanel {
        height: 30%;
        background: $panel;
        border-top: solid $accent;
        padding: 1;
    }
    
    .detail-section {
        margin-bottom: 1;
        border-bottom: solid $surface;
    }
    
    .detail-label {
        color: $text-muted;
    }
    
    .detail-value {
        color: $text;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Label("📋 Details", id="detail-header")
        yield Container(id="detail-content")
    
    def update_selection(self, item_type: str, item_data: dict) -> None:
        """Update panel based on selected item."""
        content = self.query_one("#detail-content", Container)
        content.remove_children()
        
        if item_type == "string":
            self._show_string_details(content, item_data)
        elif item_type == "import":
            self._show_import_details(content, item_data)
        elif item_type == "export":
            self._show_export_details(content, item_data)
        elif item_type == "function":
            self._show_function_details(content, item_data)
        else:
            content.mount(Static("Select an item to see details"))
```

### 3. Item-Type Specific Handlers

**String Details**:
```python
def _show_string_details(self, container: Container, data: dict) -> None:
    """Display string-specific details."""
    string_value = data['value']
    
    # Basic info section
    with Section("String Information", container):
        yield KeyValue("Value", string_value[:200])  # Truncate
        yield KeyValue("Length", str(len(string_value)))
        yield KeyValue("Encoding", data.get('encoding', 'ASCII'))
        yield KeyValue("Category", data.get('category', 'Generic'))
    
    # Cross-references section
    xrefs = self._get_string_xrefs(data['address'])
    if xrefs:
        with Section("Cross-References", container):
            for xref in xrefs[:10]:  # Show first 10
                yield Label(f"→ {xref['function']} @ {hex(xref['address'])}")
    
    # Quick actions
    with Section("Actions", container):
        yield Button("Copy String", id="copy-string")
        yield Button("Find All", id="find-all-string")
        yield Button("Go to Address", id="goto-address")
```

**Import Details**:
```python
def _show_import_details(self, container: Container, data: dict) -> None:
    """Display import-specific details."""
    import_name = data['name']
    library = data['library']
    
    # Basic info
    with Section("Import Information", container):
        yield KeyValue("Function", import_name)
        yield KeyValue("Library", library)
        yield KeyValue("Address", hex(data.get('address', 0)))
        yield KeyValue("Risk Level", data.get('risk', 'Unknown'))
    
    # Library info
    lib_info = self._get_library_info(library)
    if lib_info:
        with Section("Library Information", container):
            yield KeyValue("Version", lib_info.get('version', 'Unknown'))
            yield KeyValue("Purpose", lib_info.get('description', 'N/A'))
    
    # Function documentation
    doc = self._get_function_doc(import_name, library)
    if doc:
        with Section("Documentation", container):
            yield Static(doc[:500])  # Truncate long docs
    
    # Usage sites
    usage = self._get_import_usage(import_name)
    with Section("Called From", container):
        for call_site in usage[:10]:
            yield Label(f"→ {call_site['function']} @ {hex(call_site['address'])}")
    
    # Actions
    with Section("Actions", container):
        yield Button("Search MSDN/Man Page", id="search-docs")
        yield Button("Find All Calls", id="find-calls")
```

**Function Details**:
```python
def _show_function_details(self, container: Container, data: dict) -> None:
    """Display function-specific details."""
    func_name = data['name']
    
    # Basic info
    with Section("Function Information", container):
        yield KeyValue("Name", func_name)
        yield KeyValue("Address", hex(data['address']))
        yield KeyValue("Size", f"{data['size']} bytes")
        yield KeyValue("Type", data.get('type', 'User'))
    
    # Statistics
    stats = self._get_function_stats(data['address'])
    with Section("Statistics", container):
        yield KeyValue("Instructions", str(stats['instruction_count']))
        yield KeyValue("Basic Blocks", str(stats['block_count']))
        yield KeyValue("Cyclomatic Complexity", str(stats['complexity']))
    
    # Calls
    calls = self._get_function_calls(data['address'])
    with Section("Calls To", container):
        for call in calls[:10]:
            yield Label(f"→ {call['target']} @ {hex(call['address'])}")
    
    # Called by
    callers = self._get_function_callers(data['address'])
    with Section("Called By", container):
        for caller in callers[:10]:
            yield Label(f"← {caller['function']} @ {hex(caller['address'])}")
    
    # Actions
    with Section("Actions", container):
        yield Button("View Disassembly", id="view-disasm")
        yield Button("View Graph", id="view-graph")
        yield Button("Analyze", id="analyze-func")
```

### 4. Cross-Reference Lookup
**Integration**: Query r2 backend for xrefs

```python
def _get_string_xrefs(self, address: int) -> List[dict]:
    """Get cross-references to a string."""
    # Use r2pipe to query
    xrefs = self.app.r2.cmdj(f"axtj @ {address}")
    return [
        {
            'function': xref.get('fcn_name', 'unknown'),
            'address': xref['from']
        }
        for xref in xrefs
    ]

def _get_import_usage(self, import_name: str) -> List[dict]:
    """Find where an import is called."""
    # Query r2 for all calls to the import
    calls = self.app.r2.cmdj(f"axtj sym.imp.{import_name}")
    return [
        {
            'function': call.get('fcn_name', 'unknown'),
            'address': call['from']
        }
        for call in calls
    ]
```

### 5. Integration with Views
**Modify each view to emit SelectionChanged messages**

```python
# In StringsView
class StringsView(Container):
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Emit selection changed message."""
        row_data = self._get_row_data(event.cursor_row)
        self.post_message(SelectionChanged(
            item_type="string",
            item_data={
                'value': row_data['string'],
                'address': row_data['address'],
                'encoding': row_data['encoding'],
                'category': row_data['category']
            }
        ))

# In CaspoonIDEApp
class CaspoonIDEApp(App):
    def on_selection_changed(self, message: SelectionChanged) -> None:
        """Handle selection changes."""
        detail_panel = self.query_one(DetailPanel)
        detail_panel.update_selection(message.item_type, message.item_data)
```

## Implementation Steps

1. **Create DetailPanel widget** (4 hours)
   - Create base widget structure
   - Implement CSS styling
   - Create section components (KeyValue, Section)
   - Add empty state ("Select an item...")
   - Test mounting/unmounting

2. **Implement item-specific handlers** (6 hours)
   - Implement `_show_string_details()`
   - Implement `_show_import_details()`
   - Implement `_show_export_details()`
   - Implement `_show_function_details()`
   - Create KeyValue widget for consistent formatting
   - Test each handler with sample data

3. **Add cross-reference queries** (4 hours)
   - Implement `_get_string_xrefs()` using r2
   - Implement `_get_import_usage()` using r2
   - Implement `_get_function_calls()` using r2
   - Implement `_get_function_callers()` using r2
   - Test with real binaries
   - Handle cases with no xrefs gracefully

4. **Integrate with views** (3 hours)
   - Add row selection handlers to StringsView
   - Add row selection handlers to ImportsExportsView
   - Add node selection handlers to FunctionsView
   - Post SelectionChanged messages
   - Test message flow from view → app → detail panel

5. **Add quick actions** (3 hours)
   - Implement action buttons for each item type
   - Wire up button handlers
   - Implement "Copy String" action
   - Implement "Go to Address" action
   - Implement "View Disassembly" action
   - Test all actions work correctly

6. **Testing** (3 hours)
   - Test detail panel with each item type
   - Test xref queries with various binaries
   - Test rapid selection changes (no lag)
   - Test with items that have no xrefs
   - Test actions trigger correct behaviors
   - Test panel collapse/expand preserves state

## Code Example

```python
# caspoon/ui/widgets/detail_panel.py
from textual.widgets import Static, Button, Label
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from textual.message import Message
from typing import Dict, List

class SelectionChanged(Message):
    """Message posted when selection changes."""
    
    def __init__(self, item_type: str, item_data: dict):
        super().__init__()
        self.item_type = item_type
        self.item_data = item_data

class KeyValue(Container):
    """Display a key-value pair."""
    
    DEFAULT_CSS = """
    KeyValue {
        layout: horizontal;
        height: auto;
    }
    
    KeyValue .key {
        width: 20;
        color: $text-muted;
    }
    
    KeyValue .value {
        width: 1fr;
        color: $text;
    }
    """
    
    def __init__(self, key: str, value: str):
        super().__init__()
        self.key = key
        self.value = value
    
    def compose(self) -> ComposeResult:
        yield Label(f"{self.key}:", classes="key")
        yield Label(self.value, classes="value")

class DetailPanel(Container):
    """Context-aware detail panel."""
    
    DEFAULT_CSS = """
    DetailPanel {
        height: 30%;
        background: $panel;
        border-top: thick $accent;
        padding: 1 2;
    }
    
    DetailPanel #detail-header {
        dock: top;
        height: 1;
        padding-bottom: 1;
        text-style: bold;
        color: $accent;
    }
    
    DetailPanel .section {
        margin-top: 1;
        padding-bottom: 1;
        border-bottom: solid $surface;
    }
    
    DetailPanel .section-title {
        text-style: bold;
        color: $primary;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Label("📋 Details", id="detail-header")
        yield Vertical(id="detail-content")
    
    def update_selection(self, item_type: str, item_data: Dict) -> None:
        """Update panel based on selected item."""
        content = self.query_one("#detail-content", Vertical)
        content.remove_children()
        
        # Route to appropriate handler
        handlers = {
            "string": self._show_string_details,
            "import": self._show_import_details,
            "export": self._show_export_details,
            "function": self._show_function_details,
        }
        
        handler = handlers.get(item_type)
        if handler:
            with content:
                handler(item_data)
        else:
            content.mount(Static("Unknown item type"))
    
    def _show_string_details(self, data: Dict) -> None:
        """Display string details."""
        # Section: Basic Info
        yield Label("String Information", classes="section-title")
        yield KeyValue("Value", data['value'][:150])
        yield KeyValue("Length", str(data.get('length', len(data['value']))))
        yield KeyValue("Encoding", data.get('encoding', 'ASCII'))
        yield KeyValue("Category", data.get('category', 'Generic'))
        
        # Section: Cross-References
        address = data.get('address')
        if address:
            xrefs = self._get_xrefs(address)
            if xrefs:
                yield Label("", classes="section")  # Divider
                yield Label("Cross-References", classes="section-title")
                for xref in xrefs[:5]:
                    yield Label(f"  → {xref['function']} @ {hex(xref['address'])}")
        
        # Section: Actions
        yield Label("", classes="section")
        yield Label("Quick Actions", classes="section-title")
        yield Button("Copy to Clipboard", id="copy-string", variant="primary")
        if address:
            yield Button("Go to Address", id="goto-address")
    
    def _show_import_details(self, data: Dict) -> None:
        """Display import details."""
        yield Label("Import Information", classes="section-title")
        yield KeyValue("Function", data['name'])
        yield KeyValue("Library", data['library'])
        yield KeyValue("Address", hex(data.get('address', 0)))
        
        risk = data.get('risk', 'Low')
        risk_color = {
            'Critical': 'red',
            'High': 'yellow',
            'Medium': 'yellow',
            'Low': 'green'
        }.get(risk, 'white')
        yield KeyValue("Risk Level", f"[{risk_color}]{risk}[/]")
        
        # Usage sites
        usage = self._get_import_usage(data['name'])
        if usage:
            yield Label("", classes="section")
            yield Label("Called From", classes="section-title")
            for call_site in usage[:5]:
                yield Label(f"  → {call_site['function']} @ {hex(call_site['address'])}")
        
        # Actions
        yield Label("", classes="section")
        yield Label("Quick Actions", classes="section-title")
        yield Button("Search Documentation", id="search-docs", variant="primary")
        yield Button("Find All Calls", id="find-calls")
    
    def _show_function_details(self, data: Dict) -> None:
        """Display function details."""
        yield Label("Function Information", classes="section-title")
        yield KeyValue("Name", data['name'])
        yield KeyValue("Address", hex(data['address']))
        yield KeyValue("Size", f"{data.get('size', 0)} bytes")
        
        # Stats
        stats = data.get('stats', {})
        if stats:
            yield Label("", classes="section")
            yield Label("Statistics", classes="section-title")
            yield KeyValue("Instructions", str(stats.get('instructions', 'N/A')))
            yield KeyValue("Complexity", str(stats.get('complexity', 'N/A')))
        
        # Actions
        yield Label("", classes="section")
        yield Label("Quick Actions", classes="section-title")
        yield Button("View Disassembly", id="view-disasm", variant="primary")
        yield Button("Analyze Function", id="analyze-func")
    
    def _get_xrefs(self, address: int) -> List[Dict]:
        """Get cross-references (stub - implement with r2)."""
        # TODO: Integrate with r2pipe
        return []
    
    def _get_import_usage(self, import_name: str) -> List[Dict]:
        """Get import usage sites (stub)."""
        # TODO: Integrate with r2pipe
        return []
```

## Testing Strategy

### Unit Tests
Create `tests/ui/widgets/test_detail_panel.py`:
- Test panel initialization
- Test update_selection with each item type
- Test KeyValue widget rendering
- Test message handling

### Integration Tests
- Select string in strings table → detail panel shows string details
- Select import in imports table → detail panel shows import details
- Select function in functions tree → detail panel shows function details
- Click "Copy String" button → string copied to clipboard
- Rapid selections → no lag or visual glitches

### Manual Testing
1. Load binary and navigate to Strings view
2. Click on a string → detail panel updates instantly
3. Verify all fields are populated correctly
4. Click action buttons → verify they work
5. Switch to Imports view
6. Click on an import → detail panel switches to import view
7. Test with binary that has no xrefs → handles gracefully

## Dependencies
- Textual widgets and message system
- r2pipe for cross-reference queries
- No new external dependencies

## Estimated Time
**23 hours total**
- Implementation: 20 hours
- Testing: 3 hours

## Success Criteria
- [ ] Detail panel displays context-specific information
- [ ] All item types supported (string, import, export, function)
- [ ] Cross-references displayed correctly
- [ ] Quick action buttons work
- [ ] Panel updates instantly on selection change (<100ms)
- [ ] Handles missing data gracefully (no crashes)
- [ ] Panel collapsible/expandable
- [ ] No memory leaks from rapid selections

## Next Steps
After completion, proceed to Subtask 5: Sidebar Enhancements to add file management and multi-binary support.
