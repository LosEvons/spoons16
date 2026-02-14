# Subtask 7: Multi-Panel Layout

## Objective

Implement a multi-panel docking layout with collapsible sidebar (tree navigation), right details panel, and bottom console, enabling multi-screen workflows and creating specialized widgets (FunctionExplorer, HexViewer) for enhanced analysis.

## Scope

**Included:**
- MainScreen with multi-panel grid layout (sidebar, content, details, console)
- Collapsible panel system with keyboard shortcuts (Ctrl+B, Ctrl+D, Ctrl+J)
- Sidebar widget with function tree navigation
- Details panel for contextual information
- Bottom console for logs/output
- FunctionExplorer widget (TreeView-based function browser)
- HexViewer widget (optional, time permitting)
- Panel state persistence in AppState
- Responsive layout that adapts to panel visibility
- Multi-screen support and layout optimization

**Excluded:**
- Drag-and-drop panel rearrangement (future enhancement)
- Custom panel layouts (future enhancement)
- Split view / side-by-side comparison (future enhancement)
- Persistent user layout preferences (save/load - future enhancement)

## Technical Approach

### 1. MainScreen Layout
**Location**: `caspoon/ui/screens/main.py`

New screen replacing existing composition:

- **Grid Layout**:
  ```
  ┌────────────┬──────────────────────┬────────────┐
  │  Sidebar   │   Content Area       │  Details   │
  │  (Tree)    │   (Tabbed Views)     │  (Info)    │
  │            │                      │            │
  │            ├──────────────────────┤            │
  │            │   Bottom Console     │            │
  └────────────┴──────────────────────┴────────────┘
  ```
- **Panel Widths**: Sidebar 20%, Content 55%, Details 25%
- **Console Height**: 10 lines (collapsed) or 30% (expanded)
- **Dynamic**: Panels can be hidden, layout re-flows
- **Textual Grid**: Use Container with CSS Grid for layout

### 2. Collapsible Panels
**Location**: Panel widgets and MainScreen

Each panel can be toggled:

- **Sidebar**:
  - Keybinding: Ctrl+B
  - Shows function tree and navigation
  - Collapses to 0 width when hidden
- **Details Panel**:
  - Keybinding: Ctrl+D
  - Shows contextual info (function details, string info, etc.)
  - Collapses to 0 width when hidden
- **Bottom Console**:
  - Keybinding: Ctrl+J
  - Shows analysis logs, errors, debug output
  - Collapses to 0 height when hidden
- **State Storage**: Panel visibility in AppState.ui_state (sidebar_visible, details_visible, console_visible)

### 3. Sidebar Widget
**Location**: `caspoon/ui/widgets/sidebar.py`

Navigation sidebar with function tree:

- **Components**:
  - Title: "Navigation"
  - FunctionExplorer widget (see below)
  - Filter input (quick search)
- **Layout**: Vertical container with filter at top, tree below
- **Integration**: Watches AppState.analysis_results for function list

### 4. Details Panel Widget
**Location**: `caspoon/ui/widgets/details_panel.py`

Context-sensitive information display:

- **Displays**:
  - Selected function details (address, size, calls, etc.)
  - Selected string details (offset, encoding, references)
  - Import/export details (library, type, etc.)
  - Current view help text
- **Updates**: Watches AppState.ui_state.selected_* properties
- **Layout**: Scrollable container with formatted text

### 5. Bottom Console Widget
**Location**: `caspoon/ui/widgets/console.py`

Log and output display:

- **Shows**:
  - Analysis progress messages
  - Error messages
  - Debug logs (if enabled)
  - User notifications
- **Features**:
  - Auto-scroll to bottom
  - Clear button
  - Expandable (Ctrl+J toggles size)
  - Color-coded messages (error=red, warning=yellow, info=white)

### 6. FunctionExplorer Widget
**Location**: `caspoon/ui/widgets/function_explorer.py`

TreeView-based function browser:

- **Inheritance**: Extends TreeView from Subtask 2
- **Hierarchy**:
  - Root nodes: Sections (.text, .plt, etc.)
  - Child nodes: Functions in each section
- **Display**: Function name, address, size
- **Interaction**:
  - Select function → jump to disassembly
  - Enter → navigate to function details
- **Sorting**: Alphabetical or by address
- **Filtering**: Quick filter by function name

### 7. HexViewer Widget (Optional)
**Location**: `caspoon/ui/widgets/hex_viewer.py`

Hex dump display (if time permits):

- **Inheritance**: BaseView or custom widget
- **Display**: Classic hex dump format (address, hex bytes, ASCII)
- **Navigation**: Scroll through binary data
- **Integration**: Show hex at selected address
- **Features**: Address highlighting, goto address

## Implementation Steps

### Step 1: Create MainScreen Layout (3 hours)
Create `caspoon/ui/screens/main.py`:
- Import Container, Grid, Vertical from Textual
- Create MainScreen(Screen) class:
  ```python
  from textual.screen import Screen
  from textual.containers import Container, Vertical, Horizontal
  from textual.binding import Binding
  from textual.widgets import Header, Footer
  
  class MainScreen(Screen):
      """Main screen with multi-panel layout."""
      
      BINDINGS = [
          Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
          Binding("ctrl+d", "toggle_details", "Toggle Details"),
          Binding("ctrl+j", "toggle_console", "Toggle Console"),
      ]
      
      CSS = """
      MainScreen {
          layout: grid;
          grid-size: 3 2;
          grid-columns: 20fr 55fr 25fr;
          grid-rows: 1fr auto;
      }
      
      #sidebar {
          column-span: 1;
          row-span: 2;
          border: solid green;
      }
      
      #content {
          column-span: 1;
          row-span: 1;
      }
      
      #details {
          column-span: 1;
          row-span: 2;
          border: solid blue;
      }
      
      #console {
          column-span: 1;
          row-span: 1;
          border: solid yellow;
          height: 10;
      }
      
      .hidden {
          display: none;
      }
      """
      
      def compose(self):
          from caspoon.ui.widgets.sidebar import Sidebar
          from caspoon.ui.widgets.details_panel import DetailsPanel
          from caspoon.ui.widgets.console import Console
          
          yield Header()
          yield Sidebar(id="sidebar")
          yield Container(id="content")  # Content area (existing views)
          yield DetailsPanel(id="details")
          yield Console(id="console")
          yield Footer()
      
      def action_toggle_sidebar(self):
          sidebar = self.query_one("#sidebar")
          sidebar.toggle_class("hidden")
          self.app.state.ui_state.sidebar_visible = not sidebar.has_class("hidden")
      
      def action_toggle_details(self):
          details = self.query_one("#details")
          details.toggle_class("hidden")
          self.app.state.ui_state.details_visible = not details.has_class("hidden")
      
      def action_toggle_console(self):
          console = self.query_one("#console")
          console.toggle_class("hidden")
          self.app.state.ui_state.console_visible = not console.has_class("hidden")
  ```
- Add CSS grid styling for responsive layout
- Implement toggle actions for each panel

### Step 2: Implement Sidebar Widget (2.5 hours)
Create `caspoon/ui/widgets/sidebar.py`:
- Create Sidebar(Container) class
- Add composition: Title + Filter Input + FunctionExplorer
- Connect to AppState for function list updates
- Implement quick filter for function search
- Style with border and title

### Step 3: Implement FunctionExplorer Widget (4 hours)
Create `caspoon/ui/widgets/function_explorer.py`:
- Import TreeView from core.base
- Create FunctionExplorer(TreeView) class:
  ```python
  from caspoon.ui.core.base import TreeView, TreeNode
  from caspoon.ui.core.models import AnalysisResults
  
  class FunctionExplorer(TreeView[AnalysisResults]):
      """Tree view of functions organized by section."""
      
      def __init__(self, **kwargs):
          super().__init__(**kwargs)
          self._functions = []
          self._sections = {}
      
      def on_mount(self):
          self.app.state.analysis_results.watch(self, "_on_results_changed")
      
      def _on_results_changed(self, old, new):
          self.data = new
      
      def render_content(self, data: AnalysisResults):
          """Organize functions by section and render tree."""
          self._functions = data.functions or []
          self._organize_by_section()
          self._render_tree()
      
      def _organize_by_section(self):
          """Group functions by section."""
          self._sections = {}
          for func in self._functions:
              section = func.get('section', '.text')
              if section not in self._sections:
                  self._sections[section] = []
              self._sections[section].append(func)
      
      def get_root_nodes(self) -> list[TreeNode]:
          """Return section nodes."""
          nodes = []
          for section, funcs in self._sections.items():
              node = TreeNode(
                  node_id=section,
                  label=f"{section} ({len(funcs)} functions)",
                  has_children=len(funcs) > 0,
                  data=section
              )
              nodes.append(node)
          return nodes
      
      def get_child_nodes(self, node_id: str) -> list[TreeNode]:
          """Return function nodes for section."""
          if node_id in self._sections:
              funcs = self._sections[node_id]
              return [
                  TreeNode(
                      node_id=f"func_{func['address']}",
                      label=f"{func['name']} (0x{func['address']:08x})",
                      has_children=False,
                      data=func
                  )
                  for func in funcs
              ]
          return []
      
      def get_item_count(self) -> int:
          return len(self._flatten_tree())
      
      def on_item_selected(self, index: int):
          """Navigate to selected function."""
          nodes = self._flatten_tree()
          if 0 <= index < len(nodes):
              node, _ = nodes[index]
              if isinstance(node.data, dict):  # Function node
                  from caspoon.ui.core.messages import SelectFunction
                  self.post_message(SelectFunction(node.data['name'], node.data['address']))
      
      def apply_filter(self, text: str):
          """Filter functions by name."""
          # Implementation: filter self._functions by text
          pass
  ```
- Implement tree rendering using Rich Tree
- Add selection handling to jump to function
- Add filtering support

### Step 4: Implement DetailsPanel Widget (2 hours)
Create `caspoon/ui/widgets/details_panel.py`:
- Create DetailsPanel(Container) class
- Watch AppState.ui_state.selected_function
- Display function details when function selected:
  - Name, address, size
  - Call references
  - Cross-references
  - Disassembly snippet
- Handle different selection types (function, string, import)
- Style with panels and formatting

### Step 5: Implement Console Widget (2 hours)
Create `caspoon/ui/widgets/console.py`:
- Create Console(Container) class
- Use RichLog widget from Textual
- Add message handler for log messages:
  ```python
  from textual.widgets import RichLog
  
  class Console(Container):
      """Bottom console for logs and messages."""
      
      def compose(self):
          yield RichLog(id="log", wrap=True, highlight=True)
      
      def write_log(self, message: str, level: str = "info"):
          """Write message to console."""
          log = self.query_one("#log", RichLog)
          
          if level == "error":
              log.write(f"[red]ERROR: {message}[/]")
          elif level == "warning":
              log.write(f"[yellow]WARNING: {message}[/]")
          elif level == "success":
              log.write(f"[green]{message}[/]")
          else:
              log.write(message)
      
      def clear(self):
          """Clear console."""
          log = self.query_one("#log", RichLog)
          log.clear()
  ```
- Add clear button
- Auto-scroll to latest message
- Color-code by message level

### Step 6: Integrate MainScreen into App (2 hours)
Modify `caspoon/ui/app.py`:
- Replace existing compose() with MainScreen:
  ```python
  def compose(self):
      from caspoon.ui.screens.main import MainScreen
      yield MainScreen()
  ```
- Move existing content views into MainScreen's content area
- Ensure CommandPalette still overlays correctly
- Update message handlers to write to console
- Test panel toggles work

### Step 7: Update AppState for Panel Visibility (1 hour)
Modify `caspoon/ui/core/models.py`:
- Add panel visibility to UIState:
  ```python
  @dataclass
  class UIState:
      # ... existing fields ...
      sidebar_visible: bool = True
      details_visible: bool = True
      console_visible: bool = True
      console_expanded: bool = False
  ```
- MainScreen reads these on mount to set initial visibility
- Panel toggles update these values

### Step 8: Implement HexViewer (Optional, 3 hours)
Create `caspoon/ui/widgets/hex_viewer.py` if time permits:
- Create HexViewer(BaseView) class
- Display hex dump format
- Implement scrolling and navigation
- Add goto address feature
- Integrate into content area or details panel

### Step 9: Unit Tests for Widgets (3 hours)
Create tests for each new widget:
- `test_sidebar.py`:
  - Test sidebar composition
  - Test function filter
  - Test visibility toggle
- `test_function_explorer.py`:
  - Test tree structure (sections → functions)
  - Test node expansion
  - Test function selection
  - Test filtering
- `test_details_panel.py`:
  - Test displays function details
  - Test handles different selection types
  - Test updates on selection change
- `test_console.py`:
  - Test log writing
  - Test color coding
  - Test clear functionality
  - Test auto-scroll
- Aim for >80% coverage per widget

### Step 10: Integration Tests (2 hours)
Create `caspoon/tests/integration/ui/test_multi_panel_layout.py`:
- `test_main_screen_layout()` - All panels present
- `test_toggle_sidebar()` - Ctrl+B toggles sidebar
- `test_toggle_details()` - Ctrl+D toggles details
- `test_toggle_console()` - Ctrl+J toggles console
- `test_function_explorer_navigation()` - Select function → content updates
- `test_details_panel_shows_selection()` - Selection updates details
- `test_console_receives_logs()` - Log messages appear in console
- `test_responsive_layout()` - Layout adapts to panel visibility
- Use app.run_test() with full app

### Step 11: Manual Testing (2 hours)
Test multi-panel layout interactively:
- Launch TUI and load binary
- Test sidebar:
  - Verify function tree displays
  - Test expand/collapse sections
  - Test function selection
  - Test filter
- Test details panel:
  - Select function → see details
  - Select string → see string info
  - Verify updates in real-time
- Test console:
  - Verify analysis logs appear
  - Test clear button
  - Test expand/collapse
- Test panel toggles:
  - Ctrl+B hides/shows sidebar
  - Ctrl+D hides/shows details
  - Ctrl+J hides/shows console
  - Layout re-flows correctly
- Test on different terminal sizes:
  - 80x24 (minimum)
  - 120x40 (medium)
  - 200x60 (large)
- Verify no visual glitches

### Step 12: Documentation and Validation (30 minutes)
- Add docstrings to all new widgets
- Create `caspoon/docs/guides/multi-panel-layout.md`:
  - Explain panel system
  - Document keyboard shortcuts
  - Show layout diagram
  - Explain FunctionExplorer usage
- Update main README with multi-panel info
- Verify all tests pass
- Check coverage for new widgets
- Final smoke test

## Code Example

See implementation details in steps above. Key example of MainScreen in Step 1.

## Testing Strategy

### Unit Tests

**Widget Tests**:
- Sidebar composition and filtering
- FunctionExplorer tree structure and navigation
- DetailsPanel display logic
- Console logging and formatting
- Aim for >80% coverage per widget

### Integration Tests

**Layout Tests**:
- Panel visibility toggles
- Layout responsiveness
- Widget communication
- State synchronization

### Manual Testing

- Interactive testing of all panels
- Different terminal sizes
- Visual appearance validation
- Performance with large datasets

## Dependencies

- **Subtask 1**: Requires AppState, messages
- **Subtask 2**: Requires TreeView base class
- **Subtask 3**: Requires integrated AppState in app
- **Textual**: Container, Grid, RichLog widgets
- **Rich**: Tree, Panel rendering

## Estimated Time

**Total: 4-5 days (32-38 hours)**

Breakdown:
- MainScreen layout: 3 hours
- Sidebar widget: 2.5 hours
- FunctionExplorer: 4 hours
- DetailsPanel: 2 hours
- Console: 2 hours
- App integration: 2 hours
- AppState updates: 1 hour
- HexViewer (optional): 3 hours
- Widget tests: 3 hours
- Integration tests: 2 hours
- Manual testing: 2 hours
- Documentation/validation: 0.5 hours

**Buffer**: 2-4 hours for layout refinement

## Success Criteria

- [ ] MainScreen with grid layout implemented
- [ ] Sidebar with FunctionExplorer displays on left
- [ ] Content area shows existing views (Overview, Strings, etc.)
- [ ] Details panel displays on right
- [ ] Bottom console displays logs and messages
- [ ] Ctrl+B toggles sidebar visibility
- [ ] Ctrl+D toggles details panel visibility
- [ ] Ctrl+J toggles console visibility
- [ ] Layout re-flows when panels hidden/shown
- [ ] FunctionExplorer shows function tree by section
- [ ] FunctionExplorer selection jumps to disassembly
- [ ] FunctionExplorer filtering works
- [ ] DetailsPanel shows selected function details
- [ ] Console displays color-coded messages
- [ ] Console clear button works
- [ ] Panel visibility state persisted in AppState
- [ ] Widget unit tests pass (minimum 20 tests)
- [ ] Integration tests pass (minimum 8 tests)
- [ ] Test coverage >80% for new widgets
- [ ] Manual testing shows good UX
- [ ] Works on terminals 80x24 and larger
- [ ] No performance degradation
- [ ] Documentation complete

## Next Steps

After completing this subtask:
1. **Advanced Layout Complete**: Users have professional multi-panel interface
2. **Proceed to Subtask 8**: Final testing, optimization, and polish
3. **User Feedback**: Gather feedback on panel layout and usability
4. **Future Enhancements**: Drag-and-drop panels, custom layouts, split views
5. **Optional**: HexViewer if not completed in this subtask
