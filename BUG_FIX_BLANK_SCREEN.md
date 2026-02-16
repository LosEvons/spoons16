# Bug Fix: Blank Screen and Tab ID Error

## Problem

When running `python -m caspoon --ui`, users experienced:

1. **Blank screen on startup** - No content visible
2. **Tab navigation error** when pressing Tab multiple times:
   ```
   ValueError: No Tab with id '--content-tab-overview-tab'
   ```
3. Command palette worked but showed only default options

## Root Cause

The issue was in `ui/app.py` and `ui/screens/main.py` where widgets were being constructed using the internal `_add_child()` method instead of proper Textual composition patterns.

### What was wrong:

```python
# WRONG - Using internal _add_child() method
content_container = Container(id="content")
input_widget = Input(...)
content_container._add_child(input_widget)  # ❌ Internal method

tabs = TabbedContent(id="tabs")
tab1 = TabPane("Overview", id="overview-tab")
tab1._add_child(ScrollableContainer(...))  # ❌ Internal method
tabs._add_child(tab1)  # ❌ Internal method
```

This approach:
- Bypassed Textual's proper widget lifecycle
- Prevented widgets from being mounted correctly
- Caused tab IDs to not be registered properly
- Resulted in blank screen (content not rendered)

## Solution

Replaced manual widget construction with proper Textual composition patterns:

### 1. Simplified CaspoonApp.compose()

**Before:**
```python
def compose(self) -> ComposeResult:
    content_container = Container(id="content")
    content_container._add_child(Input(...))
    # ... manual construction
    yield MainScreen(content_container)
```

**After:**
```python
def compose(self) -> ComposeResult:
    yield MainScreen()  # Let MainScreen compose its own content
    yield CommandPalette(...)
```

### 2. MainScreen composes its own content

**Before:**
```python
def __init__(self, content_area: Container, **kwargs):
    super().__init__(**kwargs)
    self._content_area = content_area

def compose(self):
    yield self._content_area  # Pre-built container
```

**After:**
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)

def compose(self):
    yield Header()
    yield Sidebar(id="sidebar")
    
    # Proper composition with context managers
    with Container(id="content"):
        yield Input(placeholder="...", id="path_input")
        
        with TabbedContent(id="tabs"):
            with TabPane("Overview", id="overview-tab"):
                yield ScrollableContainer(OverviewView(...))
            # ... more tabs
    
    yield DetailsPanel(id="details")
    yield Console(id="console")
    yield Footer()
```

### 3. Fixed tab ID bindings

**Before:**
```python
Binding("1", "switch_tab('overview')", ...),  # ❌ Wrong ID
```

**After:**
```python
Binding("1", "switch_tab('overview-tab')", ...),  # ✓ Correct ID
```

## How Textual Composition Works

Textual widgets must be composed using one of these patterns:

1. **Direct yield:**
   ```python
   def compose(self):
       yield Widget()
   ```

2. **Context manager (with statement):**
   ```python
   def compose(self):
       with Container():
           yield Widget()
   ```

3. **Never use internal methods:**
   ```python
   # ❌ WRONG
   container._add_child(widget)
   
   # ✓ CORRECT
   with container:
       yield widget
   ```

## Testing

After the fix:
- ✅ No `_add_child()` usage in main UI files
- ✅ Tab IDs are consistent throughout
- ✅ Proper Textual composition pattern
- ✅ Widgets will be properly mounted and rendered
- ✅ Tab navigation will work correctly

## Files Changed

- `caspoon/ui/app.py` - Simplified compose(), fixed tab bindings
- `caspoon/ui/screens/main.py` - Proper composition with context managers

## Verification

Run the UI:
```bash
python -m caspoon --ui
```

Expected behavior:
1. UI shows input field and tabs immediately (no blank screen)
2. Overview tab is visible by default
3. Pressing Tab navigates between tabs without error
4. Number keys (1-5) switch to specific tabs
5. Command palette (Ctrl+P) shows all registered commands
