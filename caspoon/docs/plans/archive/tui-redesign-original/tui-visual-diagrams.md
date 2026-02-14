# TUI Architecture Visual Diagrams

This document contains ASCII diagrams and visual aids for understanding the TUI architecture.

---

## 1. Data Flow - Complete Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                          │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
          Keyboard Input       Mouse Click
           (Ctrl+P)             (Button)
                  │                   │
                  └─────────┬─────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          WIDGET LAYER                                   │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Command    │  │ Function    │  │ Disassembly  │  │ Status       │  │
│  │ Palette    │  │ List        │  │ View         │  │ Bar          │  │
│  └────────────┘  └─────────────┘  └──────────────┘  └──────────────┘  │
│         │                │                 │                │           │
│         └────────────────┴─────────────────┴────────────────┘           │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │ post_message()
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ACTION/MESSAGE BUS                              │
│  LoadBinary | SelectFunction | JumpToAddress | TogglePanel | ...       │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
   [UI Action]      [Async Worker]      [State Update]
    (instant)       (long operation)      (reactive)
         │                  │                  │
         │                  │ Progress         │
         │                  │ Messages         │
         │                  ▼                  │
         │          ┌──────────────┐          │
         └────────→ │   AppState   │ ←────────┘
                    │  (Reactive)  │
                    └───────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
      watch_binary_info  watch_results  watch_ui_state
              │             │             │
┌─────────────────────────────────────────────────────────────────────────┐
│                          VIEW LAYER (Reactive)                          │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Overview   │  │ Functions   │  │ Strings      │  │ Protections  │  │
│  │ View       │  │ View        │  │ View         │  │ View         │  │
│  └────────────┘  └─────────────┘  └──────────────┘  └──────────────┘  │
│         │                │                 │                │           │
│         └────────────────┴─────────────────┴────────────────┘           │
│                                  │                                      │
│                            render_content()                             │
│                                  ▼                                      │
│                          ┌──────────────┐                               │
│                          │ Rich/Textual │                               │
│                          │   Rendering  │                               │
│                          └──────────────┘                               │
└───────────────────────────┬─────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          TERMINAL OUTPUT                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. State Management - Detail View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AppState (Central Store)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  BinaryInfo (reactive)                                            │ │
│  │  • path: str                                                      │ │
│  │  • architecture: str                                              │ │
│  │  • bits: int                                                      │ │
│  │  • file_type: str                                                 │ │
│  │  • stripped: bool                                                 │ │
│  │  • file_size: int                                                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│         │                                                               │
│         └──► Watches: [OverviewView, StatusBar, FileInfoPanel]         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  AnalysisResults (reactive)                                       │ │
│  │  • functions: list[dict]                                          │ │
│  │  • sections: list[dict]                                           │ │
│  │  • strings: list[str]                                             │ │
│  │  • imports: list[str]                                             │ │
│  │  • exports: list[str]                                             │ │
│  │  • protections: dict                                              │ │
│  │  • disassembly: list[dict]                                        │ │
│  │  • raw_report: ExecutableReport                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│         │                                                               │
│         └──► Watches: [All analysis views]                             │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  UIState (reactive)                                               │ │
│  │  • current_screen: str                                            │ │
│  │  • current_tab: str                                               │ │
│  │  • sidebar_collapsed: bool                                        │ │
│  │  • details_collapsed: bool                                        │ │
│  │  • bottom_collapsed: bool                                         │ │
│  │  • is_analyzing: bool                                             │ │
│  │  • analysis_progress: float                                       │ │
│  │  • analysis_message: str                                          │ │
│  │  • selected_function: str                                         │ │
│  │  • selected_address: int                                          │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│         │                                                               │
│         └──► Watches: [MainScreen, StatusBar, Panels]                  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  UserPreferences (reactive, persistent)                           │ │
│  │  • theme: str                                                     │ │
│  │  • keybindings: dict                                              │ │
│  │  • show_addresses: bool                                           │ │
│  │  • show_bytes: bool                                               │ │
│  │  • max_strings: int                                               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│         │                                                               │
│         └──► Watches: [All views that use preferences]                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                             Reactive Flow:
                    
    State Change              Trigger              View Update
         │                       │                      │
         ▼                       ▼                      ▼
  app.state.binary_info  →  watch_binary_info()  →  render_content()
         = new_value            callback               with new data
```

---

## 3. Widget Class Hierarchy - Inheritance Tree

```
textual.widgets.Static
    │
    ├─── BaseView[T] ────────────────┐
    │       │                        │ (Generic base for all data views)
    │       │                        │
    │       ├─ render_content(T)     │ (Abstract: implement in subclass)
    │       ├─ show_loading()        │ (Built-in loading state)
    │       ├─ show_error(str)       │ (Built-in error state)
    │       ├─ on_show()            │ (Lifecycle hook)
    │       ├─ on_hide()            │ (Lifecycle hook)
    │       │                        │
    │       │                        │
    │       ├─── InteractiveView[T] ───────────┐
    │       │        │                          │ (Add selection & keyboard nav)
    │       │        │                          │
    │       │        ├─ selected_index: int    │
    │       │        ├─ filter_text: str       │
    │       │        ├─ action_move_up()       │
    │       │        ├─ action_move_down()     │
    │       │        ├─ action_select_item()   │
    │       │        ├─ get_item_count()       │ (Abstract)
    │       │        ├─ on_item_selected(int)  │ (Abstract)
    │       │        │                          │
    │       │        │                          │
    │       │        ├─── TreeView[T] ──────────────────┐
    │       │        │        │                          │ (Hierarchical data)
    │       │        │        │                          │
    │       │        │        ├─ expanded_nodes: set    │
    │       │        │        ├─ action_toggle_expand() │
    │       │        │        ├─ get_selected_node_id() │ (Abstract)
    │       │        │        │                          │
    │       │        │        ├─── FunctionExplorer     │ (Custom widget)
    │       │        │        └─── SectionExplorer      │ (Custom widget)
    │       │        │                                   │
    │       │        │                                   │
    │       │        └─── TableView[T] ──────────────────┐
    │       │                 │                          │ (Tabular data)
    │       │                 │                          │
    │       │                 ├─ sort_column: str        │
    │       │                 ├─ sort_descending: bool   │
    │       │                 ├─ action_sort_by_column() │
    │       │                 ├─ get_columns()           │ (Abstract)
    │       │                 │                          │
    │       │                 ├─── FilterableTable      │ (Standard widget)
    │       │                 └─── ImportsTableView     │ (Custom widget)
    │       │                                            │
    │       │                                            │
    │       ├─── (Direct BaseView subclasses) ──────────┐
    │       │                                            │ (Simple views)
    │       │                                            │
    │       ├─── OverviewView                           │
    │       ├─── ProtectionsView                        │
    │       ├─── StringsView                            │
    │       ├─── DisassemblyView                        │
    │       └─── HexViewer                              │
    │                                                    │
    │                                                    │
    └─── (Other Static widgets) ───────────────────────┐
            │                                           │ (Non-data widgets)
            │                                           │
            ├─── StatusBar                             │
            ├─── CommandPalette                        │
            ├─── ProgressView                          │
            └─── SearchableList                        │


Legend:
  [T] = Generic type parameter (data type the view displays)
  ├─ = Inherits from
  ├─ method() = Method provided by class
  (Abstract) = Must be implemented by subclass
```

---

## 4. Screen Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MainScreen (App)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌──────────────┐      ┌────────────────┐     ┌────────────────┐
    │  StatusBar   │      │  MainLayout    │     │  BottomPanel   │
    │  (Vertical)  │      │  (Horizontal)  │     │  (Tabs)        │
    └──────────────┘      └────────────────┘     └────────────────┘
          ▲                       │                       ▲
          │                       │                       │
          │         ┌─────────────┼─────────────┐        │
          │         │             │             │        │
          │         ▼             ▼             ▼        │
          │   ┌─────────┐  ┌─────────┐  ┌─────────┐    │
          │   │ Sidebar │  │ Content │  │ Details │    │
          │   │(Vertical│  │ (Tabs)  │  │(Vertical│    │
          │   └─────────┘  └─────────┘  └─────────┘    │
          │         │             │             │        │
          │         │             │             │        │
          │         ▼             ▼             ▼        │
          │   ┌─────────┐  ┌─────────┐  ┌─────────┐    │
          │   │• Tree   │  │Overview │  │Props    │    │
          │   │• Funcs  │  │Functions│  │Context  │    │
          │   │• Sects  │  │Strings  │  │Actions  │    │
          │   │• Filter │  │Imports  │  │         │    │
          │   └─────────┘  │Disasm   │  └─────────┘    │
          │                │Hex      │                  │
          │                └─────────┘                  │
          │                                             │
          └─────────────── watches ui_state ────────────┘


Layout Control Flow:
───────────────────

    User Action                State Update              UI Update
         │                          │                        │
         │                          │                        │
    Press Ctrl+B              ui_state.sidebar_       Sidebar.add_class
         │                    collapsed = True              ("collapsed")
         │                          │                        │
         └──────► post_message() ───┴──► on_toggle_panel() ─┘
                   TogglePanel           watches ui_state
                   ("sidebar")           triggers update
```

---

## 5. Message Flow - Example Scenario

**Scenario**: User selects a function from the function list

```
Step 1: User Interaction
────────────────────────
        User
          │
          │ presses Enter on function "main"
          ▼
    FunctionListView
          │
          │ selected_index = 5
          │ _filtered[5] = {"name": "main", "address": 0x1234}
          │
          │
          
Step 2: Post Message
────────────────────
    FunctionListView
          │
          │ post_message(SelectFunction("main", 0x1234))
          │
          ▼
    Message Bus
          │
          │ Broadcast to all listeners
          │
          ├───────────────┬───────────────┬───────────────┐
          │               │               │               │
          ▼               ▼               ▼               ▼


Step 3: Multiple Handlers
──────────────────────────
  CaspoonApp         DetailsPanel    DisassemblyView   StatusBar
       │                  │                 │              │
       │                  │                 │              │
  on_select_         on_select_        on_select_     (no handler,
  function()         function()        function()      ignores)
       │                  │                 │
       │                  │                 │
       ▼                  ▼                 ▼
  Update state:     Show function    Jump to function
  state.ui_state.   details:         address:
  selected_func =   • Name           • Scroll to 0x1234
  "main"            • Size           • Highlight
  state.ui_state.   • Type           • Show disassembly
  selected_addr =   • Refs
  0x1234


Step 4: Reactive Updates
─────────────────────────
    AppState
    (state changed)
          │
          │ Trigger all watchers
          │
          ├───────────────┬───────────────┐
          │               │               │
          ▼               ▼               ▼
    StatusBar       FunctionList     OtherView
          │               │               │
          │               │               │
    Update status:  Highlight       (Re-render if
    "Selected:      selected        watching
    main"           row             selected_func)


Complete Flow:
──────────────
User Input → Widget → Message → Handlers → State → Watchers → UI Update
   (Enter)   (List)   (Select)  (App+Views) (State) (All Views) (Render)
```

---

## 6. Testing Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Testing Pyramid                                │
└─────────────────────────────────────────────────────────────────────────┘

                            ╱╲
                           ╱  ╲
                          ╱ E2E╲         End-to-End Tests
                         ╱──────╲        (Rare, slow, full app)
                        ╱        ╲       • test_full_analysis_workflow()
                       ╱──────────╲      
                      ╱Integration╲     Integration Tests
                     ╱──────────────╲   (Medium, with Pilot)
                    ╱                ╲  • test_command_palette()
                   ╱──────────────────╲ • test_screen_navigation()
                  ╱      Unit Tests    ╲ Unit Tests
                 ╱────────────────────────╲ (Many, fast, isolated)
                ╱__________________________╲ • test_filter_functions()
                                             • test_state_update()


Testing Layers:
───────────────

┌─────────────────────────────────────────────────────────────────────────┐
│ Unit Tests (No Rendering)                                              │
├─────────────────────────────────────────────────────────────────────────┤
│  • Test widget logic in isolation                                      │
│  • Mock dependencies (app, state)                                      │
│  • Fast, many tests                                                    │
│                                                                         │
│  def test_filter():                                                    │
│      view = FunctionListView()                                         │
│      view.render_content(test_data)                                    │
│      view.apply_filter("main")                                         │
│      assert len(view._filtered) == expected                            │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Integration Tests (With Pilot)                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  • Test user interactions                                              │
│  • Simulate key presses, clicks                                        │
│  • Assert on app state                                                 │
│  • Medium speed                                                        │
│                                                                         │
│  async def test_workflow():                                            │
│      async with app.run_test() as pilot:                              │
│          await pilot.press("ctrl+p")                                   │
│          await pilot.press("enter")                                    │
│          assert pilot.app.state.is_analyzing                           │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ End-to-End Tests (Full System)                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  • Test complete workflows                                             │
│  • Real binary analysis (small test files)                             │
│  • Slowest, fewest tests                                               │
│                                                                         │
│  async def test_analyze_binary():                                      │
│      app = CaspoonApp()                                                │
│      async with app.run_test():                                        │
│          app.post_message(LoadBinary("test.elf"))                      │
│          await wait_for_analysis()                                     │
│          assert app.state.analysis_results.functions                   │
└─────────────────────────────────────────────────────────────────────────┘


Mocking Strategy:
─────────────────

    Real Component          Mock in Tests           Test Focus
    ──────────────          ─────────────           ──────────
    ├─ Widget Logic    →    NO MOCK              → Logic & State
    ├─ App State       →    NO MOCK              → Reactive Updates
    ├─ Async Workers   →    MOCK (AsyncMock)     → Message Handling
    └─ ReconRunner     →    MOCK (Mock)          → UI Behavior
```

---

## 7. Command System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ActionRegistry                                   │
│  (Central command & keybinding registry)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  _actions: dict[str, Command] = {                                      │
│      "analyze_binary": Command(                                        │
│          id="analyze_binary",                                          │
│          name="Analyze Binary",                                        │
│          handler=app.analyze,                                          │
│          keybinding="ctrl+o",                                          │
│          category="File"                                               │
│      ),                                                                │
│      "goto_functions": Command(...),                                   │
│      ...                                                               │
│  }                                                                     │
│                                                                         │
│  _keybindings: dict[str, str] = {                                     │
│      "ctrl+o": "analyze_binary",                                       │
│      "alt+2": "goto_functions",                                        │
│      ...                                                               │
│  }                                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
           │                                  │
           │                                  │
           ▼                                  ▼
    ┌─────────────┐                  ┌──────────────┐
    │  Keybinding │                  │   Command    │
    │   Handler   │                  │   Palette    │
    └─────────────┘                  └──────────────┘
           │                                  │
           │ User presses Ctrl+O              │ User types "ana"
           ▼                                  ▼
    handle_keybinding("ctrl+o")      search_commands("ana")
           │                                  │
           ├─ lookup in _keybindings          ├─ fuzzy match
           ├─ get action "analyze_binary"     ├─ score & sort
           ├─ execute(action)                 ├─ show top results
           │                                  │
           ▼                                  ▼
    Call command.handler()           (User selects & confirms)
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
                  Action Executed
                  (e.g., app.analyze())
                          │
                          ▼
                  State Updates / Side Effects


Command Registration Flow:
───────────────────────────

1. App Initialization
   └─> register_default_commands()
       └─> ActionRegistry.register(...)
           ├─> Create Command object
           ├─> Add to _actions dict
           ├─> Add to _keybindings dict
           └─> Check for conflicts

2. Plugin/Extension Registration
   └─> plugin.register_plugin(app)
       └─> app.action_registry.register(...)
           └─> (Same as above)

3. Command Palette Update
   └─> ActionRegistry.update_command_palette(palette)
       └─> palette.register_command(cmd) for each command


Keybinding Lookup:
──────────────────

  Key Press                Lookup              Execution
      │                       │                    │
      │ "ctrl+p"              │                    │
      ▼                       ▼                    ▼
  on_key()  →  handle_keybinding()  →  execute("command_id")
      │              │                        │
      │              ├─ _keybindings lookup   │
      │              │   "ctrl+p" → "cmd_id"  │
      │              │                        │
      │              ├─ _actions lookup       │
      │              │   "cmd_id" → Command   │
      │              │                        │
      │              └─ command.handler()     │
      │                        │              │
      │                        └──────────────┘
      │                                │
      └────────────────────────────────┘
```

---

## 8. Worker Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Async Worker Lifecycle                             │
└─────────────────────────────────────────────────────────────────────────┘

    User Action             Worker Started           Worker Running
         │                       │                        │
         │ LoadBinary            │                        │
         ▼                       ▼                        │
    ┌─────────┐           ┌──────────┐                  │
    │  App    │           │  Worker  │                  │
    │  calls  │───────────>  Created  │                  │
    │run_     │           │          │                  │
    │worker() │           └────┬─────┘                  │
    └─────────┘                │                        │
         │                     │ start()                │
         │                     ▼                        │
         │              ┌──────────────┐               │
         │              │   Worker     │               │
         │              │   Running    │               │
         │              └──────┬───────┘               │
         │                     │                        │
         │                     │ Progress Updates       │
         │                     │                        │
         │                     ├──> post_message(       │
         │                     │      AnalysisProgress  │
         │                     │      (25%, "Step 1")   │
         │                     │    )                   │
         │                     │                        │
         │                     ├──> post_message(       │
         │                     │      AnalysisProgress  │
         │                     │      (50%, "Step 2")   │
         │                     │    )                   │
         │                     │                        │
         │                     ├──> post_message(       │
         │                     │      AnalysisProgress  │
         │                     │      (75%, "Step 3")   │
         │                     │    )                   │
         │                     │                        │
         │                     ▼                        │
         │              ┌──────────────┐               │
         │              │   Worker     │               │
         │              │  Complete    │               │
         │              └──────┬───────┘               │
         │                     │                        │
         │                     ├──> post_message(       │
         │                     │      AnalysisComplete  │
         │                     │      (results)         │
         │                     │    )                   │
         │                     │                        │
         │                     ▼                        │
         │              ┌──────────────┐               │
         │              │   Cleanup    │               │
         │              └──────────────┘               │
         │                                             │
         └─────────────> State Updated                 │
                              │                        │
                              ▼                        │
                         Views React                   │
                              │                        │
                              ▼                        │
                         UI Updates                    │


Error Handling:
───────────────

    Worker Running              Exception               Error Handler
         │                          │                        │
         │                          │                        │
         │ async operation fails    │                        │
         ├──────────────────────────┤                        │
         │        try:              │                        │
         │          analyze()       │                        │
         │        except Exception: │                        │
         │          e               │                        │
         │          │               │                        │
         │          └───────────────┼────> post_message(     │
         │                          │       AnalysisError    │
         │                          │       (str(e))         │
         │                          │      )                 │
         │                          │                        │
         └──────────────────────────┴────> on_analysis_error()
                                                   │
                                                   ├─> Update state
                                                   │   (is_analyzing=False)
                                                   │
                                                   ├─> Show error UI
                                                   │   (ErrorDialog)
                                                   │
                                                   └─> Log error


Cancellation:
─────────────

    User Action          Check & Cancel         Start New
         │                     │                     │
         │ LoadBinary #2       │                     │
         ▼                     ▼                     ▼
    ┌─────────┐         ┌──────────┐          ┌──────────┐
    │ Check   │────────>│ Cancel   │─────────>│ Start    │
    │ if      │         │ existing │          │ new      │
    │ worker  │         │ worker   │          │ worker   │
    │ running │         │          │          │          │
    └─────────┘         └──────────┘          └──────────┘
         │                     │                     │
         │ Yes                 │ worker.cancel()     │
         └─────────────────────┘                     │
                                                     │
         │ No                                        │
         └───────────────────────────────────────────┘
```

---

These diagrams provide visual references for understanding the TUI architecture. Use them in conjunction with the main architecture document and implementation examples.
