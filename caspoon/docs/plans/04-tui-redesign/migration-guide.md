# View Migration Guide: Static → BaseView

## Overview

This guide documents the pattern for migrating Caspoon TUI views from the old `Static` widget pattern with manual `update_data()` calls to the new reactive `BaseView` architecture with centralized `AppState` management.

This pattern was validated with OverviewView and ProtectionsView in Subtask 3. Use this guide as a reference when migrating remaining views (StringsView, ImportsExportsView, R2View, etc.) in Subtask 4.

## Why Migrate?

**Old Pattern Problems:**
- Manual update propagation (calling `update_data()` on every view)
- Tight coupling between app and views
- No single source of truth
- Difficult to test in isolation
- Views can't react to state changes from other sources

**New Pattern Benefits:**
- Automatic reactive updates via AppState
- Loose coupling (views subscribe to state)
- Single source of truth (AppState)
- Easy to test (mock AppState)
- Views update automatically when relevant state changes

## Migration Pattern

### Step-by-Step Checklist

For each view you're migrating, follow these steps:

- [ ] **Step 1:** Update imports
- [ ] **Step 2:** Change class inheritance
- [ ] **Step 3:** Add `on_mount()` subscription
- [ ] **Step 4:** Add state change handler
- [ ] **Step 5:** Rename render method to `render_content()`
- [ ] **Step 6:** Update render method signature
- [ ] **Step 7:** Add backward compatibility shim
- [ ] **Step 8:** Write unit tests
- [ ] **Step 9:** Write integration tests
- [ ] **Step 10:** Manual testing

### Detailed Steps

#### Step 1: Update Imports

**Before:**
```python
from rich.table import Table
from textual.widgets import Static

from caspoon.core.models import ExecutableReport
```

**After:**
```python
import logging

from rich.table import Table
from rich.panel import Panel

from caspoon.core.models import ExecutableReport
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import BinaryInfo  # Or appropriate model type

logger = logging.getLogger(__name__)
```

**Key Changes:**
- Add `logging` import
- Keep `ExecutableReport` for backward compatibility
- Import `BaseView` from `caspoon.ui.core.base`
- Import appropriate model type from `caspoon.ui.core.models`
- Remove `Static` import
- Optionally add `Panel` for better visual formatting

#### Step 2: Change Class Inheritance

**Before:**
```python
class MyView(Static):
    """My view documentation."""
    
    def update_data(self, report: ExecutableReport) -> None:
        # ... old rendering logic ...
```

**After:**
```python
class MyView(BaseView[DataType]):
    """My view documentation.
    
    Automatically updates when AppState.property_name changes.
    """
    
    # update_data() removed (will add back as shim later)
```

**Key Changes:**
- Inherit from `BaseView[T]` instead of `Static`
- `T` is the type of data this view displays:
  - `BinaryInfo` for file metadata
  - `dict` for protections, simple key-value data
  - `list[str]` for strings
  - `AnalysisResults` for complete analysis data
- Update docstring to mention reactive updates

#### Step 3: Add `on_mount()` Subscription

**Pattern:**
```python
def on_mount(self) -> None:
    """Subscribe to state updates when view is mounted.
    
    This is called when the view is added to the app. It sets up
    the reactive subscription to AppState property changes.
    """
    app = self.app
    if hasattr(app, 'state'):
        # Subscribe to the relevant AppState property
        app.state.subscribe("property_name", self._on_property_changed)
        logger.debug(f"{self.__class__.__name__} subscribed to property_name updates")
```

**Property Name Mapping:**
| View Type | Subscribe To | Data Type |
|-----------|-------------|-----------|
| File info (overview) | `"binary_info"` | `BinaryInfo` |
| Protections | `"analysis_results"` | `AnalysisResults` (extract protections) |
| Strings | `"analysis_results"` | `AnalysisResults` (extract strings) |
| Imports/Exports | `"analysis_results"` | `AnalysisResults` (extract imports/exports) |
| Disassembly | `"analysis_results"` | `AnalysisResults` (extract disassembly) |

**Key Points:**
- Always check `hasattr(app, 'state')` for defensive coding
- Use a private method name like `_on_property_changed`
- Add debug logging to help troubleshooting

#### Step 4: Add State Change Handler

**Pattern:**
```python
def _on_property_changed(self, new_value: DataType | None) -> None:
    """Handle state property changes.
    
    Args:
        new_value: New property value (or None if cleared)
    """
    # Option A: Direct assignment (for simple cases)
    self.data = new_value
    
    # Option B: Extract relevant data (for complex cases)
    if new_value and hasattr(new_value, 'relevant_field'):
        self.data = new_value.relevant_field
    else:
        self.data = default_value  # e.g., [] or {}
```

**Examples:**

**Direct Assignment (OverviewView):**
```python
def _on_binary_info_changed(self, new_value: BinaryInfo | None) -> None:
    """Update view when binary info changes."""
    self.data = new_value
```

**Extraction (ProtectionsView):**
```python
def _on_results_changed(self, new_value: AnalysisResults | None) -> None:
    """Extract protections from analysis results."""
    if new_value and new_value.protections:
        self.data = new_value.protections
    else:
        self.data = {}
```

**Key Points:**
- Setting `self.data` triggers `render_content()` via BaseView's `watch_data()`
- Handle None values gracefully
- Extract only the data your view needs

#### Step 5: Rename Render Method

**Before:**
```python
def update_data(self, report: ExecutableReport) -> None:
    """Update the view with new report data."""
    table = self._build_table(report)
    self.update(table)
```

**After:**
```python
def render_content(self, data: DataType) -> None:
    """Render the view content with the given data.
    
    Args:
        data: The data to render
    """
    table = self._build_table(data)
    
    # Optionally wrap in Panel for better visual separation
    panel = Panel(
        table,
        title="[bold]View Title[/bold]",
        border_style="blue",
        padding=(1, 2)
    )
    
    self.update(panel)
```

**Key Changes:**
- Method name: `update_data()` → `render_content()`
- Parameter type: `ExecutableReport` → specific data type (`BinaryInfo`, `dict`, etc.)
- Still call `self.update()` with a Rich renderable
- Consider adding Panel wrapper for consistent styling

#### Step 6: Update Rendering Logic

**Before (extracts from report):**
```python
def _build_table(self, report: ExecutableReport) -> Table:
    table = Table(title="Overview")
    table.add_column("Field")
    table.add_column("Value")
    
    table.add_row("Path", report.path)
    table.add_row("Arch", report.arch or "unknown")
    table.add_row("Bits", str(report.bits or "unknown"))
    
    return table
```

**After (uses typed data parameter):**
```python
def _build_table(self, data: BinaryInfo) -> Table:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", justify="right")
    table.add_column(style="white")
    
    table.add_row("Path:", data.path)
    table.add_row("Architecture:", data.architecture)
    table.add_row("Bits:", f"{data.bits}-bit" if data.bits else "unknown")
    
    return table
```

**Key Changes:**
- Use `data` parameter instead of extracting from `report`
- Field names match the new model (e.g., `architecture` not `arch`)
- Add color coding and formatting improvements
- Handle missing/None values gracefully

#### Step 7: Add Backward Compatibility Shim

Keep the old `update_data()` method during the migration period to ensure non-migrated code still works:

```python
def update_data(self, report: ExecutableReport) -> None:
    """Legacy compatibility shim for old-style view updates.

    This method maintains backward compatibility with the old update pattern.
    New code should update AppState instead, which will trigger reactive updates.

    Args:
        report: ExecutableReport containing analysis results
    """
    logger.warning(
        f"{self.__class__.__name__}.update_data() is deprecated. "
        "Use app.state.property_name = ... for reactive updates."
    )
    
    # Still works - use old rendering path
    # Copy the old implementation here
    table = Table(title="View Title")
    # ... old table building logic ...
    self.update(table)
```

**Key Points:**
- Keep the old method signature exactly
- Log a deprecation warning
- Maintain old behavior (direct rendering)
- Remove this method once all views are migrated

#### Step 8: Write Unit Tests

Create `test_myview.py` in `caspoon/tests/unit/ui/views/`:

```python
"""Unit tests for MyView migration to BaseView architecture."""

import pytest
from textual.app import App, ComposeResult

from caspoon.ui.views.myview import MyView
from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import DataType
from caspoon.ui.core.state import AppState


class TestMyViewInheritance:
    """Test proper inheritance."""
    
    def test_inherits_baseview(self):
        assert issubclass(MyView, BaseView)
    
    def test_has_render_content(self):
        assert hasattr(MyView, "render_content")
        assert callable(MyView.render_content)


class TestMyViewInitialization:
    """Test initialization."""
    
    def test_initializes(self):
        view = MyView()
        assert view is not None


class TestMyViewSubscription:
    """Test state subscription."""
    
    def test_subscribes_on_mount(self):
        # Create test app with state
        class TestApp(App):
            def __init__(self):
                super().__init__()
                self.state = AppState()
            
            def compose(self) -> ComposeResult:
                yield MyView()
        
        app = TestApp()
        view = MyView()
        view._app = app
        
        # Mock subscribe to verify it's called
        called = False
        def mock_subscribe(prop, callback):
            nonlocal called
            called = True
        
        app.state.subscribe = mock_subscribe
        view.on_mount()
        
        assert called


class TestMyViewRendering:
    """Test rendering."""
    
    def test_renders_data(self, mock_data):
        view = MyView()
        view.render_content(mock_data)
        # If we got here, render succeeded


class TestMyViewBackwardCompat:
    """Test backward compatibility."""
    
    def test_has_update_data(self):
        view = MyView()
        assert hasattr(view, "update_data")
```

**Minimum Test Coverage:**
- Inheritance check
- Initialization
- Subscription setup
- Basic rendering
- Backward compatibility

**Target: >85% coverage**

#### Step 9: Write Integration Tests

Add tests to `test_core_views_integration.py`:

```python
@pytest.mark.asyncio
async def test_myview_updates_on_analysis(self, mock_report):
    """Verify MyView updates when analysis completes."""
    app = CaspoonApp()
    
    async with app.run_test() as pilot:
        myview = app.query_one("#myview", MyView)
        
        # Update state
        app.state.update_from_report(mock_report)
        await pilot.pause()
        
        # Verify view updated
        assert myview.data is not None
```

#### Step 10: Manual Testing

Manual test checklist:

```bash
# Launch TUI
python -m caspoon.ui

# Test cases:
1. Load a known binary (e.g., /bin/ls)
   → View displays correct data
2. Load a stripped binary
   → View handles missing data gracefully
3. Load multiple binaries sequentially
   → View updates each time
4. Switch between tabs
   → View maintains state
5. Load a non-executable file
   → View shows appropriate error/empty state
```

## Common Patterns

### Pattern 1: Simple Direct Mapping

**Use Case:** View displays data directly from a single AppState property

**Example:** OverviewView displays BinaryInfo

```python
class OverviewView(BaseView[BinaryInfo]):
    def on_mount(self) -> None:
        if hasattr(self.app, 'state'):
            self.app.state.subscribe("binary_info", self._on_changed)
    
    def _on_changed(self, new_value: BinaryInfo | None) -> None:
        self.data = new_value
    
    def render_content(self, data: BinaryInfo) -> None:
        # Use data directly
        table = self._build_table(data)
        self.update(table)
```

### Pattern 2: Extraction from Complex Data

**Use Case:** View displays a subset of a larger data structure

**Example:** ProtectionsView extracts protections dict from AnalysisResults

```python
class ProtectionsView(BaseView[dict]):
    def on_mount(self) -> None:
        if hasattr(self.app, 'state'):
            self.app.state.subscribe("analysis_results", self._on_changed)
    
    def _on_changed(self, new_value: AnalysisResults | None) -> None:
        if new_value and new_value.protections:
            self.data = new_value.protections
        else:
            self.data = {}
    
    def render_content(self, data: dict) -> None:
        # Use extracted dict
        table = self._build_protections_table(data)
        self.update(table)
```

### Pattern 3: List/Collection View

**Use Case:** View displays a list of items (strings, imports, functions)

**Example:** StringsView displays list of strings

```python
class StringsView(BaseView[list[str]]):
    def on_mount(self) -> None:
        if hasattr(self.app, 'state'):
            self.app.state.subscribe("analysis_results", self._on_changed)
    
    def _on_changed(self, new_value: AnalysisResults | None) -> None:
        if new_value:
            self.data = new_value.strings
        else:
            self.data = []
    
    def render_content(self, data: list[str]) -> None:
        if not data:
            self.update("[dim]No strings found[/dim]")
            return
        
        table = Table(title=f"Strings ({len(data)})")
        table.add_column("String")
        
        for string in data[:1000]:  # Limit display
            table.add_row(string)
        
        self.update(table)
```

## Common Pitfalls

### Pitfall 1: Forgetting to Set self.data

**Problem:**
```python
def _on_changed(self, new_value):
    # Forgot to set self.data!
    pass
```

**Solution:**
```python
def _on_changed(self, new_value):
    self.data = new_value  # Always set self.data to trigger render
```

### Pitfall 2: Not Handling None Data

**Problem:**
```python
def render_content(self, data: BinaryInfo) -> None:
    # Crashes if data is None!
    table.add_row("Path", data.path)
```

**Solution:**
```python
def render_content(self, data: BinaryInfo) -> None:
    if not data:
        self.update("[dim]No data available[/dim]")
        return
    
    table.add_row("Path", data.path)
```

### Pitfall 3: Wrong AppState Property

**Problem:**
```python
# ProtectionsView subscribing to wrong property
app.state.subscribe("binary_info", self._on_changed)  # WRONG!
```

**Solution:**
```python
# Subscribe to the property that contains your data
app.state.subscribe("analysis_results", self._on_changed)  # Correct
```

### Pitfall 4: Forgetting on_mount()

**Problem:**
```python
class MyView(BaseView[DataType]):
    # Forgot to implement on_mount()!
    
    def render_content(self, data):
        # View never gets data because no subscription
```

**Solution:**
```python
class MyView(BaseView[DataType]):
    def on_mount(self) -> None:
        # Always implement on_mount() to subscribe
        if hasattr(self.app, 'state'):
            self.app.state.subscribe("property_name", self._on_changed)
```

### Pitfall 5: Type Mismatch

**Problem:**
```python
class MyView(BaseView[BinaryInfo]):
    def _on_changed(self, new_value):
        # Setting wrong type!
        self.data = new_value.strings  # list[str], not BinaryInfo
```

**Solution:**
```python
class MyView(BaseView[list[str]]):  # Match the actual data type
    def _on_changed(self, new_value):
        self.data = new_value.strings  # Now types match
```

## Testing Strategy

### Unit Test Coverage Goals

For each migrated view, aim for these coverage targets:

- **Overall:** >85% line coverage
- **Core methods:** 100% coverage
  - `on_mount()`
  - `_on_*_changed()` handlers
  - `render_content()`
- **Edge cases:** Well tested
  - None data
  - Empty data
  - Missing fields
  - Invalid types

### Integration Test Coverage

Each view should have at least:

1. **State Update Test:** Verify view updates when AppState changes
2. **Multiple Update Test:** Verify view handles repeated state changes
3. **Concurrent Update Test:** Verify multiple views update together
4. **Backward Compat Test:** Verify old `update_data()` still works

## Visual Consistency

All migrated views should:

1. **Use Panels:** Wrap content in Rich Panel for visual separation
2. **Consistent Borders:** Use appropriate border colors:
   - Blue for info/overview
   - Yellow for warnings/protections
   - Green for success/exports
   - Red for errors
   - Cyan for data/imports
3. **Padding:** Use `padding=(1, 2)` for consistent spacing
4. **Titles:** Use `[bold]Title[/bold]` format
5. **Empty States:** Display helpful messages for empty data

## Migration Progress Tracking

Use this checklist to track migration progress:

### Subtask 3 (Complete):
- [x] OverviewView
- [x] ProtectionsView

### Subtask 4 (Remaining):
- [ ] StringsView
- [ ] ImportsExportsView
- [ ] R2View

### After All Migrations (Cleanup):
- [ ] Remove all `update_data()` compatibility shims
- [ ] Remove old `display_report()` method from CaspoonApp
- [ ] Update documentation to reflect new architecture
- [ ] Remove deprecation warnings

## Additional Resources

- **BaseView source:** `caspoon/ui/core/base.py`
- **AppState source:** `caspoon/ui/core/state.py`
- **Models source:** `caspoon/ui/core/models.py`
- **Example migrations:** 
  - `caspoon/ui/views/overview.py`
  - `caspoon/ui/views/protections.py`
- **Test examples:**
  - `caspoon/tests/unit/ui/views/test_overview.py`
  - `caspoon/tests/unit/ui/views/test_protections.py`
  - `caspoon/tests/integration/ui/test_core_views_integration.py`

## Getting Help

If you encounter issues during migration:

1. **Reference the examples:** OverviewView and ProtectionsView are complete, working examples
2. **Check the tests:** Unit and integration tests show expected behavior
3. **Check logs:** Enable debug logging to see subscription and update flow
4. **Verify types:** Use type checker (`mypy`) to catch type mismatches early
5. **Ask the Architect:** The architecture agent can help with design questions

## Summary

**Key Takeaways:**

1. Inherit from `BaseView[T]` with appropriate type parameter
2. Implement `on_mount()` to subscribe to AppState
3. Set `self.data` in state change handler to trigger render
4. Implement `render_content(data: T)` to display data
5. Keep `update_data()` shim for backward compatibility
6. Write comprehensive unit and integration tests
7. Manual testing to verify visual appearance

**Benefits of New Architecture:**

- ✅ Automatic reactive updates
- ✅ Single source of truth
- ✅ Better testability
- ✅ Loose coupling
- ✅ Easier to extend

Follow this pattern for all remaining view migrations in Subtask 4.
