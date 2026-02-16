# Subtask 2: Base Widget Classes

## Objective

Create reusable base widget classes (BaseView, InteractiveView, TableView, TreeView) that provide standard patterns for reactive data binding, keyboard interaction, and content rendering across all TUI views.

## Scope

**Included:**
- BaseView abstract class with reactive data binding and lifecycle hooks
- InteractiveView class with selection, keyboard navigation, and filtering
- TableView class with column sorting and table rendering
- TreeView class for hierarchical data display
- Comprehensive unit tests for widget logic (no rendering tests)
- Integration with AppState reactive properties

**Excluded:**
- Actual view implementations using these widgets (covered in Subtasks 3-4)
- Command palette widget (covered in Subtask 6)
- Multi-panel layout widgets (covered in Subtask 7)
- Async worker integration (covered in Subtask 5)

## Technical Approach

### 1. BaseView Widget
**Location**: `caspoon/ui/core/base.py`

Foundation widget class that all views inherit from:

- **Generic Type Parameter**: `BaseView[T]` where T is the data type (BinaryInfo, list[dict], etc.)
- **Reactive Data**: `data: reactive[Optional[T]]` - triggers render when changed
- **Lifecycle Hooks**:
  - `on_mount()` - Subscribe to AppState reactive properties
  - `on_show()` - View becomes visible (hook for future optimization)
  - `on_hide()` - View hidden (cleanup hook)
- **Abstract Methods**:
  - `render_content(data: T) -> None` - Subclass implements rendering logic
- **Built-in Features**:
  - Loading state management
  - Error display handling
  - Automatic re-rendering on data changes via watch()

### 2. InteractiveView Widget
**Location**: `caspoon/ui/core/base.py` (extends BaseView)

Adds keyboard/mouse interaction capabilities:

- **Selection Management**: `selected_index: reactive[int]` - track current selection
- **Filter Support**: `filter_text: reactive[str]` - for search/filter functionality
- **Keyboard Navigation**:
  - Built-in bindings: up/down/home/end/page_up/page_down
  - Actions: `action_move_up()`, `action_move_down()`, `action_select_item()`
- **Abstract Methods**:
  - `get_item_count() -> int` - Return filtered item count
  - `on_item_selected(index: int) -> None` - Handle selection
  - `apply_filter(text: str) -> None` - Implement filtering logic

### 3. TableView Widget
**Location**: `caspoon/ui/core/base.py` (extends InteractiveView)

Specialized for tabular data:

- **Sorting State**: `sort_column: reactive[str]`, `sort_descending: reactive[bool]`
- **Abstract Methods**:
  - `get_columns() -> list[str]` - Define column names
  - `get_row_data(index: int) -> list[str]` - Get data for row
- **Built-in Actions**:
  - `action_sort_by_column(col: str)` - Toggle sort for column
- **Helper Methods**:
  - `_render_table() -> Table` - Standard Rich table rendering

### 4. TreeView Widget
**Location**: `caspoon/ui/core/base.py` (extends InteractiveView)

For hierarchical data:

- **Expansion State**: Track expanded/collapsed nodes
- **Abstract Methods**:
  - `get_root_nodes() -> list[TreeNode]` - Top-level nodes
  - `get_child_nodes(node: TreeNode) -> list[TreeNode]` - Children
- **Built-in Actions**:
  - `action_toggle_node()` - Expand/collapse current node
  - `action_expand_all()`, `action_collapse_all()`

## Implementation Steps

### Step 1: Implement BaseView Class (2 hours)
Create `caspoon/ui/core/base.py` with BaseView:
- Import necessary Textual components (Static, reactive, Generic, TypeVar)
- Define TypeVar `T` for generic typing
- Create BaseView(Static, ABC, Generic[T]) class
- Add reactive property: `data: reactive[Optional[T]] = reactive(None)`
- Implement `watch_data(old, new)` - calls `render_content(new)` when data changes
- Add abstract method `render_content(data: T) -> None` with docstring
- Add optional lifecycle hooks: `on_show()`, `on_hide()` (empty implementations)
- Add error handling wrapper for `render_content()` to catch exceptions
- Add docstrings explaining usage pattern

### Step 2: Implement InteractiveView Class (2.5 hours)
Add InteractiveView to `caspoon/ui/core/base.py`:
- Create InteractiveView(BaseView[T], ABC) class
- Add reactive properties: `selected_index: reactive[int] = reactive(0)`, `filter_text: reactive[str] = reactive("")`
- Define BINDINGS list with keyboard shortcuts (up, down, enter, home, end, pageup, pagedown)
- Implement action methods:
  - `action_move_up()` - decrement selected_index with bounds check
  - `action_move_down()` - increment selected_index with bounds check
  - `action_move_to_top()` - set selected_index = 0
  - `action_move_to_bottom()` - set selected_index = get_item_count() - 1
  - `action_select_item()` - call `on_item_selected(selected_index)`
- Add abstract methods: `get_item_count()`, `on_item_selected(index)`, `apply_filter(text)`
- Implement `watch_selected_index(old, new)` to ensure selection stays in bounds
- Implement `watch_filter_text(old, new)` to call `apply_filter(new)`

### Step 3: Implement TableView Class (2 hours)
Add TableView to `caspoon/ui/core/base.py`:
- Create TableView(InteractiveView[T], ABC) class
- Add reactive properties: `sort_column: reactive[Optional[str]] = reactive(None)`, `sort_descending: reactive[bool] = reactive(False)`
- Define additional BINDINGS for sorting (s: toggle sort)
- Add abstract methods: `get_columns() -> list[str]`, `get_row_data(index: int) -> list[str]`
- Implement `action_sort_by_column(column: str)`:
  - If same column, toggle sort_descending
  - If different column, set sort_column and sort_descending = False
  - Call subclass sorting logic
- Add helper method `_build_rich_table() -> Table`:
  - Create Rich Table with columns from get_columns()
  - Iterate through filtered items calling get_row_data()
  - Apply selection highlighting (reverse style on selected_index row)
  - Show sort indicator in column header (↑/↓)

### Step 4: Implement TreeView Class (2 hours)
Add TreeView to `caspoon/ui/core/base.py`:
- Create TreeView(InteractiveView[T], ABC) class
- Add dataclass `TreeNode(node_id: str, label: str, has_children: bool, data: Any)`
- Add reactive property: `expanded_nodes: reactive[set[str]] = reactive(set)`
- Add abstract methods: `get_root_nodes() -> list[TreeNode]`, `get_child_nodes(node_id: str) -> list[TreeNode]`
- Implement `action_toggle_node()`:
  - Get current node from flattened list at selected_index
  - Add/remove from expanded_nodes set
  - Trigger re-render
- Implement `action_expand_all()`, `action_collapse_all()`
- Add helper method `_flatten_tree() -> list[tuple[TreeNode, int]]`:
  - Walk tree respecting expanded_nodes
  - Return flat list with indent level for rendering
- Add helper method `_build_rich_tree() -> Tree`:
  - Use Rich Tree component to render hierarchy

### Step 5: Export Classes (15 minutes)
Update `caspoon/ui/core/__init__.py`:
- Add exports for BaseView, InteractiveView, TableView, TreeView
- Add export for TreeNode dataclass
- Document what each class is for (brief comment)

### Step 6: Unit Tests for BaseView (2 hours)
Create `caspoon/tests/unit/ui/core/test_base_view.py`:
- `test_baseview_initialization()` - Verify data starts as None
- `test_baseview_data_change_triggers_render()` - Set data, verify render_content called
- `test_baseview_render_with_none_data()` - Ensure no crash with None data
- `test_baseview_subclass_must_implement_render()` - Verify abstract method enforced
- `test_baseview_error_handling()` - render_content raises exception, verify caught
- Use mock subclass for testing since BaseView is abstract
- Aim for >90% coverage of BaseView logic

### Step 7: Unit Tests for InteractiveView (2.5 hours)
Create `caspoon/tests/unit/ui/core/test_interactive_view.py`:
- `test_interactiveview_initialization()` - Verify selected_index = 0, filter_text = ""
- `test_move_up_action()` - Test action_move_up() decrements index
- `test_move_down_action()` - Test action_move_down() increments index
- `test_move_up_at_boundary()` - At index 0, stays at 0
- `test_move_down_at_boundary()` - At max, stays at max
- `test_move_to_top()` - Sets index to 0
- `test_move_to_bottom()` - Sets index to item_count - 1
- `test_select_item_calls_handler()` - action_select_item() calls on_item_selected()
- `test_filter_text_triggers_apply_filter()` - Setting filter_text calls apply_filter()
- `test_abstract_methods_enforced()` - Verify get_item_count, on_item_selected, apply_filter required
- Create mock subclass with 10 test items for testing
- Aim for >85% coverage

### Step 8: Unit Tests for TableView (1.5 hours)
Create `caspoon/tests/unit/ui/core/test_table_view.py`:
- `test_tableview_initialization()` - Verify sort_column = None, sort_descending = False
- `test_sort_by_column()` - Set sort_column, verify state change
- `test_toggle_sort_direction()` - Sort same column twice, verify direction toggles
- `test_get_columns_abstract()` - Verify abstract method
- `test_get_row_data_abstract()` - Verify abstract method
- `test_build_rich_table()` - Verify _build_rich_table() creates Table with correct structure
- Create mock subclass with sample table data for testing
- Aim for >80% coverage

### Step 9: Unit Tests for TreeView (1.5 hours)
Create `caspoon/tests/unit/ui/core/test_tree_view.py`:
- `test_treeview_initialization()` - Verify expanded_nodes is empty set
- `test_toggle_node_expands()` - Expand node, verify in expanded_nodes
- `test_toggle_node_collapses()` - Collapse expanded node, verify removed
- `test_flatten_tree_root_only()` - No expanded nodes, returns only roots
- `test_flatten_tree_with_children()` - Expanded nodes, returns children
- `test_expand_all()` - All nodes with children expanded
- `test_collapse_all()` - All nodes collapsed
- Create mock tree structure with 3 levels for testing
- Aim for >80% coverage

### Step 10: Integration Test (1 hour)
Create `caspoon/tests/unit/ui/core/test_base_integration.py`:
- `test_baseview_with_appstate()` - BaseView watches AppState, data updates
- `test_interactiveview_selection_flow()` - Navigate, select, verify messages
- `test_tableview_sort_and_filter()` - Sort + filter work together
- `test_treeview_navigation()` - Navigate tree with up/down
- Mock AppState and test reactive property watching
- Verify widgets work with Textual's message system

### Step 11: Documentation and Validation (30 minutes)
- Add comprehensive docstrings to all classes and methods
- Create usage examples in docstrings showing how to subclass
- Verify all tests pass: `pytest caspoon/tests/unit/ui/core/test_base*.py -v`
- Check coverage: `pytest --cov=caspoon/ui/core/base --cov-report=term-missing`
- Ensure target >85% coverage achieved
- Document known limitations (e.g., no rendering tests)

## Code Example

```python
# caspoon/ui/core/base.py
from abc import ABC, abstractmethod
from textual.reactive import reactive
from textual.widgets import Static
from textual.binding import Binding
from typing import Generic, TypeVar, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseView(Static, ABC, Generic[T]):
    """Base class for all Caspoon views with reactive data binding.
    
    Provides:
    - Automatic re-rendering when data changes
    - Lifecycle hooks for mount/show/hide
    - Error handling for render failures
    - Standard interface for all views
    
    Subclasses must implement:
    - render_content(data: T) -> None
    
    Example:
        class FileInfoView(BaseView[BinaryInfo]):
            def on_mount(self):
                self.app.state.binary_info.watch(self, "_on_data_changed")
            
            def _on_data_changed(self, old, new):
                self.data = new  # Triggers render_content()
            
            def render_content(self, data: BinaryInfo) -> None:
                table = self._build_table(data)
                self.update(table)
    """
    
    # Reactive data - triggers render when changed
    data: reactive[Optional[T]] = reactive(None)
    
    def watch_data(self, old_value: Optional[T], new_value: Optional[T]) -> None:
        """Called when data changes. Triggers render_content()."""
        if new_value is not None:
            try:
                self.render_content(new_value)
            except Exception as e:
                logger.error(f"Error rendering {self.__class__.__name__}: {e}")
                self.update(f"[red]Error: {e}[/]")
    
    @abstractmethod
    def render_content(self, data: T) -> None:
        """Render the view content. Must call self.update() with Rich renderable.
        
        Args:
            data: The data to render
        """
        pass
    
    def on_show(self) -> None:
        """Called when view becomes visible. Override for optimizations."""
        pass
    
    def on_hide(self) -> None:
        """Called when view becomes hidden. Override for cleanup."""
        pass


class InteractiveView(BaseView[T], ABC):
    """Base class for views with keyboard/mouse interaction.
    
    Adds:
    - Selection state (selected_index)
    - Keyboard navigation (up/down/home/end)
    - Filter support (filter_text)
    - Item selection handling
    
    Subclasses must implement (in addition to render_content):
    - get_item_count() -> int
    - on_item_selected(index: int) -> None
    - apply_filter(text: str) -> None
    
    Example:
        class FunctionListView(InteractiveView[list[Function]]):
            BINDINGS = [
                Binding("enter", "select_item", "Select"),
            ]
            
            def get_item_count(self):
                return len(self._filtered_items)
            
            def on_item_selected(self, index: int):
                func = self._filtered_items[index]
                self.post_message(SelectFunction(func.name))
            
            def apply_filter(self, text: str):
                self._filtered_items = [
                    f for f in self.data 
                    if text.lower() in f.name.lower()
                ]
                self._rerender()
    """
    
    BINDINGS = [
        Binding("up,k", "move_up", "Move Up", show=False),
        Binding("down,j", "move_down", "Move Down", show=False),
        Binding("home", "move_to_top", "First", show=False),
        Binding("end", "move_to_bottom", "Last", show=False),
        Binding("enter", "select_item", "Select", show=True),
    ]
    
    # Current selection index
    selected_index: reactive[int] = reactive(0)
    
    # Current filter text
    filter_text: reactive[str] = reactive("")
    
    @abstractmethod
    def get_item_count(self) -> int:
        """Return number of items (after filtering)."""
        pass
    
    @abstractmethod
    def on_item_selected(self, index: int) -> None:
        """Handle item selection at index."""
        pass
    
    @abstractmethod
    def apply_filter(self, text: str) -> None:
        """Apply filter and re-render view."""
        pass
    
    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """Ensure selected_index stays in valid range."""
        count = self.get_item_count()
        if count == 0:
            self.selected_index = 0
        elif new_value < 0:
            self.selected_index = 0
        elif new_value >= count:
            self.selected_index = count - 1
    
    def watch_filter_text(self, old_value: str, new_value: str) -> None:
        """Apply filter when filter_text changes."""
        self.apply_filter(new_value)
    
    def action_move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
    
    def action_move_down(self) -> None:
        """Move selection down."""
        if self.selected_index < self.get_item_count() - 1:
            self.selected_index += 1
    
    def action_move_to_top(self) -> None:
        """Move to first item."""
        self.selected_index = 0
    
    def action_move_to_bottom(self) -> None:
        """Move to last item."""
        count = self.get_item_count()
        self.selected_index = count - 1 if count > 0 else 0
    
    def action_select_item(self) -> None:
        """Select current item."""
        if self.get_item_count() > 0:
            self.on_item_selected(self.selected_index)


class TableView(InteractiveView[T], ABC):
    """Base class for table views with sorting.
    
    Adds:
    - Column sorting (sort_column, sort_descending)
    - Table rendering helpers
    
    Subclasses must implement (in addition to InteractiveView methods):
    - get_columns() -> list[str]
    - get_row_data(index: int) -> list[str]
    """
    
    sort_column: reactive[Optional[str]] = reactive(None)
    sort_descending: reactive[bool] = reactive(False)
    
    @abstractmethod
    def get_columns(self) -> list[str]:
        """Return list of column names."""
        pass
    
    @abstractmethod
    def get_row_data(self, index: int) -> list[str]:
        """Return data for row at index."""
        pass
    
    def action_sort_by_column(self, column: str) -> None:
        """Sort by column, toggling direction if already sorted by this column."""
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False


@dataclass
class TreeNode:
    """Node in a tree structure."""
    node_id: str
    label: str
    has_children: bool
    data: any = None


class TreeView(InteractiveView[T], ABC):
    """Base class for tree/hierarchical views.
    
    Adds:
    - Node expansion state
    - Tree navigation
    
    Subclasses must implement (in addition to InteractiveView methods):
    - get_root_nodes() -> list[TreeNode]
    - get_child_nodes(node_id: str) -> list[TreeNode]
    """
    
    expanded_nodes: reactive[set[str]] = reactive(set, init=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expanded_nodes = set()
    
    @abstractmethod
    def get_root_nodes(self) -> list[TreeNode]:
        """Return top-level nodes."""
        pass
    
    @abstractmethod
    def get_child_nodes(self, node_id: str) -> list[TreeNode]:
        """Return children of node."""
        pass
    
    def action_toggle_node(self) -> None:
        """Expand/collapse current node."""
        nodes = self._flatten_tree()
        if 0 <= self.selected_index < len(nodes):
            node, _ = nodes[self.selected_index]
            if node.has_children:
                if node.node_id in self.expanded_nodes:
                    self.expanded_nodes.remove(node.node_id)
                else:
                    self.expanded_nodes.add(node.node_id)
    
    def _flatten_tree(self) -> list[tuple[TreeNode, int]]:
        """Flatten tree into list for rendering. Returns (node, indent_level)."""
        result = []
        
        def walk(nodes: list[TreeNode], level: int):
            for node in nodes:
                result.append((node, level))
                if node.has_children and node.node_id in self.expanded_nodes:
                    children = self.get_child_nodes(node.node_id)
                    walk(children, level + 1)
        
        walk(self.get_root_nodes(), 0)
        return result
```

## Testing Strategy

### Unit Tests

**BaseView Tests** (`test_base_view.py`):
- Test initialization with None data
- Test data change triggers render_content()
- Test error handling in render_content()
- Test abstract method enforcement
- Use mock subclass for testing

**InteractiveView Tests** (`test_interactive_view.py`):
- Test selection navigation (up/down/home/end)
- Test boundary conditions (can't go below 0 or above count)
- Test select_item calls on_item_selected()
- Test filter_text triggers apply_filter()
- Test abstract method enforcement
- Mock subclass with 10 test items

**TableView Tests** (`test_table_view.py`):
- Test column sorting state changes
- Test sort direction toggle
- Test get_columns() and get_row_data() requirements
- Mock subclass with sample table

**TreeView Tests** (`test_tree_view.py`):
- Test node expansion/collapse
- Test tree flattening with expanded nodes
- Test navigation respects hierarchy
- Mock tree with 3 levels

### Integration Tests

**Widget Integration** (`test_base_integration.py`):
- Test BaseView + AppState reactive watching
- Test InteractiveView selection flow with messages
- Test TableView sort + filter combination
- Test TreeView expand + navigate

### Manual Testing

Since these are base classes, manual testing happens in Subtask 3-4 when implementing actual views.

```bash
# Run all tests
pytest caspoon/tests/unit/ui/core/test_base*.py -v

# Check coverage
pytest --cov=caspoon/ui/core/base --cov-report=term-missing caspoon/tests/unit/ui/core/test_base*.py

# Target: >85% coverage
```

## Dependencies

- **Textual**: Already available (reactive, Static, Binding)
- **Rich**: Already available (Table, Tree rendering)
- **typing**: Standard library (Generic, TypeVar)
- **dataclasses**: Standard library (TreeNode)
- **abc**: Standard library (ABC, abstractmethod)
- **pytest**: Already available for testing
- **Subtask 1**: Requires AppState and message types

## Estimated Time

**Total: 3-4 days (26-30 hours)**

Breakdown:
- BaseView implementation: 2 hours
- InteractiveView implementation: 2.5 hours
- TableView implementation: 2 hours
- TreeView implementation: 2 hours
- Export setup: 0.25 hours
- BaseView tests: 2 hours
- InteractiveView tests: 2.5 hours
- TableView tests: 1.5 hours
- TreeView tests: 1.5 hours
- Integration tests: 1 hour
- Documentation/validation: 0.5 hours

**Buffer**: 1-2 hours for unexpected issues

## Success Criteria

- [ ] BaseView class implemented with reactive data and render_content() abstract method
- [ ] InteractiveView class implemented with selection, navigation, and filtering
- [ ] TableView class implemented with sorting support
- [ ] TreeView class implemented with expansion state
- [ ] All classes properly exported from `caspoon/ui/core/__init__.py`
- [ ] Unit tests pass (minimum 40 tests total across all widget classes)
- [ ] Test coverage >85% for `caspoon/ui/core/base.py`
- [ ] All abstract methods properly enforced (instantiation fails without implementation)
- [ ] BaseView can watch AppState reactive properties (tested with mock)
- [ ] InteractiveView keyboard navigation works (up/down/home/end/enter)
- [ ] TableView sorting state changes correctly
- [ ] TreeView expansion/collapse works correctly
- [ ] Integration test shows BaseView + AppState working together
- [ ] Documentation complete with usage examples in docstrings

## Next Steps

After completing this subtask:
1. **Proceed to Subtask 3**: Migrate OverviewView and ProtectionsView to use BaseView
2. **Pattern Validation**: First real views will validate the base class design
3. **Iterate if Needed**: May need to adjust base classes based on real usage
4. **Remaining Migrations**: Once pattern proven, migrate all other views in Subtask 4
