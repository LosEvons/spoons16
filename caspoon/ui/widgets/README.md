# Interactive Widgets

This package provides interactive Textual widgets for the Caspoon binary analysis UI.

## Widgets

### InteractiveDisasmView

A keyboard-driven disassembly viewer with navigation support.

**Features:**
- Arrow key navigation through disassembly
- Visual indicators for navigable addresses
- Jump to target addresses (Enter key)
- Browser-like back/forward history
- Go-to-address dialog
- Cross-reference viewing
- Integrated syntax highlighting

**Usage:**
```python
from caspoon.ui.widgets import InteractiveDisasmView

widget = InteractiveDisasmView()
widget.update_disassembly(ops, "main")
```

See [`interactive-disassembly-widget.md`](../../docs/guides/interactive-disassembly-widget.md) for full documentation.

### GotoDialog

A modal dialog for entering addresses to navigate to.

**Features:**
- Multiple address format support (hex, decimal, symbols)
- Address validation and normalization
- Error display
- Keyboard shortcuts (ESC to cancel)

**Usage:**
```python
from caspoon.ui.widgets import GotoDialog

def show_goto():
    app.push_screen(GotoDialog(), callback=handle_address)
```

## Demo

Run the interactive demo:

```bash
python -m caspoon.ui.widgets.demo
```

**Controls:**
- `↑`/`↓` - Navigate lines
- `Enter` - Jump to address
- `Alt+←`/`Alt+→` - History back/forward
- `g` - Go to address
- `x` - Show xrefs
- `q` - Quit

## Testing

Run the widget tests:

```bash
# All widget tests
pytest caspoon/tests/unit/ui/widgets/ -v

# Just interactive disasm
pytest caspoon/tests/unit/ui/widgets/test_interactive_disasm.py -v

# Just goto dialog
pytest caspoon/tests/unit/ui/widgets/test_goto_dialog.py -v
```

**Test Coverage:**
- 91 total tests
- 100% pass rate
- 87% line coverage on InteractiveDisasmView
- 54% line coverage on GotoDialog (UI methods require app context)

## Architecture

Both widgets follow Textual best practices:

1. **Message-based communication**: Events emitted as messages
2. **Reactive properties**: UI updates automatically
3. **Composable**: Can be embedded in any Textual app
4. **Keyboard-first**: Efficient navigation without mouse
5. **Testable**: Comprehensive unit test coverage

## Integration

The widgets integrate with:
- **NavigationManager** (`caspoon.ui.navigation`): History tracking
- **AsmHighlighter** (`caspoon.ui.syntax`): Syntax highlighting
- **Architecture detection** (`caspoon.ui.syntax.arch_detector`): Auto-detect ISA

## Files

```
caspoon/ui/widgets/
├── __init__.py              # Package exports
├── interactive_disasm.py    # Interactive disassembly widget
├── goto_dialog.py           # Go-to-address dialog
├── demo.py                  # Demo application
└── README.md               # This file

caspoon/tests/unit/ui/widgets/
├── test_interactive_disasm.py  # Widget tests (52 tests)
└── test_goto_dialog.py         # Dialog tests (39 tests)
```

## See Also

- [User Guide](../../docs/guides/interactive-disassembly-widget.md)
- [Implementation Summary](../../docs/plans/01-syntax-highlighting/implementation-summary-subtask-4.md)
- [Plan Document](../../docs/plans/01-syntax-highlighting/subtask-4-interactive-navigation.md)
