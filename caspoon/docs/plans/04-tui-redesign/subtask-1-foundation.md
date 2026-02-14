# Subtask 1: Foundation & State Management

## Objective

Establish the foundational architecture for the TUI redesign by implementing centralized reactive state management, a message-based action system, and the core directory structure.

## Scope

**Included:**
- Centralized AppState with reactive properties for binary data, analysis results, UI state, and user preferences
- Message types for decoupled component communication (analysis events, navigation, UI actions)
- Action registry for command/keybinding management
- Core directory structure (`ui/core/`, `ui/widgets/`, `ui/screens/`, `ui/workers/`)
- Comprehensive unit tests for state management and action system

**Excluded:**
- Actual widget implementations (covered in Subtask 2)
- View migrations (covered in Subtasks 3-4)
- Command palette UI (covered in Subtask 6)
- Multi-panel layout (covered in Subtask 7)

## Technical Approach

### 1. Directory Structure
**Location**: `caspoon/ui/`

Create new directories for organized architecture:
```
caspoon/ui/
├── core/          # Core architecture (state, messages, actions)
├── widgets/       # Reusable widget library (created empty)
├── screens/       # Screen management (created empty)
└── workers/       # Async worker patterns (created empty)
```

### 2. State Management
**Location**: `caspoon/ui/core/state.py`, `caspoon/ui/core/models.py`

Implement centralized reactive state using Textual's `reactive()` properties:

- **AppState**: Single source of truth with reactive properties
  - `binary_info: Optional[BinaryInfo]` - Current binary metadata
  - `analysis_results: Optional[AnalysisResults]` - Complete analysis data
  - `ui_state: UIState` - UI state (loading, progress, selections)
  - `user_prefs: UserPreferences` - User settings and preferences
  
- **Data Models**: UI-specific dataclasses
  - `BinaryInfo` - Path, architecture, bits, file type, stripped status, size
  - `AnalysisResults` - Functions, strings, imports, exports, sections, protections
  - `UIState` - Analysis progress, selected function, active tab, panel states
  - `UserPreferences` - Theme, display options, analysis defaults

**Key Methods:**
- `reset()` - Clear all state back to initial values
- `update_from_report(report)` - Populate state from ExecutableReport

### 3. Message System
**Location**: `caspoon/ui/core/messages.py`

Define standard message types extending Textual's `Message` class for event-driven communication:

**Analysis Messages:**
- `StartAnalysis(path)` - Request binary analysis
- `AnalysisProgress(percent, message)` - Progress updates during analysis
- `AnalysisComplete(report)` - Analysis finished successfully
- `AnalysisError(error)` - Analysis failed with error

**Navigation Messages:**
- `SelectFunction(function_name, address)` - User selected a function
- `JumpToAddress(address)` - Navigate to specific address
- `SwitchTab(tab_id)` - Switch active content tab

**UI Messages:**
- `TogglePanel(panel_id)` - Show/hide panel (sidebar, details, bottom)
- `ShowCommandPalette()` - Open command palette
- `ExecuteCommand(command_id)` - Run a registered command

### 4. Action Registry
**Location**: `caspoon/ui/core/actions.py`

Command registry for extensible action management:

- **Action Dataclass**: `Action(action_id, name, handler, description, keybinding, category, enabled)`
- **ActionRegistry Methods**:
  - `register(action_id, name, handler, ...)` - Register new action
  - `execute(action_id, *args, **kwargs)` - Execute action by ID
  - `get_action(action_id)` - Retrieve action details
  - `get_by_keybinding(key)` - Find action by keyboard shortcut
  - `get_by_category(category)` - Get all actions in category
  - `search(query)` - Fuzzy search actions for command palette

**Built-in Actions:**
- File: Open binary, close, quit
- View: Switch tabs, toggle panels
- Analysis: Start analysis, cancel analysis
- Navigation: Jump to function, go to address
- Help: Show help, show keybindings

## Implementation Steps

### Step 1: Create Directory Structure (30 minutes)
- Create `caspoon/ui/core/` directory with `__init__.py`
- Create `caspoon/ui/widgets/` directory with `__init__.py`
- Create `caspoon/ui/screens/` directory with `__init__.py`
- Create `caspoon/ui/workers/` directory with `__init__.py`
- Create corresponding test directories in `caspoon/tests/unit/ui/`

### Step 2: Implement Data Models (1 hour)
Create `caspoon/ui/core/models.py` with dataclasses:
- `BinaryInfo` - Binary metadata (path, arch, bits, type, stripped, size, entry_point)
- `AnalysisResults` - Analysis data (functions, strings, imports, exports, sections, protections, disassembly)
- `UIState` - UI state (is_analyzing, analysis_progress, analysis_message, selected_function, active_tab, panel states)
- `UserPreferences` - User settings (theme, show_line_numbers, auto_analyze, max_strings)

### Step 3: Implement AppState (2 hours)
Create `caspoon/ui/core/state.py` with:
- Import reactive from `textual.reactive`
- Define `AppState` class with reactive properties for each data model
- Implement `__init__()` to initialize with default values
- Implement `reset()` method to clear all state
- Implement `update_from_report(report)` to populate from ExecutableReport
- Add type hints and comprehensive docstrings

### Step 4: Implement Message Types (1.5 hours)
Create `caspoon/ui/core/messages.py` with:
- Import `Message` from `textual.message`
- Define 10+ message classes for analysis, navigation, and UI events
- Each message has appropriate data attributes and `__init__` method
- Use dataclass-style for consistency where appropriate
- Add docstrings explaining when each message is used

### Step 5: Implement Action Registry (2.5 hours)
Create `caspoon/ui/core/actions.py` with:
- `Action` dataclass for action metadata
- `ActionRegistry` class with dict storage for actions, keybindings, categories
- Implement `register()` method with validation
- Implement `execute()` method with error handling
- Implement query methods: `get_action()`, `get_by_keybinding()`, `get_by_category()`
- Implement `search(query)` with simple substring matching (fuzzy search later)
- Add logging for registration and execution events

### Step 6: Unit Tests for State (2 hours)
Create `caspoon/tests/unit/ui/core/test_state.py`:
- `test_state_initialization()` - Verify default values
- `test_state_reset()` - Verify reset clears all data
- `test_binary_info_update()` - Test setting binary info
- `test_analysis_results_update()` - Test setting analysis results
- `test_ui_state_updates()` - Test UI state changes
- `test_user_prefs_updates()` - Test preference changes
- `test_update_from_report()` - Test populating from ExecutableReport (mock report)
- `test_reactive_properties()` - Verify reactive properties work (if testable without full app)
- Aim for >90% coverage of `state.py`

### Step 7: Unit Tests for Messages (1 hour)
Create `caspoon/tests/unit/ui/core/test_messages.py`:
- Test each message type can be instantiated
- Test message attributes are accessible
- Test messages can be posted (mock post_message)
- Verify message inheritance from Textual's Message

### Step 8: Unit Tests for Actions (2 hours)
Create `caspoon/tests/unit/ui/core/test_actions.py`:
- `test_action_creation()` - Verify Action dataclass
- `test_register_action()` - Register action successfully
- `test_register_duplicate_warns()` - Duplicate registration warning
- `test_execute_action()` - Execute action calls handler
- `test_execute_disabled_action()` - Disabled action doesn't execute
- `test_execute_nonexistent_action()` - Nonexistent action returns False
- `test_get_by_keybinding()` - Retrieve action by keyboard shortcut
- `test_get_by_category()` - Retrieve actions by category
- `test_search_actions()` - Search by name/description
- Aim for >85% coverage of `actions.py`

### Step 9: Integration Test (1 hour)
Create `caspoon/tests/unit/ui/core/test_integration.py`:
- Test AppState + messages work together
- Test ActionRegistry + messages work together
- Verify state can be updated and messages posted in sequence
- Simulate mini workflow: register action → execute action → update state

### Step 10: Documentation and Validation (30 minutes)
- Update `caspoon/ui/core/__init__.py` to export main classes
- Verify all tests pass: `pytest caspoon/tests/unit/ui/core/ -v`
- Check coverage: `pytest --cov=caspoon/ui/core --cov-report=term-missing`
- Ensure existing TUI still launches: `python -m caspoon.ui`
- Document any breaking changes or deprecations

## Code Example

```python
# caspoon/ui/core/state.py
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
        """Initialize state with default values."""
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


# caspoon/ui/core/messages.py
from textual.message import Message
from typing import Optional, Any

class StartAnalysis(Message):
    """Request to start binary analysis."""
    
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__()


class SelectFunction(Message):
    """Function selected by user."""
    
    def __init__(self, function_name: str, address: Optional[str] = None) -> None:
        self.function_name = function_name
        self.address = address
        super().__init__()


# caspoon/ui/core/actions.py
from dataclasses import dataclass
from typing import Callable, Optional, Dict, List

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
    """Central registry for all application actions."""
    
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
        """Register a new action."""
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
        if not action or not action.enabled:
            return False
        
        try:
            action.handler(*args, **kwargs)
            return True
        except Exception:
            return False
    
    def get_by_keybinding(self, key: str) -> Optional[Action]:
        """Get action associated with keybinding."""
        action_id = self._keybindings.get(key)
        return self._actions.get(action_id) if action_id else None
```

## Testing Strategy

### Unit Tests

**State Management Tests** (`test_state.py`):
- Test initialization with default values
- Test reactive property assignment and retrieval
- Test `reset()` clears all data
- Test `update_from_report()` correctly extracts data from ExecutableReport
- Test edge cases: None values, empty lists, missing attributes

**Message Tests** (`test_messages.py`):
- Test each message type instantiation
- Test message attributes are correctly set
- Test messages inherit from Textual's Message
- Test message can be posted (integration with app)

**Action Registry Tests** (`test_actions.py`):
- Test action registration (single, multiple, duplicates)
- Test action execution (success, failure, disabled)
- Test keybinding lookup
- Test category grouping
- Test search functionality
- Test error handling for nonexistent actions

### Integration Tests

**Foundation Integration** (`test_integration.py`):
- Test state + messages work together in sequence
- Test action registry + messages trigger state changes
- Simulate mini workflow: load binary → update state → views react

### Manual Testing

1. **Verify No Breaking Changes**:
   ```bash
   python -m caspoon.ui  # Existing TUI should still launch
   ```

2. **Import Test**:
   ```python
   from caspoon.ui.core.state import AppState
   from caspoon.ui.core.messages import StartAnalysis
   from caspoon.ui.core.actions import ActionRegistry
   
   state = AppState()
   registry = ActionRegistry()
   # No errors = success
   ```

3. **Run All Tests**:
   ```bash
   pytest caspoon/tests/unit/ui/core/ -v
   pytest caspoon/tests/unit/ui/core/ --cov=caspoon/ui/core --cov-report=term-missing
   ```

## Dependencies

- **Textual**: Already available, provides reactive() and Message
- **typing**: Standard library, type hints
- **dataclasses**: Standard library, data models
- **pytest**: Already available, testing framework
- No new external dependencies required

## Estimated Time

**Total: 3-4 days (24-32 hours)**

Breakdown:
- Directory structure: 0.5 hours
- Data models: 1 hour
- AppState: 2 hours
- Messages: 1.5 hours
- Action registry: 2.5 hours
- Unit tests (state): 2 hours
- Unit tests (messages): 1 hour
- Unit tests (actions): 2 hours
- Integration tests: 1 hour
- Documentation/validation: 0.5 hours

## Success Criteria

- [ ] Directory structure created (`ui/core/`, `ui/widgets/`, `ui/screens/`, `ui/workers/`)
- [ ] AppState class implemented with all reactive properties
- [ ] AppState can be instantiated and used without errors
- [ ] All 10+ message types defined and tested
- [ ] ActionRegistry implemented with register/execute/query methods
- [ ] Unit tests pass (minimum 25 tests total across all files)
- [ ] Test coverage >85% for all core modules (state, messages, actions)
- [ ] Existing TUI still launches without errors
- [ ] No import errors when importing core modules
- [ ] `AppState.update_from_report()` correctly populates state from mock ExecutableReport
- [ ] ActionRegistry can register, find by keybinding, and execute actions
- [ ] Integration test demonstrates state + messages + actions working together

## Next Steps

After completing this subtask:
1. **Proceed to Subtask 2**: Implement base widget classes (BaseView, InteractiveView, TreeView, TableView) that use AppState
2. **Integration**: Base widgets will watch AppState reactive properties for automatic updates
3. **Testing Foundation**: All future widgets will use patterns established here

This foundation enables all subsequent work. The reactive state ensures views update automatically, messages enable loose coupling, and the action registry supports the command palette.
