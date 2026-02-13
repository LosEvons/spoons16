# Subtask 6: Polish & Performance

## Objective
Optimize performance, refine UX, add themes, and complete documentation for production-ready release.

## Scope
Implement lazy loading for large datasets, add background threading for analysis, create progress indicators, refine themes, add tooltips and animations, complete testing, and finalize documentation.

## Technical Approach

### 1. Performance Optimizations

**Lazy Loading for Large Datasets**:
```python
class LazyDataTable(DataTable):
    """DataTable with lazy loading and virtual scrolling."""
    
    CHUNK_SIZE = 100
    PREFETCH_THRESHOLD = 20  # Load next chunk when within 20 rows of end
    
    def __init__(self, data_provider: Callable[[int, int], List]):
        super().__init__()
        self.data_provider = data_provider
        self.loaded_chunks = set()
        self.total_rows = 0
    
    async def load_chunk(self, chunk_index: int) -> None:
        """Load a chunk of data asynchronously."""
        if chunk_index in self.loaded_chunks:
            return
        
        start = chunk_index * self.CHUNK_SIZE
        end = start + self.CHUNK_SIZE
        
        # Load data in background
        rows = await self.run_in_executor(
            self.data_provider, start, end
        )
        
        # Add to table
        for row in rows:
            self.add_row(*row)
        
        self.loaded_chunks.add(chunk_index)
    
    def on_scroll(self, event: ScrollEvent) -> None:
        """Prefetch data when scrolling near bottom."""
        current_row = self.cursor_row
        
        if current_row > (len(self.rows) - self.PREFETCH_THRESHOLD):
            next_chunk = len(self.loaded_chunks)
            self.load_chunk(next_chunk)
```

**Background Analysis Threading**:
```python
from concurrent.futures import ThreadPoolExecutor
from textual.worker import Worker

class CaspoonIDEApp(App):
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def analyze_binary(self, path: str) -> None:
        """Analyze binary in background thread."""
        # Show progress indicator
        self.show_progress("Analyzing binary...")
        
        # Run analysis in background
        worker = Worker(
            self._run_analysis,
            path,
            group="analysis"
        )
        
        # Wait for completion
        result = await worker.wait()
        
        # Update UI with results
        self.hide_progress()
        self.update_views(result)
    
    def _run_analysis(self, path: str) -> ExecutableReport:
        """CPU-intensive analysis in thread."""
        runner = ReconRunner()
        return runner.run(path)
```

**Debounced Search**:
```python
from asyncio import CancelledError, sleep

class SearchableView(Container):
    """View with debounced search."""
    
    DEBOUNCE_MS = 300
    
    def __init__(self):
        super().__init__()
        self._search_task: Optional[asyncio.Task] = None
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Debounce search input."""
        # Cancel previous search
        if self._search_task:
            self._search_task.cancel()
        
        # Schedule new search
        self._search_task = asyncio.create_task(
            self._debounced_search(event.value)
        )
    
    async def _debounced_search(self, query: str) -> None:
        """Execute search after debounce delay."""
        try:
            await sleep(self.DEBOUNCE_MS / 1000)
            self._perform_search(query)
        except CancelledError:
            pass  # Search was cancelled
```

### 2. Progress Indicators

**Loading Indicator**:
```python
class LoadingIndicator(Container):
    """Animated loading indicator."""
    
    DEFAULT_CSS = """
    LoadingIndicator {
        align: center middle;
        width: 40;
        height: 10;
        background: $panel;
        border: solid $primary;
    }
    
    LoadingIndicator #spinner {
        text-align: center;
    }
    
    LoadingIndicator #progress {
        width: 30;
        height: 3;
    }
    """
    
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        yield Label("⏳ " + self.message, id="spinner")
        yield ProgressBar(id="progress")
    
    def update_progress(self, percent: int) -> None:
        """Update progress bar."""
        progress = self.query_one("#progress", ProgressBar)
        progress.update(progress=percent)

# Usage in app
class CaspoonIDEApp(App):
    async def analyze_binary(self, path: str) -> None:
        """Analyze with progress indicator."""
        indicator = LoadingIndicator("Analyzing binary...")
        self.mount(indicator)
        
        try:
            # Run analysis with progress updates
            async for progress in self._analyze_with_progress(path):
                indicator.update_progress(progress)
        finally:
            indicator.remove()
```

### 3. Themes

**Theme System**:
```python
# caspoon/ui/themes/base.py
from dataclasses import dataclass

@dataclass
class Theme:
    """Theme definition."""
    name: str
    primary: str
    accent: str
    background: str
    surface: str
    text: str
    text_muted: str
    success: str
    warning: str
    error: str

# Built-in themes
DARK_THEME = Theme(
    name="dark",
    primary="#61afef",
    accent="#c678dd",
    background="#282c34",
    surface="#21252b",
    text="#abb2bf",
    text_muted="#5c6370",
    success="#98c379",
    warning="#e5c07b",
    error="#e06c75",
)

LIGHT_THEME = Theme(
    name="light",
    primary="#0078d4",
    accent="#8764b8",
    background="#ffffff",
    surface="#f3f3f3",
    text="#000000",
    text_muted="#717171",
    success="#107c10",
    warning="#ffa500",
    error="#d13438",
)

# Theme manager
class ThemeManager:
    def __init__(self, app: App):
        self.app = app
        self.current_theme = DARK_THEME
    
    def apply_theme(self, theme: Theme) -> None:
        """Apply theme to app."""
        self.current_theme = theme
        
        # Update CSS variables
        css = f"""
        :root {{
            $primary: {theme.primary};
            $accent: {theme.accent};
            $background: {theme.background};
            $surface: {theme.surface};
            $text: {theme.text};
            $text-muted: {theme.text_muted};
            $success: {theme.success};
            $warning: {theme.warning};
            $error: {theme.error};
        }}
        """
        self.app.stylesheet = css
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.current_theme.name == "dark":
            self.apply_theme(LIGHT_THEME)
        else:
            self.apply_theme(DARK_THEME)
```

### 4. UX Refinements

**Tooltips**:
```python
class TooltipMixin:
    """Mixin to add tooltip support to widgets."""
    
    def __init__(self, *args, tooltip: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltip_text = tooltip
    
    def on_mouse_move(self, event: MouseMove) -> None:
        """Show tooltip on hover."""
        if self.tooltip_text and self._is_mouse_over():
            self.app.show_tooltip(self.tooltip_text, event.x, event.y)
    
    def on_mouse_leave(self, event: MouseLeave) -> None:
        """Hide tooltip on leave."""
        self.app.hide_tooltip()
```

**Confirmation Dialogs**:
```python
class ConfirmDialog(Container):
    """Modal confirmation dialog."""
    
    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
        width: 50;
        height: 15;
        background: $surface;
        border: thick $primary;
    }
    
    ConfirmDialog #dialog-message {
        text-align: center;
        padding: 2;
    }
    
    ConfirmDialog #dialog-buttons {
        align: center middle;
        width: 100%;
        height: 3;
    }
    """
    
    def __init__(self, message: str, callback: Callable[[bool], None]):
        super().__init__()
        self.message = message
        self.callback = callback
    
    def compose(self) -> ComposeResult:
        yield Label(self.message, id="dialog-message")
        with Horizontal(id="dialog-buttons"):
            yield Button("Confirm", id="confirm", variant="primary")
            yield Button("Cancel", id="cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        confirmed = event.button.id == "confirm"
        self.callback(confirmed)
        self.remove()

# Usage
async def action_close_binary(self) -> None:
    """Close binary with confirmation."""
    dialog = ConfirmDialog(
        "Close current binary? Unsaved changes will be lost.",
        callback=self._handle_close_confirmation
    )
    self.mount(dialog)

def _handle_close_confirmation(self, confirmed: bool) -> None:
    """Handle close confirmation."""
    if confirmed:
        self.binary_manager.unload(self.active_binary)
        self.refresh_views()
```

**Error Handling**:
```python
class ErrorDialog(Container):
    """User-friendly error display."""
    
    def __init__(self, error: Exception, context: str):
        super().__init__()
        self.error = error
        self.context = context
    
    def compose(self) -> ComposeResult:
        yield Label("❌ Error", classes="error-header")
        yield Label(f"Context: {self.context}")
        yield Label(f"Error: {str(self.error)}")
        
        # Provide actionable suggestions
        suggestions = self._get_suggestions(self.error)
        if suggestions:
            yield Label("Suggestions:")
            for suggestion in suggestions:
                yield Label(f"  • {suggestion}")
        
        yield Button("OK", id="dismiss", variant="primary")
    
    def _get_suggestions(self, error: Exception) -> List[str]:
        """Provide helpful suggestions based on error type."""
        if isinstance(error, FileNotFoundError):
            return ["Check if the file path is correct", "Verify file exists"]
        elif isinstance(error, PermissionError):
            return ["Check file permissions", "Run with sudo/admin rights"]
        elif isinstance(error, ValueError):
            return ["Verify the file is a valid executable", "Check file format"]
        return []
```

### 5. Keyboard Shortcuts Reference

**Comprehensive Shortcuts Table** (from SHORTCUTS.md):
```python
KEYBOARD_SHORTCUTS = {
    "Global": {
        "Ctrl+P": "Open command palette",
        "Ctrl+O": "Open file dialog",
        "Ctrl+W": "Close current tab",
        "Ctrl+Q": "Quit application",
        "Ctrl+B": "Toggle sidebar",
        "Ctrl+D": "Toggle detail panel",
        "F5": "Reload current binary",
        "F1": "Show help",
        "F9": "Toggle theme",
    },
    "Navigation": {
        "Alt+1-9": "Switch to tab 1-9",
        "Ctrl+Tab": "Next tab",
        "Ctrl+Shift+Tab": "Previous tab",
        "Ctrl+G": "Go to address",
        "Ctrl+F": "Find in current view",
    },
    "Analysis": {
        "Ctrl+R": "Analyze binary",
        "Ctrl+Shift+R": "Deep analysis",
        "Ctrl+E": "Export report",
    },
    "DataTable": {
        "↑↓": "Navigate rows",
        "/": "Search/filter",
        "Enter": "Show details",
        "Ctrl+C": "Copy selected",
    }
}
```

## Implementation Steps

1. **Implement lazy loading** (6 hours)
   - Create LazyDataTable class
   - Add chunk loading logic
   - Implement prefetching
   - Test with 10,000+ rows
   - Measure performance improvement

2. **Add background threading** (4 hours)
   - Create Worker wrapper for analysis
   - Implement thread pool
   - Add cancellation support
   - Test with large binaries
   - Ensure UI remains responsive

3. **Create progress indicators** (4 hours)
   - Create LoadingIndicator widget
   - Create ProgressBar integration
   - Add to long-running operations
   - Test with various operations
   - Ensure smooth animations

4. **Implement theme system** (5 hours)
   - Create Theme dataclass
   - Define dark and light themes
   - Create ThemeManager
   - Add F9 toggle shortcut
   - Persist theme preference
   - Test all UI elements with both themes

5. **Add UX refinements** (6 hours)
   - Implement tooltip system
   - Create confirmation dialogs
   - Improve error messages
   - Add suggestions to errors
   - Test all dialogs and tooltips

6. **Debounce search inputs** (2 hours)
   - Add debouncing to all search fields
   - Set 300ms delay
   - Test responsiveness
   - Measure performance impact

7. **Complete testing** (8 hours)
   - Test with various binary types (ELF, PE, Mach-O)
   - Test with large files (>100MB)
   - Test with large datasets (10,000+ strings)
   - Keyboard-only navigation testing
   - Performance profiling
   - Memory leak testing
   - Edge case testing

8. **Documentation** (5 hours)
   - Update README with screenshots
   - Create user guide
   - Document keyboard shortcuts
   - Update developer docs
   - Add code examples
   - Record demo GIF/video

## Code Example

```python
# caspoon/ui/ide_app.py - Performance optimizations
from textual.worker import Worker, WorkerState
from concurrent.futures import ThreadPoolExecutor

class CaspoonIDEApp(App):
    """IDE app with performance optimizations."""
    
    BINDINGS = [
        # ... existing bindings
        ("F9", "toggle_theme", "Toggle Theme"),
    ]
    
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.theme_manager = ThemeManager(self)
        self.loading_indicator: Optional[LoadingIndicator] = None
    
    async def action_analyze_binary(self, path: str) -> None:
        """Analyze binary with progress indicator."""
        # Show loading indicator
        self.loading_indicator = LoadingIndicator("Analyzing binary...")
        self.mount(self.loading_indicator)
        
        try:
            # Run analysis in background
            worker = self.run_worker(
                self._analyze_in_thread,
                path,
                group="analysis",
                thread=True
            )
            
            # Monitor progress
            while worker.state != WorkerState.SUCCESS:
                if worker.state == WorkerState.ERROR:
                    raise worker.error
                
                # Update progress (if available)
                progress = getattr(worker, 'progress', 0)
                self.loading_indicator.update_progress(progress)
                
                await asyncio.sleep(0.1)
            
            # Get result
            report = worker.result
            
            # Update views
            await self._refresh_all_views(report)
            
            # Add to recent files
            self.recent_files.add(path, {
                'arch': report.architecture,
                'size': report.size
            })
            
            # Update sidebar
            sidebar = self.query_one(Sidebar)
            sidebar.update_recent_files(self.recent_files.get_all())
            
        except Exception as e:
            # Show error dialog
            error_dialog = ErrorDialog(e, f"Analyzing {path}")
            self.mount(error_dialog)
        
        finally:
            # Hide loading indicator
            if self.loading_indicator:
                self.loading_indicator.remove()
                self.loading_indicator = None
    
    def _analyze_in_thread(self, path: str) -> ExecutableReport:
        """CPU-intensive analysis in background thread."""
        runner = ReconRunner()
        return runner.run(path)
    
    def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        self.notify("Theme changed")
    
    async def show_confirmation(
        self,
        message: str
    ) -> bool:
        """Show confirmation dialog and wait for response."""
        result = []
        
        def callback(confirmed: bool):
            result.append(confirmed)
        
        dialog = ConfirmDialog(message, callback)
        self.mount(dialog)
        
        # Wait for dialog to close
        while not result:
            await asyncio.sleep(0.1)
        
        return result[0]
```

## Testing Strategy

### Performance Testing
- Load binary with 10,000+ strings → measure load time
- Filter strings → measure update time (<300ms)
- Scroll DataTable → ensure smooth scrolling
- Switch between binaries → measure switch time (<500ms)
- Memory profiling → no leaks after multiple operations

### UX Testing
- Test all keyboard shortcuts work
- Test all buttons have tooltips
- Test confirmations appear for destructive actions
- Test error messages are clear and helpful
- Test theme toggle works correctly
- Test progress indicators appear for long operations

### Compatibility Testing
- Test on Linux with various terminal emulators
- Test on macOS with Terminal.app and iTerm2
- Test on Windows with Windows Terminal
- Test with different terminal sizes
- Test with screen readers (basic accessibility)

## Dependencies
- No new external dependencies
- Uses Textual's built-in threading and worker system

## Estimated Time
**40 hours total**
- Implementation: 32 hours
- Testing: 8 hours

## Success Criteria
- [ ] Lazy loading works with 10,000+ row datasets
- [ ] Analysis runs in background without blocking UI
- [ ] Progress indicators appear for operations >500ms
- [ ] Dark and light themes work correctly
- [ ] Theme preference persisted across sessions
- [ ] All buttons have tooltips
- [ ] Confirmation dialogs for destructive actions
- [ ] Error messages clear and actionable
- [ ] Search debounced (300ms delay)
- [ ] No memory leaks or performance degradation
- [ ] Documentation complete and accurate
- [ ] All keyboard shortcuts documented

## Next Steps
After completion, the IDE UI is production-ready for release. Consider:
- User acceptance testing
- Beta release
- Gather feedback
- Plan next iteration based on user feedback
