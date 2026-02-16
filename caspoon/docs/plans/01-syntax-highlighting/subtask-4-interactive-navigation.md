# Subtask 4: Interactive Navigation

**Status**: ⏸️ NOT STARTED  
**Dependencies**: ✅ Subtasks 1-3 complete, ✅ Plan 4 (TUI Redesign) complete  
**Prerequisites**: New reactive TUI architecture with command palette, multi-panel layout, and async workers

## Objective
Add interactive features to the disassembly view, allowing users to navigate to function calls, jump targets, and cross-references.

## Scope
- Clickable/selectable addresses and function names
- Jump to definition/reference
- Back/forward navigation history
- Keyboard shortcuts for navigation
- Integration with new command palette and panel system

## Technical Approach

### 1. Enhanced R2 Analysis View with Selection (4 hours)
**Location**: `caspoon/ui/views/r2_view.py`

Enhance the existing R2View to support selection and navigation:

```python
from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.messages import JumpToAddress

class R2View(InteractiveView[dict | None]):
    """Interactive disassembly view with navigation support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._highlighter = AsmHighlighter()
        self._address_map = {}  # Maps line numbers to addresses
    
    def on_key(self, event):
        """Handle keyboard navigation."""
        if event.key == "enter":
            # Jump to selected address
            selected_line = self.get_selected_line()
            address = self._address_map.get(selected_line)
            if address:
                self.post_message(JumpToAddress(address))
        elif event.key == "x":
            # Show cross-references for current line
            self.show_xrefs()
```

### 2. Navigation State Management (3 hours)
**Location**: `caspoon/ui/core/state.py`

Extend AppState with navigation history:

```python
class AppState:
    # Existing reactive properties...
    
    # Navigation history
    navigation_history: Reactive[list[str]] = Reactive([])
    current_nav_index: Reactive[int] = Reactive(-1)
    
    def navigate_to(self, address: str):
        """Navigate to address, adding to history."""
        if self.current_nav_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.current_nav_index + 1]
        self.navigation_history.append(address)
        self.current_nav_index += 1
    
    def go_back(self) -> str | None:
        """Navigate back in history."""
        if self.current_nav_index > 0:
            self.current_nav_index -= 1
            return self.navigation_history[self.current_nav_index]
        return None
    
    def go_forward(self) -> str | None:
        """Navigate forward in history."""
        if self.current_nav_index < len(self.navigation_history) - 1:
            self.current_nav_index += 1
            return self.navigation_history[self.current_nav_index]
        return None
```

### 3. Cross-Reference Extraction (4 hours)
**Location**: `caspoon/backends/r2_analyzer.py`

Enhance r2 backend to extract xrefs:

```python
def analyze_with_r2(path: str) -> Dict[str, Any]:
    # ... existing analysis code ...
    
    # Extract cross-references for all functions
    xrefs = {}
    for func in functions:
        addr = func.get('offset')
        
        # Get xrefs TO this function (callers)
        xref_to_json = r2.cmd(f"axtj @ {addr}")
        xrefs_to = json.loads(xref_to_json) if xref_to_json.strip() else []
        
        # Get xrefs FROM this function (callees)
        xref_from_json = r2.cmd(f"axfj @ {addr}")
        xrefs_from = json.loads(xref_from_json) if xref_from_json.strip() else []
        
        xrefs[hex(addr)] = {
            'callers': xrefs_to,
            'callees': xrefs_from
        }
    
    return {
        "functions": functions,
        "xrefs": xrefs,
        # ... other data ...
    }
```

### 4. Function Explorer Integration (3 hours)
**Location**: `caspoon/ui/widgets/function_explorer.py`

Enhance existing FunctionExplorer widget to emit navigation messages:

```python
# The FunctionExplorer already exists, enhance it:

def on_tree_node_selected(self, event):
    """Handle function selection in tree."""
    node = event.node
    if hasattr(node.data, 'address'):
        # Post message to navigate to function
        self.post_message(JumpToAddress(node.data.address))
```

### 5. Command Palette Integration (2 hours)
**Location**: `caspoon/ui/widgets/command_palette.py`

Add "Go to Address" and "Show XRefs" commands to existing palette:

```python
# Add new commands to the existing command palette:
Command(
    id="goto_address",
    label="Go to Address",
    description="Jump to a specific address",
    action=lambda: self.app.show_goto_dialog(),
    category="Navigation"
),
Command(
    id="show_xrefs",
    label="Show Cross-References",
    description="Display cross-references for current address",
    action=lambda: self.app.show_xrefs_panel(),
    category="Navigation"
),
Command(
    id="nav_back",
    label="Navigate Back",
    description="Go back in navigation history",
    action=lambda: self.app.state.go_back(),
    category="Navigation",
    keys=["Alt+Left"]
),
Command(
    id="nav_forward",
    label="Navigate Forward",
    description="Go forward in navigation history",
    action=lambda: self.app.state.go_forward(),
    category="Navigation",
    keys=["Alt+Right"]
),
```

### 6. Details Panel Enhancement (2 hours)
**Location**: `caspoon/ui/widgets/details_panel.py`

Use existing details panel to show xrefs:

```python
def show_xrefs(self, address: str, xref_data: dict):
    """Display cross-references in details panel."""
    table = Table(title=f"Cross-References for {address}")
    table.add_column("Type")
    table.add_column("Address")
    table.add_column("Function")
    
    for caller in xref_data.get('callers', []):
        table.add_row("Called from", caller['from'], caller.get('fcn_name', ''))
    
    for callee in xref_data.get('callees', []):
        table.add_row("Calls", callee['to'], callee.get('fcn_name', ''))
    
    self.update(table)
```

## Implementation Steps

1. **Extend AppState with navigation** (2 hours)
   - Add navigation_history and current_nav_index to AppState
   - Implement navigate_to, go_back, go_forward methods
   - Add reactive watchers for navigation state changes

2. **Enhance R2 backend for xrefs** (4 hours)
   - Modify r2_analyzer.py to extract xrefs (to/from)
   - Parse xref data from radare2
   - Store in ExecutableReport.raw_backend_data

3. **Make R2View interactive** (4 hours)
   - Convert R2View to InteractiveView
   - Add address_map to track line->address mapping
   - Handle Enter key to jump to addresses
   - Handle 'x' key to show xrefs
   - Emit JumpToAddress messages

4. **Enhance FunctionExplorer** (2 hours)
   - Emit JumpToAddress when function is selected
   - Integrate with navigation history

5. **Add navigation commands to palette** (2 hours)
   - Add "Go to Address" command with dialog
   - Add "Show XRefs" command
   - Add navigation back/forward commands
   - Bind Alt+Left/Right shortcuts

6. **Display xrefs in details panel** (2 hours)
   - Create xref display formatter
   - Show callers and callees in table format
   - Make xref entries clickable/selectable

7. **Testing and refinement** (2 hours)
   - Test with various binaries
   - Test navigation flow
   - Test with nested calls
   - Handle edge cases (no xrefs, invalid addresses)

## Integration with New TUI

The new reactive TUI architecture (Plan 4) provides several advantages:

### Existing Infrastructure to Leverage
✅ **AppState**: Centralized reactive state management - perfect for navigation history  
✅ **Message System**: `JumpToAddress` message already defined in `ui/core/messages.py`  
✅ **Command Palette**: Can add navigation commands (Ctrl+P → type "goto")  
✅ **Details Panel**: Already exists for showing contextual info - perfect for xrefs  
✅ **InteractiveView Base**: Already supports selection and keyboard navigation  
✅ **Function Explorer**: Sidebar tree already exists - just needs to emit navigation messages

### Architecture Alignment
- Use **reactive properties** for navigation state
- Use **message passing** for navigation events
- Use **async workers** if xref extraction is slow
- Integrate with **command palette** for keyboard-driven workflow

## Challenges and Solutions

### Challenge 1: Textual Selection Model
**Status**: ✅ RESOLVED - Plan 4 implemented InteractiveView base class with selection support

**Original Challenge**: Textual may not support all interactive features needed.

**Solution**: The new TUI already provides:
- InteractiveView with built-in selection
- Keyboard-driven navigation (arrow keys, enter)
- Message-based architecture for events

### Challenge 2: Performance
**Status**: ⚠️ TO ADDRESS - Consider for subtask 6

**Challenge**: Large disassembly outputs may be slow to navigate.

**Solutions**:
- Leverage existing MAX_DISASM_OPS limits in r2_view
- Use async workers if xref extraction is slow
- Cache xref data in AppState
- Consider pagination if needed

### Challenge 3: Address Resolution
**Status**: ✅ PARTIALLY SOLVED - r2 backend provides symbols

**Challenge**: Resolving addresses to functions requires mapping.

**Solutions**:
- Build address->function map during analysis
- Use r2's symbol resolution (already available)
- Store in raw_backend_data for quick lookup
- Handle both relative and absolute addresses

### Challenge 4: Cross-Reference Data Model
**Status**: ⏸️ TO DESIGN

**Challenge**: Need to decide how to store and access xref data efficiently.

**Options**:
1. Store in ExecutableReport.raw_backend_data['r2']['xrefs']
2. Create dedicated xref cache in AppState
3. Fetch on-demand from r2 (slower but less memory)

**Recommendation**: Option 1 (store in raw_backend_data) with Option 2 (AppState cache) for frequently accessed xrefs.

## Testing Strategy

### Manual Testing
1. Load binary with multiple functions
2. Click/select an address
3. Verify navigation to that address
4. Use back/forward navigation
5. Test keyboard shortcuts

### Integration Tests
- Test navigation between functions
- Verify xref display
- Test history management

## Estimated Time
**18 hours total** → **16 hours revised** (leveraging new TUI infrastructure)
- Extend AppState: 2 hours
- R2 backend xrefs: 4 hours
- Make R2View interactive: 4 hours (was 5, now easier with InteractiveView)
- Enhance FunctionExplorer: 2 hours (was part of widget creation)
- Command palette integration: 2 hours (was part of shortcuts)
- Details panel xrefs: 2 hours (replaces custom xref panel)
- Testing: 2 hours (was 2, unchanged)

## Success Criteria
- [ ] Users can navigate to addresses by pressing Enter on selected line
- [ ] Back/forward navigation works with Alt+Left/Alt+Right
- [ ] Cross-references are displayed in details panel
- [ ] Keyboard shortcuts provide efficient navigation
- [ ] Navigation history is maintained in AppState
- [ ] Function explorer selection navigates to function
- [ ] Command palette includes navigation commands
- [ ] Performance remains acceptable

## Dependencies

### Completed Prerequisites
✅ Plan 4 (TUI Redesign) - Provides reactive architecture  
✅ Subtasks 1-3 - Syntax highlighting with architecture support  
✅ AppState with reactive properties  
✅ Message system with JumpToAddress  
✅ InteractiveView base class  
✅ Command palette (Ctrl+P)  
✅ Details panel widget  
✅ Function explorer widget

### New Components Required
⏸️ Navigation history in AppState  
⏸️ Xref extraction in r2_analyzer.py  
⏸️ Interactive mode for R2View  
⏸️ Navigation commands in palette  
⏸️ Xref display in details panel

## Next Steps
After completion, proceed to Subtask 5: Cross-Reference Display (which may be partially completed by this subtask's details panel work).
