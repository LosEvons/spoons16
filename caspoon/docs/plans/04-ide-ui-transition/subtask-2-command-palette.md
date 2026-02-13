# Subtask 2: Command Palette Integration

## Objective
Implement a command palette (Ctrl+P) for quick access to all major actions and navigation, with fuzzy search filtering.

## Scope
Create a command palette system that allows users to quickly execute actions without memorizing keyboard shortcuts. Includes command registration, fuzzy search, command categories, and keyboard navigation.

## Technical Approach

### 1. Command System Architecture
**Location**: `caspoon/ui/commands/`

```python
# Structure:
- commands/__init__.py
- commands/base.py         # Command base class
- commands/registry.py     # Command registry
- commands/palette.py      # Palette widget
- commands/provider.py     # Built-in command provider
```

### 2. Command Base Class
**Location**: `caspoon/ui/commands/base.py`

```python
class Command:
    """Base command class."""
    id: str           # Unique identifier (e.g., "file.open")
    title: str        # Display name (e.g., "Open File")
    category: str     # Category (File, View, Analysis, Help)
    shortcuts: List[str]  # Keyboard shortcuts
    
    async def execute(self, app: App) -> None:
        """Execute the command."""
        pass
```

### 3. Command Registry
**Location**: `caspoon/ui/commands/registry.py`

```python
class CommandRegistry:
    """Central registry for all commands."""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
    
    def register(self, command: Command) -> None:
        """Register a command."""
        self.commands[command.id] = command
    
    def search(self, query: str) -> List[Command]:
        """Fuzzy search commands by title/id."""
        # Use simple scoring: substring match in title
        matches = []
        query_lower = query.lower()
        for cmd in self.commands.values():
            score = self._score(query_lower, cmd.title.lower())
            if score > 0:
                matches.append((score, cmd))
        # Sort by score descending
        matches.sort(key=lambda x: x[0], reverse=True)
        return [cmd for score, cmd in matches]
    
    def _score(self, query: str, text: str) -> int:
        """Calculate match score."""
        if query in text:
            return 100 - text.index(query)  # Earlier match = higher score
        # Fuzzy matching: all chars present in order
        pos = 0
        for char in query:
            pos = text.find(char, pos)
            if pos == -1:
                return 0
            pos += 1
        return 50  # Lower score for fuzzy match
```

### 4. Command Palette Widget
**Location**: `caspoon/ui/commands/palette.py`

```python
class CommandPalette(Container):
    """Overlay command palette widget."""
    
    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
        width: 80%;
        height: 60%;
        background: $surface;
        border: thick $primary;
    }
    
    #palette-input {
        dock: top;
        height: 3;
    }
    
    #palette-results {
        height: 1fr;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type command...", id="palette-input")
        yield ListView(id="palette-results")
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types."""
        query = event.value
        results = self.app.command_registry.search(query)
        
        # Update results list
        results_list = self.query_one("#palette-results", ListView)
        results_list.clear()
        for cmd in results[:10]:  # Show top 10
            results_list.append(ListItem(
                Label(f"{cmd.title} ({cmd.category})")
            ))
```

### 5. Built-in Commands
**Location**: `caspoon/ui/commands/provider.py`

Define all built-in commands:

```python
BUILTIN_COMMANDS = [
    # File Operations
    Command("file.open", "Open File", "File", ["ctrl+o"]),
    Command("file.close", "Close File", "File", ["ctrl+w"]),
    Command("file.reload", "Reload Current Binary", "File", ["F5"]),
    Command("file.export", "Export Report (HTML)", "File", ["ctrl+e"]),
    
    # Navigation
    Command("nav.overview", "Go to Overview", "Navigation", ["alt+1"]),
    Command("nav.protections", "Go to Protections", "Navigation", ["alt+2"]),
    Command("nav.strings", "Go to Strings", "Navigation", ["alt+3"]),
    Command("nav.imports", "Go to Imports", "Navigation", ["alt+4"]),
    Command("nav.r2", "Go to R2 Analysis", "Navigation", ["alt+5"]),
    
    # Analysis
    Command("analysis.run", "Analyze Binary", "Analysis", ["ctrl+r"]),
    Command("analysis.deep", "Deep Analysis (R2)", "Analysis", ["ctrl+shift+r"]),
    Command("analysis.strings", "Search Strings", "Analysis", ["ctrl+shift+f"]),
    
    # View
    Command("view.toggle_sidebar", "Toggle Sidebar", "View", ["ctrl+b"]),
    Command("view.toggle_detail", "Toggle Detail Panel", "View", ["ctrl+d"]),
    Command("view.theme", "Toggle Theme", "View", ["F9"]),
    
    # Help
    Command("help.shortcuts", "Show Shortcuts", "Help", ["F1"]),
    Command("help.about", "About Caspoon", "Help", []),
]
```

### 6. Integration into IDE App
**Location**: `caspoon/ui/ide_app.py`

```python
class CaspoonIDEApp(App):
    BINDINGS = [
        ("ctrl+p", "show_command_palette", "Commands"),
        # ... other bindings
    ]
    
    def on_mount(self) -> None:
        """Initialize app."""
        # Create command registry
        self.command_registry = CommandRegistry()
        
        # Register built-in commands
        for cmd in BUILTIN_COMMANDS:
            self.command_registry.register(cmd)
    
    def action_show_command_palette(self) -> None:
        """Show command palette."""
        palette = CommandPalette()
        self.mount(palette)
```

## Implementation Steps

1. **Create command infrastructure** (3 hours)
   - Create `commands/` directory
   - Implement `Command` dataclass
   - Implement `CommandRegistry` with fuzzy search
   - Write unit tests for search algorithm

2. **Implement CommandPalette widget** (4 hours)
   - Create overlay container with input and list
   - Wire up input filtering
   - Handle keyboard navigation (up/down arrows, enter)
   - Handle escape to close
   - Style with CSS

3. **Define built-in commands** (2 hours)
   - Create all file operation commands
   - Create navigation commands (tab switching)
   - Create view toggle commands
   - Create help commands
   - Implement command execution callbacks

4. **Integrate into IDE app** (2 hours)
   - Add Ctrl+P binding
   - Mount/unmount palette overlay
   - Connect command execution to app actions
   - Test all commands work correctly

5. **Add help dialog** (2 hours)
   - Create `HelpDialog` widget showing shortcuts
   - Bind to F1
   - Display all commands grouped by category
   - Include keyboard shortcuts

6. **Testing** (2 hours)
   - Test fuzzy search with various queries
   - Test command execution for each command
   - Test keyboard navigation in palette
   - Test rapid open/close (no memory leaks)
   - Test with empty query (should show all commands)

## Code Example

```python
# caspoon/ui/commands/palette.py
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container
from textual.app import ComposeResult
from dataclasses import dataclass
from typing import Callable

@dataclass
class Command:
    """Represents an executable command."""
    id: str
    title: str
    category: str
    shortcuts: list[str]
    callback: Callable
    
class CommandPalette(Container):
    """Command palette overlay."""
    
    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("up", "cursor_up", "Up"),
        ("down", "cursor_down", "Down"),
        ("enter", "execute", "Execute"),
    ]
    
    DEFAULT_CSS = """
    CommandPalette {
        width: 80;
        height: 30;
        background: $panel;
        border: thick $primary;
        margin: 2 4;
    }
    
    #command-input {
        dock: top;
        height: 3;
        border-bottom: solid $accent;
    }
    
    #command-list {
        height: 1fr;
        padding: 1;
    }
    """
    
    def __init__(self, registry: 'CommandRegistry'):
        super().__init__()
        self.registry = registry
        self.filtered_commands = []
    
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Type command name...",
            id="command-input"
        )
        yield ListView(id="command-list")
    
    def on_mount(self) -> None:
        """Focus input on mount."""
        self.query_one(Input).focus()
        self._update_results("")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types."""
        self._update_results(event.value)
    
    def _update_results(self, query: str) -> None:
        """Update command list based on query."""
        self.filtered_commands = self.registry.search(query)
        
        list_view = self.query_one(ListView)
        list_view.clear()
        
        for cmd in self.filtered_commands[:15]:  # Show top 15
            shortcut = f" ({cmd.shortcuts[0]})" if cmd.shortcuts else ""
            label = f"{cmd.title}{shortcut} - {cmd.category}"
            list_view.append(ListItem(Label(label)))
    
    def action_execute(self) -> None:
        """Execute selected command."""
        list_view = self.query_one(ListView)
        index = list_view.index
        
        if 0 <= index < len(self.filtered_commands):
            cmd = self.filtered_commands[index]
            self.app.execute_command(cmd.id)
            self.remove()
    
    def action_dismiss(self) -> None:
        """Close palette."""
        self.remove()
```

## Testing Strategy

### Unit Tests
Create `tests/ui/commands/test_registry.py`:
- Test command registration
- Test fuzzy search algorithm
  - Exact match: "Open" → "Open File" (high score)
  - Substring: "file" → "Open File" (medium score)
  - Fuzzy: "opfi" → "Open File" (lower score)
  - No match: "xyz" → []
- Test command execution

### Integration Tests
- Launch IDE app
- Press Ctrl+P → palette appears
- Type "open" → "Open File" appears at top
- Press Enter → file dialog opens
- Press Ctrl+P again
- Type "tog sid" → "Toggle Sidebar" appears
- Press Enter → sidebar toggles
- Press Escape → palette closes

### Manual Testing
1. Test all built-in commands execute correctly
2. Test fuzzy search with partial/misspelled queries
3. Test keyboard navigation (arrows, enter, escape)
4. Test palette doesn't interfere with other shortcuts
5. Test rapid toggling (Ctrl+P, Esc, Ctrl+P)

## Dependencies
- Textual widgets: Input, ListView, ListItem, Label
- No new external dependencies

## Estimated Time
**15 hours total**
- Implementation: 13 hours
- Testing: 2 hours

## Success Criteria
- [ ] Command palette opens with Ctrl+P
- [ ] Fuzzy search filters commands as user types
- [ ] All built-in commands registered and working
- [ ] Keyboard navigation works (arrows, enter, escape)
- [ ] Commands execute their intended actions
- [ ] Help dialog (F1) shows all shortcuts
- [ ] No performance lag when filtering
- [ ] Palette dismisses cleanly without leaving artifacts

## Next Steps
After completion, proceed to Subtask 3: Enhanced Data Views to upgrade all views to interactive widgets.
