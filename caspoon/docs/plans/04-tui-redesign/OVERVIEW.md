# Implementation Plan: TUI Redesign - IDE-Like Interface

## Overview

This plan transforms Caspoon's TUI from a simple tabbed interface into a professional, IDE-like experience using Textual's advanced features. The redesign implements reactive state management, event-driven architecture, async workers for non-blocking analysis, a command palette for keyboard-driven workflows, and a multi-panel layout for efficient navigation.

The current TUI suffers from blocking analysis operations, manual view updates that don't scale, limited keyboard support, and a static single-view-at-a-time layout. The new architecture addresses these limitations with a single source of truth for state (AppState), automatic reactive view updates, message-based component communication, background workers with progress reporting, and a flexible multi-panel docking layout.

This redesign follows an incremental migration strategy where old and new code coexist safely. Each subtask produces working, testable code with clear acceptance criteria. The architecture is extensible and plugin-ready from day one, with comprehensive testing for both logic and behavior.

## Goals

1. Implement reactive state management with automatic view updates
2. Create event-driven message-based architecture for loose component coupling
3. Build async worker pattern for non-blocking binary analysis with progress reporting
4. Implement command palette (Ctrl+P) for keyboard-driven command discovery
5. Design multi-panel layout (sidebar, content tabs, details panel, bottom console)
6. Create reusable base widget classes (BaseView, InteractiveView, TreeView, TableView)
7. Migrate all existing views to new architecture with feature parity
8. Achieve comprehensive test coverage for UI logic without rendering dependencies

## Architecture Impact

### Modified Components

- **UI App**: `ui/app.py` - Integrate AppState, command palette, multi-panel layout
- **Existing Views**: All view files migrated to new base classes
  - `ui/views/overview.py` - Use BaseView with reactive properties
  - `ui/views/protections.py` - React to state changes automatically
  - `ui/views/strings.py` - Add filtering with InteractiveView
  - `ui/views/imports_exports.py` - Use TableView for sortable data
  - `ui/views/r2_view.py` - Integrate async workers for analysis
- **Recon Runner**: `core/runner.py` - Support async execution with progress callbacks
- **Models**: `core/models.py` - May add new data structures for UI state

### New Components

- `ui/core/state.py` - Centralized reactive state store (AppState)
- `ui/core/models.py` - UI-specific data models (BinaryInfo, AnalysisResults, UIState, UserPreferences)
- `ui/core/actions.py` - Action registry and command system
- `ui/core/messages.py` - Custom message types for event-driven communication
- `ui/widgets/base.py` - Base widget classes (BaseView, InteractiveView)
- `ui/widgets/tree.py` - TreeView widget for hierarchical navigation
- `ui/widgets/table.py` - TableView widget with sorting and filtering
- `ui/widgets/command_palette.py` - Command palette overlay (Ctrl+P)
- `ui/widgets/progress.py` - Progress indicators for async operations
- `ui/widgets/sidebar.py` - Collapsible sidebar with navigation tree
- `ui/widgets/details_panel.py` - Context-sensitive details panel
- `ui/workers/` - Async worker patterns (AnalysisWorker, SearchWorker)
- `ui/screens/` - Screen management (MainScreen, SettingsScreen, HelpScreen)

## Technical Dependencies

### Required Libraries

- **Textual**: Already available, TUI framework with reactive properties and widgets
- **Rich**: Already available, terminal rendering and syntax highlighting
- **pytest**: Already available, testing framework
- **pytest-asyncio**: Already available, async test support
- **typing-extensions**: For advanced type hints (may be needed for Python 3.9 compatibility)

### Integration Points

- **Radare2 Integration**: Async workers wrap r2pipe calls for non-blocking analysis
- **ReconRunner**: Extended to support progress callbacks and cancellation
- **Existing Backend**: All analysis backends (r2_analyzer, lief_analyzer, etc.) used through async workers
- **File I/O**: Async file loading and export operations

## Complexity Assessment

### Difficulty: High

- **State Management**: Medium - Textual's reactive system is well-designed but requires understanding
- **Event-Driven Architecture**: Medium - Message system is straightforward but needs careful design
- **Base Widget Classes**: Medium-High - Must balance reusability with specific view needs
- **View Migration**: Medium - Pattern is clear after first migration, but each view has unique features
- **Async Workers**: High - Async patterns and worker lifecycle management are complex
- **Command Palette**: Medium-High - Fuzzy search, keybindings, and action dispatching require integration
- **Multi-Panel Layout**: High - Docking, collapsible panels, and state persistence are challenging
- **Testing Strategy**: Medium - Testing logic without rendering is novel but achievable

### Estimated Effort

- Subtask 1 (Foundation & State): 3-4 days
- Subtask 2 (Base Widgets): 3-4 days
- Subtask 3 (Core View Migration): 4-5 days
- Subtask 4 (Analysis View Migration): 4-5 days
- Subtask 5 (Async Workers): 3-4 days
- Subtask 6 (Command Palette): 3-4 days
- Subtask 7 (Multi-Panel Layout): 4-5 days
- Subtask 8 (Testing & Polish): 3-4 days
- **Total**: 27-35 days (5-7 weeks)

## Success Criteria

1. AppState serves as single source of truth - all views react to state changes automatically
2. Views do not manually update other views - all communication through messages or state
3. Binary analysis runs in background workers without freezing the UI
4. Command palette (Ctrl+P) provides fuzzy-searchable access to all actions
5. Multi-panel layout allows viewing multiple views simultaneously (functions + disassembly)
6. All existing TUI functionality preserved with feature parity after migration
7. Test coverage >80% for UI logic, with tests independent of rendering
8. Performance: Analysis progress updates at least every 500ms during long operations
9. Keybindings documented and discoverable (via help screen and command palette)
10. User preferences persist across sessions (theme, layout, defaults)

## Implementation Phases

### Phase 1: Foundation (Subtasks 1-2) - Weeks 1-2

Build core architecture components that all other work depends on:
- Reactive state management (AppState)
- Action registry and message system
- Base widget classes (BaseView, InteractiveView)
- Testing infrastructure for stateless widget logic

**Milestone**: Foundation tested and ready for view migration

### Phase 2: Prove Pattern (Subtask 3) - Week 3

Migrate one simple view to validate the architecture works end-to-end:
- Migrate OverviewView to use AppState and BaseView
- Integrate reactive updates
- Prove pattern with comprehensive tests

**Milestone**: One view fully migrated, pattern validated

### Phase 3: View Migration (Subtask 4) - Weeks 4-5

Migrate remaining views to new architecture:
- ProtectionsView, StringsView (with filtering)
- ImportsExportsView (with TableView)
- R2View (complex, with syntax highlighting)

**Milestone**: All views use new architecture, old patterns removed

### Phase 4: Advanced Features (Subtasks 5-7) - Weeks 6-8

Add IDE-like features that differentiate the new TUI:
- Async workers with progress reporting
- Command palette with fuzzy search
- Multi-panel docking layout
- Navigation tree and details panel

**Milestone**: Complete IDE-like experience

### Phase 5: Polish (Subtask 8) - Week 9

Testing, optimization, documentation, and final validation:
- Comprehensive integration tests
- Performance testing and optimization
- User documentation and guides
- Final bug fixes

**Milestone**: Production-ready release

## Risk Assessment

### Technical Risks

- **Textual API Changes**: Textual is evolving, APIs may change between versions
  - *Mitigation*: Pin Textual version, monitor releases, abstract Textual-specific code
  
- **Async Complexity**: Worker patterns and cancellation can have edge cases
  - *Mitigation*: Comprehensive async tests, use proven patterns from examples
  
- **State Management Bugs**: Reactive updates can cause unexpected cascading changes
  - *Mitigation*: Keep state flat and normalized, test state changes in isolation
  
- **Performance Degradation**: Reactive updates and multi-panel rendering may slow down
  - *Mitigation*: Lazy loading, pagination, performance profiling early
  
- **Breaking Existing Workflows**: Users accustomed to current TUI may resist changes
  - *Mitigation*: Preserve keybindings where possible, provide migration guide

### Integration Risks

- **ReconRunner Integration**: Making runner async may break existing CLI code
  - *Mitigation*: Keep synchronous interface, add async variant alongside
  
- **Backend Compatibility**: Analysis backends may not support cancellation
  - *Mitigation*: Wrap backends in workers, implement timeout-based pseudo-cancellation
  
- **Testing Complexity**: Testing async UI components is non-trivial
  - *Mitigation*: Use pytest-asyncio, test logic separately from rendering

## Dependencies on Other Plans

- **Plan 01 (Syntax Highlighting)**: Syntax highlighting integration in R2View (Subtask 4)
  - R2View migration will integrate syntax highlighting if available
  - Can proceed independently, integration is additive
  
- **Plan 02 (Pattern Detection)**: Pattern results displayed in dedicated view
  - New pattern view can use TableView or TreeView base classes
  - Architecture designed to support adding new views easily
  
- **Plan 03 (Syscall/API Detection)**: API calls highlighted in disassembly
  - Async workers can trigger API detection in background
  - Results displayed in multi-panel layout

This plan provides foundation for all future UI enhancements.

## Future Enhancements

Post-implementation possibilities:

- **Plugin System**: Third-party plugins can register views, commands, and actions
- **Custom Themes**: User-defined color schemes and layout preferences
- **Workspace Management**: Save and restore analysis sessions
- **Diff View**: Compare two binaries side-by-side in ComparisonScreen
- **Graph Views**: Call graphs and control flow graphs using rich rendering
- **Export Options**: Export views as JSON, HTML, or text reports
- **Remote Analysis**: Connect to remote radare2 instance for large binaries
- **Collaborative Features**: Share analysis sessions with team members
- **Integration with External Tools**: Launch IDA, Ghidra, or debuggers from TUI
- **Advanced Search**: Search across all views with live results

## Key Design Principles

### 1. Reactive State Management

Single source of truth with automatic view updates:

```python
# ✅ New way
app.state.binary_info = report.info
# All views watching binary_info automatically update
```

### 2. Event-Driven Architecture

All actions as messages for loose coupling:

```python
# Widget posts message
self.post_message(SelectFunction("main"))

# App/views handle it
def on_select_function(self, msg):
    self.state.selected_function = msg.function_name
```

### 3. Async-First

Non-blocking operations with workers:

```python
# Run analysis in background
self.run_worker(self._analyze_binary(path))

# UI stays responsive
```

### 4. Testable by Design

Test logic without rendering:

```python
def test_view():
    view = MyView()
    view.data = test_data
    assert view._filtered_data == expected
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CaspoonApp (App)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              AppState (Reactive Store)                 │ │
│  │  • BinaryInfo  • AnalysisResults  • UIState  • Prefs  │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ▲                                  │
│                           │ Reactive Watchers                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  MainScreen Layout                     │ │
│  │  ┌──────────┬──────────────────┬──────────────────┐   │ │
│  │  │ Sidebar  │  Content Tabs     │  Details Panel   │   │ │
│  │  │  • Tree  │  [Overview] [...] │  • Properties    │   │ │
│  │  │  • Funcs │  Active View      │  • Actions       │   │ │
│  │  └──────────┴──────────────────┴──────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │         Bottom Panel (Console/Logs)              │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Command Palette (Ctrl+P, modal overlay)         │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Workers (Async Background)               │ │
│  │  AnalysisWorker | SearchWorker | ExportWorker         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Widget Class Hierarchy

```
BaseView (ABC)
├── render_content() -> RenderableType  # Subclass implements
├── error handling and empty states
├── reactive data property
│
├── InteractiveView (adds selection/filtering)
│   ├── on_key() for navigation
│   ├── apply_filter()
│   ├── _filtered_data property
│   │
│   ├── TreeView (hierarchical navigation)
│   │   └── FunctionsTreeView, SectionsTreeView
│   │
│   └── TableView (sortable, filterable tables)
│       └── ImportsExportsView, StringsView
│
└── StaticView (read-only content)
    └── OverviewView, ProtectionsView
```

## References

- [Textual Documentation - Reactive Programming](https://textual.textualize.io/guide/reactivity/)
- [Textual Documentation - Workers](https://textual.textualize.io/guide/workers/)
- [Textual Documentation - Messages](https://textual.textualize.io/guide/events/)
- [Rich Documentation - Tables](https://rich.readthedocs.io/en/latest/tables.html)
- [Design Document - TUI Architecture](../tui-architecture-redesign.md) (original)
- [Design Decisions - Rationale](../tui-design-decisions.md) (original)

## Subtasks

1. [Foundation & State Management](subtask-1-foundation.md) - 3-4 days
2. [Base Widget Architecture](subtask-2-base-widgets.md) - 3-4 days
3. [View Migration - Core Views](subtask-3-core-views.md) - 4-5 days
4. [View Migration - Analysis Views](subtask-4-analysis-views.md) - 4-5 days
5. [Async Workers & Progress](subtask-5-async-workers.md) - 3-4 days
6. [Command Palette & Keybindings](subtask-6-command-palette.md) - 3-4 days
7. [Multi-Panel Layout & Navigation](subtask-7-multi-panel.md) - 4-5 days
8. [Testing, Optimization & Polish](subtask-8-polish.md) - 3-4 days

**Total Estimated Time**: 27-35 days (5-7 weeks)
