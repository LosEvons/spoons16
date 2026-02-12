# Subtask 4: Interactive Navigation

## Objective
Add interactive features to the disassembly view, allowing users to navigate to function calls, jump targets, and cross-references.

## Scope
- Clickable addresses and function names
- Jump to definition/reference
- Back/forward navigation history
- Keyboard shortcuts for navigation

## Technical Approach

### 1. Custom Disassembly Widget (5 hours)
**Location**: `caspoon/ui/widgets/interactive_disasm.py`

Create custom Textual widget with clickable elements:

```python
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message

class InteractiveDisasmView(Static):
    """Interactive disassembly view with navigation."""
    
    current_address = reactive("0x0")
    
    class AddressClicked(Message):
        """Message sent when address is clicked."""
        def __init__(self, address: str):
            self.address = address
            super().__init__()
    
    def on_click(self, event):
        # Detect if click is on an address/function
        # Emit AddressClicked message
        pass
```

### 2. Navigation Manager (3 hours)
**Location**: `caspoon/ui/navigation/manager.py`

Manage navigation history and context:

```python
class NavigationManager:
    def __init__(self):
        self.history = []
        self.current_index = -1
        self.address_map = {}  # address -> function info
    
    def navigate_to(self, address: str):
        """Navigate to address, adding to history."""
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        self.history.append(address)
        self.current_index += 1
    
    def go_back(self):
        """Navigate back in history."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
    
    def go_forward(self):
        """Navigate forward in history."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
```

### 3. Cross-Reference Extraction (4 hours)
Enhance r2_analyzer.py to extract xrefs:

```python
def analyze_with_r2(path: str) -> Dict[str, Any]:
    # ... existing code ...
    
    # Extract cross-references for functions
    xrefs = {}
    for func in functions:
        addr = func.get('offset')
        # Get xrefs to this function
        xref_json = r2.cmd(f"axtj @ {addr}")
        xrefs[addr] = json.loads(xref_json) if xref_json.strip() else []
    
    return {
        "functions": functions,
        "xrefs": xrefs,
        # ... other data ...
    }
```

### 4. Clickable Links in UI (4 hours)
Implement clickable addresses using Rich markup:

```python
def make_address_clickable(address: str) -> Text:
    """Create clickable address text."""
    text = Text()
    text.append(address, style="link " + address)
    return text
```

Note: Textual's clickable link support is limited. May need to:
- Use buttons for navigation
- Implement custom event handling
- Or use hoverable regions with keyboard shortcuts

### 5. Keyboard Shortcuts (2 hours)
Add keyboard navigation:
- `g`: Go to address/function (open prompt)
- `Alt+Left`: Navigate back
- `Alt+Right`: Navigate forward
- `Enter` on selected address: Jump to target
- `x`: Show cross-references for current line

```python
def on_key(self, event):
    if event.key == "g":
        self.show_goto_prompt()
    elif event.key == "alt+left":
        self.navigation_manager.go_back()
    # ... other shortcuts
```

## Implementation Steps

1. **Research Textual capabilities** (2 hours)
   - Investigate clickable element support
   - Test interactive widget patterns
   - Determine feasibility of various approaches

2. **Implement NavigationManager** (3 hours)
   - Create manager class
   - Add history tracking
   - Implement back/forward logic

3. **Extract xrefs from r2** (4 hours)
   - Modify r2_analyzer.py
   - Parse xref data
   - Store in report structure

4. **Create interactive widget** (5 hours)
   - Build custom disassembly widget
   - Handle click/keyboard events
   - Integrate with navigation manager

5. **Add keyboard shortcuts** (2 hours)
   - Implement key bindings
   - Add goto address functionality
   - Test navigation flow

6. **Testing and refinement** (2 hours)
   - Test with various binaries
   - Refine UX based on usability
   - Handle edge cases

## Challenges

### Challenge 1: Textual Limitations
Textual may not support all interactive features needed.

**Solutions**:
- Use alternative approaches (keyboard-driven instead of mouse-driven)
- Implement selection-based navigation
- Use modal dialogs for "go to" functionality

### Challenge 2: Performance
Large disassembly outputs may be slow to navigate.

**Solutions**:
- Implement pagination
- Lazy load function disassembly
- Cache rendered output

### Challenge 3: Address Resolution
Resolving addresses to functions requires mapping.

**Solutions**:
- Build address->function map during analysis
- Use r2's symbol resolution
- Handle relative and absolute addresses

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
**18 hours total**
- Research: 2 hours
- Navigation manager: 3 hours
- Xref extraction: 4 hours
- Interactive widget: 5 hours
- Keyboard shortcuts: 2 hours
- Testing: 2 hours

## Success Criteria
- [ ] Users can navigate to addresses by clicking/selecting
- [ ] Back/forward navigation works correctly
- [ ] Cross-references are displayed for functions
- [ ] Keyboard shortcuts provide efficient navigation
- [ ] Navigation history is maintained across views
- [ ] Performance remains acceptable

## Next Steps
Proceed to Subtask 5: Cross-Reference Display for enhanced xref visualization.
