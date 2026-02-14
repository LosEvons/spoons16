# TUI Architecture Quick Reference

**Companion to**: [TUI Architecture Redesign](./tui-architecture-redesign.md)

This is a quick reference for developers working with the new TUI architecture.

---

## Widget Base Classes Decision Tree

```
                  Need to display data?
                          │
                   ┌──────┴──────┐
                   │             │
                  YES            NO
                   │             │
                   ▼             ▼
         Use BaseView[T]    Use Static/Container
                   │
         ┌─────────┴─────────┐
         │                   │
    Interactive?         Display only?
         │                   │
        YES                 NO
         │                   │
         ▼                   ▼
   InteractiveView      BaseView[T]
         │                 done!
         │
    ┌────┴─────┐
    │          │
Hierarchical? Tabular?
    │          │
   YES        YES
    │          │
    ▼          ▼
TreeView   TableView
```

## Class Hierarchy

```
textual.widgets.Static
    │
    ├─ BaseView[T]
    │    ├─ InteractiveView[T]
    │    │    ├─ TreeView[T]
    │    │    │    └─ FunctionExplorer
    │    │    │    └─ SectionExplorer
    │    │    │
    │    │    ├─ TableView[T]
    │    │    │    └─ FilterableTable
    │    │    │
    │    │    └─ SearchableList
    │    │
    │    ├─ OverviewView
    │    ├─ ProtectionsView
    │    ├─ StringsView
    │    └─ DisassemblyView
    │
    └─ (other non-data widgets)
         ├─ StatusBar
         ├─ CommandPalette
         └─ ProgressView
```

---

## State Management Patterns

### Pattern 1: View Subscribes to State

```python
class MyView(BaseView[DataType]):
    def on_mount(self) -> None:
        # Subscribe to state changes
        app: CaspoonApp = self.app
        app.state.some_data.watch(self, "_on_data_changed")
    
    def _on_data_changed(self, old, new) -> None:
        self.data = new  # Triggers render_content()
    
    def render_content(self, data: DataType) -> None:
        # Render UI with data
        self.update(...)
```

### Pattern 2: Action → State → View Update

```python
# 1. User action
def on_button_clicked(self):
    self.post_message(LoadBinary("/path/to/binary"))

# 2. App handles action
def on_load_binary(self, action: LoadBinary):
    self.run_worker(self._analyze_binary(action.path))

# 3. Worker updates state
async def _analyze_binary(self, path: str):
    result = await analyze(path)
    self.state.analysis_results = result  # ← State update

# 4. Views reactively update
# (Happens automatically via watch())
```

### Pattern 3: Inter-Widget Communication

```python
# Widget A posts message
self.post_message(SelectFunction("main"))

# Widget B handles message (if it cares)
def on_select_function(self, msg: SelectFunction):
    self.highlight_function(msg.function_name)
```

---

## Command Registration Pattern

```python
# In CaspoonApp.on_mount() or plugin registration
def register_commands(self):
    self.action_registry.register(
        action_id="my_action",
        name="My Action",
        handler=self.do_my_action,
        description="Does something useful",
        keybinding="ctrl+shift+m",
        category="MyPlugin"
    )

def do_my_action(self):
    # Implementation
    pass
```

---

## Screen Navigation Patterns

```python
# Push screen (adds to stack)
self.app.push_screen(SettingsScreen())

# Push and wait for result (modal)
result = await self.app.push_screen_wait(ConfirmDialog("Are you sure?"))
if result:
    # User confirmed
    pass

# Pop screen (go back)
self.app.pop_screen()

# Replace screen (don't keep in history)
self.app.switch_screen(MainScreen())
```

---

## Testing Patterns

### Unit Test a Widget

```python
def test_my_widget():
    widget = MyWidget()
    widget.data = test_data
    
    # Assert on internal state
    assert widget._computed_value == expected
    
    # Assert on rendered content (if needed)
    # (Usually better to test behavior, not rendering)
```

### Integration Test with Pilot

```python
@pytest.mark.asyncio
async def test_user_workflow():
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        # Simulate user actions
        await pilot.press("ctrl+p")  # Open command palette
        await pilot.press("a", "n", "a")  # Type "ana"
        await pilot.press("enter")  # Execute command
        
        # Assert on state
        assert pilot.app.state.ui_state.is_analyzing
        
        # Wait for async operation
        await pilot.pause()
        
        # Assert final state
        assert not pilot.app.state.ui_state.is_analyzing
```

### Mock Async Worker

```python
@pytest.mark.asyncio
async def test_with_mock_worker():
    app = CaspoonApp()
    
    with patch('caspoon.ui.app.ReconRunner') as mock:
        mock.return_value.run = AsyncMock(return_value=mock_report)
        
        async with app.run_test() as pilot:
            app.post_message(LoadBinary("/test/file"))
            await pilot.pause()
            
            assert app.state.binary_info.path == "/test/file"
```

---

## Keybindings Reference

### Global Keybindings

| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+P` | Command Palette | Open command palette |
| `Ctrl+O` | Analyze Binary | Open file dialog |
| `Ctrl+R` | Reload | Re-analyze current binary |
| `Ctrl+S` | Save Report | Export report |
| `Ctrl+Q` | Quit | Exit application |
| `F1` | Help | Show help screen |
| `Ctrl+,` | Settings | Open settings |

### Navigation

| Key | Action | Description |
|-----|--------|-------------|
| `Alt+1` | Overview | Go to Overview tab |
| `Alt+2` | Functions | Go to Functions tab |
| `Alt+3` | Strings | Go to Strings tab |
| `Alt+4` | Imports | Go to Imports/Exports tab |
| `Alt+5` | Disassembly | Go to Disassembly tab |
| `Alt+6` | Hex | Go to Hex view |
| `Ctrl+Tab` | Next Tab | Switch to next tab |
| `Ctrl+Shift+Tab` | Previous Tab | Switch to previous tab |

### Panels

| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+B` | Toggle Sidebar | Show/hide sidebar |
| `Ctrl+D` | Toggle Details | Show/hide details panel |
| `Ctrl+J` | Toggle Bottom | Show/hide bottom panel |

### Within Views (Interactive)

| Key | Action | Description |
|-----|--------|-------------|
| `↑` / `k` | Move Up | Select previous item |
| `↓` / `j` | Move Down | Select next item |
| `Enter` | Select | Activate selected item |
| `/` | Filter | Focus filter input |
| `Esc` | Clear Filter | Clear filter/go back |
| `Ctrl+F` | Search | Search in view |
| `Ctrl+G` | Jump to Address | Jump to specific address |

---

## Message Types Reference

### User Actions

```python
LoadBinary(path: str)           # Load and analyze a binary
SelectFunction(name: str)       # Select a function
JumpToAddress(address: int)     # Jump to address
UpdateFilter(text: str)         # Update filter text
TogglePanel(panel: str)         # Toggle panel visibility
```

### System Events

```python
WorkerStarted(name: str)
WorkerProgress(percent: float, message: str)
WorkerComplete(result: Any)
WorkerError(error: str)
```

### State Events

```python
StateChanged[BinaryInfo]
StateChanged[AnalysisResults]
StateChanged[UIState]
```

---

## Component Lifecycle

```
Widget Created
    │
    ├─ __init__()
    │    └─ Initialize instance variables
    │
    ├─ compose()  (if Container)
    │    └─ Yield child widgets
    │
    ├─ on_mount()
    │    ├─ Subscribe to state
    │    ├─ Setup watchers
    │    └─ Initial data load
    │
    ├─ (User interactions)
    │    ├─ on_key()
    │    ├─ on_click()
    │    └─ action_*()
    │
    ├─ watch_*()
    │    └─ React to property changes
    │
    ├─ on_show() / on_hide()
    │    └─ Tab becomes visible/hidden
    │
    └─ on_unmount()
         └─ Cleanup
```

---

## File Organization

```
Want to create...                 Put it in...
────────────────                  ────────────
New base widget class      →     ui/core/base.py
State data structure       →     ui/core/state.py
Action/message type        →     ui/core/actions.py
Command registration       →     ui/core/actions_registry.py

Reusable widget            →     ui/widgets/standard.py
Caspoon-specific widget    →     ui/widgets/custom.py
Command palette            →     ui/widgets/command_palette.py

New screen                 →     ui/screens/
Modal dialog               →     ui/dialogs/

Analysis view              →     ui/views/
Syntax highlighting        →     ui/syntax/
```

---

## Common Gotchas

### ❌ Don't: Direct DOM manipulation from outside widget

```python
# BAD
view = self.query_one("#my_view")
view.update("new content")
```

### ✅ Do: Update state, let views react

```python
# GOOD
self.app.state.my_data = new_data
# View automatically updates via reactive watch
```

---

### ❌ Don't: Block the UI thread

```python
# BAD
def on_button_clicked(self):
    result = long_running_operation()  # Freezes UI!
    self.display(result)
```

### ✅ Do: Use async workers

```python
# GOOD
def on_button_clicked(self):
    self.run_worker(self._long_operation())

async def _long_operation(self):
    result = await long_running_operation()
    self.app.state.result = result
```

---

### ❌ Don't: Tight coupling between widgets

```python
# BAD
class WidgetA:
    def update_widget_b(self):
        widget_b = self.app.query_one("#widget_b")
        widget_b.do_something()
```

### ✅ Do: Use messages for communication

```python
# GOOD
class WidgetA:
    def something_happened(self):
        self.post_message(SomethingHappened())

class WidgetB:
    def on_something_happened(self, msg):
        self.do_something()
```

---

## Debugging Tips

### Enable Textual Dev Console

```bash
textual console
# In another terminal:
python -m caspoon.ui.app
```

### Log to console

```python
self.log("Debug message")
self.log.info("Info message")
self.log.error("Error message")
```

### Inspect widget tree

```python
# Press Ctrl+\\ to toggle DOM inspector
# Or in code:
self.app.tree_view()
```

### Breakpoint in async worker

```python
async def _analyze_binary(self, path: str):
    import pdb; pdb.set_trace()
    result = await analyze(path)
```

---

## Performance Tips

### Limit rendered items

```python
# Don't render 10,000 items at once
def render_content(self, data: list):
    # Only render visible items + buffer
    visible = data[:1000]
    if len(data) > 1000:
        self.update(f"Showing 1000 of {len(data)} items")
```

### Debounce filter updates

```python
from textual.reactive import reactive

class MyView(BaseView):
    filter_text: reactive[str] = reactive("")
    
    def watch_filter_text(self, text: str):
        # Debounce filter to avoid re-rendering on every keystroke
        self.set_timer(0.3, lambda: self.apply_filter(text))
```

### Use virtual scrolling for large lists

```python
# Use DataTable widget for large datasets
# It only renders visible rows
from textual.widgets import DataTable
```

---

## Migration Checklist

Migrating an old view to new architecture:

- [ ] Identify what state the view needs
- [ ] Create reactive data type if needed (in `state.py`)
- [ ] Change base class: `Static` → `BaseView[T]` or subclass
- [ ] Rename `update_data()` → `render_content()`
- [ ] Add `on_mount()` to subscribe to state
- [ ] Update tests to use new interface
- [ ] Remove direct `query_one()` calls to this view from app
- [ ] Update app to update state instead of calling view methods
- [ ] Test with both new and old views to ensure compatibility
- [ ] Update documentation

---

## Plugin Development Template

```python
# my_plugin.py

from caspoon.ui.core.base import BaseView
from caspoon.ui.core.actions import Action


class MyPluginView(BaseView[MyDataType]):
    """My custom view."""
    
    def render_content(self, data: MyDataType) -> None:
        # Render UI
        pass


class MyPluginAction(Action):
    """Custom action."""
    def __init__(self, param: str):
        super().__init__()
        self.param = param


def register_plugin(app: CaspoonApp):
    """Register plugin with app."""
    # Register commands
    app.action_registry.register(
        "my_plugin_action",
        "My Plugin Action",
        lambda: app.do_my_thing(),
        description="Does something",
        keybinding="ctrl+shift+p",
        category="MyPlugin"
    )
    
    # Register views (if needed)
    # Add to tab or sidebar
    
    # Register state (if needed)
    app.state.my_plugin_data = MyPluginData()


# In app startup:
# from my_plugin import register_plugin
# register_plugin(app)
```

---

## Resources

- **Textual Docs**: https://textual.textualize.io/
- **Rich Docs**: https://rich.readthedocs.io/
- **Full Architecture**: [TUI Architecture Redesign](./tui-architecture-redesign.md)
- **Caspoon Core**: [Core Architecture](../reference/core-architecture.md)

---

**Last Updated**: 2024
