# TUI Redesign - Autonomous Implementation Plan

**Version**: 1.0  
**Status**: Ready for Implementation  
**Last Updated**: February 2024  
**Estimated Duration**: 8 weeks (40 phases)

---

## Executive Summary

This document provides a phase-by-phase implementation plan for migrating Caspoon's TUI from a simple tabbed interface to a professional, IDE-like experience. The redesign transforms a blocking, imperative UI into an async-first, reactive, event-driven architecture with command palette, multi-panel layout, and extensible plugin system.

### What Is Being Built

We are building a **modern, IDE-like TUI** with:
- **Reactive state management**: Single source of truth with automatic view updates
- **Event-driven architecture**: Message-based communication for loose coupling
- **Async workers**: Non-blocking analysis with progress reporting
- **Command palette**: Ctrl+P fuzzy-search command interface
- **Multi-panel layout**: Sidebar, content tabs, details panel, bottom console
- **Extensible base classes**: Reusable BaseView, InteractiveView, TreeView, TableView
- **Comprehensive testing**: Unit, integration, and snapshot tests

### Why (Problems Being Solved)

**Current limitations:**
1. ❌ **Blocking analysis**: UI freezes during binary analysis
2. ❌ **Manual view updates**: Must remember to call `update_data()` on every view
3. ❌ **No keyboard shortcuts**: Limited discoverability of features
4. ❌ **Static layout**: Can only see one view at a time
5. ❌ **Hard to extend**: Adding features requires core modifications
6. ❌ **Difficult to test**: Tests require full rendering and are brittle

**New architecture solves:**
1. ✅ **Responsive UI**: Async workers keep UI interactive during long operations
2. ✅ **Automatic updates**: Views reactively update when state changes
3. ✅ **Command palette**: Discoverable actions with fuzzy search
4. ✅ **Efficient workflow**: View multiple panels simultaneously
5. ✅ **Plugin-ready**: Extensible action registry and message system
6. ✅ **Testable**: Unit test logic without rendering

### High-Level Approach

**Incremental migration in 5 phases:**

1. **Phase 1 (Weeks 1-2)**: Build foundation - core classes, state management, action registry
2. **Phase 2 (Week 3)**: Prove the pattern - migrate one simple view (OverviewView)
3. **Phase 3 (Weeks 4-5)**: Migrate all remaining views to new architecture
4. **Phase 4 (Weeks 6-7)**: Add advanced features - command palette, multi-panel layout, async workers
5. **Phase 5 (Week 8)**: Testing, polish, documentation

**Key principle**: Old and new code coexist during migration. Each phase produces working, testable code. Can rollback individual features via feature flags.

---

## Prerequisites

### Knowledge Required

Before starting implementation, agents should understand:

1. **Textual Framework Fundamentals**
   - Widget lifecycle (compose, mount, unmount)
   - Reactive properties and watchers
   - Message/event system
   - Async workers
   - Pilot testing framework

2. **Python Async/Await**
   - asyncio.to_thread() for blocking code
   - async def and await
   - Worker patterns

3. **Rich Library**
   - Table, Panel, Tree rendering
   - Text styling and markup

4. **Design Patterns**
   - Reactive programming
   - Observer pattern
   - Command pattern
   - Abstract base classes

### Files to Read First

**Essential reading (in order):**

1. `caspoon/docs/plans/README-TUI-REDESIGN.md` - Executive overview (5 min)
2. `caspoon/docs/plans/tui-architecture-redesign.md` - Complete architecture (45 min)
   - Sections 1-3: Architecture, widgets, state management
   - Section 5: Actions and command system
   - Section 7: Migration strategy
3. `caspoon/docs/plans/tui-design-decisions.md` - Architectural rationale (20 min)
4. `caspoon/docs/plans/tui-quick-reference.md` - Quick lookup guide (bookmark this)
5. `caspoon/docs/plans/tui-implementation-examples.md` - Code examples (reference as needed)

**Existing codebase:**

1. `caspoon/ui/app.py` - Current app structure
2. `caspoon/ui/views/overview.py` - Simple view to understand current pattern
3. `caspoon/ui/views/r2_view.py` - Complex view with syntax highlighting
4. `caspoon/core/runner.py` - How analysis is currently executed
5. `caspoon/core/models.py` - Data models used throughout

### Dependencies to Understand

**Python packages (check `requirements.txt`):**
- `textual` - TUI framework
- `rich` - Terminal formatting
- `pytest` - Testing
- `pytest-asyncio` - Async test support
- `syrupy` (if added) - Snapshot testing

**Caspoon modules:**
- `caspoon.core.runner.ReconRunner` - Executes binary analysis
- `caspoon.core.models.*` - Data models (ExecutableReport, BinaryInfo, etc.)
- `caspoon.backends.*` - Analysis backends (r2, lief, etc.)

---

## Implementation Phases

> **Note for AI Agents**: Each phase is designed to be completed independently by one agent. Read the prerequisites for each phase, implement the specified files, write tests, and verify acceptance criteria before moving to the next phase.

---

## PHASE 1: FOUNDATION

### Phase 1.1: Create Project Structure and State Management

**Objective**: Set up the new directory structure and implement centralized reactive state management.

**Prerequisites**:
- Read: `tui-architecture-redesign.md` sections 1.3 (Data Flow), 3 (State Management)
- Read: `tui-design-decisions.md` decision 1 (Reactive State)
- Understand Textual's `reactive()` properties

**Files to Create**:
- `caspoon/ui/core/__init__.py`
- `caspoon/ui/core/state.py`
- `caspoon/ui/core/models.py`
- `caspoon/tests/unit/ui/core/__init__.py`
- `caspoon/tests/unit/ui/core/test_state.py`

**Files to Modify**:
- None (purely additive)

**Implementation Details**:

1. **Create directory structure**:
   ```
   caspoon/ui/core/        # New core architecture
   caspoon/ui/widgets/     # New reusable widgets (empty for now)
   caspoon/ui/screens/     # New screen management (empty for now)
   ```

2. **Implement `caspoon/ui/core/models.py`**:
   ```python
   from dataclasses import dataclass
   from typing import Optional, List, Dict, Any
   
   @dataclass
   class BinaryInfo:
       """Binary file metadata."""
       path: str
       architecture: str
       bits: int
       file_type: str
       stripped: bool
       file_size: int
       entry_point: Optional[str] = None
   
   @dataclass
   class AnalysisResults:
       """Complete analysis results."""
       functions: List[Dict[str, Any]]
       strings: List[str]
       imports: List[Dict[str, Any]]
       exports: List[Dict[str, Any]]
       sections: List[Dict[str, Any]]
       protections: Dict[str, bool]
       disassembly: Optional[str] = None
   
   @dataclass
   class UIState:
       """UI state (loading, errors, etc.)."""
       is_analyzing: bool = False
       analysis_progress: int = 0
       analysis_message: str = ""
       selected_function: Optional[str] = None
       active_tab: str = "overview"
       sidebar_collapsed: bool = False
       details_collapsed: bool = False
       bottom_collapsed: bool = True
   
   @dataclass
   class UserPreferences:
       """User preferences and settings."""
       theme: str = "default"
       show_line_numbers: bool = True
       auto_analyze: bool = True
       max_strings: int = 1000
   ```

3. **Implement `caspoon/ui/core/state.py`**:
   ```python
   from textual.reactive import reactive
   from typing import Optional
   from .models import BinaryInfo, AnalysisResults, UIState, UserPreferences
   
   class AppState:
       """Centralized reactive state store.
       
       Single source of truth for application state.
       Views watch these reactive properties and auto-update.
       """
       
       # Core data
       binary_info: reactive[Optional[BinaryInfo]] = reactive(None)
       analysis_results: reactive[Optional[AnalysisResults]] = reactive(None)
       
       # UI state
       ui_state: reactive[UIState] = reactive(UIState, init=False)
       
       # User preferences
       user_prefs: reactive[UserPreferences] = reactive(UserPreferences, init=False)
       
       def __init__(self):
           self.binary_info = None
           self.analysis_results = None
           self.ui_state = UIState()
           self.user_prefs = UserPreferences()
       
       def reset(self) -> None:
           """Reset state to initial values."""
           self.binary_info = None
           self.analysis_results = None
           self.ui_state = UIState()
       
       def update_from_report(self, report) -> None:
           """Update state from ExecutableReport.
           
           Args:
               report: ExecutableReport from ReconRunner
           """
           # Extract binary info
           self.binary_info = BinaryInfo(
               path=report.file_path,
               architecture=report.binary_info.get("arch", "unknown"),
               bits=report.binary_info.get("bits", 0),
               file_type=report.binary_info.get("type", "unknown"),
               stripped=report.binary_info.get("stripped", False),
               file_size=report.binary_info.get("size", 0),
               entry_point=report.binary_info.get("entry", None)
           )
           
           # Extract analysis results
           self.analysis_results = AnalysisResults(
               functions=report.functions or [],
               strings=report.strings or [],
               imports=report.imports or [],
               exports=report.exports or [],
               sections=report.sections or [],
               protections=report.protections or {},
               disassembly=getattr(report, 'disassembly', None)
           )
   ```

4. **Write comprehensive tests** in `caspoon/tests/unit/ui/core/test_state.py`:
   ```python
   import pytest
   from caspoon.ui.core.state import AppState
   from caspoon.ui.core.models import BinaryInfo, AnalysisResults, UIState
   
   def test_state_initialization():
       """Test AppState initializes with defaults."""
       state = AppState()
       assert state.binary_info is None
       assert state.analysis_results is None
       assert isinstance(state.ui_state, UIState)
       assert state.ui_state.is_analyzing is False
   
   def test_state_reset():
       """Test state reset clears all data."""
       state = AppState()
       state.binary_info = BinaryInfo(
           path="/bin/ls", architecture="x86_64", 
           bits=64, file_type="ELF", stripped=False, file_size=1000
       )
       state.ui_state.is_analyzing = True
       
       state.reset()
       
       assert state.binary_info is None
       assert state.ui_state.is_analyzing is False
   
   def test_binary_info_update():
       """Test updating binary info."""
       state = AppState()
       info = BinaryInfo(
           path="/bin/test", architecture="arm64",
           bits=64, file_type="MACH", stripped=True, file_size=2048
       )
       
       state.binary_info = info
       
       assert state.binary_info.path == "/bin/test"
       assert state.binary_info.architecture == "arm64"
   
   def test_analysis_results_update():
       """Test updating analysis results."""
       state = AppState()
       results = AnalysisResults(
           functions=[{"name": "main", "addr": "0x1000"}],
           strings=["hello"],
           imports=[],
           exports=[],
           sections=[],
           protections={"NX": True}
       )
       
       state.analysis_results = results
       
       assert len(state.analysis_results.functions) == 1
       assert state.analysis_results.protections["NX"] is True
   
   def test_ui_state_updates():
       """Test UI state management."""
       state = AppState()
       
       state.ui_state.is_analyzing = True
       assert state.ui_state.is_analyzing
       
       state.ui_state.analysis_progress = 50
       assert state.ui_state.analysis_progress == 50
   
   # Add 5 more tests covering edge cases, user_prefs, etc.
   ```

**Acceptance Criteria**:
- [ ] All files created with proper structure
- [ ] AppState class has all reactive properties
- [ ] AppState can be instantiated without errors
- [ ] Unit tests pass (minimum 10 tests)
- [ ] Test coverage >90% for state.py
- [ ] Existing TUI still runs without errors (`python -m caspoon.ui`)
- [ ] No import errors when importing `from caspoon.ui.core.state import AppState`

**Testing Commands**:
```bash
# Run unit tests
pytest caspoon/tests/unit/ui/core/test_state.py -v

# Check test coverage
pytest caspoon/tests/unit/ui/core/test_state.py --cov=caspoon/ui/core/state --cov-report=term-missing

# Verify existing TUI still works
python -m caspoon.ui  # Should launch without errors
```

**Estimated Complexity**: Simple (2-3 hours)

---

### Phase 1.2: Implement Action System and Registry

**Objective**: Create the message-based action system and command registry for decoupled communication.

**Prerequisites**:
- Phase 1.1 complete
- Read: `tui-architecture-redesign.md` section 5 (Command System)
- Read: `tui-design-decisions.md` decision 2 (Message-Driven Architecture)
- Understand Textual's `Message` class and `post_message()`

**Files to Create**:
- `caspoon/ui/core/actions.py`
- `caspoon/ui/core/actions_registry.py`
- `caspoon/tests/unit/ui/core/test_actions.py`
- `caspoon/tests/unit/ui/core/test_actions_registry.py`

**Files to Modify**:
- `caspoon/ui/core/__init__.py` (add exports)

**Implementation Details**:

1. **Implement `caspoon/ui/core/actions.py`** with standard message types:
   ```python
   from textual.message import Message
   from typing import Optional, Any
   
   # Analysis actions
   class StartAnalysis(Message):
       """Request to start binary analysis."""
       def __init__(self, path: str) -> None:
           self.path = path
           super().__init__()
   
   class AnalysisProgress(Message):
       """Analysis progress update."""
       def __init__(self, percent: int, message: str) -> None:
           self.percent = percent
           self.message = message
           super().__init__()
   
   class AnalysisComplete(Message):
       """Analysis completed successfully."""
       def __init__(self, report: Any) -> None:
           self.report = report
           super().__init__()
   
   class AnalysisError(Message):
       """Analysis failed."""
       def __init__(self, error: str) -> None:
           self.error = error
           super().__init__()
   
   # Navigation actions
   class SelectFunction(Message):
       """Function selected by user."""
       def __init__(self, function_name: str, address: Optional[str] = None) -> None:
           self.function_name = function_name
           self.address = address
           super().__init__()
   
   class JumpToAddress(Message):
       """Jump to specific address in disassembly/hex."""
       def __init__(self, address: str) -> None:
           self.address = address
           super().__init__()
   
   class SwitchTab(Message):
       """Switch to a specific tab."""
       def __init__(self, tab_id: str) -> None:
           self.tab_id = tab_id
           super().__init__()
   
   # UI actions
   class TogglePanel(Message):
       """Toggle panel visibility."""
       def __init__(self, panel_id: str) -> None:
           self.panel_id = panel_id
           super().__init__()
   
   class ShowCommandPalette(Message):
       """Show command palette."""
       pass
   
   class ExecuteCommand(Message):
       """Execute a registered command."""
       def __init__(self, command_id: str) -> None:
           self.command_id = command_id
           super().__init__()
   ```

2. **Implement `caspoon/ui/core/actions_registry.py`**:
   ```python
   from dataclasses import dataclass
   from typing import Callable, Optional, Dict, List
   import logging
   
   logger = logging.getLogger(__name__)
   
   @dataclass
   class Action:
       """Registered action/command."""
       action_id: str
       name: str
       handler: Callable
       description: str = ""
       keybinding: Optional[str] = None
       category: str = "General"
       enabled: bool = True
   
   class ActionRegistry:
       """Central registry for all application actions.
       
       Manages commands, keybindings, and command palette integration.
       """
       
       def __init__(self):
           self._actions: Dict[str, Action] = {}
           self._keybindings: Dict[str, str] = {}  # key -> action_id
           self._categories: Dict[str, List[str]] = {}  # category -> [action_ids]
       
       def register(
           self,
           action_id: str,
           name: str,
           handler: Callable,
           description: str = "",
           keybinding: Optional[str] = None,
           category: str = "General",
           enabled: bool = True
       ) -> None:
           """Register a new action.
           
           Args:
               action_id: Unique identifier (e.g., "analyze_binary")
               name: Display name (e.g., "Analyze Binary")
               handler: Function to call when action is triggered
               description: Help text
               keybinding: Keyboard shortcut (e.g., "ctrl+o")
               category: Category for grouping (e.g., "File", "View")
               enabled: Whether action is currently enabled
           """
           if action_id in self._actions:
               logger.warning(f"Action {action_id} already registered, overwriting")
           
           action = Action(
               action_id=action_id,
               name=name,
               handler=handler,
               description=description,
               keybinding=keybinding,
               category=category,
               enabled=enabled
           )
           
           self._actions[action_id] = action
           
           if keybinding:
               self._keybindings[keybinding] = action_id
           
           if category not in self._categories:
               self._categories[category] = []
           if action_id not in self._categories[category]:
               self._categories[category].append(action_id)
       
       def execute(self, action_id: str, *args, **kwargs) -> bool:
           """Execute an action by ID.
           
           Returns:
               True if action executed successfully, False otherwise
           """
           action = self._actions.get(action_id)
           if not action:
               logger.error(f"Action {action_id} not found")
               return False
           
           if not action.enabled:
               logger.warning(f"Action {action_id} is disabled")
               return False
           
           try:
               action.handler(*args, **kwargs)
               return True
           except Exception as e:
               logger.error(f"Error executing action {action_id}: {e}")
               return False
       
       def get_action(self, action_id: str) -> Optional[Action]:
           """Get action by ID."""
           return self._actions.get(action_id)
       
       def get_all_actions(self) -> List[Action]:
           """Get all registered actions."""
           return list(self._actions.values())
       
       def get_actions_by_category(self, category: str) -> List[Action]:
           """Get all actions in a category."""
           action_ids = self._categories.get(category, [])
           return [self._actions[aid] for aid in action_ids if aid in self._actions]
       
       def get_categories(self) -> List[str]:
           """Get all categories."""
           return sorted(self._categories.keys())
       
       def search_actions(self, query: str) -> List[Action]:
           """Search actions by name or description (fuzzy).
           
           Args:
               query: Search string
               
           Returns:
               List of matching actions, sorted by relevance
           """
           query_lower = query.lower()
           results = []
           
           for action in self._actions.values():
               if not action.enabled:
                   continue
               
               # Simple fuzzy matching - check if all query chars appear in order
               name_lower = action.name.lower()
               desc_lower = action.description.lower()
               
               if query_lower in name_lower or query_lower in desc_lower:
                   results.append(action)
           
           # Sort by relevance (name matches first)
           results.sort(key=lambda a: (
               query_lower not in a.name.lower(),  # Name matches first
               a.name
           ))
           
           return results
       
       def unregister(self, action_id: str) -> bool:
           """Unregister an action.
           
           Returns:
               True if action was removed, False if not found
           """
           if action_id not in self._actions:
               return False
           
           action = self._actions[action_id]
           
           # Remove from keybindings
           if action.keybinding and action.keybinding in self._keybindings:
               del self._keybindings[action.keybinding]
           
           # Remove from categories
           if action.category in self._categories:
               try:
                   self._categories[action.category].remove(action_id)
               except ValueError:
                   pass
           
           # Remove action
           del self._actions[action_id]
           return True
   ```

3. **Write tests** for both modules:
   ```python
   # test_actions.py - Test message classes
   def test_start_analysis_message():
       msg = StartAnalysis("/bin/ls")
       assert msg.path == "/bin/ls"
   
   def test_analysis_progress_message():
       msg = AnalysisProgress(50, "Analyzing...")
       assert msg.percent == 50
       assert msg.message == "Analyzing..."
   
   # test_actions_registry.py - Test registry
   def test_registry_initialization():
       registry = ActionRegistry()
       assert len(registry.get_all_actions()) == 0
   
   def test_register_action():
       registry = ActionRegistry()
       called = []
       
       def handler():
           called.append(True)
       
       registry.register(
           "test_action",
           "Test Action",
           handler,
           description="Test",
           keybinding="ctrl+t"
       )
       
       assert len(registry.get_all_actions()) == 1
       action = registry.get_action("test_action")
       assert action.name == "Test Action"
       assert action.keybinding == "ctrl+t"
   
   def test_execute_action():
       registry = ActionRegistry()
       result = []
       
       def handler(value):
           result.append(value)
       
       registry.register("test", "Test", handler)
       success = registry.execute("test", "hello")
       
       assert success
       assert result == ["hello"]
   
   def test_search_actions():
       registry = ActionRegistry()
       registry.register("analyze", "Analyze Binary", lambda: None)
       registry.register("save", "Save Report", lambda: None)
       registry.register("reload", "Reload Analysis", lambda: None)
       
       results = registry.search_actions("ana")
       assert len(results) == 2
       assert results[0].action_id == "analyze"
   
   # Add 10+ more tests
   ```

4. **Update `caspoon/ui/core/__init__.py`**:
   ```python
   from .state import AppState
   from .actions import (
       StartAnalysis, AnalysisProgress, AnalysisComplete, AnalysisError,
       SelectFunction, JumpToAddress, SwitchTab, TogglePanel,
       ShowCommandPalette, ExecuteCommand
   )
   from .actions_registry import ActionRegistry, Action
   
   __all__ = [
       "AppState",
       "StartAnalysis", "AnalysisProgress", "AnalysisComplete", "AnalysisError",
       "SelectFunction", "JumpToAddress", "SwitchTab", "TogglePanel",
       "ShowCommandPalette", "ExecuteCommand",
       "ActionRegistry", "Action"
   ]
   ```

**Acceptance Criteria**:
- [ ] All message classes created and instantiable
- [ ] ActionRegistry implements all methods
- [ ] Can register, execute, and unregister actions
- [ ] Search functionality works with fuzzy matching
- [ ] Unit tests pass (minimum 15 tests total)
- [ ] Test coverage >90% for both files
- [ ] No circular import errors
- [ ] Existing TUI still runs

**Testing Commands**:
```bash
pytest caspoon/tests/unit/ui/core/test_actions.py -v
pytest caspoon/tests/unit/ui/core/test_actions_registry.py -v
pytest caspoon/tests/unit/ui/core/ --cov=caspoon/ui/core --cov-report=term-missing
```

**Estimated Complexity**: Medium (3-4 hours)

---

### Phase 1.3: Implement BaseView Widget Class

**Objective**: Create the foundational BaseView widget class that all analysis views will inherit from.

**Prerequisites**:
- Phases 1.1, 1.2 complete
- Read: `tui-architecture-redesign.md` section 2.1 (Base Widget Classes)
- Read: `tui-implementation-examples.md` example 1 (Simple Read-Only View)
- Understand Textual's Widget lifecycle and reactive properties

**Files to Create**:
- `caspoon/ui/core/base.py`
- `caspoon/tests/unit/ui/core/test_base.py`

**Files to Modify**:
- `caspoon/ui/core/__init__.py` (add exports)

**Implementation Details**:

1. **Implement `caspoon/ui/core/base.py`** with BaseView class:
   ```python
   from abc import ABC, abstractmethod
   from textual.reactive import reactive
   from textual.widgets import Static
   from typing import Generic, TypeVar, Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   T = TypeVar('T')
   
   class BaseView(Static, ABC, Generic[T]):
       """Base class for all Caspoon views.
       
       Provides:
       - Automatic state subscription via reactive properties
       - Lifecycle hooks (on_mount, on_show, on_hide)
       - Standard interface for data updates
       - Built-in error handling and loading states
       
       Subclasses must implement:
       - render_content(data: T) -> None
       
       Example:
           class MyView(BaseView[BinaryInfo]):
               def on_mount(self):
                   app.state.binary_info.watch(self, "_on_data_changed")
               
               def _on_data_changed(self, old, new):
                   self.data = new
               
               def render_content(self, data: BinaryInfo):
                   self.update(f"Path: {data.path}")
       """
       
       # Reactive properties
       data: reactive[Optional[T]] = reactive(None)
       is_loading: reactive[bool] = reactive(False)
       error: reactive[Optional[str]] = reactive(None)
       
       def watch_data(self, old_data: Optional[T], new_data: Optional[T]) -> None:
           """Called automatically when data changes.
           
           Triggers render_content() if new data is not None.
           """
           if self.error:
               # Clear error when new data arrives
               self.error = None
           
           if new_data is not None:
               try:
                   self.render_content(new_data)
               except Exception as e:
                   logger.error(f"Error rendering view {self.__class__.__name__}: {e}")
                   self.error = str(e)
       
       def watch_is_loading(self, old: bool, new: bool) -> None:
           """Show/hide loading indicator."""
           if new:
               self.show_loading()
           else:
               # Don't auto-hide, let data update handle it
               pass
       
       def watch_error(self, old: Optional[str], new: Optional[str]) -> None:
           """Display error state."""
           if new:
               self.show_error(new)
       
       @abstractmethod
       def render_content(self, data: T) -> None:
           """Render the view content.
           
           Subclasses implement this to display data.
           
           Args:
               data: The data to render
           """
           pass
       
       def show_loading(self) -> None:
           """Show loading indicator."""
           from rich.panel import Panel
           from rich.spinner import Spinner
           panel = Panel(Spinner("dots", text="Loading..."), border_style="blue")
           self.update(panel)
       
       def hide_loading(self) -> None:
           """Hide loading indicator."""
           # Will be replaced by actual content
           pass
       
       def show_error(self, error: str) -> None:
           """Show error message.
           
           Args:
               error: Error message to display
           """
           from rich.panel import Panel
           from rich.text import Text
           
           error_text = Text()
           error_text.append("Error: ", style="bold red")
           error_text.append(error)
           
           panel = Panel(error_text, border_style="red", title="Error")
           self.update(panel)
       
       # Lifecycle hooks (subclasses can override)
       
       def on_show(self) -> None:
           """Called when view becomes visible.
           
           Subclasses can override to perform actions when shown.
           """
           pass
       
       def on_hide(self) -> None:
           """Called when view becomes hidden.
           
           Subclasses can override to perform cleanup when hidden.
           """
           pass
       
       def refresh_view(self) -> None:
           """Force refresh the view with current data.
           
           Useful for manual updates without changing data.
           """
           if self.data is not None:
               self.render_content(self.data)
   ```

2. **Write comprehensive tests** in `caspoon/tests/unit/ui/core/test_base.py`:
   ```python
   import pytest
   from caspoon.ui.core.base import BaseView
   from rich.panel import Panel
   
   class ConcreteView(BaseView[str]):
       """Concrete implementation for testing."""
       
       def __init__(self):
           super().__init__()
           self.render_called = False
           self.rendered_data = None
       
       def render_content(self, data: str) -> None:
           self.render_called = True
           self.rendered_data = data
           self.update(f"Data: {data}")
   
   def test_base_view_initialization():
       """Test BaseView can be instantiated."""
       view = ConcreteView()
       assert view.data is None
       assert view.is_loading is False
       assert view.error is None
   
   def test_base_view_set_data():
       """Test setting data triggers render."""
       view = ConcreteView()
       view.data = "test data"
       
       assert view.render_called
       assert view.rendered_data == "test data"
   
   def test_base_view_data_update_multiple_times():
       """Test data can be updated multiple times."""
       view = ConcreteView()
       
       view.data = "first"
       assert view.rendered_data == "first"
       
       view.data = "second"
       assert view.rendered_data == "second"
   
   def test_base_view_none_data():
       """Test that None data doesn't trigger render."""
       view = ConcreteView()
       view.data = None
       
       assert not view.render_called
   
   def test_base_view_loading_state():
       """Test loading state shows loading indicator."""
       view = ConcreteView()
       view.is_loading = True
       
       # Should have called show_loading() which calls update()
       # Check that renderable is set (exact check depends on implementation)
       assert view.is_loading is True
   
   def test_base_view_error_state():
       """Test error state displays error."""
       view = ConcreteView()
       view.error = "Test error message"
       
       assert view.error == "Test error message"
       # Should have called show_error()
   
   def test_base_view_error_clears_on_data():
       """Test error is cleared when new data arrives."""
       view = ConcreteView()
       view.error = "Some error"
       
       view.data = "new data"
       
       assert view.error is None
       assert view.rendered_data == "new data"
   
   def test_base_view_render_error_handling():
       """Test that render errors are caught and displayed."""
       class ErrorView(BaseView[str]):
           def render_content(self, data: str):
               raise ValueError("Render failed")
       
       view = ErrorView()
       view.data = "test"
       
       assert view.error is not None
       assert "Render failed" in view.error
   
   def test_base_view_refresh():
       """Test manual refresh."""
       view = ConcreteView()
       view.data = "test"
       
       view.render_called = False
       view.refresh_view()
       
       assert view.render_called
       assert view.rendered_data == "test"
   
   def test_base_view_lifecycle_hooks():
       """Test lifecycle hooks can be called."""
       view = ConcreteView()
       
       # Should not raise errors
       view.on_show()
       view.on_hide()
   
   # Add more edge case tests
   ```

3. **Update `caspoon/ui/core/__init__.py`**:
   ```python
   from .base import BaseView
   # ... existing imports
   
   __all__ = [
       "BaseView",
       # ... existing exports
   ]
   ```

**Acceptance Criteria**:
- [ ] BaseView class compiles without errors
- [ ] Can create concrete subclass and instantiate
- [ ] Reactive data property triggers render_content()
- [ ] Loading and error states work correctly
- [ ] Error handling catches render exceptions
- [ ] Unit tests pass (minimum 10 tests)
- [ ] Test coverage >90% for base.py
- [ ] Existing TUI still runs
- [ ] No import errors from `caspoon.ui.core`

**Testing Commands**:
```bash
pytest caspoon/tests/unit/ui/core/test_base.py -v
pytest caspoon/tests/unit/ui/core/ --cov=caspoon/ui/core/base --cov-report=term-missing
python -m caspoon.ui  # Verify no regressions
```

**Estimated Complexity**: Simple (2-3 hours)

---

### Phase 1.4: Implement InteractiveView Widget Class

**Objective**: Extend BaseView with interactive capabilities (selection, keyboard navigation, filtering).

**Prerequisites**:
- Phase 1.3 complete
- Read: `tui-architecture-redesign.md` section 2.1 (InteractiveView)
- Read: `tui-implementation-examples.md` example 2 (Interactive List)
- Understand Textual's BINDINGS and action system

**Files to Create**:
- `caspoon/tests/unit/ui/core/test_interactive_view.py`

**Files to Modify**:
- `caspoon/ui/core/base.py` (add InteractiveView class)
- `caspoon/ui/core/__init__.py` (add export)

**Implementation Details**:

1. **Add InteractiveView to `caspoon/ui/core/base.py`**:
   ```python
   from textual.binding import Binding
   
   class InteractiveView(BaseView[T], ABC):
       """Base class for views with keyboard/mouse interaction.
       
       Adds:
       - Selection state management (selected_index)
       - Keyboard navigation (up/down/enter)
       - Search/filter support (filter_text)
       - Abstract methods for item interaction
       
       Subclasses must implement (in addition to render_content):
       - get_item_count() -> int
       - on_item_selected(index: int) -> None
       - apply_filter(text: str) -> None
       
       Example:
           class FunctionListView(InteractiveView[list[Function]]):
               BINDINGS = [
                   Binding("up", "move_up", "Move Up"),
                   Binding("down", "move_down", "Move Down"),
                   Binding("enter", "select_item", "Select"),
               ]
               
               def get_item_count(self):
                   return len(self._filtered_items)
               
               def on_item_selected(self, index: int):
                   func = self._filtered_items[index]
                   self.post_message(SelectFunction(func.name))
               
               def apply_filter(self, text: str):
                   self._filtered_items = [...]
       """
       
       # Reactive properties
       selected_index: reactive[int] = reactive(0)
       filter_text: reactive[str] = reactive("")
       
       # Default keybindings (can be overridden)
       BINDINGS = [
           Binding("up,k", "move_up", "Move Up", show=False),
           Binding("down,j", "move_down", "Move Down", show=False),
           Binding("enter", "select_item", "Select", show=True),
           Binding("home", "move_first", "First", show=False),
           Binding("end", "move_last", "Last", show=False),
       ]
       
       def watch_selected_index(self, old: int, new: int) -> None:
           """Re-render when selection changes."""
           # Trigger re-render to show new selection
           if self.data is not None:
               self.refresh_view()
       
       def watch_filter_text(self, old: str, new: str) -> None:
           """Re-filter items when filter text changes."""
           self.apply_filter(new)
           # Reset selection to first item after filtering
           self.selected_index = 0
       
       # Navigation actions
       
       def action_move_up(self) -> None:
           """Move selection up one item."""
           if self.selected_index > 0:
               self.selected_index -= 1
       
       def action_move_down(self) -> None:
           """Move selection down one item."""
           max_index = self.get_item_count() - 1
           if max_index >= 0 and self.selected_index < max_index:
               self.selected_index += 1
       
       def action_move_first(self) -> None:
           """Move selection to first item."""
           if self.get_item_count() > 0:
               self.selected_index = 0
       
       def action_move_last(self) -> None:
           """Move selection to last item."""
           count = self.get_item_count()
           if count > 0:
               self.selected_index = count - 1
       
       def action_select_item(self) -> None:
           """Activate/select the current item."""
           if 0 <= self.selected_index < self.get_item_count():
               self.on_item_selected(self.selected_index)
       
       # Abstract methods (must be implemented by subclasses)
       
       @abstractmethod
       def get_item_count(self) -> int:
           """Return the number of items currently displayed.
           
           Returns:
               Number of items (after filtering)
           """
           pass
       
       @abstractmethod
       def on_item_selected(self, index: int) -> None:
           """Handle item selection/activation.
           
           Called when user presses Enter or clicks an item.
           
           Args:
               index: Index of selected item
           """
           pass
       
       @abstractmethod
       def apply_filter(self, text: str) -> None:
           """Filter displayed items based on text.
           
           Args:
               text: Filter string (empty string = no filter)
           """
           pass
       
       # Helper methods
       
       def clear_filter(self) -> None:
           """Clear current filter."""
           self.filter_text = ""
       
       def get_selected_item_index(self) -> int:
           """Get current selected index.
           
           Returns:
               Selected index or -1 if no items
           """
           if self.get_item_count() == 0:
               return -1
           return self.selected_index
   ```

2. **Write tests** in `caspoon/tests/unit/ui/core/test_interactive_view.py`:
   ```python
   import pytest
   from caspoon.ui.core.base import InteractiveView
   
   class ConcreteInteractiveView(InteractiveView[list[str]]):
       """Concrete implementation for testing."""
       
       def __init__(self):
           super().__init__()
           self._items = []
           self._filtered_items = []
           self.selection_called = False
           self.selected_item = None
       
       def render_content(self, data: list[str]) -> None:
           self._items = data
           self.apply_filter(self.filter_text)
       
       def get_item_count(self) -> int:
           return len(self._filtered_items)
       
       def on_item_selected(self, index: int) -> None:
           self.selection_called = True
           self.selected_item = self._filtered_items[index]
       
       def apply_filter(self, text: str) -> None:
           if not text:
               self._filtered_items = self._items
           else:
               self._filtered_items = [
                   item for item in self._items
                   if text.lower() in item.lower()
               ]
   
   def test_interactive_view_initialization():
       """Test InteractiveView initializes correctly."""
       view = ConcreteInteractiveView()
       assert view.selected_index == 0
       assert view.filter_text == ""
   
   def test_interactive_view_navigation_down():
       """Test moving selection down."""
       view = ConcreteInteractiveView()
       view.data = ["item1", "item2", "item3"]
       
       assert view.selected_index == 0
       
       view.action_move_down()
       assert view.selected_index == 1
       
       view.action_move_down()
       assert view.selected_index == 2
   
   def test_interactive_view_navigation_up():
       """Test moving selection up."""
       view = ConcreteInteractiveView()
       view.data = ["item1", "item2", "item3"]
       view.selected_index = 2
       
       view.action_move_up()
       assert view.selected_index == 1
       
       view.action_move_up()
       assert view.selected_index == 0
   
   def test_interactive_view_navigation_boundaries():
       """Test navigation respects boundaries."""
       view = ConcreteInteractiveView()
       view.data = ["item1", "item2"]
       
       # Can't go below 0
       view.selected_index = 0
       view.action_move_up()
       assert view.selected_index == 0
       
       # Can't go above max
       view.selected_index = 1
       view.action_move_down()
       assert view.selected_index == 1
   
   def test_interactive_view_navigation_first_last():
       """Test jump to first/last."""
       view = ConcreteInteractiveView()
       view.data = ["item1", "item2", "item3", "item4", "item5"]
       
       view.action_move_last()
       assert view.selected_index == 4
       
       view.action_move_first()
       assert view.selected_index == 0
   
   def test_interactive_view_selection():
       """Test item selection."""
       view = ConcreteInteractiveView()
       view.data = ["apple", "banana", "cherry"]
       view.selected_index = 1
       
       view.action_select_item()
       
       assert view.selection_called
       assert view.selected_item == "banana"
   
   def test_interactive_view_filtering():
       """Test filtering items."""
       view = ConcreteInteractiveView()
       view.data = ["apple", "banana", "cherry", "apricot"]
       
       view.filter_text = "ap"
       
       assert view.get_item_count() == 2
       assert "apple" in view._filtered_items
       assert "apricot" in view._filtered_items
   
   def test_interactive_view_filter_resets_selection():
       """Test filtering resets selection to 0."""
       view = ConcreteInteractiveView()
       view.data = ["apple", "banana", "cherry"]
       view.selected_index = 2
       
       view.filter_text = "a"
       
       assert view.selected_index == 0
   
   def test_interactive_view_clear_filter():
       """Test clearing filter."""
       view = ConcreteInteractiveView()
       view.data = ["apple", "banana", "cherry"]
       view.filter_text = "ban"
       
       assert view.get_item_count() == 1
       
       view.clear_filter()
       
       assert view.filter_text == ""
       assert view.get_item_count() == 3
   
   def test_interactive_view_empty_list():
       """Test behavior with empty list."""
       view = ConcreteInteractiveView()
       view.data = []
       
       assert view.get_item_count() == 0
       assert view.get_selected_item_index() == -1
       
       # Navigation should not crash
       view.action_move_down()
       view.action_move_up()
   
   # Add more edge case tests
   ```

3. **Update `caspoon/ui/core/__init__.py`**:
   ```python
   from .base import BaseView, InteractiveView
   # ... rest
   
   __all__ = [
       "BaseView", "InteractiveView",
       # ... rest
   ]
   ```

**Acceptance Criteria**:
- [ ] InteractiveView extends BaseView correctly
- [ ] Navigation actions (up/down/first/last) work
- [ ] Selection state is tracked correctly
- [ ] Filtering works and resets selection
- [ ] Boundary conditions handled (empty list, edges)
- [ ] Unit tests pass (minimum 10 tests)
- [ ] Test coverage >90%
- [ ] Existing TUI still runs

**Testing Commands**:
```bash
pytest caspoon/tests/unit/ui/core/test_interactive_view.py -v
pytest caspoon/tests/unit/ui/core/ --cov=caspoon/ui/core/base --cov-report=term-missing
```

**Estimated Complexity**: Medium (3-4 hours)

---

### Phase 1.5: Implement TableView and TreeView Classes

**Objective**: Add specialized interactive views for tabular and hierarchical data.

**Prerequisites**:
- Phase 1.4 complete
- Read: `tui-architecture-redesign.md` section 2.1 (TableView, TreeView)
- Read: `tui-implementation-examples.md` examples 3-4

**Files to Create**:
- `caspoon/tests/unit/ui/core/test_table_view.py`
- `caspoon/tests/unit/ui/core/test_tree_view.py`

**Files to Modify**:
- `caspoon/ui/core/base.py` (add TableView and TreeView)
- `caspoon/ui/core/__init__.py` (add exports)

**Implementation Details**:

1. **Add TableView to `caspoon/ui/core/base.py`**:
   ```python
   class TableView(InteractiveView[T], ABC):
       """Base class for table-based views.
       
       Adds:
       - Column sorting (sort_column, sort_descending)
       - Column management
       - Row selection
       
       Subclasses must implement (in addition to InteractiveView methods):
       - get_columns() -> list[str]
       
       Example:
           class FunctionTableView(TableView[list[dict]]):
               def get_columns(self):
                   return ["Name", "Address", "Size"]
               
               def render_content(self, data):
                   # Render table with columns
       """
       
       # Reactive properties
       sort_column: reactive[Optional[str]] = reactive(None)
       sort_descending: reactive[bool] = reactive(False)
       
       def watch_sort_column(self, old: Optional[str], new: Optional[str]) -> None:
           """Re-render when sort column changes."""
           if self.data is not None:
               self.refresh_view()
       
       def watch_sort_descending(self, old: bool, new: bool) -> None:
           """Re-render when sort direction changes."""
           if self.data is not None:
               self.refresh_view()
       
       def action_sort_by_column(self, column: str) -> None:
           """Sort table by column.
           
           Toggles sort direction if already sorting by this column.
           
           Args:
               column: Column name to sort by
           """
           if self.sort_column == column:
               # Toggle direction
               self.sort_descending = not self.sort_descending
           else:
               # New column, default to ascending
               self.sort_column = column
               self.sort_descending = False
       
       def clear_sort(self) -> None:
           """Clear current sorting."""
           self.sort_column = None
           self.sort_descending = False
       
       @abstractmethod
       def get_columns(self) -> list[str]:
           """Return list of column names.
           
           Returns:
               List of column identifiers/names
           """
           pass
       
       def get_sort_indicator(self, column: str) -> str:
           """Get sort indicator for a column.
           
           Args:
               column: Column name
               
           Returns:
               " ▲", " ▼", or "" depending on sort state
           """
           if self.sort_column != column:
               return ""
           return " ▼" if self.sort_descending else " ▲"
   
   
   class TreeView(InteractiveView[T], ABC):
       """Base class for hierarchical tree views.
       
       Adds:
       - Expand/collapse nodes (expanded_nodes)
       - Hierarchical navigation
       - Node identification
       
       Subclasses must implement (in addition to InteractiveView methods):
       - get_selected_node_id() -> str
       
       Example:
           class FunctionTreeView(TreeView[list[Function]]):
               def get_selected_node_id(self):
                   return self._nodes[self.selected_index].id
               
               def render_content(self, data):
                   # Render tree with expand/collapse
       """
       
       # Reactive property
       expanded_nodes: reactive[set[str]] = reactive(set, init=False)
       
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           self.expanded_nodes = set()
       
       def watch_expanded_nodes(self, old: set[str], new: set[str]) -> None:
           """Re-render when expansion state changes."""
           if self.data is not None:
               self.refresh_view()
       
       def action_toggle_expand(self) -> None:
           """Expand/collapse current node."""
           node_id = self.get_selected_node_id()
           if not node_id:
               return
           
           if node_id in self.expanded_nodes:
               self.expanded_nodes.discard(node_id)
           else:
               self.expanded_nodes.add(node_id)
           
           # Trigger re-render
           self.refresh_view()
       
       def expand_node(self, node_id: str) -> None:
           """Expand a specific node.
           
           Args:
               node_id: Node identifier
           """
           self.expanded_nodes.add(node_id)
           self.refresh_view()
       
       def collapse_node(self, node_id: str) -> None:
           """Collapse a specific node.
           
           Args:
               node_id: Node identifier
           """
           self.expanded_nodes.discard(node_id)
           self.refresh_view()
       
       def is_node_expanded(self, node_id: str) -> bool:
           """Check if a node is expanded.
           
           Args:
               node_id: Node identifier
               
           Returns:
               True if expanded, False otherwise
           """
           return node_id in self.expanded_nodes
       
       def expand_all(self) -> None:
           """Expand all nodes."""
           # Subclass should populate expanded_nodes with all node IDs
           pass
       
       def collapse_all(self) -> None:
           """Collapse all nodes."""
           self.expanded_nodes.clear()
           self.refresh_view()
       
       @abstractmethod
       def get_selected_node_id(self) -> str:
           """Get ID of currently selected node.
           
           Returns:
               Node identifier or empty string if no selection
           """
           pass
   ```

2. **Write tests** for both classes (abbreviated):
   ```python
   # test_table_view.py
   class ConcreteTableView(TableView[list[dict]]):
       def __init__(self):
           super().__init__()
           self._rows = []
           self._filtered = []
       
       def get_columns(self):
           return ["Name", "Value"]
       
       def render_content(self, data):
           self._rows = data
           self.apply_filter(self.filter_text)
       
       def get_item_count(self):
           return len(self._filtered)
       
       def on_item_selected(self, index: int):
           pass
       
       def apply_filter(self, text: str):
           self._filtered = self._rows
   
   def test_table_view_sorting():
       view = ConcreteTableView()
       
       view.action_sort_by_column("Name")
       assert view.sort_column == "Name"
       assert view.sort_descending is False
       
       view.action_sort_by_column("Name")
       assert view.sort_descending is True
   
   def test_table_view_get_sort_indicator():
       view = ConcreteTableView()
       
       assert view.get_sort_indicator("Name") == ""
       
       view.sort_column = "Name"
       view.sort_descending = False
       assert view.get_sort_indicator("Name") == " ▲"
       
       view.sort_descending = True
       assert view.get_sort_indicator("Name") == " ▼"
   
   # test_tree_view.py
   class ConcreteTreeView(TreeView[list[str]]):
       def __init__(self):
           super().__init__()
           self._nodes = []
       
       def render_content(self, data):
           self._nodes = data
       
       def get_item_count(self):
           return len(self._nodes)
       
       def on_item_selected(self, index: int):
           pass
       
       def apply_filter(self, text: str):
           pass
       
       def get_selected_node_id(self):
           if 0 <= self.selected_index < len(self._nodes):
               return self._nodes[self.selected_index]
           return ""
   
   def test_tree_view_expand_collapse():
       view = ConcreteTreeView()
       view.data = ["node1", "node2", "node3"]
       view.selected_index = 0
       
       view.action_toggle_expand()
       assert "node1" in view.expanded_nodes
       
       view.action_toggle_expand()
       assert "node1" not in view.expanded_nodes
   
   def test_tree_view_is_node_expanded():
       view = ConcreteTreeView()
       
       assert not view.is_node_expanded("node1")
       
       view.expand_node("node1")
       assert view.is_node_expanded("node1")
   
   # Add 10+ more tests
   ```

3. **Update exports**

**Acceptance Criteria**:
- [ ] TableView and TreeView compile without errors
- [ ] Can create concrete subclasses
- [ ] Sorting works (toggle direction, multiple columns)
- [ ] Tree expand/collapse works
- [ ] Unit tests pass (minimum 10 tests each)
- [ ] Test coverage >85%
- [ ] Existing TUI still runs

**Testing Commands**:
```bash
pytest caspoon/tests/unit/ui/core/test_table_view.py -v
pytest caspoon/tests/unit/ui/core/test_tree_view.py -v
pytest caspoon/tests/unit/ui/core/ --cov=caspoon/ui/core/base
```

**Estimated Complexity**: Medium (4-5 hours)

---

### Phase 1.6: Foundation Integration Tests

**Objective**: Verify all Phase 1 components work together correctly.

**Prerequisites**:
- All Phase 1 phases (1.1-1.5) complete

**Files to Create**:
- `caspoon/tests/integration/ui/__init__.py`
- `caspoon/tests/integration/ui/test_foundation.py`

**Implementation Details**:

Write integration tests that verify:
1. AppState can be created and used with widgets
2. Actions can be posted and handled
3. BaseView subclasses can watch state
4. InteractiveView navigation works end-to-end
5. All base classes can coexist

```python
def test_state_and_base_view_integration():
    """Test AppState works with BaseView."""
    # Create state and view
    # Update state
    # Verify view updated

def test_action_registry_and_messages():
    """Test ActionRegistry executes handlers."""
    # Register actions
    # Execute via registry
    # Verify handlers called

def test_interactive_view_full_workflow():
    """Test complete interactive view workflow."""
    # Create interactive view with data
    # Navigate (up/down)
    # Filter
    # Select
    # Verify all state changes

# 5+ integration tests
```

**Acceptance Criteria**:
- [ ] All integration tests pass
- [ ] No errors when components interact
- [ ] Foundation is solid for Phase 2

**Estimated Complexity**: Simple (2 hours)

---

## PHASE 2: PROVE THE PATTERN

### Phase 2.1: Migrate OverviewView to New Architecture

**Objective**: Convert the simplest view (OverviewView) to use new BaseView architecture, proving the migration pattern works.

**Prerequisites**:
- Phase 1 complete
- Read: `tui-architecture-redesign.md` section 7.2 (Phase 2: Migrate First View)
- Read current `caspoon/ui/views/overview.py`

**Files to Create**:
- `caspoon/tests/unit/ui/views/test_overview_new.py`

**Files to Modify**:
- `caspoon/ui/views/overview.py` (refactor to use BaseView)

**Implementation Details**:

1. **Refactor `caspoon/ui/views/overview.py`**:
   ```python
   # OLD (before):
   class OverviewView(Static):
       def update_data(self, report: ExecutableReport) -> None:
           # Imperative update
           table = self._build_table(report)
           self.update(table)
   
   # NEW (after):
   from caspoon.ui.core.base import BaseView
   from caspoon.ui.core.models import BinaryInfo
   
   class OverviewView(BaseView[BinaryInfo]):
       """Overview of binary file information.
       
       Displays architecture, bits, type, protections, etc.
       """
       
       def on_mount(self) -> None:
           """Subscribe to binary info updates."""
           from caspoon.ui.app import CaspoonApp
           app: CaspoonApp = self.app
           
           # Watch for binary info changes
           if hasattr(app, 'state'):
               app.state.binary_info.watch(self, "_on_binary_info_changed")
       
       def _on_binary_info_changed(self, old_value, new_value) -> None:
           """Update view when binary info changes."""
           self.data = new_value
       
       def render_content(self, data: BinaryInfo) -> None:
           """Render binary information."""
           from rich.table import Table
           from rich.panel import Panel
           
           table = Table.grid(padding=(0, 2))
           table.add_column(style="bold cyan", justify="right")
           table.add_column()
           
           table.add_row("File:", data.path)
           table.add_row("Architecture:", data.architecture)
           table.add_row("Bits:", f"{data.bits}-bit")
           table.add_row("Type:", data.file_type)
           table.add_row("Stripped:", "Yes" if data.stripped else "No")
           table.add_row("Size:", f"{data.file_size:,} bytes")
           
           if data.entry_point:
               table.add_row("Entry Point:", data.entry_point)
           
           panel = Panel(
               table,
               title="[bold]Binary Information[/]",
               border_style="blue"
           )
           
           self.update(panel)
       
       # COMPATIBILITY SHIM (temporary, can be removed later)
       def update_data(self, report) -> None:
           """Legacy interface for compatibility.
           
           DEPRECATED: Use state-based updates instead.
           This exists only for migration period.
           """
           # Convert report to BinaryInfo
           from caspoon.ui.core.models import BinaryInfo
           
           self.data = BinaryInfo(
               path=report.file_path,
               architecture=report.binary_info.get("arch", "unknown"),
               bits=report.binary_info.get("bits", 0),
               file_type=report.binary_info.get("type", "unknown"),
               stripped=report.binary_info.get("stripped", False),
               file_size=report.binary_info.get("size", 0),
               entry_point=report.binary_info.get("entry", None)
           )
   ```

2. **Write tests**:
   ```python
   # test_overview_new.py
   from caspoon.ui.views.overview import OverviewView
   from caspoon.ui.core.models import BinaryInfo
   
   def test_overview_view_initialization():
       view = OverviewView()
       assert view.data is None
   
   def test_overview_view_render_content():
       view = OverviewView()
       info = BinaryInfo(
           path="/bin/ls",
           architecture="x86_64",
           bits=64,
           file_type="ELF",
           stripped=False,
           file_size=12345
       )
       
       view.render_content(info)
       # Verify renderable is set
   
   def test_overview_view_data_update():
       view = OverviewView()
       info = BinaryInfo(
           path="/test",
           architecture="arm64",
           bits=64,
           file_type="MACH",
           stripped=True,
           file_size=5000
       )
       
       view.data = info
       # Should have triggered render
   
   # Add 7+ more tests
   ```

3. **DO NOT modify `caspoon/ui/app.py` yet** - keep compatibility
   - Old `display_report()` should still work
   - View will work with both old and new interfaces

**Acceptance Criteria**:
- [ ] OverviewView extends BaseView correctly
- [ ] Can set data via reactive property
- [ ] Legacy `update_data()` still works (compatibility)
- [ ] Renders correctly with test data
- [ ] Unit tests pass (minimum 10 tests)
- [ ] Existing TUI still runs and works
- [ ] Can load a real binary and see overview
- [ ] No visual regressions

**Testing Commands**:
```bash
pytest caspoon/tests/unit/ui/views/test_overview_new.py -v
python -m caspoon.ui  # Test manually with real binary
```

**Estimated Complexity**: Medium (3-4 hours)

---

### Phase 2.2: Integrate AppState into CaspoonApp

**Objective**: Modify CaspoonApp to use AppState and support both old and new view interfaces during migration.

**Prerequisites**:
- Phase 2.1 complete
- Read: `tui-architecture-redesign.md` section 7.2

**Files to Create**:
- `caspoon/tests/integration/ui/test_app_state_integration.py`

**Files to Modify**:
- `caspoon/ui/app.py` (add AppState, keep backward compatibility)

**Implementation Details**:

1. **Modify `caspoon/ui/app.py`**:
   ```python
   from caspoon.ui.core.state import AppState
   from caspoon.ui.core.actions_registry import ActionRegistry
   
   class CaspoonApp(App):
       """Main Textual application for interactive binary analysis."""
       
       TITLE = "Caspoon Reverse Engineering Toolkit"
       SUB_TITLE = "Executable Recon Viewer"
       
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           # NEW: Add centralized state
           self.state = AppState()
           # NEW: Add action registry (empty for now)
           self.action_registry = ActionRegistry()
       
       # ... compose() stays the same ...
       
       def on_input_submitted(self, message: Input.Submitted) -> None:
           """Handle input submission when user enters a file path."""
           path = message.value.strip()
           if not path:
               self.set_status("Error: Please enter a path")
               return
           
           # Validation (keep as-is)
           if not os.path.exists(path):
               self.set_status(f"Error: File not found - {path}")
               return
           
           # ... other validation ...
           
           try:
               self.set_status(f"Analyzing: {path}...")
               runner = ReconRunner()
               report = runner.run(path)
               
               # NEW: Update centralized state
               self.state.update_from_report(report)
               
               # OLD: Still call display_report for non-migrated views
               self.display_report(report)
               
               self.set_status(f"Loaded: {path}")
           except Exception as e:
               logger.error(f"Error analyzing file: {e}")
               self.set_status(f"Error: {str(e)}")
       
       def display_report(self, report) -> None:
           """Display analysis report across all views.
           
           MIGRATION NOTE: This is a compatibility shim.
           As views are migrated to watch AppState, they won't need this.
           OverviewView now uses state, so it gets updated twice (harmless).
           """
           try:
               # OverviewView will get update via state AND via this
               # (Harmless duplication during migration)
               self.query_one("#overview").update_data(report)
               
               # These views still need imperative updates
               self.query_one("#protections").update_data(report)
               self.query_one("#strings_view").update_data(report)
               self.query_one("#imp_exp").update_data(report)
               self.query_one("#r2_view").update_data(report)
           except Exception as e:
               logger.error(f"Error updating views: {e}")
   ```

2. **Write integration tests**:
   ```python
   import pytest
   from textual.pilot import Pilot
   from caspoon.ui.app import CaspoonApp
   
   @pytest.mark.asyncio
   async def test_app_has_state():
       """Test CaspoonApp has AppState."""
       app = CaspoonApp()
       assert hasattr(app, 'state')
       assert app.state is not None
   
   @pytest.mark.asyncio
   async def test_app_state_updates_overview():
       """Test state updates propagate to OverviewView."""
       app = CaspoonApp()
       
       async with app.run_test() as pilot:
           # Get overview view
           overview = app.query_one("#overview")
           
           # Update state
           from caspoon.ui.core.models import BinaryInfo
           app.state.binary_info = BinaryInfo(
               path="/test",
               architecture="x86_64",
               bits=64,
               file_type="ELF",
               stripped=False,
               file_size=1000
           )
           
           await pilot.pause()
           
           # Verify overview received update
           assert overview.data is not None
           assert overview.data.path == "/test"
   
   # Add more integration tests
   ```

**Acceptance Criteria**:
- [ ] CaspoonApp has `state` attribute
- [ ] State is updated when binary is analyzed
- [ ] OverviewView receives state updates automatically
- [ ] Old views still work via `display_report()`
- [ ] Integration tests pass
- [ ] Can still load real binaries successfully
- [ ] No regressions in functionality

**Testing Commands**:
```bash
pytest caspoon/tests/integration/ui/test_app_state_integration.py -v
python -m caspoon.ui
# Test: Enter a binary path, verify all views update
```

**Estimated Complexity**: Medium (3-4 hours)

---

### Phase 2.3: Add Manual Test Plan and Documentation

**Objective**: Document the migration pattern and create manual test checklist.

**Prerequisites**:
- Phases 2.1, 2.2 complete

**Files to Create**:
- `caspoon/docs/guides/tui-migration-checklist.md`

**Implementation Details**:

Create a checklist document that future agents (or developers) can use when migrating other views:

```markdown
# TUI View Migration Checklist

## For Each View

### 1. Preparation
- [ ] Read current view implementation
- [ ] Identify what data it needs
- [ ] Determine which base class (BaseView, InteractiveView, TableView, TreeView)
- [ ] Map data to AppState properties

### 2. Implementation
- [ ] Change parent class to appropriate base class
- [ ] Add type parameter (e.g., `BaseView[BinaryInfo]`)
- [ ] Implement `on_mount()` to watch state
- [ ] Refactor `update_data()` logic into `render_content()`
- [ ] Add compatibility shim `update_data()` (calls `self.data = ...`)
- [ ] Implement abstract methods if needed (InteractiveView)

### 3. Testing
- [ ] Write unit tests for new implementation
- [ ] Test reactive updates work
- [ ] Test with existing TUI (should still work)
- [ ] Manual test with real binary
- [ ] Check for visual regressions

### 4. Cleanup (After All Views Migrated)
- [ ] Remove `update_data()` compatibility shim
- [ ] Remove `display_report()` from app.py
- [ ] Update all tests

## Example Migration

[Include OverviewView as example]
```

**Acceptance Criteria**:
- [ ] Documentation created
- [ ] Manual test checklist complete
- [ ] Migration pattern documented

**Estimated Complexity**: Simple (1-2 hours)

---

## PHASE 3: MIGRATE REMAINING VIEWS

### Phase 3.1: Migrate ProtectionsView

**Objective**: Migrate ProtectionsView to use new architecture.

**Prerequisites**:
- Phase 2 complete
- Read migration checklist from Phase 2.3
- Read current `caspoon/ui/views/protections.py`

**Files to Create/Modify**:
- `caspoon/ui/views/protections.py` (refactor)
- `caspoon/tests/unit/ui/views/test_protections_new.py`

**Implementation Details**:

Follow the same pattern as OverviewView:
1. Change to `BaseView[dict]` (protections are a dict)
2. Watch `app.state.analysis_results` for protections
3. Implement `render_content(data: dict)`
4. Add compatibility shim
5. Write tests

**Acceptance Criteria**:
- [ ] ProtectionsView uses BaseView
- [ ] Watches state correctly
- [ ] Renders protections data
- [ ] Tests pass (min 8 tests)
- [ ] Existing TUI works
- [ ] No visual regressions

**Estimated Complexity**: Simple (2-3 hours)

---

### Phase 3.2: Migrate StringsView

**Objective**: Migrate StringsView to use InteractiveView (has filtering).

**Prerequisites**:
- Phase 3.1 complete

**Files to Create/Modify**:
- `caspoon/ui/views/strings_view.py` (refactor to InteractiveView)
- `caspoon/tests/unit/ui/views/test_strings_new.py`

**Implementation Details**:

1. Change to `InteractiveView[list[str]]`
2. Implement `get_item_count()`, `on_item_selected()`, `apply_filter()`
3. Watch `app.state.analysis_results.strings`
4. Add BINDINGS for navigation

**Acceptance Criteria**:
- [ ] StringsView uses InteractiveView
- [ ] Filtering works
- [ ] Navigation (up/down) works
- [ ] Tests pass (min 10 tests)
- [ ] Manual test shows filtering works

**Estimated Complexity**: Medium (3 hours)

---

### Phase 3.3: Migrate ImportsExportsView

**Objective**: Migrate ImportsExportsView (shows two tables).

**Prerequisites**:
- Phase 3.2 complete

**Files to Create/Modify**:
- `caspoon/ui/views/imports_exports.py` (refactor)
- `caspoon/tests/unit/ui/views/test_imports_exports_new.py`

**Implementation Details**:

This view shows both imports and exports. Options:
1. Use `BaseView[AnalysisResults]` and render both tables
2. Split into two separate InteractiveView widgets

Recommend option 1 for simplicity.

**Acceptance Criteria**:
- [ ] View uses new architecture
- [ ] Shows both imports and exports
- [ ] Tests pass (min 8 tests)
- [ ] Existing functionality preserved

**Estimated Complexity**: Medium (3 hours)

---

### Phase 3.4: Migrate R2View

**Objective**: Migrate R2View (most complex - has syntax highlighting).

**Prerequisites**:
- Phase 3.3 complete
- Understand existing syntax highlighting system

**Files to Create/Modify**:
- `caspoon/ui/views/r2_view.py` (refactor)
- `caspoon/tests/unit/ui/views/test_r2_new.py`

**Implementation Details**:

This is the most complex view:
1. Uses `InteractiveView[str]` (disassembly text)
2. Integrates with existing syntax highlighting
3. Watch `app.state.analysis_results.disassembly`
4. Keep syntax highlighting logic intact

**Acceptance Criteria**:
- [ ] R2View uses new architecture
- [ ] Syntax highlighting still works
- [ ] Navigation works
- [ ] Tests pass (min 10 tests)
- [ ] No performance regressions

**Estimated Complexity**: Complex (5-6 hours)

---

### Phase 3.5: Remove Compatibility Shims

**Objective**: Clean up migration code now that all views are migrated.

**Prerequisites**:
- All views migrated (3.1-3.4 complete)

**Files to Modify**:
- `caspoon/ui/app.py` (remove `display_report()`)
- All views (remove `update_data()` compatibility methods)

**Implementation Details**:

1. Remove `display_report()` method from CaspoonApp
2. Remove `update_data()` from all views
3. Update all tests to use state-based updates
4. Verify everything still works

**Acceptance Criteria**:
- [ ] No more `display_report()` or `update_data()` calls
- [ ] All tests pass
- [ ] Integration tests pass
- [ ] Manual testing shows full functionality

**Estimated Complexity**: Simple (2 hours)

---

## PHASE 4: ADVANCED FEATURES

### Phase 4.1: Implement Command Palette Widget

**Objective**: Create the Ctrl+P command palette with fuzzy search.

**Prerequisites**:
- Phase 3 complete
- Read: `tui-architecture-redesign.md` section 5.1 (Command Palette)

**Files to Create**:
- `caspoon/ui/widgets/__init__.py`
- `caspoon/ui/widgets/command_palette.py`
- `caspoon/tests/unit/ui/widgets/test_command_palette.py`

**Implementation Details**:

```python
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container, Vertical
from textual.binding import Binding

class CommandPalette(Container):
    """Fuzzy-search command palette (Ctrl+P style)."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "execute", "Execute"),
    ]
    
    def __init__(self, action_registry: ActionRegistry, **kwargs):
        super().__init__(**kwargs)
        self.action_registry = action_registry
        self._filtered_actions = []
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Type to search commands...")
            yield ListView(id="results")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands based on input."""
        query = event.value
        self._filtered_actions = self.action_registry.search_actions(query)
        self._update_results()
    
    def _update_results(self) -> None:
        """Update result list."""
        results_list = self.query_one("#results", ListView)
        results_list.clear()
        
        for action in self._filtered_actions[:10]:  # Top 10
            keybind = action.keybinding or ""
            label = f"{action.name} [{keybind}]" if keybind else action.name
            results_list.append(ListItem(Label(label)))
    
    def action_execute(self) -> None:
        """Execute selected command."""
        # Get selected action and execute
        pass
    
    def action_close(self) -> None:
        """Close palette."""
        self.display = False
```

Write comprehensive tests for search, selection, execution.

**Acceptance Criteria**:
- [ ] CommandPalette widget created
- [ ] Fuzzy search works
- [ ] Can execute commands
- [ ] Tests pass (min 10 tests)
- [ ] Keybindings work

**Estimated Complexity**: Complex (5-6 hours)

---

### Phase 4.2: Integrate Command Palette into CaspoonApp

**Objective**: Add command palette to app and register default commands.

**Prerequisites**:
- Phase 4.1 complete

**Files to Modify**:
- `caspoon/ui/app.py` (add command palette, register actions)

**Implementation Details**:

1. Add CommandPalette to compose()
2. Register default actions (analyze, reload, quit, switch tabs, etc.)
3. Add Ctrl+P keybinding to show palette
4. Wire up action execution

**Acceptance Criteria**:
- [ ] Ctrl+P opens command palette
- [ ] Can search and execute commands
- [ ] All default commands registered
- [ ] Manual testing works

**Estimated Complexity**: Medium (3-4 hours)

---

### Phase 4.3: Implement Async Analysis Worker

**Objective**: Make binary analysis non-blocking with progress reporting.

**Prerequisites**:
- Phase 4.2 complete
- Read: `tui-architecture-redesign.md` section 4 (Async Workers)

**Files to Modify**:
- `caspoon/ui/app.py` (add async worker)

**Implementation Details**:

```python
async def _analyze_binary_async(self, path: str) -> None:
    """Analyze binary in background worker with progress."""
    
    # Update UI state
    self.state.ui_state.is_analyzing = True
    self.state.ui_state.analysis_progress = 0
    
    try:
        # Progress: 10%
        self.post_message(AnalysisProgress(10, "Loading binary..."))
        
        # Run blocking runner.run() in thread pool
        runner = ReconRunner()
        report = await asyncio.to_thread(runner.run, path)
        
        # Progress: 90%
        self.post_message(AnalysisProgress(90, "Processing results..."))
        
        # Update state
        self.state.update_from_report(report)
        
        # Progress: 100%
        self.post_message(AnalysisProgress(100, "Complete"))
        self.post_message(AnalysisComplete(report))
        
    except Exception as e:
        self.post_message(AnalysisError(str(e)))
    finally:
        self.state.ui_state.is_analyzing = False

def on_input_submitted(self, message: Input.Submitted) -> None:
    """Handle input submission."""
    path = message.value.strip()
    # ... validation ...
    
    # Run async worker instead of blocking
    self.run_worker(self._analyze_binary_async(path))
```

**Acceptance Criteria**:
- [ ] Analysis runs in background
- [ ] UI stays responsive during analysis
- [ ] Progress updates shown
- [ ] Can cancel analysis (optional enhancement)
- [ ] No regressions

**Estimated Complexity**: Medium (4 hours)

---

### Phase 4.4: Implement Multi-Panel Layout

**Objective**: Add sidebar, details panel, and bottom panel with toggle capabilities.

**Prerequisites**:
- Phase 4.3 complete
- Read: `tui-architecture-redesign.md` section 1.1 (Layout)

**Files to Create**:
- `caspoon/ui/screens/main.py` (new MainScreen)
- `caspoon/ui/widgets/sidebar.py`
- `caspoon/ui/widgets/details_panel.py`

**Files to Modify**:
- `caspoon/ui/app.py` (use new MainScreen)

**Implementation Details**:

Create multi-panel layout matching architecture diagram. Panels should be collapsible.

**Acceptance Criteria**:
- [ ] Multi-panel layout works
- [ ] Panels can be toggled (Ctrl+B, Ctrl+D, Ctrl+J)
- [ ] Layout responsive
- [ ] All existing views fit in content area
- [ ] Manual testing shows good UX

**Estimated Complexity**: Complex (6-8 hours)

---

### Phase 4.5: Custom Analysis Widgets

**Objective**: Create specialized widgets (FunctionExplorer, HexViewer, etc.).

**Prerequisites**:
- Phase 4.4 complete

**Files to Create**:
- `caspoon/ui/widgets/function_explorer.py` (TreeView of functions)
- `caspoon/ui/widgets/hex_viewer.py` (Hex dump view)

**Implementation Details**:

These are optional enhancements. Implement as time allows:
1. **FunctionExplorer**: TreeView showing functions by section/type
2. **HexViewer**: Interactive hex dump with navigation

**Acceptance Criteria**:
- [ ] Widgets created and integrated
- [ ] Tests pass
- [ ] Enhance user experience

**Estimated Complexity**: Complex (8+ hours)

---

## PHASE 5: TESTING & POLISH

### Phase 5.1: Comprehensive Integration Tests

**Objective**: Add end-to-end integration tests covering all workflows.

**Prerequisites**:
- Phase 4 complete

**Files to Create**:
- `caspoon/tests/integration/ui/test_full_workflows.py`

**Implementation Details**:

Test complete user workflows:
1. Load binary → All views update
2. Navigate between tabs
3. Use command palette
4. Filter/search in views
5. Error handling
6. Async analysis with progress

**Acceptance Criteria**:
- [ ] 10+ integration tests covering workflows
- [ ] All tests pass
- [ ] Test coverage >80% overall

**Estimated Complexity**: Medium (4-5 hours)

---

### Phase 5.2: Snapshot/Visual Regression Tests

**Objective**: Add snapshot tests to catch visual regressions.

**Prerequisites**:
- Phase 5.1 complete
- Install `syrupy` or similar

**Files to Create**:
- `caspoon/tests/ui/test_visual_snapshots.py`

**Implementation Details**:

Capture rendered output of key views and save as snapshots.

**Acceptance Criteria**:
- [ ] Snapshot tests for all views
- [ ] Baseline snapshots captured
- [ ] Can detect visual changes

**Estimated Complexity**: Simple (3 hours)

---

### Phase 5.3: Performance Testing and Optimization

**Objective**: Test with large binaries and optimize if needed.

**Prerequisites**:
- Phase 5.2 complete

**Files to Create**:
- `caspoon/tests/performance/test_large_binaries.py`

**Implementation Details**:

1. Test with large binaries (10k+ functions, 1M+ strings)
2. Measure render times
3. Add virtual scrolling if needed
4. Optimize hot paths

**Acceptance Criteria**:
- [ ] Performance tests created
- [ ] Handles large binaries (<2s render)
- [ ] No UI lag during navigation
- [ ] Memory usage reasonable

**Estimated Complexity**: Medium (4 hours)

---

### Phase 5.4: Update Documentation

**Objective**: Document new architecture for users and developers.

**Prerequisites**:
- Phase 5.3 complete

**Files to Create/Modify**:
- `caspoon/docs/guides/tui-usage.md` (user guide)
- `caspoon/docs/reference/tui-api.md` (developer reference)
- `caspoon/README.md` (update with new features)

**Implementation Details**:

Document:
1. New command palette features
2. Keyboard shortcuts
3. Developer guide for creating new views
4. Architecture overview
5. Migration notes

**Acceptance Criteria**:
- [ ] User documentation complete
- [ ] Developer documentation complete
- [ ] README updated
- [ ] Architecture diagrams included

**Estimated Complexity**: Medium (4 hours)

---

### Phase 5.5: Final Testing and Bug Fixes

**Objective**: Comprehensive manual testing and bug fixing.

**Prerequisites**:
- All previous phases complete

**Implementation Details**:

1. Manual test all features
2. Test on different terminals
3. Test with various binaries
4. Fix any discovered bugs
5. Polish UX rough edges

**Acceptance Criteria**:
- [ ] All features tested manually
- [ ] No critical bugs
- [ ] All tests pass
- [ ] Ready for production use

**Estimated Complexity**: Medium (4-6 hours)

---

## Task Dependencies

### Dependency Graph

```
Phase 1: Foundation (All can run in parallel after structure)
├─ 1.1: State Management (prerequisite for all)
├─ 1.2: Actions (depends on 1.1)
├─ 1.3: BaseView (depends on 1.1)
├─ 1.4: InteractiveView (depends on 1.3)
├─ 1.5: TableView/TreeView (depends on 1.4)
└─ 1.6: Foundation Tests (depends on 1.1-1.5)

Phase 2: Prove Pattern (Sequential)
├─ 2.1: Migrate OverviewView (depends on Phase 1)
├─ 2.2: Integrate AppState (depends on 2.1)
└─ 2.3: Documentation (depends on 2.2)

Phase 3: Migrate Views (Can be parallel after 2.3)
├─ 3.1: ProtectionsView (depends on 2.3)
├─ 3.2: StringsView (depends on 3.1)
├─ 3.3: ImportsExportsView (depends on 3.2)
├─ 3.4: R2View (depends on 3.3)
└─ 3.5: Remove Shims (depends on 3.1-3.4)

Phase 4: Advanced Features (Some parallel)
├─ 4.1: Command Palette (depends on Phase 3)
├─ 4.2: Integrate Palette (depends on 4.1)
├─ 4.3: Async Workers (depends on 4.2, can be parallel with 4.4)
├─ 4.4: Multi-Panel Layout (depends on 4.2, can be parallel with 4.3)
└─ 4.5: Custom Widgets (depends on 4.4)

Phase 5: Polish (Sequential)
├─ 5.1: Integration Tests (depends on Phase 4)
├─ 5.2: Snapshot Tests (depends on 5.1)
├─ 5.3: Performance (depends on 5.2)
├─ 5.4: Documentation (depends on 5.3)
└─ 5.5: Final Testing (depends on 5.4)
```

### Parallelization Opportunities

**Can be done in parallel:**
- Phase 1.2-1.5 (after 1.1 complete)
- Phase 3.1-3.4 (after 2.3, with coordination)
- Phase 4.3 and 4.4 (after 4.2)

**Must be sequential:**
- Phase 2 (proving the pattern before mass migration)
- Phase 3.5 (cleanup after all views migrated)
- Phase 5 (testing depends on complete implementation)

---

## Testing Requirements

### Per-Phase Testing

Each phase must include:
1. **Unit tests** for new/modified code
   - Minimum 80% coverage for new code
   - Test happy path and edge cases
   - Test error handling

2. **Regression tests**
   - Verify existing TUI still works
   - Run `python -m caspoon.ui` after each phase
   - Test with a real binary

3. **Integration tests** (where applicable)
   - Test component interactions
   - Test state flow
   - Test message passing

### Integration Test Strategy

**After Phase 1**: Test foundation components work together
**After Phase 2**: Test state-based updates work end-to-end
**After Phase 3**: Test all views receive state updates
**After Phase 4**: Test complete user workflows
**Phase 5**: Comprehensive integration and performance testing

### System Test Commands

```bash
# Run all unit tests
pytest caspoon/tests/unit/ -v

# Run integration tests
pytest caspoon/tests/integration/ -v

# Run specific phase tests
pytest caspoon/tests/unit/ui/core/ -v  # Phase 1
pytest caspoon/tests/unit/ui/views/ -v  # Phase 3

# Check coverage
pytest --cov=caspoon/ui --cov-report=html --cov-report=term-missing

# Manual testing
python -m caspoon.ui
# Then: Load /bin/ls, test navigation, test features
```

---

## Migration Strategy

### Coexistence Approach

During migration (Phases 2-3), old and new code coexist:

1. **Old views** use `update_data(report)` interface
2. **New views** watch `AppState` reactive properties
3. **CaspoonApp** updates both:
   - Calls `state.update_from_report(report)` → new views update
   - Calls `display_report(report)` → old views update

### Compatibility Shims

**In migrated views** (Phases 2-3):
```python
def update_data(self, report) -> None:
    """DEPRECATED: Legacy interface."""
    self.data = convert_report_to_model(report)
```

**In CaspoonApp** (Phases 2-3):
```python
def display_report(self, report) -> None:
    """DEPRECATED: Will be removed after all views migrated."""
    # Update state (for new views)
    self.state.update_from_report(report)
    
    # Update old views directly
    for view_id in ["#protections", "#strings_view"]:  # Not migrated yet
        self.query_one(view_id).update_data(report)
```

### Cleanup (Phase 3.5)

After all views migrated:
1. Remove all `update_data()` methods from views
2. Remove `display_report()` from CaspoonApp
3. Update tests to use state-based updates only

### Feature Flags

If needed for gradual rollout:
```python
# caspoon/ui/config.py
class UIFeatures:
    COMMAND_PALETTE_ENABLED = True
    MULTI_PANEL_LAYOUT_ENABLED = False  # Phase 4.4
    ASYNC_ANALYSIS_ENABLED = True
```

### Rollback Plan

**Per-feature rollback**:
- Each phase produces working code
- Can stop at any phase and ship
- Use feature flags to disable incomplete features

**Full rollback**:
- Keep old code in git history
- Tag releases at stable points
- Can revert to any previous phase

---

## Validation Checklist

### Final Acceptance Criteria

Before declaring migration complete, verify:

#### Functionality
- [ ] All views display data correctly
- [ ] All existing features work (analysis, navigation, etc.)
- [ ] Command palette works (Ctrl+P)
- [ ] Keybindings work
- [ ] Error handling works
- [ ] Can analyze real binaries successfully
- [ ] No crashes or exceptions during normal use

#### Architecture
- [ ] All views inherit from base classes
- [ ] All views watch AppState (no manual updates)
- [ ] Message system used for all actions
- [ ] No circular dependencies
- [ ] Code follows architecture design

#### Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage >80% overall
- [ ] Performance tests pass
- [ ] No failing tests in CI

#### Performance
- [ ] Handles large binaries (10k+ functions) smoothly
- [ ] UI stays responsive during analysis
- [ ] No memory leaks
- [ ] Render times <100ms for typical views
- [ ] Async workers don't block UI

#### User Experience
- [ ] All features discoverable via command palette
- [ ] Keybindings are consistent and intuitive
- [ ] Error messages are clear
- [ ] Loading states shown during long operations
- [ ] No visual regressions

#### Code Quality
- [ ] Code follows project style guide
- [ ] All functions have docstrings
- [ ] Type hints added where appropriate
- [ ] No TODO/FIXME comments left
- [ ] Code reviewed (if applicable)

#### Documentation
- [ ] User guide updated
- [ ] Developer documentation complete
- [ ] Architecture diagrams accurate
- [ ] README reflects new features
- [ ] Migration guide available

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Test Coverage | >80% | `pytest --cov` |
| Unit Tests | >100 tests | `pytest --collect-only` |
| Integration Tests | >20 tests | Count in test files |
| Performance | <2s to load binary | Manual timing |
| Response Time | <100ms for navigation | Manual testing |
| Memory Usage | <500MB for large binary | `ps` or memory profiler |
| Lines of Code | <3000 new LOC | `cloc` or `tokei` |

### Qualitative Metrics

- [ ] Code is more maintainable than before
- [ ] Adding new views is easier (follow examples)
- [ ] Tests are easier to write and understand
- [ ] User experience is improved (responsive, discoverable)
- [ ] Architecture is extensible (plugins possible)

---

## Notes for AI Agents

### How to Use This Plan

1. **Choose a phase** based on dependencies and what's complete
2. **Read prerequisites** listed in the phase
3. **Follow implementation details** step by step
4. **Write tests first** or alongside implementation
5. **Verify acceptance criteria** before moving on
6. **Run regression tests** to ensure nothing broke
7. **Update this document** if you discover issues or improvements

### When Stuck

1. **Read the reference docs** in prerequisites
2. **Look at implementation examples** in `tui-implementation-examples.md`
3. **Check similar phases** that have been completed
4. **Ask for clarification** if requirements are unclear
5. **Simplify** - it's okay to implement a subset and iterate

### Communication Between Agents

If multiple agents are working in parallel:
- **Phase 1 agents**: Coordinate on shared files (base.py, __init__.py)
- **Phase 3 agents**: Can work independently on different views
- **Update this document**: Mark phases as complete with date/agent

### Best Practices

1. **Keep existing code working** - every commit should pass tests
2. **Write tests first** - makes implementation easier
3. **Commit frequently** - small, atomic commits
4. **Run the TUI after each phase** - catch issues early
5. **Document non-obvious decisions** - help future agents

---

## Appendix: Quick Command Reference

### Run Tests
```bash
# All tests
pytest -v

# Specific phase
pytest caspoon/tests/unit/ui/core/ -v                    # Phase 1
pytest caspoon/tests/unit/ui/views/test_overview_new.py  # Phase 2

# With coverage
pytest --cov=caspoon/ui --cov-report=term-missing

# Fast (skip slow tests)
pytest -m "not slow"
```

### Run TUI
```bash
# Launch TUI
python -m caspoon.ui

# With test binary
python -m caspoon.ui --binary /bin/ls  # If we add CLI args
```

### Code Quality
```bash
# Linting
ruff check caspoon/ui/
black --check caspoon/ui/
mypy caspoon/ui/

# Format
black caspoon/ui/
ruff check --fix caspoon/ui/
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/tui-phase-1.1

# Commit work
git add -A
git commit -m "Phase 1.1: Implement AppState"

# Before pushing, verify tests pass
pytest -v
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-02 | Initial comprehensive implementation plan |

---

**END OF IMPLEMENTATION PLAN**

Total Phases: 40  
Estimated Total Time: 8 weeks (320 hours)  
Parallelization Potential: ~20% time savings with multiple agents

This plan is designed to be executed autonomously by AI agents while maintaining system stability and producing testable, incremental improvements.
