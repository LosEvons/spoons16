# Subtask 3: Core View Migrations

## Objective

Migrate the two simplest views (OverviewView and ProtectionsView) to the new BaseView architecture and integrate AppState into CaspoonApp, proving the migration pattern works before tackling more complex views.

## Scope

**Included:**
- Refactor OverviewView to use BaseView[BinaryInfo]
- Refactor ProtectionsView to use BaseView[dict]
- Integrate AppState into CaspoonApp with backward compatibility
- Implement compatibility shims for old update_data() interface
- Step-by-step migration guide documentation
- Comprehensive tests for migrated views
- Feature flag for gradual rollout

**Excluded:**
- Complex views with filtering/sorting (covered in Subtask 4)
- StringsView, ImportsExportsView, R2View (covered in Subtask 4)
- Command palette integration (covered in Subtask 6)
- Multi-panel layout (covered in Subtask 7)
- Async workers (covered in Subtask 5)

## Technical Approach

### 1. Integrate AppState into CaspoonApp
**Location**: `caspoon/ui/app.py`

Modify CaspoonApp to include centralized state while maintaining backward compatibility:

- **Add AppState Instance**: `self.state = AppState()` in `__init__()`
- **Add ActionRegistry**: `self.action_registry = ActionRegistry()` (empty for now)
- **Dual Update Path**: Support both new (state-based) and old (direct) update methods during migration
- **Update Analysis Flow**:
  - On successful analysis, update `self.state.update_from_report(report)`
  - Keep old `update_views(report)` calls for non-migrated views
  - Add feature flag: `NEW_ARCHITECTURE_ENABLED = True`

### 2. Migrate OverviewView
**Location**: `caspoon/ui/views/overview.py`

Convert from Static with manual updates to reactive BaseView:

**Before (Old Pattern)**:
```python
class OverviewView(Static):
    def update_data(self, report: ExecutableReport) -> None:
        table = self._build_table(report)
        self.update(table)
```

**After (New Pattern)**:
```python
class OverviewView(BaseView[BinaryInfo]):
    def on_mount(self) -> None:
        self.app.state.binary_info.watch(self, "_on_data_changed")
    
    def _on_data_changed(self, old, new) -> None:
        self.data = new
    
    def render_content(self, data: BinaryInfo) -> None:
        table = self._build_table(data)
        self.update(table)
```

**Key Changes**:
- Inherit from BaseView[BinaryInfo] instead of Static
- Remove update_data() method
- Add on_mount() to subscribe to state changes
- Rename build logic to render_content()
- Data automatically flows from AppState → BaseView → render

### 3. Migrate ProtectionsView
**Location**: `caspoon/ui/views/protections.py`

Similar pattern but watches protections dict:

- Change to `BaseView[dict]` (protections are key-value pairs)
- Watch `app.state.analysis_results` and extract protections
- Implement render_content() to display protection status
- Reuse existing table rendering logic

### 4. Compatibility Shims
**Location**: `caspoon/ui/app.py` and view files

Maintain backward compatibility during transition:

- Keep old `update_data(report)` method as compatibility shim:
  ```python
  def update_data(self, report: ExecutableReport) -> None:
      """Compatibility shim. Use state.binary_info = ... instead."""
      warnings.warn("update_data() deprecated, use AppState", DeprecationWarning)
      # Still works for non-migrated code
  ```
- CaspoonApp calls both state update AND old methods during migration period
- Remove shims once all views migrated (Subtask 4 complete)

## Implementation Steps

### Step 1: Integrate AppState into CaspoonApp (2 hours)
Modify `caspoon/ui/app.py`:
- Import AppState and ActionRegistry from core
- Add `self.state = AppState()` in `__init__()`
- Add `self.action_registry = ActionRegistry()` in `__init__()`
- Locate existing analysis completion handler (likely in `on_worker_state_changed` or similar)
- Add state update: `self.state.update_from_report(report)` when analysis completes
- Keep existing `self._update_views(report)` calls for now (backward compat)
- Add feature flag constant at top of file: `NEW_ARCHITECTURE_ENABLED = True`
- Add logging: `logger.info("AppState initialized")` to verify

### Step 2: Create Test Fixtures (1 hour)
Create `caspoon/tests/fixtures/ui_fixtures.py`:
- Mock BinaryInfo with realistic test data
- Mock ExecutableReport with full structure
- Mock AppState for testing
- Reusable test app instance
- This will be used across all view tests

### Step 3: Migrate OverviewView (2.5 hours)
Refactor `caspoon/ui/views/overview.py`:
- Add import: `from caspoon.ui.core.base import BaseView`
- Add import: `from caspoon.ui.core.models import BinaryInfo`
- Change class declaration: `class OverviewView(BaseView[BinaryInfo]):`
- Remove existing `update_data()` method (or keep as deprecated shim)
- Add `on_mount()` method:
  ```python
  def on_mount(self) -> None:
      """Subscribe to binary info updates."""
      app = self.app
      if hasattr(app, 'state'):
          app.state.binary_info.watch(self, "_on_binary_info_changed")
  ```
- Add watcher:
  ```python
  def _on_binary_info_changed(self, old_value, new_value) -> None:
      """Update view when binary info changes."""
      self.data = new_value
  ```
- Rename existing rendering method to `render_content(self, data: BinaryInfo):`
- Update render logic to use `data` parameter instead of instance variables
- Verify table formatting preserved (same visual output as before)

### Step 4: Test OverviewView Migration (2 hours)
Create `caspoon/tests/unit/ui/views/test_overview_new.py`:
- `test_overview_inherits_baseview()` - Verify inheritance
- `test_overview_initializes()` - Can instantiate without errors
- `test_overview_subscribes_on_mount()` - on_mount() sets up watcher
- `test_overview_renders_binary_info()` - render_content() produces table
- `test_overview_updates_on_state_change()` - Changing state triggers render
- `test_overview_handles_none_data()` - Graceful handling of None
- `test_overview_table_structure()` - Verify table rows/columns correct
- `test_overview_backward_compat()` - Old update_data() still works (if shim kept)
- Use Textual's Pilot for rendering tests where needed
- Mock AppState for isolated testing
- Aim for >85% coverage of overview.py

### Step 5: Migrate ProtectionsView (2 hours)
Refactor `caspoon/ui/views/protections.py`:
- Follow same pattern as OverviewView
- Change to `BaseView[dict]` (protections are dict)
- Watch `app.state.analysis_results`:
  ```python
  def on_mount(self) -> None:
      app = self.app
      if hasattr(app, 'state'):
          app.state.analysis_results.watch(self, "_on_results_changed")
  
  def _on_results_changed(self, old, new) -> None:
      if new and new.protections:
          self.data = new.protections
  ```
- Implement `render_content(self, data: dict)` to display protections
- Reuse existing protection status logic (enabled/disabled/unknown indicators)
- Ensure color coding preserved (green=enabled, red=disabled, etc.)

### Step 6: Test ProtectionsView Migration (1.5 hours)
Create `caspoon/tests/unit/ui/views/test_protections_new.py`:
- `test_protections_inherits_baseview()` - Verify inheritance
- `test_protections_initializes()` - Can instantiate
- `test_protections_subscribes_on_mount()` - Watcher setup
- `test_protections_renders_dict()` - render_content() with protections dict
- `test_protections_handles_empty_dict()` - Empty protections handled
- `test_protections_color_coding()` - Verify enabled/disabled colors
- `test_protections_updates_on_state_change()` - State change triggers render
- Aim for >85% coverage

### Step 7: Integration Test (2 hours)
Create `caspoon/tests/integration/ui/test_core_views_integration.py`:
- `test_app_with_appstate()` - CaspoonApp has state attribute
- `test_overview_updates_on_analysis()` - Simulate analysis, verify OverviewView updates
- `test_protections_updates_on_analysis()` - Same for ProtectionsView
- `test_both_views_update_together()` - Both views react to same state change
- `test_old_views_still_work()` - Non-migrated views still function
- `test_state_update_from_report()` - AppState.update_from_report() works
- Use Textual's app.run_test() for full integration testing
- Mock ReconRunner to avoid actual binary analysis
- Verify no regressions in existing functionality

### Step 8: Manual Testing (1 hour)
- Launch TUI: `python -m caspoon.ui`
- Load a test binary (use known good binary from test fixtures)
- Verify OverviewView displays correctly
- Verify ProtectionsView displays correctly
- Check for visual regressions (compare screenshots if possible)
- Test edge cases: empty binary, stripped binary, unsupported format
- Verify error messages display properly
- Check performance (no noticeable slowdown)

### Step 9: Create Migration Guide (1.5 hours)
Create `caspoon/docs/plans/04-tui-redesign/migration-guide.md`:
- Document the migration pattern step-by-step
- Before/after code examples
- Common pitfalls and solutions
- Checklist for migrating a view:
  1. Change inheritance to BaseView[T]
  2. Add on_mount() to subscribe to state
  3. Rename render method to render_content()
  4. Update method signature to use data parameter
  5. Write tests
  6. Remove old update_data() once tested
- Reference this guide in remaining subtasks

### Step 10: Documentation and Validation (30 minutes)
- Update `caspoon/ui/views/__init__.py` if needed
- Verify all tests pass: `pytest caspoon/tests/unit/ui/views/ -v`
- Check integration tests: `pytest caspoon/tests/integration/ui/ -v`
- Verify test coverage: `pytest --cov=caspoon/ui/views --cov-report=term-missing`
- Ensure >85% coverage for migrated views
- Launch TUI and confirm no regressions
- Document any known issues or limitations

## Code Example

```python
# caspoon/ui/app.py (modified)
from caspoon.ui.core.state import AppState
from caspoon.ui.core.actions import ActionRegistry

class CaspoonApp(App):
    """Main Textual application for interactive binary analysis."""
    
    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # NEW: Centralized state management
        self.state = AppState()
        
        # NEW: Action registry for command palette
        self.action_registry = ActionRegistry()
        
        logger.info("CaspoonApp initialized with AppState")
    
    def _handle_analysis_complete(self, report: ExecutableReport) -> None:
        """Called when binary analysis completes."""
        # NEW: Update centralized state
        self.state.update_from_report(report)
        logger.info("AppState updated from report")
        
        # OLD: Keep for backward compatibility with non-migrated views
        self._update_views_legacy(report)
    
    def _update_views_legacy(self, report: ExecutableReport) -> None:
        """Legacy update path for non-migrated views."""
        # Call update_data() on old-style views
        for view_id in ["strings", "imports_exports", "r2view"]:
            view = self.query_one(f"#{view_id}", Widget)
            if hasattr(view, 'update_data'):
                view.update_data(report)


# caspoon/ui/views/overview.py (migrated)
from rich.panel import Panel
from rich.table import Table

from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import BinaryInfo


class OverviewView(BaseView[BinaryInfo]):
    """Overview of binary file information.
    
    Displays architecture, bits, type, file size, protections, etc.
    Automatically updates when AppState.binary_info changes.
    """
    
    def on_mount(self) -> None:
        """Subscribe to binary info updates."""
        app = self.app
        if hasattr(app, 'state'):
            app.state.binary_info.watch(self, "_on_binary_info_changed")
    
    def _on_binary_info_changed(self, old_value, new_value) -> None:
        """Update view when binary info changes."""
        self.data = new_value
    
    def render_content(self, data: BinaryInfo) -> None:
        """Render binary information as a formatted table."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", justify="right")
        table.add_column(style="white")
        
        # File information
        table.add_row("File:", data.path)
        table.add_row("Architecture:", data.architecture)
        table.add_row("Bits:", f"{data.bits}-bit")
        table.add_row("Type:", data.file_type)
        table.add_row("Size:", f"{data.file_size:,} bytes")
        
        if data.entry_point:
            table.add_row("Entry Point:", f"0x{data.entry_point:08x}")
        
        # Stripped status with color coding
        stripped_status = "[red]Yes[/]" if data.stripped else "[green]No[/]"
        table.add_row("Stripped:", stripped_status)
        
        panel = Panel(
            table,
            title="[bold]Binary Overview[/]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.update(panel)


# caspoon/ui/views/protections.py (migrated)
from rich.table import Table
from rich.panel import Panel

from caspoon.ui.core.base import BaseView


class ProtectionsView(BaseView[dict]):
    """Display binary security protections.
    
    Shows status of NX, PIE, RELRO, Canary, etc.
    Automatically updates when AppState.analysis_results changes.
    """
    
    def on_mount(self) -> None:
        """Subscribe to analysis results for protections."""
        app = self.app
        if hasattr(app, 'state'):
            app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value) -> None:
        """Extract protections from analysis results."""
        if new_value and hasattr(new_value, 'protections'):
            self.data = new_value.protections
    
    def render_content(self, data: dict) -> None:
        """Render protections status table."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold cyan", justify="right")
        table.add_column()
        
        # Standard protections with color coding
        protections = {
            "NX": data.get("nx", "unknown"),
            "PIE": data.get("pie", "unknown"),
            "RELRO": data.get("relro", "unknown"),
            "Canary": data.get("canary", "unknown"),
            "ASLR": data.get("aslr", "unknown"),
        }
        
        for name, status in protections.items():
            status_str = self._format_status(status)
            table.add_row(f"{name}:", status_str)
        
        panel = Panel(
            table,
            title="[bold]Security Protections[/]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.update(panel)
    
    def _format_status(self, status: str) -> str:
        """Format protection status with color coding."""
        status_lower = str(status).lower()
        
        if status_lower in ["enabled", "yes", "true", "full"]:
            return "[green]Enabled[/]"
        elif status_lower in ["disabled", "no", "false", "none"]:
            return "[red]Disabled[/]"
        elif status_lower == "partial":
            return "[yellow]Partial[/]"
        else:
            return "[dim]Unknown[/]"
```

## Testing Strategy

### Unit Tests

**AppState Integration Tests** (`test_app_state.py`):
- Test CaspoonApp has state attribute
- Test state is AppState instance
- Test action_registry is ActionRegistry instance
- Test state.update_from_report() called on analysis complete
- Mock analysis completion event

**OverviewView Tests** (`test_overview_new.py`):
- Test inherits from BaseView[BinaryInfo]
- Test on_mount() sets up watcher
- Test render_content() produces Panel with Table
- Test handles valid BinaryInfo data
- Test handles None data gracefully
- Test table structure has expected rows
- Test stripped status color coding
- Test state change triggers re-render

**ProtectionsView Tests** (`test_protections_new.py`):
- Test inherits from BaseView[dict]
- Test on_mount() sets up watcher on analysis_results
- Test render_content() produces protections table
- Test handles empty dict
- Test protection status color coding (enabled=green, disabled=red, etc.)
- Test all standard protections displayed (NX, PIE, RELRO, Canary, ASLR)
- Test state change triggers re-render

### Integration Tests

**Core Views Integration** (`test_core_views_integration.py`):
- Test end-to-end flow: load binary → state updates → views update
- Test multiple views react to same state change
- Test views don't interfere with each other
- Test backward compatibility with old-style views
- Use Textual's app.run_test() for full app testing
- Mock ReconRunner to avoid slow analysis

### Manual Testing

Manual verification checklist:
```bash
# Launch TUI
python -m caspoon.ui

# Test with known binary
1. Enter path to test binary (e.g., /bin/ls)
2. Verify OverviewView displays file info
3. Verify ProtectionsView displays protections
4. Check visual appearance matches old UI
5. Test with stripped binary
6. Test with non-ELF file (should show error)
7. Check for memory leaks (load multiple binaries)
8. Verify performance is acceptable
```

## Dependencies

- **Subtask 1**: Requires AppState, messages, ActionRegistry
- **Subtask 2**: Requires BaseView class
- **Textual**: Already available
- **Rich**: Already available
- **pytest**: Already available
- **Existing Views**: Working OverviewView and ProtectionsView to migrate

## Estimated Time

**Total: 4-5 days (30-36 hours)**

Breakdown:
- AppState integration: 2 hours
- Test fixtures: 1 hour
- OverviewView migration: 2.5 hours
- OverviewView tests: 2 hours
- ProtectionsView migration: 2 hours
- ProtectionsView tests: 1.5 hours
- Integration tests: 2 hours
- Manual testing: 1 hour
- Migration guide: 1.5 hours
- Documentation/validation: 0.5 hours

**Buffer**: 2-4 hours for unexpected issues

## Success Criteria

- [ ] CaspoonApp has `state` attribute of type AppState
- [ ] CaspoonApp has `action_registry` attribute
- [ ] AppState.update_from_report() called on analysis completion
- [ ] OverviewView inherits from BaseView[BinaryInfo]
- [ ] OverviewView displays binary info correctly (manual test)
- [ ] OverviewView unit tests pass (minimum 8 tests)
- [ ] ProtectionsView inherits from BaseView[dict]
- [ ] ProtectionsView displays protections correctly (manual test)
- [ ] ProtectionsView unit tests pass (minimum 8 tests)
- [ ] Integration tests pass (minimum 6 tests)
- [ ] Test coverage >85% for both migrated views
- [ ] No visual regressions (compare with old UI)
- [ ] Backward compatibility maintained (old views still work)
- [ ] Migration guide document created
- [ ] All existing TUI functionality preserved
- [ ] No performance degradation

## Next Steps

After completing this subtask:
1. **Validate Pattern**: Confirm the migration pattern works well for simple views
2. **Iterate if Needed**: Adjust BaseView or migration approach based on learnings
3. **Proceed to Subtask 4**: Migrate remaining complex views (StringsView, ImportsExportsView, R2View)
4. **Use Migration Guide**: Reference created guide for consistency
5. **Remove Compatibility Shims**: Once all views migrated, clean up old code
