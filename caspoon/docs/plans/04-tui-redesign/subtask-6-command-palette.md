# Subtask 6: Command Palette

## Objective

Create a Ctrl+P-style command palette widget with fuzzy search, integrate it into CaspoonApp, and register comprehensive commands for keyboard-driven workflows across all TUI functionality.

## Scope

**Included:**
- CommandPalette widget with fuzzy search UI
- Command search and filtering (substring matching, fuzzy scoring)
- Action execution via ActionRegistry integration
- Keyboard navigation in command palette (up/down/enter/escape)
- Comprehensive command registration (file operations, view switching, analysis control, navigation)
- Keybinding display in command palette
- Category-based command organization
- Unit tests for command palette widget
- Integration tests for command execution

**Excluded:**
- Custom keyboard shortcut configuration (future enhancement)
- Command history/favorites (future enhancement)
- Multi-panel layout (covered in Subtask 7)
- Command chaining/macros (future enhancement)

## Technical Approach

### 1. CommandPalette Widget
**Location**: `caspoon/ui/widgets/command_palette.py`

Modal overlay widget activated by Ctrl+P:

- **Layout**:
  - Input field at top for search query
  - ListView below showing filtered commands
  - Max 10-15 visible results with scrolling
- **Behavior**:
  - Opens centered, semi-transparent overlay
  - Focus on input field when opened
  - Real-time filtering as user types
  - Up/Down to navigate results
  - Enter to execute selected command
  - Escape to close without executing
- **Display Format**: `Command Name    (Keybinding)    Category`
- **Integration**: Uses ActionRegistry from app.action_registry

### 2. Fuzzy Search
**Location**: `caspoon/ui/widgets/command_palette.py` or `caspoon/ui/core/search.py`

Search algorithm for command matching:

- **Substring Match**: Primary matching (fast, simple)
- **Case-Insensitive**: All matching case-insensitive
- **Score Ranking**:
  - Exact name match: score 100
  - Name starts with query: score 80
  - Name contains query: score 60
  - Description contains query: score 40
  - Category contains query: score 20
- **Sorting**: Results sorted by score (highest first)
- **Optional**: Fuzzy matching library (fuzzywuzzy, rapidfuzz) for better UX

### 3. Command Registration
**Location**: `caspoon/ui/app.py`

Register all app actions on startup:

**File Commands**:
- Open Binary (Ctrl+O)
- Close Binary (Ctrl+W)
- Quit Application (Ctrl+Q)
- Reload Binary (Ctrl+R)

**View Commands**:
- Switch to Overview (1)
- Switch to Protections (2)
- Switch to Strings (3)
- Switch to Imports/Exports (4)
- Switch to Disassembly (5)
- Next Tab (Ctrl+Tab)
- Previous Tab (Ctrl+Shift+Tab)

**Analysis Commands**:
- Start Analysis (F5)
- Cancel Analysis (Ctrl+C)
- Re-analyze (Shift+F5)

**Navigation Commands**:
- Jump to Function (Ctrl+F)
- Jump to Address (Ctrl+G)
- Go Back (Alt+Left)
- Go Forward (Alt+Right)

**Filter Commands**:
- Focus Filter (/)
- Clear Filter (Ctrl+Shift+F)

**Panel Commands** (for Subtask 7):
- Toggle Sidebar (Ctrl+B)
- Toggle Details (Ctrl+D)
- Toggle Console (Ctrl+J)

**Help Commands**:
- Show Help (F1)
- Show Keybindings (Ctrl+?)
- Show Command Palette (Ctrl+P)

### 4. Integration with CaspoonApp
**Location**: `caspoon/ui/app.py`

Wire up command palette:

- **Initialization**: Create ActionRegistry and register all commands in `__init__`
- **Keybinding**: Bind Ctrl+P to show command palette
- **Action Handlers**: Implement handler methods for each action
- **Command Palette Mount**: Add CommandPalette to screen composition (hidden by default)
- **Execution**: CommandPalette executes via `app.action_registry.execute(action_id)`

## Implementation Steps

### Step 1: Create CommandPalette Widget (4 hours)
Create `caspoon/ui/widgets/command_palette.py`:
- Import Textual widgets: Container, Input, ListView, ListItem, Label
- Import Binding for keybindings
- Create CommandPalette(Container) class:
  ```python
  from textual.containers import Container, Vertical
  from textual.widgets import Input, ListView, ListItem, Label
  from textual.binding import Binding
  
  class CommandPalette(Container):
      """Fuzzy-search command palette (Ctrl+P style).
      
      Provides quick keyboard-driven access to all app commands.
      """
      
      DEFAULT_CSS = """
      CommandPalette {
          display: none;
          layer: overlay;
          align: center middle;
          width: 70%;
          height: 60%;
          background: $surface;
          border: thick $primary;
      }
      
      CommandPalette.visible {
          display: block;
      }
      
      CommandPalette Input {
          margin: 1;
          border: solid $accent;
      }
      
      CommandPalette ListView {
          height: 1fr;
          margin: 0 1 1 1;
      }
      """
      
      BINDINGS = [
          Binding("escape", "close", "Close", show=False),
          Binding("up", "cursor_up", "Up", show=False),
          Binding("down", "cursor_down", "Down", show=False),
          Binding("enter", "execute", "Execute", show=True),
      ]
      
      def __init__(self, action_registry, **kwargs):
          super().__init__(**kwargs)
          self.action_registry = action_registry
          self._filtered_actions = []
          self._selected_index = 0
      
      def compose(self):
          with Vertical():
              yield Input(placeholder="Type to search commands...", id="search")
              yield ListView(id="results")
      
      def on_mount(self):
          """Focus search input when mounted."""
          self.query_one("#search", Input).focus()
      
      def on_show(self):
          """Reset and show all commands when palette shown."""
          search_input = self.query_one("#search", Input)
          search_input.value = ""
          search_input.focus()
          self._update_results("")
      
      def on_input_changed(self, event: Input.Changed):
          """Filter commands as user types."""
          if event.input.id == "search":
              self._update_results(event.value)
      
      def _update_results(self, query: str):
          """Update result list with filtered commands."""
          # Search actions
          self._filtered_actions = self.action_registry.search(query)
          
          # Update ListView
          results = self.query_one("#results", ListView)
          results.clear()
          
          for action in self._filtered_actions[:15]:  # Top 15
              keybind = f"({action.keybinding})" if action.keybinding else ""
              label_text = f"{action.name}  [dim]{keybind}[/]  [dim italic]{action.category}[/]"
              
              results.append(ListItem(Label(label_text), id=action.action_id))
      
      def action_execute(self):
          """Execute selected command."""
          results = self.query_one("#results", ListView)
          if results.highlighted_child:
              action_id = results.highlighted_child.id
              self.action_registry.execute(action_id)
              self.action_close()
      
      def action_close(self):
          """Close command palette."""
          self.add_class("hidden")
          self.remove_class("visible")
  ```
- Add CSS styling for modal overlay appearance
- Implement keyboard navigation (up/down within ListView)
- Add visual highlighting for selected command

### Step 2: Implement Search Logic (2 hours)
Add search scoring to ActionRegistry or separate module:
- Update `caspoon/ui/core/actions.py` with improved search:
  ```python
  def search(self, query: str) -> list[Action]:
      """Search actions with scoring.
      
      Args:
          query: Search query string
      
      Returns:
          List of matching actions, sorted by relevance
      """
      if not query:
          # Return all enabled actions
          return [a for a in self._actions.values() if a.enabled]
      
      query_lower = query.lower()
      scored = []
      
      for action in self._actions.values():
          if not action.enabled:
              continue
          
          score = 0
          name_lower = action.name.lower()
          desc_lower = action.description.lower()
          
          # Exact match
          if name_lower == query_lower:
              score = 100
          # Name starts with query
          elif name_lower.startswith(query_lower):
              score = 80
          # Name contains query
          elif query_lower in name_lower:
              score = 60
          # Description contains query
          elif query_lower in desc_lower:
              score = 40
          # Category contains query
          elif query_lower in action.category.lower():
              score = 20
          
          if score > 0:
              scored.append((score, action))
      
      # Sort by score (descending)
      scored.sort(key=lambda x: x[0], reverse=True)
      return [action for score, action in scored]
  ```

### Step 3: Register Commands in App (3 hours)
Modify `caspoon/ui/app.py`:
- Add method `_register_commands()` called in `__init__`:
  ```python
  def _register_commands(self):
      """Register all application commands."""
      reg = self.action_registry
      
      # File commands
      reg.register("file.open", "Open Binary", self.action_open_binary,
                   "Open a binary file for analysis", "ctrl+o", "File")
      reg.register("file.close", "Close Binary", self.action_close_binary,
                   "Close current binary", "ctrl+w", "File")
      reg.register("file.reload", "Reload Binary", self.action_reload_binary,
                   "Reload current binary", "ctrl+r", "File")
      reg.register("file.quit", "Quit", self.action_quit,
                   "Exit the application", "ctrl+q", "File")
      
      # View commands
      reg.register("view.overview", "Show Overview", lambda: self.action_switch_tab("overview"),
                   "Switch to Overview tab", "1", "View")
      reg.register("view.protections", "Show Protections", lambda: self.action_switch_tab("protections"),
                   "Switch to Protections tab", "2", "View")
      reg.register("view.strings", "Show Strings", lambda: self.action_switch_tab("strings"),
                   "Switch to Strings tab", "3", "View")
      reg.register("view.imports", "Show Imports/Exports", lambda: self.action_switch_tab("imports"),
                   "Switch to Imports/Exports tab", "4", "View")
      reg.register("view.disassembly", "Show Disassembly", lambda: self.action_switch_tab("disassembly"),
                   "Switch to Disassembly tab", "5", "View")
      
      # Analysis commands
      reg.register("analysis.start", "Start Analysis", self.action_start_analysis,
                   "Analyze current binary", "f5", "Analysis")
      reg.register("analysis.cancel", "Cancel Analysis", self.action_cancel_analysis,
                   "Cancel ongoing analysis", "ctrl+c", "Analysis")
      
      # Navigation commands
      reg.register("nav.jump_function", "Jump to Function", self.action_jump_to_function,
                   "Jump to a specific function", "ctrl+f", "Navigation")
      reg.register("nav.jump_address", "Jump to Address", self.action_jump_to_address,
                   "Jump to a specific address", "ctrl+g", "Navigation")
      
      # Filter commands
      reg.register("filter.focus", "Focus Filter", self.action_focus_filter,
                   "Focus the filter input", "/", "Filter")
      reg.register("filter.clear", "Clear Filter", self.action_clear_filter,
                   "Clear current filter", "ctrl+shift+f", "Filter")
      
      # Help commands
      reg.register("help.show", "Show Help", self.action_show_help,
                   "Show help documentation", "f1", "Help")
      reg.register("help.keybindings", "Show Keybindings", self.action_show_keybindings,
                   "Show all keybindings", "ctrl+?", "Help")
      reg.register("help.command_palette", "Show Command Palette", self.action_show_command_palette,
                   "Open command palette", "ctrl+p", "Help")
  ```
- Implement action handler methods (stub implementations initially):
  ```python
  def action_open_binary(self):
      """Show file open dialog."""
      # Implementation from existing code
      pass
  
  def action_switch_tab(self, tab_id: str):
      """Switch to specified tab."""
      # Implementation: self.query_one(TabbedContent).active = tab_id
      pass
  
  def action_jump_to_function(self):
      """Show function jump dialog."""
      # Implementation: show input dialog for function name
      pass
  
  # ... etc for all commands
  ```

### Step 4: Integrate CommandPalette into App (2 hours)
Modify `caspoon/ui/app.py`:
- Add CommandPalette to screen composition:
  ```python
  def compose(self):
      yield Header()
      # ... existing widgets ...
      yield Footer()
      
      # Command palette (hidden by default)
      yield CommandPalette(self.action_registry, id="command_palette", classes="hidden")
  ```
- Add Ctrl+P keybinding:
  ```python
  BINDINGS = [
      Binding("ctrl+p", "show_command_palette", "Commands"),
      # ... other bindings ...
  ]
  
  def action_show_command_palette(self):
      """Show command palette."""
      palette = self.query_one("#command_palette", CommandPalette)
      palette.remove_class("hidden")
      palette.add_class("visible")
      palette.on_show()
  ```
- Handle command palette close (Escape key)

### Step 5: Unit Tests for CommandPalette (2.5 hours)
Create `caspoon/tests/unit/ui/widgets/test_command_palette.py`:
- `test_command_palette_initialization()` - Can create with registry
- `test_command_palette_compose()` - Has Input and ListView
- `test_command_palette_shows_all_when_empty()` - Empty query shows all
- `test_command_palette_filters_by_name()` - Filter by command name
- `test_command_palette_filters_by_description()` - Filter by description
- `test_command_palette_filters_by_category()` - Filter by category
- `test_command_palette_keyboard_navigation()` - Up/down moves selection
- `test_command_palette_execute_command()` - Enter executes selected
- `test_command_palette_close()` - Escape closes palette
- `test_command_palette_displays_keybindings()` - Shows keybinding in results
- `test_command_palette_limits_results()` - Max 15 results shown
- Mock ActionRegistry with test actions
- Use Textual's Pilot for widget testing
- Aim for >85% coverage

### Step 6: Unit Tests for Search (1.5 hours)
Create or update `caspoon/tests/unit/ui/core/test_actions.py`:
- `test_search_empty_query()` - Returns all enabled actions
- `test_search_exact_match()` - Exact match scores highest
- `test_search_name_starts_with()` - Prefix match high score
- `test_search_name_contains()` - Contains match medium score
- `test_search_description_contains()` - Description match lower score
- `test_search_category_contains()` - Category match lowest score
- `test_search_case_insensitive()` - Case doesn't affect matching
- `test_search_sorting()` - Results sorted by score
- `test_search_disabled_excluded()` - Disabled actions not in results
- Create ActionRegistry with diverse test actions
- Aim for >90% coverage of search method

### Step 7: Integration Tests (2 hours)
Create `caspoon/tests/integration/ui/test_command_palette.py`:
- `test_open_command_palette()` - Ctrl+P opens palette
- `test_search_and_execute()` - Type, select, execute command
- `test_close_palette()` - Escape closes palette
- `test_command_execution_via_palette()` - Command actually executes
- `test_palette_with_real_commands()` - Test with registered app commands
- `test_keybinding_display()` - Keybindings shown in palette
- `test_category_filtering()` - Can filter by category
- Use Textual's app.run_test() for full app testing
- Mock command handlers to verify execution
- Verify state changes (e.g., tab switches)

### Step 8: Manual Testing (1.5 hours)
Test command palette interactively:
- Launch TUI: `python -m caspoon.ui`
- Press Ctrl+P → verify palette opens
- Type "open" → verify "Open Binary" appears
- Test navigation: up/down keys work
- Test execution: Enter runs command
- Test escape: palette closes
- Test all command categories:
  - File: open, close, reload, quit
  - View: switch tabs (1-5)
  - Analysis: start, cancel
  - Navigation: jump to function/address
  - Filter: focus, clear
  - Help: show help, keybindings
- Test fuzzy search:
  - Type "bin" → matches "Open Binary"
  - Type "str" → matches "Show Strings"
  - Type partial words → relevant results
- Test visual appearance:
  - Centered modal overlay
  - Readable text and keybindings
  - Selected item highlighted
  - Scrolling works with many results

### Step 9: Implement Action Handlers (2 hours)
Implement stub action handler methods in `caspoon/ui/app.py`:
- `action_open_binary()` - Show file selection (existing code)
- `action_close_binary()` - Clear state, reset views
- `action_reload_binary()` - Re-analyze current file
- `action_quit()` - Exit app (existing)
- `action_switch_tab(tab_id)` - Switch to tab
- `action_start_analysis()` - Post StartAnalysis message
- `action_cancel_analysis()` - Post CancelAnalysis message
- `action_jump_to_function()` - Show function selection dialog
- `action_jump_to_address()` - Show address input dialog
- `action_focus_filter()` - Focus filter input in current view
- `action_clear_filter()` - Clear filter in current view
- `action_show_help()` - Show help screen
- `action_show_keybindings()` - Show keybinding list
- Some handlers may be stubs if full implementation requires Subtask 7

### Step 10: Documentation and Validation (30 minutes)
- Add comprehensive docstrings to CommandPalette
- Create `caspoon/docs/guides/command-palette.md`:
  - Explain Ctrl+P workflow
  - List all available commands by category
  - Show keybindings
  - Include screenshots
- Update main README with command palette info
- Verify all tests pass: `pytest caspoon/tests/unit/ui/widgets/test_command_palette.py -v`
- Check coverage: `pytest --cov=caspoon/ui/widgets/command_palette --cov-report=term-missing`
- Run integration tests: `pytest caspoon/tests/integration/ui/test_command_palette.py -v`
- Final manual smoke test

## Code Example

See full implementation in Step 1 above. Key highlights:

```python
# Usage in app
class CaspoonApp(App):
    BINDINGS = [
        Binding("ctrl+p", "show_command_palette", "Commands"),
    ]
    
    def __init__(self):
        super().__init__()
        self.action_registry = ActionRegistry()
        self._register_commands()
    
    def compose(self):
        yield Header()
        yield MainContent()
        yield Footer()
        yield CommandPalette(self.action_registry, id="command_palette")
    
    def action_show_command_palette(self):
        palette = self.query_one("#command_palette", CommandPalette)
        palette.display = True
        palette.on_show()
```

## Testing Strategy

### Unit Tests

**CommandPalette Widget Tests**:
- Initialization, composition, display
- Filtering and search
- Keyboard navigation
- Command execution
- Close/cancel behavior
- Aim for >85% coverage

**Search Logic Tests**:
- Scoring algorithm
- Case-insensitivity
- Result sorting
- Edge cases (empty, no matches)
- Aim for >90% coverage

### Integration Tests

**Command Palette Integration**:
- Open/close in running app
- Search and execute commands
- Verify command effects
- Test with real ActionRegistry

### Manual Testing

- Interactive testing of all commands
- Visual appearance validation
- Fuzzy search effectiveness
- Performance with many commands

## Dependencies

- **Subtask 1**: Requires ActionRegistry, messages
- **Subtask 3**: Requires CaspoonApp with state
- **Textual**: Container, Input, ListView widgets
- **Rich**: Text formatting and styling

## Estimated Time

**Total: 3-4 days (28-32 hours)**

Breakdown:
- CommandPalette widget: 4 hours
- Search logic: 2 hours
- Command registration: 3 hours
- App integration: 2 hours
- Widget tests: 2.5 hours
- Search tests: 1.5 hours
- Integration tests: 2 hours
- Manual testing: 1.5 hours
- Action handler implementation: 2 hours
- Documentation/validation: 0.5 hours

**Buffer**: 2-4 hours for UX refinement

## Success Criteria

- [ ] CommandPalette widget implemented and styled
- [ ] Ctrl+P opens command palette as modal overlay
- [ ] Search input filters commands in real-time
- [ ] Up/Down navigate through results
- [ ] Enter executes selected command
- [ ] Escape closes palette
- [ ] All app commands registered (minimum 20 commands)
- [ ] Commands organized by category (File, View, Analysis, Navigation, Filter, Help)
- [ ] Keybindings displayed in palette results
- [ ] Search scores and sorts results by relevance
- [ ] Exact matches appear first, partial matches follow
- [ ] Case-insensitive search works correctly
- [ ] Widget unit tests pass (minimum 11 tests)
- [ ] Search unit tests pass (minimum 9 tests)
- [ ] Integration tests pass (minimum 7 tests)
- [ ] Test coverage >85% for command palette module
- [ ] Manual testing shows smooth UX
- [ ] All registered commands work when executed
- [ ] Documentation complete with command list

## Next Steps

After completing this subtask:
1. **Keyboard-Driven Workflow**: Users can access all features via Ctrl+P
2. **Proceed to Subtask 7**: Implement multi-panel docking layout
3. **Enhanced Search**: Consider fuzzy matching library (rapidfuzz) for better results
4. **Command History**: Track frequently used commands (future enhancement)
5. **Custom Keybindings**: Allow user configuration (future enhancement)
