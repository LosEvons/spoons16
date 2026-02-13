# Subtask 3: Enhanced Data Views

## Objective
Upgrade all static views to interactive widgets (DataTable, Tree) with search, filter, sort, and selection capabilities.

## Scope
Replace `Static` widgets with interactive `DataTable` and `Tree` widgets for Strings, Imports/Exports, and add new Functions view. Implement search/filter UI, pagination for large datasets, and color-coding for security-relevant items.

## Technical Approach

### 1. Strings View Upgrade
**Location**: `caspoon/ui/views/strings_view.py`

**Changes**:
- Replace `Static` with `DataTable`
- Add columns: String, Length, Encoding, Category, Address
- Implement search bar (Ctrl+F within view)
- Add filters: min length, category (URL, Path, Suspicious, etc.)
- Color-code suspicious patterns (red/yellow)

```python
class StringsView(Container):
    """Interactive strings view with filtering."""
    
    def compose(self) -> ComposeResult:
        # Filter controls
        with Horizontal(id="filter-bar"):
            yield Input(placeholder="Search...", id="string-search")
            yield Select(
                options=[("All", "all"), ("URLs", "url"), ("Paths", "path")],
                id="string-category"
            )
            yield Input(placeholder="Min length", id="min-length")
        
        # DataTable for strings
        yield DataTable(id="strings-table")
    
    def update_data(self, report: ExecutableReport) -> None:
        """Populate table with strings."""
        table = self.query_one("#strings-table", DataTable)
        table.clear()
        table.add_columns("String", "Length", "Encoding", "Category", "Address")
        
        for string_obj in report.strings:
            # Categorize string
            category = self._categorize_string(string_obj.value)
            
            # Color-code suspicious strings
            style = "red" if category == "Suspicious" else None
            
            table.add_row(
                string_obj.value[:80],  # Truncate long strings
                str(string_obj.length),
                string_obj.encoding,
                category,
                hex(string_obj.address) if string_obj.address else "N/A",
                style=style
            )
```

### 2. Imports/Exports View Upgrade
**Location**: `caspoon/ui/views/imports_exports_view.py`

**Structure**: Split view with two DataTables

```python
class ImportsExportsView(Container):
    """Split view for imports and exports."""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            # Imports section (top 60%)
            with Container(id="imports-section"):
                yield Label("Imported Functions", classes="section-header")
                yield Input(placeholder="Search imports...", id="imports-search")
                yield DataTable(id="imports-table")
            
            # Exports section (bottom 40%)
            with Container(id="exports-section"):
                yield Label("Exported Functions", classes="section-header")
                yield Input(placeholder="Search exports...", id="exports-search")
                yield DataTable(id="exports-table")
    
    def update_data(self, report: ExecutableReport) -> None:
        """Populate both tables."""
        self._populate_imports(report.imports)
        self._populate_exports(report.exports)
    
    def _populate_imports(self, imports: List[Import]) -> None:
        """Populate imports table with risk color-coding."""
        table = self.query_one("#imports-table", DataTable)
        table.clear()
        table.add_columns("Function", "Library", "Risk", "Address")
        
        for imp in imports:
            risk_level = self._assess_risk(imp.name)
            style = {
                "Critical": "bold red",
                "High": "bold yellow",
                "Medium": "yellow",
                "Low": "green"
            }.get(risk_level, "white")
            
            table.add_row(
                imp.name,
                imp.library,
                risk_level,
                hex(imp.address) if imp.address else "N/A",
                style=style
            )
```

### 3. Functions View (NEW)
**Location**: `caspoon/ui/views/functions_view.py`

**Structure**: Split view with Tree (left) and DataTable (right)

```python
class FunctionsView(Container):
    """Hierarchical functions view with tree navigation."""
    
    DEFAULT_CSS = """
    FunctionsView Horizontal {
        height: 100%;
    }
    
    #functions-tree {
        width: 40%;
        border-right: solid $accent;
    }
    
    #functions-details {
        width: 60%;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            # Left: Tree view of functions
            yield Tree("Functions", id="functions-tree")
            
            # Right: Details table
            with Vertical(id="functions-details"):
                yield Label("Function Details", classes="section-header")
                yield DataTable(id="function-details-table")
    
    def update_data(self, report: ExecutableReport) -> None:
        """Populate tree with function hierarchy."""
        tree = self.query_one("#functions-tree", Tree)
        tree.clear()
        
        # Group functions by library/section
        root = tree.root
        
        # Add user-defined functions
        user_node = root.add("User Functions")
        for func in report.functions:
            if not func.is_import:
                user_node.add_leaf(f"{func.name} @ {hex(func.address)}")
        
        # Add imported functions grouped by library
        imports_node = root.add("Imported Functions")
        grouped = self._group_by_library(report.imports)
        for lib, funcs in grouped.items():
            lib_node = imports_node.add(lib)
            for func in funcs:
                lib_node.add_leaf(func.name)
    
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Update details table when function selected."""
        # Fetch function details and display in table
        details = self._get_function_details(event.node.label)
        self._populate_details_table(details)
```

### 4. Pagination for Large Datasets
**Implementation**: Virtual scrolling + chunking

```python
class PaginatedDataTable(DataTable):
    """DataTable with lazy loading for large datasets."""
    
    CHUNK_SIZE = 100
    
    def __init__(self, data_provider: Callable):
        super().__init__()
        self.data_provider = data_provider
        self.current_chunk = 0
        self.total_items = 0
    
    def load_chunk(self, chunk_index: int) -> None:
        """Load a chunk of data."""
        start = chunk_index * self.CHUNK_SIZE
        end = start + self.CHUNK_SIZE
        rows = self.data_provider(start, end)
        
        for row in rows:
            self.add_row(*row)
    
    def on_scroll(self, event: ScrollEvent) -> None:
        """Load more data when scrolling near bottom."""
        if event.y > (self.row_count - 10):
            self.load_chunk(self.current_chunk + 1)
            self.current_chunk += 1
```

### 5. Search/Filter Implementation
**Pattern**: Input widget + live filtering

```python
class SearchableTable(Container):
    """DataTable with integrated search."""
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield DataTable(id="data-table")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter table rows based on search query."""
        query = event.value.lower()
        table = self.query_one("#data-table", DataTable)
        
        # Filter rows (simple substring match)
        visible_rows = []
        for row in self.all_rows:
            if any(query in str(cell).lower() for cell in row):
                visible_rows.append(row)
        
        # Update table
        table.clear()
        for row in visible_rows:
            table.add_row(*row)
```

## Implementation Steps

1. **Upgrade Strings View** (6 hours)
   - Replace Static with DataTable
   - Add columns and populate from report.strings
   - Implement string categorization logic
   - Add search input with live filtering
   - Add category dropdown filter
   - Add min length filter
   - Color-code suspicious strings
   - Test with binary containing 10,000+ strings

2. **Upgrade Imports/Exports View** (5 hours)
   - Create split layout with two sections
   - Replace Static with two DataTables
   - Implement risk assessment logic for imports
   - Color-code by risk level (red/yellow/green)
   - Add search for both imports and exports
   - Add library filter dropdown for imports
   - Test with binary with 1,000+ imports

3. **Create Functions View** (6 hours)
   - Create new FunctionsView class
   - Implement Tree widget for function hierarchy
   - Group functions by library/section
   - Add DataTable for function details
   - Synchronize tree selection with details table
   - Display function metadata (address, size, calls)
   - Test with complex binary (many functions)

4. **Implement Pagination** (4 hours)
   - Create PaginatedDataTable base class
   - Implement lazy loading logic
   - Add scroll event handling
   - Test with 10,000+ item datasets
   - Measure performance (load time <500ms per chunk)

5. **Add Search/Filter UI** (3 hours)
   - Create reusable SearchableTable component
   - Implement debounced filtering (300ms delay)
   - Add "X results found" indicator
   - Add clear button for filters
   - Test search performance

6. **Testing** (4 hours)
   - Test each view with various binaries
   - Test search/filter with edge cases (empty query, no results)
   - Test sorting by clicking column headers
   - Test keyboard navigation in tables (arrows, page up/down)
   - Performance test with large datasets
   - Test selection and detail panel integration

## Code Example

```python
# caspoon/ui/views/strings_view.py
from textual.widgets import DataTable, Input, Select
from textual.containers import Container, Horizontal
from textual.app import ComposeResult
from caspoon.models import ExecutableReport
import re

class StringsView(Container):
    """Enhanced strings view with interactive table."""
    
    BINDINGS = [
        ("ctrl+f", "focus_search", "Search"),
        ("escape", "clear_search", "Clear"),
    ]
    
    def __init__(self):
        super().__init__()
        self.all_strings = []  # Cache all strings
        self.filtered_strings = []
    
    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-bar", classes="filter-bar"):
            yield Input(
                placeholder="Search strings...",
                id="string-search"
            )
            yield Select(
                options=[
                    ("All Categories", "all"),
                    ("URLs", "url"),
                    ("File Paths", "path"),
                    ("Suspicious", "suspicious"),
                ],
                id="category-filter",
                value="all"
            )
            yield Input(
                placeholder="Min length",
                id="min-length",
                max_length=4
            )
        
        yield DataTable(
            id="strings-table",
            cursor_type="row",
            zebra_stripes=True
        )
    
    def update_data(self, report: ExecutableReport) -> None:
        """Populate table with strings from report."""
        self.all_strings = report.strings
        self._apply_filters()
    
    def _apply_filters(self) -> None:
        """Apply current filters and update table."""
        # Get filter values
        search_query = self.query_one("#string-search", Input).value.lower()
        category_filter = self.query_one("#category-filter", Select).value
        min_length_str = self.query_one("#min-length", Input).value
        min_length = int(min_length_str) if min_length_str.isdigit() else 0
        
        # Filter strings
        filtered = []
        for string_obj in self.all_strings:
            # Apply filters
            if len(string_obj.value) < min_length:
                continue
            
            if search_query and search_query not in string_obj.value.lower():
                continue
            
            category = self._categorize_string(string_obj.value)
            if category_filter != "all" and category.lower() != category_filter:
                continue
            
            filtered.append((string_obj, category))
        
        self.filtered_strings = filtered
        self._update_table()
    
    def _update_table(self) -> None:
        """Update DataTable with filtered strings."""
        table = self.query_one("#strings-table", DataTable)
        table.clear(columns=True)
        
        # Add columns
        table.add_columns("String", "Length", "Encoding", "Category")
        
        # Add rows
        for string_obj, category in self.filtered_strings:
            # Determine row style based on category
            if category == "Suspicious":
                style = "bold red"
            elif category == "URL":
                style = "cyan"
            elif category == "Path":
                style = "yellow"
            else:
                style = None
            
            table.add_row(
                string_obj.value[:100],  # Truncate long strings
                str(len(string_obj.value)),
                string_obj.encoding or "ASCII",
                category,
                style=style
            )
        
        # Update status
        self.post_message(StatusUpdate(f"{len(self.filtered_strings)} strings"))
    
    def _categorize_string(self, value: str) -> str:
        """Categorize string by content."""
        if re.match(r'https?://', value, re.IGNORECASE):
            return "URL"
        elif re.match(r'[A-Z]:\\|^/', value):
            return "Path"
        elif any(sus in value.lower() for sus in ['password', 'secret', 'token', 'api_key']):
            return "Suspicious"
        elif re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', value):
            return "Email"
        else:
            return "Generic"
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Re-filter when any filter changes."""
        self._apply_filters()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Re-filter when category changes."""
        self._apply_filters()
    
    def action_focus_search(self) -> None:
        """Focus search input."""
        self.query_one("#string-search", Input).focus()
    
    def action_clear_search(self) -> None:
        """Clear all filters."""
        self.query_one("#string-search", Input).value = ""
        self.query_one("#min-length", Input).value = ""
        self._apply_filters()
```

## Testing Strategy

### Unit Tests
Create `tests/ui/views/test_strings_view.py`:
- Test string categorization logic
- Test filtering with various queries
- Test min length filter
- Test category filter
- Test table population

### Integration Tests
- Load binary with many strings
- Type in search → table updates instantly
- Select category "URLs" → only URLs shown
- Enter min length "10" → short strings filtered out
- Clear filters → all strings reappear
- Click column header → table sorts by that column

### Performance Tests
- Test with 10,000 strings → initial load <1 second
- Test filtering 10,000 strings → filter updates <300ms
- Test scrolling performance → smooth, no lag
- Test memory usage → no leaks from repeated filtering

## Dependencies
- Textual widgets: DataTable, Input, Select, Tree
- Python regex for string categorization
- No new external dependencies

## Estimated Time
**28 hours total**
- Implementation: 24 hours
- Testing: 4 hours

## Success Criteria
- [ ] Strings view uses DataTable with search/filter
- [ ] Imports/exports view split with color-coded risk levels
- [ ] Functions view created with Tree + DataTable
- [ ] Pagination works smoothly with large datasets
- [ ] Search updates in <300ms (debounced)
- [ ] Color-coding applied correctly
- [ ] Tables sortable by clicking headers
- [ ] Keyboard navigation works (arrows, page up/down)
- [ ] Selection emits events for detail panel
- [ ] No performance degradation with 10,000+ items

## Next Steps
After completion, proceed to Subtask 4: Detail Panel to add context-aware information display.
