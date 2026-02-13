# Subtask 1: Foundation Layout Structure

## Objective
Create the new IDE-style multi-panel layout structure with collapsible sidebar, main content area, and detail panel.

## Scope
Implement the foundational layout system that will host all future UI components. This includes creating the new `CaspoonIDEApp` class, setting up panel containers, adding collapse/expand functionality, and migrating existing tabs to the new structure.

## Technical Approach

### 1. Create New IDE App Entry Point
**Location**: `caspoon/ui/ide_app.py`

```python
# Key components:
- CaspoonIDEApp(App) class with custom CSS
- Three-panel layout: sidebar | main content | (detail panel below main)
- Horizontal container for sidebar + vertical split
- VerticalSplit for main content + detail panel
- Collapse handlers for sidebar (Ctrl+B) and detail (Ctrl+D)
```

### 2. Layout Structure
**CSS Approach**: Use Textual CSS for responsive layout

```css
/* In CaspoonIDEApp.CSS */
Horizontal {
    height: 100%;
}

#sidebar {
    width: 25;
    min-width: 20;
    max-width: 40;
    border-right: solid $accent;
}

#main-content {
    width: 3fr;
}

#detail-panel {
    height: 30%;
    border-top: solid $accent;
}

.collapsed {
    display: none;
}
```

### 3. Panel Components
Create container widgets:

```python
class Sidebar(Container):
    """Left sidebar container."""
    DEFAULT_CSS = """
    Sidebar {
        width: 25;
        background: $panel;
    }
    """
    
class MainContent(Container):
    """Main content area with tabs."""
    DEFAULT_CSS = """
    MainContent {
        width: 1fr;
    }
    """
    
class DetailPanel(Container):
    """Bottom detail panel."""
    DEFAULT_CSS = """
    DetailPanel {
        height: 30%;
        background: $panel;
    }
    """
```

### 4. Update CLI Entry Point
**Location**: `caspoon/cli.py`

**Changes**:
- Add `--ui` argument with choices: `simple`, `ide` (default: `simple`)
- Import and launch `CaspoonIDEApp` when `--ui ide`

```python
# Before:
from caspoon.ui.app import CaspoonApp
app = CaspoonApp()
app.run()

# After:
if args.ui == 'ide':
    from caspoon.ui.ide_app import CaspoonIDEApp
    app = CaspoonIDEApp()
else:
    from caspoon.ui.app import CaspoonApp
    app = CaspoonApp()
app.run()
```

## Implementation Steps

1. **Create ide_app.py skeleton** (2 hours)
   - Define `CaspoonIDEApp` class extending `App`
   - Set up CSS for three-panel layout
   - Create `compose()` method with placeholder containers
   - Add basic header and footer

2. **Implement panel containers** (2 hours)
   - Create `Sidebar`, `MainContent`, `DetailPanel` widgets
   - Add proper CSS styling
   - Wire up in main app's `compose()`
   - Test basic layout rendering

3. **Add collapse/expand functionality** (3 hours)
   - Create `toggle_sidebar()` action bound to Ctrl+B
   - Create `toggle_detail_panel()` action bound to Ctrl+D
   - Implement state tracking (sidebar_visible, detail_visible)
   - Add CSS class toggling for `.collapsed`
   - Update footer hints dynamically

4. **Migrate existing tabs** (4 hours)
   - Import existing view classes from `ui/views/`
   - Create `TabbedContent` inside `MainContent` container
   - Add all existing tabs: Overview, Protections, Strings, Imports, R2 Analysis
   - Test data flow: file input → analysis → view updates
   - Ensure all existing functionality works

5. **Update CLI** (1 hour)
   - Add `--ui` argument to argparse
   - Import and route to appropriate app class
   - Test both `--ui simple` and `--ui ide` modes
   - Update help text

6. **Testing** (3 hours)
   - Test layout on different terminal sizes (80x24, 120x40, 200x60)
   - Verify panel collapse/expand works smoothly
   - Test with sample binaries to ensure data flows correctly
   - Keyboard-only navigation test
   - Test rapid toggling (no crashes or visual glitches)

## Code Example

```python
# caspoon/ui/ide_app.py
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static

class Sidebar(Container):
    """Left sidebar for file browser and loaded binaries."""
    pass

class MainContent(Container):
    """Main content area with tabs."""
    pass

class DetailPanel(Container):
    """Bottom detail panel for context information."""
    pass

class CaspoonIDEApp(App):
    """Caspoon IDE-style TUI application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 25 1fr;
    }
    
    Sidebar {
        width: 25;
        background: $panel;
        border-right: solid $accent;
    }
    
    #main-container {
        width: 1fr;
    }
    
    DetailPanel {
        height: 10;
        background: $panel;
        border-top: solid $accent;
    }
    
    .collapsed {
        display: none;
    }
    """
    
    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+d", "toggle_detail", "Toggle Detail"),
        ("ctrl+q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.sidebar_visible = True
        self.detail_visible = True
    
    def compose(self) -> ComposeResult:
        """Create layout structure."""
        yield Header()
        
        with Horizontal():
            # Left sidebar
            with Sidebar(id="sidebar"):
                yield Static("📁 EXPLORE", classes="sidebar-section")
                yield Static("(File tree placeholder)")
                yield Static("📋 RECENT", classes="sidebar-section")
                yield Static("(Recent files placeholder)")
            
            # Main content + detail panel
            with Vertical(id="main-container"):
                with MainContent():
                    with TabbedContent():
                        with TabPane("Overview", id="tab-overview"):
                            yield Static("Overview content")
                        with TabPane("Protections", id="tab-protections"):
                            yield Static("Protections content")
                        with TabPane("Strings", id="tab-strings"):
                            yield Static("Strings content")
                        with TabPane("Imports", id="tab-imports"):
                            yield Static("Imports content")
                        with TabPane("R2 Analysis", id="tab-r2"):
                            yield Static("R2 Analysis content")
                
                with DetailPanel(id="detail-panel"):
                    yield Static("📋 Detail Panel\n(Select an item to see details)")
        
        yield Footer()
    
    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar")
        self.sidebar_visible = not self.sidebar_visible
        sidebar.set_class(not self.sidebar_visible, "collapsed")
    
    def action_toggle_detail(self) -> None:
        """Toggle detail panel visibility."""
        detail = self.query_one("#detail-panel")
        self.detail_visible = not self.detail_visible
        detail.set_class(not self.detail_visible, "collapsed")
```

## Testing Strategy

### Unit Tests
Create `tests/ui/test_ide_app.py`:
- Test app initialization
- Test layout structure (sidebar, main, detail present)
- Test toggle actions (sidebar, detail panel)
- Test CSS class application

### Integration Tests
- Launch IDE app: `python -m caspoon --ui ide`
- Verify three-panel layout renders correctly
- Press Ctrl+B → sidebar collapses
- Press Ctrl+B again → sidebar expands
- Press Ctrl+D → detail panel collapses
- Press Ctrl+D again → detail panel expands
- Resize terminal → layout adapts responsively

### Manual Testing
1. Test on small terminal (80x24): Layout should work but be cramped
2. Test on medium terminal (120x40): Comfortable layout
3. Test on large terminal (200x60): Use extra space effectively
4. Load a binary and verify existing tabs still work
5. Navigate between tabs with keyboard (Ctrl+Tab)

## Dependencies
- Textual >= 0.40.0 (already available)
- Existing view classes (`ui/views/*`)
- No new external dependencies

## Estimated Time
**15 hours total**
- Implementation: 12 hours
- Testing: 3 hours

## Success Criteria
- [ ] New `CaspoonIDEApp` class created and functional
- [ ] Three-panel layout renders correctly
- [ ] Sidebar toggles with Ctrl+B
- [ ] Detail panel toggles with Ctrl+D
- [ ] All existing tabs migrated and working
- [ ] CLI supports `--ui ide` flag
- [ ] Layout responsive to terminal resizing
- [ ] No visual glitches or crashes
- [ ] Keyboard-only navigation works

## Next Steps
After completion, proceed to Subtask 2: Command Palette to add quick actions and navigation.
