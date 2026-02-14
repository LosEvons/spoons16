# Subtask 4: Analysis View Migrations

## Objective

Migrate the remaining complex analysis views (StringsView, ImportsExportsView, R2View) to the new architecture, implementing filtering, sorting, and syntax highlighting features while ensuring feature parity with the old implementation.

## Scope

**Included:**
- Migrate StringsView to InteractiveView with filtering capability
- Migrate ImportsExportsView to BaseView showing both imports and exports
- Migrate R2View (disassembly) with syntax highlighting integration
- Feature parity validation for all migrated views
- Performance testing for large datasets (1000+ strings, functions, etc.)
- Remove legacy compatibility shims from Subtask 3

**Excluded:**
- Async analysis workers (covered in Subtask 5)
- Command palette (covered in Subtask 6)
- Multi-panel layout (covered in Subtask 7)
- New features beyond parity (save for later phases)

## Technical Approach

### 1. StringsView Migration
**Location**: `caspoon/ui/views/strings_view.py`

Convert to InteractiveView with filtering:

- **Inheritance**: Change to `InteractiveView[list[str]]`
- **State Binding**: Watch `app.state.analysis_results.strings`
- **Filtering**: Implement `apply_filter(text)` for substring search
- **Navigation**: Use built-in up/down from InteractiveView
- **Selection**: Post SelectionChanged message for string details
- **Display**: Show index, offset, length, and string content
- **Performance**: Handle 10,000+ strings efficiently with pagination

### 2. ImportsExportsView Migration
**Location**: `caspoon/ui/views/imports_exports.py`

Dual-table view for imports and exports:

- **Inheritance**: Use `BaseView[AnalysisResults]` (needs both imports and exports)
- **State Binding**: Watch `app.state.analysis_results`
- **Layout**: Two side-by-side or stacked tables
- **Sorting**: Optional per-table sorting (name, address)
- **Display**: Show name, address, type/library for each item
- **Empty Handling**: Show "No imports" / "No exports" when empty

### 3. R2View Migration
**Location**: `caspoon/ui/views/r2_view.py`

Disassembly view with syntax highlighting:

- **Inheritance**: `InteractiveView[str]` or `BaseView[str]` depending on if navigation needed
- **State Binding**: Watch `app.state.analysis_results.disassembly`
- **Syntax Highlighting**: Integrate with existing syntax highlighting system
- **Address Navigation**: Jump to address functionality
- **Performance**: Handle large disassembly output (paginate if needed)
- **Fallback**: Graceful degradation if r2 unavailable

### 4. Feature Parity Validation

Ensure all existing features work:

- **StringsView**: Filtering by text, showing filtered count, selection
- **ImportsExportsView**: Display all imports/exports, readable format
- **R2View**: Syntax highlighting, scrolling, address display
- **Visual Consistency**: Same look and feel as old views
- **Keyboard Shortcuts**: All keybindings preserved
- **Error Handling**: Same error messages and handling

### 5. Performance Optimization

Test with large datasets:

- **Strings**: 10,000+ strings (typical in large binaries)
- **Imports/Exports**: 500+ imports (DLL-heavy binaries)
- **Disassembly**: Large functions (1000+ instructions)
- **Profiling**: Identify bottlenecks in render loops
- **Lazy Loading**: Consider pagination or virtual scrolling if needed
- **Target**: <100ms render time for typical data, <500ms for large data

## Implementation Steps

### Step 1: Migrate StringsView (3 hours)
Refactor `caspoon/ui/views/strings_view.py`:
- Change inheritance: `class StringsView(InteractiveView[list[dict]]):`
- Add on_mount() to watch analysis_results.strings
- Store full string list and filtered list as instance vars
- Implement `get_item_count()` → return len(filtered_strings)
- Implement `on_item_selected(index)` → post message or show details
- Implement `apply_filter(text: str)`:
  ```python
  def apply_filter(self, text: str) -> None:
      if not text:
          self._filtered = self._strings
      else:
          text_lower = text.lower()
          self._filtered = [s for s in self._strings if text_lower in s['string'].lower()]
      self.selected_index = 0  # Reset selection
      self._render_strings()
  ```
- Implement `render_content(data: list[dict])`:
  - Store data in self._strings
  - Apply current filter
  - Render filtered list
- Create Rich table with columns: Index, Offset, Length, String
- Add bindings: `/` to focus filter input, `c` to clear filter
- Show filtered count in title: "Strings (150 / 1200)"

### Step 2: Test StringsView (2.5 hours)
Create `caspoon/tests/unit/ui/views/test_strings_new.py`:
- `test_strings_inherits_interactiveview()` - Verify inheritance
- `test_strings_initializes()` - Can instantiate
- `test_strings_subscribes_on_mount()` - Watcher setup
- `test_strings_displays_all_strings()` - No filter shows all
- `test_strings_filter_by_text()` - Filter reduces list
- `test_strings_filter_case_insensitive()` - Case doesn't matter
- `test_strings_clear_filter()` - Empty filter shows all
- `test_strings_selection_navigation()` - Up/down moves selection
- `test_strings_filtered_count_display()` - Shows "X / Y" in title
- `test_strings_handles_empty_list()` - No crash with empty strings
- `test_strings_performance()` - Test with 10,000 strings (benchmark)
- Use mock data with various string types (ASCII, unicode, etc.)
- Aim for >85% coverage

### Step 3: Migrate ImportsExportsView (2.5 hours)
Refactor `caspoon/ui/views/imports_exports.py`:
- Change to `BaseView[AnalysisResults]` (needs both imports and exports)
- Add on_mount() to watch analysis_results
- Implement `render_content(data: AnalysisResults)`:
  ```python
  def render_content(self, data: AnalysisResults) -> None:
      imports_table = self._build_imports_table(data.imports)
      exports_table = self._build_exports_table(data.exports)
      
      # Use Rich layout to show both tables
      from rich.columns import Columns
      layout = Columns([imports_table, exports_table], equal=True, expand=True)
      self.update(layout)
  ```
- Helper method `_build_imports_table(imports: list[dict]) -> Table`:
  - Columns: Name, Address, Library
  - Color coding: different colors for local vs external
  - Show count in title
- Helper method `_build_exports_table(exports: list[dict]) -> Table`:
  - Columns: Name, Address, Type
  - Show count in title
- Handle empty lists: show "No imports" message
- Consider making tables sortable (optional enhancement)

### Step 4: Test ImportsExportsView (2 hours)
Create `caspoon/tests/unit/ui/views/test_imports_exports_new.py`:
- `test_imports_exports_inherits_baseview()` - Verify inheritance
- `test_imports_exports_initializes()` - Can instantiate
- `test_imports_exports_subscribes_on_mount()` - Watcher setup
- `test_imports_exports_displays_both_tables()` - Shows imports and exports
- `test_imports_exports_handles_empty_imports()` - No imports → message
- `test_imports_exports_handles_empty_exports()` - No exports → message
- `test_imports_exports_table_structure()` - Verify columns correct
- `test_imports_exports_shows_counts()` - Titles show item counts
- `test_imports_exports_performance()` - Test with 500+ imports
- Mock data with typical import/export structures
- Aim for >85% coverage

### Step 5: Migrate R2View (3 hours)
Refactor `caspoon/ui/views/r2_view.py`:
- Decide: BaseView or InteractiveView? (BaseView if just display, Interactive if need navigation)
- Change to `BaseView[Optional[str]]` (disassembly is text)
- Add on_mount() to watch analysis_results.disassembly
- Implement `render_content(data: Optional[str])`:
  ```python
  def render_content(self, data: Optional[str]) -> None:
      if not data:
          self.update("[dim]No disassembly available[/]")
          return
      
      # Apply syntax highlighting
      highlighted = self._apply_syntax_highlighting(data)
      
      # Render in scrollable panel
      from rich.panel import Panel
      from rich.text import Text
      panel = Panel(highlighted, title="Disassembly", border_style="magenta")
      self.update(panel)
  ```
- Integrate existing syntax highlighting:
  - Locate current highlighting logic (likely in old r2_view.py)
  - Extract into `_apply_syntax_highlighting(text: str) -> Text`
  - Color opcodes, registers, addresses, comments differently
- Add jump-to-address functionality (optional, can defer):
  - Input address → scroll to that address in disassembly
  - This might require InteractiveView if we want to select lines
- Handle r2 errors gracefully: show error message instead of crash

### Step 6: Test R2View (2 hours)
Create `caspoon/tests/unit/ui/views/test_r2_new.py`:
- `test_r2_inherits_baseview()` - Verify inheritance
- `test_r2_initializes()` - Can instantiate
- `test_r2_subscribes_on_mount()` - Watcher setup
- `test_r2_displays_disassembly()` - Shows text when data available
- `test_r2_handles_none_data()` - Shows "No disassembly" message
- `test_r2_syntax_highlighting()` - Verify highlighting applied
- `test_r2_syntax_highlighting_opcodes()` - Opcodes colored
- `test_r2_syntax_highlighting_registers()` - Registers colored
- `test_r2_syntax_highlighting_addresses()` - Addresses colored
- `test_r2_performance()` - Test with 1000+ lines of disassembly
- Mock disassembly text with various instruction types
- Aim for >80% coverage

### Step 7: Feature Parity Validation (2 hours)
Manual and automated testing:
- Launch TUI and load test binary: `python -m caspoon.ui /path/to/test/binary`
- **StringsView**:
  - Verify all strings displayed
  - Test filtering with various search terms
  - Verify filtered count accurate
  - Test navigation (up/down/page up/down)
  - Check selection highlighting visible
- **ImportsExportsView**:
  - Verify all imports displayed with correct libraries
  - Verify all exports displayed
  - Check empty handling (binary with no imports)
  - Verify table formatting readable
- **R2View**:
  - Verify disassembly displayed
  - Check syntax highlighting works (colors visible)
  - Test scrolling through long disassembly
  - Verify error handling if r2 not available
- Compare with old UI side-by-side using screenshots
- Document any differences or regressions

### Step 8: Performance Testing (2 hours)
Create `caspoon/tests/performance/test_view_performance.py`:
- **StringsView Performance**:
  - Generate 10,000 test strings
  - Time render_content() call
  - Time filtering operation
  - Target: <200ms for full render, <50ms for filter
- **ImportsExportsView Performance**:
  - Generate 500 imports, 500 exports
  - Time render_content() call
  - Target: <150ms for full render
- **R2View Performance**:
  - Generate 5000 lines of disassembly
  - Time render_content() call
  - Time syntax highlighting operation
  - Target: <300ms for full render with highlighting
- Use `pytest-benchmark` for consistent measurements
- Profile with cProfile if performance issues found
- Optimize hot paths (likely in filtering and highlighting)

### Step 9: Remove Compatibility Shims (1 hour)
Clean up backward compatibility code from Subtask 3:
- Remove deprecated `update_data()` methods from migrated views
- Remove `_update_views_legacy()` from CaspoonApp
- Remove feature flags (NEW_ARCHITECTURE_ENABLED)
- Update app to only use state-based updates
- Verify all views using new architecture
- Run full test suite to ensure nothing breaks

### Step 10: Integration Test (1.5 hours)
Create `caspoon/tests/integration/ui/test_all_views_integration.py`:
- `test_all_views_update_on_analysis()` - Load binary → all views update
- `test_strings_filter_integration()` - Filter strings in running app
- `test_imports_exports_display_integration()` - Both tables shown
- `test_r2_disassembly_integration()` - Disassembly displayed with highlighting
- `test_view_switching()` - Switch between tabs, all views work
- `test_performance_full_app()` - Load large binary, measure total time
- Use Textual's app.run_test() for full integration
- Mock ReconRunner with realistic data
- Verify memory usage reasonable (no leaks)

### Step 11: Documentation and Validation (30 minutes)
- Update view documentation with new architecture details
- Document any limitations or known issues
- Update migration guide with learnings from complex views
- Verify all tests pass: `pytest caspoon/tests/unit/ui/views/ -v`
- Verify integration tests: `pytest caspoon/tests/integration/ui/ -v`
- Check overall coverage: `pytest --cov=caspoon/ui/views --cov-report=html`
- Generate coverage report and review untested code
- Launch TUI and do final smoke test

## Code Example

```python
# caspoon/ui/views/strings_view.py (migrated)
from rich.table import Table
from rich.panel import Panel
from textual.binding import Binding

from caspoon.ui.core.base import InteractiveView
from caspoon.ui.core.models import AnalysisResults


class StringsView(InteractiveView[list[dict]]):
    """Interactive strings view with filtering.
    
    Displays all strings found in binary with filtering capability.
    Automatically updates when AppState.analysis_results.strings changes.
    """
    
    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("enter", "select_item", "Select", show=True),
        Binding("/", "focus_filter", "Filter", show=True),
        Binding("c", "clear_filter", "Clear Filter", show=True),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._strings = []
        self._filtered = []
    
    def on_mount(self) -> None:
        """Subscribe to analysis results for strings."""
        app = self.app
        if hasattr(app, 'state') and hasattr(app.state, 'analysis_results'):
            app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value) -> None:
        """Update when analysis results change."""
        if new_value and hasattr(new_value, 'strings'):
            self.data = new_value.strings
    
    def render_content(self, data: list[dict]) -> None:
        """Render strings list with current filter applied."""
        self._strings = data
        self.apply_filter(self.filter_text)
    
    def apply_filter(self, text: str) -> None:
        """Filter strings by text (case-insensitive substring match)."""
        if not text:
            self._filtered = self._strings
        else:
            text_lower = text.lower()
            self._filtered = [
                s for s in self._strings
                if text_lower in s.get('string', '').lower()
            ]
        
        # Reset selection to top when filter changes
        self.selected_index = 0
        self._render_strings()
    
    def _render_strings(self) -> None:
        """Render the filtered string list."""
        table = Table(show_header=True, show_edge=False, expand=True)
        table.add_column("Index", style="dim", width=6)
        table.add_column("Offset", style="cyan", width=10)
        table.add_column("Length", style="yellow", width=8)
        table.add_column("String", style="white", overflow="ellipsis")
        
        for i, string_data in enumerate(self._filtered[:1000]):  # Limit to 1000 for performance
            idx = str(i)
            offset = f"0x{string_data.get('offset', 0):08x}"
            length = str(string_data.get('length', 0))
            string = string_data.get('string', '')
            
            # Truncate very long strings
            if len(string) > 80:
                string = string[:77] + "..."
            
            # Highlight selected row
            style = "reverse bold" if i == self.selected_index else ""
            table.add_row(idx, offset, length, string, style=style)
        
        # Show count with filter status
        total = len(self._strings)
        filtered = len(self._filtered)
        if filtered < total:
            title = f"[bold]Strings ({filtered} / {total})[/]"
        else:
            title = f"[bold]Strings ({total})[/]"
        
        if self.filter_text:
            title += f" [dim]- filter: '{self.filter_text}'[/]"
        
        panel = Panel(table, title=title, border_style="green")
        self.update(panel)
    
    def get_item_count(self) -> int:
        """Return number of filtered strings."""
        return len(self._filtered)
    
    def on_item_selected(self, index: int) -> None:
        """Handle string selection."""
        if 0 <= index < len(self._filtered):
            string_data = self._filtered[index]
            # Could post message to show string details in side panel
            from caspoon.ui.core.messages import StringSelected
            self.post_message(StringSelected(string_data))
    
    def action_clear_filter(self) -> None:
        """Clear current filter."""
        self.filter_text = ""
    
    def watch_selected_index(self, old_index: int, new_index: int) -> None:
        """Re-render when selection changes."""
        self._render_strings()


# caspoon/ui/views/imports_exports.py (migrated)
from rich.table import Table
from rich.columns import Columns
from rich.panel import Panel

from caspoon.ui.core.base import BaseView
from caspoon.ui.core.models import AnalysisResults


class ImportsExportsView(BaseView[AnalysisResults]):
    """Display imports and exports side-by-side.
    
    Shows all imported and exported symbols from the binary.
    Automatically updates when AppState.analysis_results changes.
    """
    
    def on_mount(self) -> None:
        """Subscribe to analysis results."""
        app = self.app
        if hasattr(app, 'state') and hasattr(app.state, 'analysis_results'):
            app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old_value, new_value) -> None:
        """Update when analysis results change."""
        self.data = new_value
    
    def render_content(self, data: AnalysisResults) -> None:
        """Render imports and exports tables."""
        imports_table = self._build_imports_table(data.imports or [])
        exports_table = self._build_exports_table(data.exports or [])
        
        # Display side-by-side
        layout = Columns([imports_table, exports_table], equal=True, expand=True)
        self.update(layout)
    
    def _build_imports_table(self, imports: list[dict]) -> Panel:
        """Build imports table."""
        table = Table(show_header=True, show_edge=False, expand=True)
        table.add_column("Name", style="cyan", overflow="ellipsis")
        table.add_column("Address", style="yellow", width=10)
        table.add_column("Library", style="magenta", overflow="ellipsis")
        
        if not imports:
            table.add_row("[dim]No imports found[/]", "", "")
        else:
            for imp in imports[:500]:  # Limit for performance
                name = imp.get('name', 'unknown')
                address = f"0x{imp.get('address', 0):08x}"
                library = imp.get('library', '')
                table.add_row(name, address, library)
        
        title = f"[bold]Imports ({len(imports)})[/]"
        return Panel(table, title=title, border_style="blue")
    
    def _build_exports_table(self, exports: list[dict]) -> Panel:
        """Build exports table."""
        table = Table(show_header=True, show_edge=False, expand=True)
        table.add_column("Name", style="green", overflow="ellipsis")
        table.add_column("Address", style="yellow", width=10)
        table.add_column("Type", style="cyan", width=12)
        
        if not exports:
            table.add_row("[dim]No exports found[/]", "", "")
        else:
            for exp in exports[:500]:  # Limit for performance
                name = exp.get('name', 'unknown')
                address = f"0x{exp.get('address', 0):08x}"
                exp_type = exp.get('type', 'function')
                table.add_row(name, address, exp_type)
        
        title = f"[bold]Exports ({len(exports)})[/]"
        return Panel(table, title=title, border_style="green")
```

## Testing Strategy

### Unit Tests

**StringsView Tests** (`test_strings_new.py`):
- Test inheritance and initialization
- Test state subscription
- Test filtering (exact, partial, case-insensitive)
- Test selection navigation
- Test empty strings list
- Test large strings list (10,000 items)
- Test very long strings (truncation)
- Aim for >85% coverage

**ImportsExportsView Tests** (`test_imports_exports_new.py`):
- Test inheritance and initialization
- Test state subscription
- Test dual table rendering
- Test empty imports/exports
- Test large imports list (500+ items)
- Test table structure validation
- Aim for >85% coverage

**R2View Tests** (`test_r2_new.py`):
- Test inheritance and initialization
- Test state subscription
- Test disassembly display
- Test syntax highlighting
- Test empty/None disassembly
- Test large disassembly (1000+ lines)
- Aim for >80% coverage

### Performance Tests

**View Performance Suite** (`test_view_performance.py`):
- Benchmark StringsView with 10,000 strings
- Benchmark ImportsExportsView with 500+ imports
- Benchmark R2View with 5000 lines
- All should complete <500ms
- Use pytest-benchmark for consistency

### Integration Tests

**Full App Integration** (`test_all_views_integration.py`):
- Test all views update on binary load
- Test view switching
- Test filtering in live app
- Test memory usage
- Full end-to-end workflow

### Manual Testing

Manual validation checklist:
- Load various binaries (ELF, PE, stripped, packed)
- Test each view's functionality
- Compare visual output with old UI
- Test edge cases (empty data, huge data)
- Verify performance acceptable

## Dependencies

- **Subtask 1**: Requires AppState and messages
- **Subtask 2**: Requires InteractiveView and BaseView
- **Subtask 3**: Pattern established, migration guide available
- **Existing Views**: StringsView, ImportsExportsView, R2View to migrate
- **Rich**: Syntax highlighting, table rendering
- **pytest-benchmark**: Performance testing

## Estimated Time

**Total: 4-5 days (32-38 hours)**

Breakdown:
- StringsView migration: 3 hours
- StringsView tests: 2.5 hours
- ImportsExportsView migration: 2.5 hours
- ImportsExportsView tests: 2 hours
- R2View migration: 3 hours
- R2View tests: 2 hours
- Feature parity validation: 2 hours
- Performance testing: 2 hours
- Remove compatibility shims: 1 hour
- Integration tests: 1.5 hours
- Documentation/validation: 0.5 hours

**Buffer**: 2-4 hours for unexpected issues

## Success Criteria

- [ ] StringsView inherits from InteractiveView[list[dict]]
- [ ] StringsView filtering works (case-insensitive, real-time)
- [ ] StringsView displays filtered count (e.g., "150 / 1200")
- [ ] StringsView unit tests pass (minimum 11 tests)
- [ ] ImportsExportsView inherits from BaseView[AnalysisResults]
- [ ] ImportsExportsView shows both imports and exports
- [ ] ImportsExportsView handles empty lists gracefully
- [ ] ImportsExportsView unit tests pass (minimum 9 tests)
- [ ] R2View inherits from BaseView
- [ ] R2View displays disassembly with syntax highlighting
- [ ] R2View syntax highlighting colors opcodes, registers, addresses
- [ ] R2View unit tests pass (minimum 10 tests)
- [ ] All views achieve >80% test coverage
- [ ] Performance benchmarks pass (all views <500ms render)
- [ ] Feature parity validated (no missing functionality vs old UI)
- [ ] No visual regressions (manual comparison)
- [ ] Integration tests pass (minimum 6 tests)
- [ ] All backward compatibility shims removed
- [ ] Full test suite passes without warnings

## Next Steps

After completing this subtask:
1. **All Core Views Migrated**: Foundation complete for new features
2. **Proceed to Subtask 5**: Implement async analysis workers for non-blocking UI
3. **Proceed to Subtask 6**: Add command palette for keyboard-driven workflows
4. **Performance Optimization**: Profile and optimize any remaining bottlenecks
5. **User Feedback**: Gather feedback on new UI responsiveness
