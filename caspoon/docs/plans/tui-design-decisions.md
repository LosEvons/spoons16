# TUI Architecture Design Decisions

**Purpose**: Document key architectural decisions, trade-offs, and rationale for the TUI redesign.

---

## Decision 1: Reactive State Management

### Decision
Use a centralized, reactive `AppState` as single source of truth, with views automatically updating when state changes.

### Context
Current architecture has imperative view updates:
```python
# Current (imperative)
report = runner.run(path)
overview.update_data(report)
protections.update_data(report)
strings.update_data(report)
# ... etc for every view
```

### Alternatives Considered

1. **Keep imperative updates**: Continue calling `update_data()` on each view
   - ❌ Doesn't scale - must remember to update every view
   - ❌ Error-prone - easy to forget views
   - ❌ Hard to test - must mock every view interaction

2. **Event bus with manual subscriptions**: Views subscribe to events manually
   - ⚠️ Better, but still requires manual wiring
   - ⚠️ No type safety on events
   - ⚠️ Hard to track what views depend on what data

3. **Reactive state with automatic updates** (CHOSEN)
   - ✅ Views declare dependencies via `watch()`
   - ✅ State changes automatically trigger updates
   - ✅ Easy to add new views - just watch state
   - ✅ Type-safe with dataclasses
   - ✅ Easy to test - just change state

### Decision Rationale

**Scalability**: As Caspoon adds more views (hex, cfg, call graphs), reactive state prevents the "update all views" problem from growing linearly.

**Testability**: Tests can update state and assert views reacted correctly, without mocking view methods.

**Developer Experience**: New views are plug-and-play - just watch the state you need.

**Performance**: Reactive updates are efficient - only views watching changed data re-render.

### Trade-offs

- ➕ **Pros**: Automatic updates, scalable, testable
- ➖ **Cons**: Slight learning curve for reactive patterns
- ➖ **Cons**: Need to understand watch() system

### Example

```python
# With reactive state
class FunctionsView(BaseView[list[Function]]):
    def on_mount(self):
        # Declare dependency
        app.state.analysis_results.watch(self, "_on_results_changed")
    
    def _on_results_changed(self, old, new):
        self.data = new.functions  # Auto-triggers render_content()
```

---

## Decision 2: Message-Driven Architecture

### Decision
All actions (user input, state changes, navigation) are implemented as messages posted to a central bus.

### Context
Need a way for components to communicate without tight coupling.

### Alternatives Considered

1. **Direct method calls**: Widgets call methods on other widgets
   - ❌ Tight coupling - widget A must know about widget B
   - ❌ Hard to test - must mock dependencies
   - ❌ Not extensible - plugins can't intercept

2. **Callbacks/delegates**: Pass callbacks to widgets
   - ⚠️ Better, but still couples widget to callback signature
   - ⚠️ Hard to compose - multiple callbacks get messy
   - ⚠️ Hard to debug - callback chains unclear

3. **Message bus** (CHOSEN)
   - ✅ Loose coupling - widgets only know message types
   - ✅ Multiple handlers - many widgets can react to same message
   - ✅ Extensible - plugins can listen to any message
   - ✅ Debuggable - message flow is explicit
   - ✅ Testable - mock post_message() to verify behavior

### Decision Rationale

**Loose Coupling**: FunctionListView doesn't know about DisassemblyView or App - it just posts `SelectFunction` message.

**Composability**: Multiple components can react to same message (e.g., `SelectFunction` updates state, details panel, and disassembly view).

**Extensibility**: Plugins can listen to messages without modifying core code.

**Debugging**: Textual's message system has built-in logging and debugging.

### Trade-offs

- ➕ **Pros**: Loose coupling, composable, extensible
- ➖ **Cons**: Indirect flow - harder to trace initially
- ➖ **Cons**: Runtime errors if message not handled

### Example

```python
# Widget posts message
self.post_message(SelectFunction("main"))

# Multiple handlers react
class DisassemblyView:
    def on_select_function(self, msg):
        self.jump_to_function(msg.function_name)

class DetailsPanel:
    def on_select_function(self, msg):
        self.show_function_details(msg.function_name)

class CaspoonApp:
    def on_select_function(self, msg):
        self.state.selected_function = msg.function_name
```

---

## Decision 3: Async Workers for Analysis

### Decision
Run long-running operations (binary analysis, search) in async workers with progress reporting.

### Context
Current implementation blocks UI during analysis:
```python
# Current (blocking)
report = runner.run(path)  # UI freezes!
self.display_report(report)
```

### Alternatives Considered

1. **Keep blocking** (status quo)
   - ❌ UI freezes during analysis
   - ❌ No progress feedback
   - ❌ Can't cancel analysis
   - ❌ Poor UX for large binaries

2. **Threading**: Run analysis in thread
   - ⚠️ Thread-safe UI updates are tricky
   - ⚠️ GIL limits parallelism
   - ⚠️ Harder to cancel/coordinate
   - ⚠️ Not idiomatic for async framework

3. **Async workers** (CHOSEN)
   - ✅ Non-blocking - UI stays responsive
   - ✅ Progress updates via messages
   - ✅ Easy to cancel
   - ✅ Textual's built-in worker system
   - ✅ Natural for async/await

### Decision Rationale

**User Experience**: Users see progress and can cancel long operations.

**Framework Fit**: Textual is async-native, workers are first-class.

**Responsiveness**: UI stays interactive even during heavy analysis.

**Cancellation**: Workers can be cancelled cleanly.

### Trade-offs

- ➕ **Pros**: Responsive UI, progress feedback, cancellable
- ➖ **Cons**: Must use asyncio patterns
- ➖ **Cons**: Blocking code (r2) must run in thread pool

### Example

```python
async def _analyze_binary(self, path: str):
    self.post_message(AnalysisProgress(10, "Parsing ELF..."))
    # Run blocking code in thread pool
    report = await asyncio.to_thread(runner.run, path)
    
    self.post_message(AnalysisProgress(100, "Complete"))
    self.post_message(AnalysisComplete(report))
```

---

## Decision 4: Base Widget Classes Hierarchy

### Decision
Create a hierarchy of base classes (BaseView → InteractiveView → TreeView/TableView) for code reuse.

### Context
Many views share common patterns (filtering, selection, sorting).

### Alternatives Considered

1. **No base classes**: Each view implements everything
   - ❌ Code duplication
   - ❌ Inconsistent behavior
   - ❌ Hard to add features (e.g., keyboard nav)

2. **Mixins**: Use mixins for shared behavior
   - ⚠️ Can work, but multiple inheritance is complex
   - ⚠️ Diamond problem
   - ⚠️ Less clear inheritance hierarchy

3. **Composition**: Have separate helper classes
   - ⚠️ Can work, but more boilerplate
   - ⚠️ Less natural for widget system

4. **Base class hierarchy** (CHOSEN)
   - ✅ Clear inheritance structure
   - ✅ Progressive enhancement (BaseView → Interactive → Table)
   - ✅ Easy to understand and extend
   - ✅ Common patterns implemented once

### Decision Rationale

**Code Reuse**: Filtering, sorting, navigation implemented once in base classes.

**Consistency**: All interactive views have same keyboard shortcuts.

**Extensibility**: New view types inherit behavior automatically.

**Clarity**: Hierarchy makes capabilities clear (TreeView has expand/collapse, TableView has sorting).

### Trade-offs

- ➕ **Pros**: Code reuse, consistency, clarity
- ➖ **Cons**: Deeper inheritance (but only 3-4 levels max)
- ➖ **Cons**: Must understand base class API

### Hierarchy

```
BaseView
  └─ InteractiveView (adds: selection, keyboard nav, filtering)
      ├─ TreeView (adds: expand/collapse)
      └─ TableView (adds: sorting, columns)
```

---

## Decision 5: Command Palette as Primary Interface

### Decision
Implement a Ctrl+P style command palette with fuzzy search as the primary way to invoke actions.

### Context
Current TUI has no command discovery - users must know keyboard shortcuts.

### Alternatives Considered

1. **Only keyboard shortcuts**: User must memorize shortcuts
   - ❌ Low discoverability
   - ❌ Limited by available key combinations
   - ❌ New features hard to expose

2. **Menu bar**: Traditional menu system
   - ⚠️ Takes screen space
   - ⚠️ Mouse-oriented (TUI is keyboard-first)
   - ⚠️ Not modern IDE feel

3. **Command palette** (CHOSEN)
   - ✅ High discoverability - type to search
   - ✅ Keyboard-first
   - ✅ Fuzzy matching
   - ✅ Shows keybindings
   - ✅ Familiar to VSCode/Sublime users
   - ✅ Easy to add new commands

### Decision Rationale

**Discoverability**: Users can find commands by typing partial names.

**User Expectations**: Modern IDEs (VSCode, IntelliJ) use command palettes.

**Scalability**: Can add unlimited commands without UI clutter.

**Keyboard-First**: Fits TUI paradigm better than menus.

### Trade-offs

- ➕ **Pros**: Discoverable, keyboard-first, scalable
- ➖ **Cons**: Must implement fuzzy search
- ➖ **Cons**: Requires good command naming

### Example

```
User presses Ctrl+P:

┌─────────────────────────────────────┐
│ > ana_____________                  │
├─────────────────────────────────────┤
│ Analyze Binary [Ctrl+O]             │
│ Analysis Settings                   │
│ Re-analyze Current File [Ctrl+R]    │
└─────────────────────────────────────┘
```

---

## Decision 6: Multi-Panel Layout with Docking

### Decision
Implement a multi-panel layout (sidebar, content, details, bottom) with collapsible panels.

### Context
Single-tab interface is limiting - users want to see multiple views simultaneously.

### Alternatives Considered

1. **Tabs only** (current)
   - ❌ Can only see one view at a time
   - ❌ Switching tabs is slow
   - ❌ Can't compare views side-by-side

2. **Split view**: Split content area horizontally/vertically
   - ⚠️ Good, but limited to 2 views
   - ⚠️ Complex layout management
   - ⚠️ Hard to remember layouts

3. **Multi-panel with docking** (CHOSEN)
   - ✅ Multiple views visible simultaneously
   - ✅ Collapsible - maximize content when needed
   - ✅ Familiar IDE layout
   - ✅ Persistent panel state

### Decision Rationale

**Efficiency**: View functions, disassembly, and details simultaneously.

**Familiarity**: Layout matches VSCode, IntelliJ, etc.

**Flexibility**: Collapse panels not needed right now.

**Context**: Keep context (properties, actions) visible while navigating.

### Trade-offs

- ➕ **Pros**: Efficient, familiar, flexible
- ➖ **Cons**: More complex layout code
- ➖ **Cons**: Takes more screen space

### Layout

```
┌────────────────────────────────────────┐
│ Status Bar                             │
├─────┬──────────────────────────┬───────┤
│     │                          │       │
│ Nav │      Content Tabs        │ Props │
│     │                          │       │
├─────┴──────────────────────────┴───────┤
│ Console / Logs                         │
└────────────────────────────────────────┘
```

---

## Decision 7: Testing Without Rendering

### Decision
Design widgets to be testable without full rendering - test logic, not pixels.

### Context
Need fast, reliable tests that don't depend on terminal capabilities.

### Alternatives Considered

1. **Snapshot tests only**: Capture rendered output
   - ⚠️ Brittle - break on minor style changes
   - ⚠️ Slow - must render full UI
   - ⚠️ Hard to debug - diff is visual, not logical

2. **End-to-end only**: Test through UI automation
   - ❌ Slow - must run full app
   - ❌ Flaky - timing issues
   - ❌ Covers less - hard to test edge cases

3. **Unit test logic, integrate test behavior** (CHOSEN)
   - ✅ Fast - test pure logic without rendering
   - ✅ Focused - test one thing at a time
   - ✅ Reliable - no timing/rendering issues
   - ✅ Debuggable - clear assertions

### Decision Rationale

**Speed**: Unit tests run in milliseconds, not seconds.

**Reliability**: Logic tests don't break on style changes.

**Coverage**: Can test edge cases easily.

**TDD**: Can write tests before implementation.

### Trade-offs

- ➕ **Pros**: Fast, reliable, high coverage
- ➖ **Cons**: Must design for testability
- ➖ **Cons**: Still need some integration tests

### Example

```python
# Fast unit test (no rendering)
def test_filter():
    view = FunctionListView()
    view.render_content(test_data)
    view.apply_filter("main")
    assert len(view._filtered) == 2

# Slower integration test (with Pilot)
async def test_navigation():
    async with app.run_test() as pilot:
        await pilot.press("ctrl+p")
        assert palette.visible
```

---

## Decision 8: Plugin-Ready Architecture

### Decision
Design core architecture to support plugins from day one (even if plugins aren't implemented yet).

### Context
Want to enable future extensions without rewriting core.

### Alternatives Considered

1. **No plugin support**: Monolithic app
   - ❌ All features must be in core
   - ❌ Hard to experiment
   - ❌ Can't contribute without core access

2. **Add plugins later**: Refactor when needed
   - ⚠️ Works, but retrofit is harder
   - ⚠️ Existing code may not be plugin-friendly

3. **Design for plugins from start** (CHOSEN)
   - ✅ Core is extensible
   - ✅ Easy to add features later
   - ✅ Encourages modular design
   - ✅ Minimal cost - just good architecture

### Decision Rationale

**Future-Proofing**: Plugins will be needed eventually (themes, custom analyzers, exporters).

**Modular Design**: Plugin-friendly architecture is also good architecture.

**Low Cost**: Just requires good interfaces (ActionRegistry, message system).

### Trade-offs

- ➕ **Pros**: Future-proof, modular, extensible
- ➖ **Cons**: Slightly more abstract initially
- ➖ **Cons**: Must define plugin APIs

### Plugin Capabilities

```python
# Plugin can register commands
registry.register("my_command", ...)

# Plugin can add views
app.add_tab("My View", MyView())

# Plugin can listen to messages
class MyPlugin:
    def on_analysis_complete(self, msg):
        # React to analysis
        pass
```

---

## Decision 9: Incremental Migration Path

### Decision
Migrate gradually, allowing new and old code to coexist during transition.

### Context
Can't rewrite entire TUI at once - too risky, too slow.

### Alternatives Considered

1. **Big-bang rewrite**: Rewrite everything, then switch
   - ❌ High risk - no fallback
   - ❌ Long feedback cycle
   - ❌ Hard to merge with ongoing work

2. **Parallel implementation**: Build new TUI alongside old
   - ⚠️ Works, but doubles maintenance
   - ⚠️ Features added to old need porting
   - ⚠️ Eventually must switch anyway

3. **Incremental migration** (CHOSEN)
   - ✅ Low risk - old code still works
   - ✅ Fast feedback - test each step
   - ✅ Easy to rollback per-feature
   - ✅ No doubling of maintenance

### Decision Rationale

**Risk Management**: Can roll back individual features if issues found.

**Feedback Loop**: Test new architecture with real usage early.

**Team Velocity**: Can ship partial migration, get value sooner.

**Compatibility**: Old and new views coexist during transition.

### Trade-offs

- ➕ **Pros**: Low risk, fast feedback, incremental value
- ➖ **Cons**: Must maintain compatibility shims temporarily
- ➖ **Cons**: Mixed code style during transition

### Migration Phases

```
Phase 1: Add new base classes (coexist)
Phase 2: Migrate one view (prove pattern)
Phase 3: Migrate all views (remove old interface)
Phase 4: Add new features (polish)
```

---

## Decision 10: CSS-Based Styling

### Decision
Use Textual's CSS system for styling rather than inline styles or Rich markup.

### Context
Views mix styling with logic (e.g., `style="bold red"`).

### Alternatives Considered

1. **Inline styles**: Style in code
   - ❌ Mixes concerns
   - ❌ Hard to theme
   - ❌ Inconsistent styles

2. **Rich markup**: Use Rich's markup syntax
   - ⚠️ Better than inline, but still in code
   - ⚠️ Hard to override
   - ⚠️ Not reusable

3. **CSS styling** (CHOSEN)
   - ✅ Separates style from logic
   - ✅ Reusable styles
   - ✅ Easy to theme
   - ✅ Textual-native

### Decision Rationale

**Separation of Concerns**: Logic in Python, style in CSS.

**Themability**: Can switch themes without code changes.

**Consistency**: Same classes produce same styling.

**Maintainability**: Style changes don't require code changes.

### Trade-offs

- ➕ **Pros**: Separation, themable, consistent
- ➖ **Cons**: Must learn Textual CSS
- ➖ **Cons**: Two languages (Python + CSS)

### Example

```python
# Python code (logic only)
class FunctionListView(TableView):
    def render_content(self, data):
        table = Table()
        table.add_row(name, address, classes="selected")

# CSS (style only)
.selected {
    background: $accent;
    text-style: bold;
}
```

---

## Summary of Decisions

| # | Decision | Primary Benefit | Main Trade-off |
|---|----------|----------------|----------------|
| 1 | Reactive state | Automatic updates, scalable | Learning curve |
| 2 | Message-driven | Loose coupling, extensible | Indirect flow |
| 3 | Async workers | Responsive UI | Async complexity |
| 4 | Base class hierarchy | Code reuse, consistency | Deeper inheritance |
| 5 | Command palette | Discoverability | Implementation effort |
| 6 | Multi-panel layout | Efficiency, familiarity | Layout complexity |
| 7 | Logic-focused testing | Fast, reliable tests | Design for testability |
| 8 | Plugin-ready | Future-proof | More abstraction |
| 9 | Incremental migration | Low risk | Temporary complexity |
| 10 | CSS styling | Themable, maintainable | Two languages |

---

## Principles Underlying Decisions

1. **User Experience First**: Responsive, discoverable, familiar
2. **Developer Experience**: Testable, debuggable, maintainable
3. **Future-Proofing**: Extensible, scalable, evolvable
4. **Framework Fit**: Use Textual's strengths (async, reactive, CSS)
5. **Progressive Enhancement**: Start simple, add complexity as needed
6. **Risk Management**: Incremental, reversible changes

---

These decisions form a coherent architecture that balances user needs, developer productivity, and long-term maintainability. Each decision reinforces others (e.g., reactive state + messages = loose coupling).
