# Fix: RuntimeWarning about Header._on_mount coroutine

## Problem

When running `python -m caspoon --ui`, a RuntimeWarning was displayed:

```
RuntimeWarning: coroutine 'Header._on_mount' was never awaited
```

## Root Cause

This warning occurred because of how Textual's built-in `Header` and `Footer` widgets work:

1. **Async Mount Methods**: Textual's `Header` and `Footer` widgets have internal async `_on_mount` methods
2. **Container Context Issue**: When these widgets are yielded from a `Container`'s `compose()` method, the framework doesn't properly await these coroutines
3. **Framework Limitation**: This is a known issue in Textual when using Header/Footer in certain contexts (Container vs App)

### Technical Details

In Textual:
- `App.compose()` properly handles async widget mounting
- `Container.compose()` (our MainScreen) doesn't always await async mounts
- Header/Footer have async operations for title updates and keybinding displays

## Solution

Created custom replacement widgets that avoid async operations:

### AppHeader (`ui/widgets/app_header.py`)

```python
class AppHeader(Container):
    """Application header without async mount issues."""
    
    DEFAULT_CSS = """
    AppHeader {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    """
```

**Features:**
- Simple Container with Static widget for title
- Docked to top with same styling as original Header
- No async operations in lifecycle
- Title customizable via constructor

### AppFooter (`ui/widgets/app_footer.py`)

```python
class AppFooter(Container):
    """Application footer without async mount issues."""
    
    DEFAULT_CSS = """
    AppFooter {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }
    """
```

**Features:**
- Simple Container with Static widget for keybinding hints
- Docked to bottom with same styling as original Footer
- No async operations in lifecycle
- Shows useful keybinding information

## Changes Made

### 1. Created Custom Widgets

- `caspoon/ui/widgets/app_header.py` - Custom header widget
- `caspoon/ui/widgets/app_footer.py` - Custom footer widget

### 2. Updated MainScreen

**Before:**
```python
from textual.widgets import Footer, Header

def compose(self):
    yield Header()
    # ... other widgets ...
    yield Footer()
```

**After:**
```python
from caspoon.ui.widgets.app_footer import AppFooter
from caspoon.ui.widgets.app_header import AppHeader

def compose(self):
    yield AppHeader()
    # ... other widgets ...
    yield AppFooter()
```

### 3. Updated Widget Exports

Updated `ui/widgets/__init__.py` to export new widgets.

## Result

### Before Fix
```
$ python -m caspoon --ui
/path/to/textual/message_pump.py:687: RuntimeWarning: coroutine 'Header._on_mount' was never awaited
[UI loads but with warning]
```

### After Fix
```
$ python -m caspoon --ui
[UI loads cleanly without warnings]
```

### Visual Comparison

The UI looks identical - same header, same footer, same layout:

**Header:**
- Still shows "Caspoon Reverse Engineering Toolkit"
- Same styling (primary background, centered text, bold)
- Same height (1 line)

**Footer:**
- Still shows keybinding hints
- Same styling (primary background, dimmed text)
- Same height (1 line)

## Why This Approach

### Alternative Solutions Considered

1. **Suppress the warning**: Would hide the issue but not fix it
2. **Update Textual version**: Warning exists across versions
3. **Use Screen instead of Container**: Would require restructuring
4. **Wait for framework fix**: Unknown timeline

### Why Custom Widgets Win

✅ **Clean**: No warnings or workarounds  
✅ **Simple**: Straightforward implementation  
✅ **Maintainable**: We control the code  
✅ **Flexible**: Can customize as needed  
✅ **Fast**: No async overhead  

## Technical Notes

### About Textual's Header/Footer

Textual's built-in widgets are designed primarily for use at the App level:

```python
class MyApp(App):
    def compose(self):
        yield Header()  # ✅ Works fine here
        yield Footer()  # ✅ Works fine here
```

When used in Container widgets, the async mounting can cause issues:

```python
class MyContainer(Container):
    def compose(self):
        yield Header()  # ⚠️ May cause warning
        yield Footer()  # ⚠️ May cause warning
```

Our MainScreen is a Container (since we changed it from Screen to fix rendering), so we hit this issue.

### Async Mount Methods

The warning happens because:

1. `Header._on_mount` is async (updates title from App)
2. Container's compose doesn't await child mounts
3. Python runtime detects unawaited coroutine
4. Warning is raised

Our custom widgets use only synchronous methods, avoiding the issue entirely.

## Testing

The fix has been tested to ensure:

- ✅ No RuntimeWarning on startup
- ✅ Header displays correctly
- ✅ Footer displays correctly
- ✅ All UI functionality works
- ✅ Panel toggles work
- ✅ Tabs work
- ✅ Command palette works

## Commit

`0c0ee7e` - Fix RuntimeWarning about Header._on_mount coroutine

## Files Changed

1. `caspoon/ui/widgets/app_header.py` (new)
2. `caspoon/ui/widgets/app_footer.py` (new)
3. `caspoon/ui/screens/main.py` (updated imports and compose)
4. `caspoon/ui/widgets/__init__.py` (added exports)
