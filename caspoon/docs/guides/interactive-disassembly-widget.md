# Interactive Disassembly Widget

## Overview

The `InteractiveDisasmView` widget provides a keyboard-driven interface for navigating through disassembly code with visual indicators and navigation history.

## Features

- **Keyboard-first navigation**: Efficient navigation using arrow keys and shortcuts
- **Visual indicators**: Clear symbols showing navigable addresses and current selection
- **Navigation history**: Browser-like back/forward functionality
- **Address jumping**: Quick navigation to specific addresses via dialog
- **Cross-reference viewing**: Display references to/from current address
- **Syntax highlighting**: Integrated with the AsmHighlighter for colored disassembly

## Basic Usage

```python
from caspoon.ui.widgets import InteractiveDisasmView
from caspoon.ui.navigation import NavigationManager
from caspoon.ui.syntax import AsmHighlighter

# Create the widget
widget = InteractiveDisasmView()

# Or with custom components
nav_manager = NavigationManager()
highlighter = AsmHighlighter()
widget = InteractiveDisasmView(
    navigation_manager=nav_manager,
    highlighter=highlighter
)

# Update with disassembly data
disasm_ops = [
    {"offset": 0x401000, "opcode": "push rbp"},
    {"offset": 0x401001, "opcode": "mov rbp, rsp"},
    {"offset": 0x401004, "opcode": "call 0x401100"},
    {"offset": 0x401009, "opcode": "ret"},
]

widget.update_disassembly(
    disasm_ops,
    function_name="main",
    current_address="0x401004"  # Optional: select this address
)
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move selection up/down |
| `Enter` | Jump to target address on selected line |
| `Alt+←` or `Ctrl+H` | Go back in navigation history |
| `Alt+→` or `Ctrl+L` | Go forward in navigation history |
| `g` | Open "Go to address" dialog |
| `x` | Show cross-references for selected line |

## Visual Indicators

The widget uses visual indicators to show navigation state:

```
  0x401000  ▸ call sym.imp.malloc        # ▸ indicates navigable address
  0x401005    mov rax, rbx                # No indicator for normal instructions
  0x401008  ▸ jmp 0x401100               # ▸ indicates navigable jump
> 0x40100a    push rbp                    # > indicates currently selected line
  0x40100b    mov rbp, rsp
```

- **`▸`** - Line contains a navigable address (call, jump, etc.)
- **`>`** - Currently selected line
- **Reverse video** - Selected line has reversed colors

## Message Handling

The widget emits custom messages for navigation events. Handle these in your Textual app:

```python
from textual.app import App
from caspoon.ui.widgets import InteractiveDisasmView, GotoDialog

class MyApp(App):
    def compose(self):
        yield InteractiveDisasmView(id="disasm")
    
    def on_interactive_disasm_view_navigate_to(self, message):
        """Handle navigation to an address."""
        target_address = message.address
        # Load disassembly at the target address
        self.load_function_at_address(target_address)
    
    def on_interactive_disasm_view_show_xrefs(self, message):
        """Handle cross-reference display request."""
        address = message.address
        # Show xrefs in a separate panel or modal
        self.display_xrefs(address)
    
    def on_interactive_disasm_view_open_goto_dialog(self, message):
        """Handle request to open goto dialog."""
        self.push_screen(GotoDialog(), callback=self.handle_goto)
    
    def handle_goto(self, address: str | None):
        """Handle address from goto dialog."""
        if address:
            widget = self.query_one("#disasm", InteractiveDisasmView)
            widget.jump_to_address(address)
```

## GotoDialog

The `GotoDialog` is a modal screen for entering addresses:

```python
from caspoon.ui.widgets import GotoDialog

# Push the dialog onto the screen stack
def show_goto_dialog(self):
    self.push_screen(GotoDialog(), callback=self.handle_address)

def handle_address(self, address: str | None):
    """Called when dialog is dismissed."""
    if address:
        # User entered an address
        print(f"Navigating to: {address}")
    else:
        # User cancelled
        pass
```

### Supported Address Formats

The dialog accepts multiple address formats:

- **Hexadecimal**: `0x401234`, `401234`, `0x00401234`
- **Decimal**: `4198964`
- **Symbols**: `main`, `sym.main`, `fcn.00401234`

All addresses are normalized to a standard format (hex with `0x` prefix for numeric addresses).

## Integration with NavigationManager

The widget maintains navigation history through the `NavigationManager`:

```python
# Access the navigation manager
nav_manager = widget.nav_manager

# Check navigation state
if nav_manager.can_go_back():
    print("Can go back")
if nav_manager.can_go_forward():
    print("Can go forward")

# Get current address
current = nav_manager.current_address()

# Clear history
nav_manager.clear_history()
```

## Address Extraction

The widget automatically extracts navigable addresses from instructions using regex patterns:

- Hex addresses: `call 0x401234`
- Symbols: `jmp sym.main`
- Function addresses: `call fcn.00401234`

Supported navigable instructions include:
- Calls: `call`
- Jumps: `jmp`, `je`, `jne`, `jz`, `jnz`, `jg`, `jl`, etc.
- ARM branches: `b`, `bl`, `beq`, `bne`, `blt`, `bgt`, etc.

## Example: Full Integration

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import ScrollableContainer

from caspoon.ui.widgets import InteractiveDisasmView, GotoDialog
from caspoon.ui.navigation import NavigationManager
from caspoon.ui.syntax import AsmHighlighter

class DisasmApp(App):
    """Example disassembly viewer app."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("g", "goto", "Go to address"),
    ]
    
    def __init__(self):
        super().__init__()
        self.nav_manager = NavigationManager()
        self.highlighter = AsmHighlighter()
        self.disasm_data = {}  # address -> ops mapping
    
    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer():
            yield InteractiveDisasmView(
                navigation_manager=self.nav_manager,
                highlighter=self.highlighter,
                id="disasm"
            )
        yield Footer()
    
    def on_mount(self):
        """Load initial disassembly."""
        self.load_function_at_address("0x401000")
    
    def load_function_at_address(self, address: str):
        """Load and display disassembly at an address."""
        # In a real app, fetch from analysis backend
        ops = self.disasm_data.get(address, [])
        
        widget = self.query_one("#disasm", InteractiveDisasmView)
        widget.update_disassembly(ops, f"Function at {address}", address)
    
    def on_interactive_disasm_view_navigate_to(self, message):
        """Handle navigation request."""
        self.load_function_at_address(message.address)
    
    def on_interactive_disasm_view_show_xrefs(self, message):
        """Handle xref display request."""
        # Show xrefs in a modal or separate panel
        self.notify(f"Xrefs for {message.address}")
    
    def action_goto(self):
        """Show goto address dialog."""
        self.push_screen(GotoDialog(), callback=self.handle_goto)
    
    def handle_goto(self, address: str | None):
        """Handle address from goto dialog."""
        if address:
            self.load_function_at_address(address)

if __name__ == "__main__":
    app = DisasmApp()
    app.run()
```

## Architecture Support

The widget supports multiple architectures through the integrated `AsmHighlighter`:

- **x86/x64**: Full support for common instructions
- **ARM**: Branch instructions (b, bl, beq, etc.)
- **MIPS**: (through highlighter)

To use architecture-specific highlighting:

```python
from caspoon.ui.syntax.arch_manager import get_instruction_classifier
from caspoon.ui.syntax import AsmHighlighter

# Create highlighter for specific architecture
classifier = get_instruction_classifier("arm")
highlighter = AsmHighlighter(instruction_classifier=classifier)

widget = InteractiveDisasmView(highlighter=highlighter)
```

## Customization

### Custom Color Schemes

```python
from caspoon.ui.syntax.schemes import ColorScheme, InstructionType
from caspoon.ui.syntax import AsmHighlighter

# Create custom color scheme
scheme = ColorScheme(
    call="bold red",
    jump="bold blue",
    # ... other colors
)

highlighter = AsmHighlighter(color_scheme=scheme)
widget = InteractiveDisasmView(highlighter=highlighter)
```

### Custom Address Patterns

Subclass the widget to customize address extraction:

```python
class CustomDisasmView(InteractiveDisasmView):
    # Override the address pattern
    ADDRESS_PATTERN = re.compile(r'your_custom_pattern')
    
    # Or override extraction method
    def _extract_target_address(self, opcode: str) -> str | None:
        # Custom extraction logic
        pass
```

## Testing

The widget includes comprehensive unit tests. Run them with:

```bash
pytest caspoon/tests/unit/ui/widgets/test_interactive_disasm.py -v
pytest caspoon/tests/unit/ui/widgets/test_goto_dialog.py -v
```

## Best Practices

1. **Reuse NavigationManager**: Share a single `NavigationManager` instance across widgets to maintain consistent history.

2. **Handle Messages**: Always handle the widget's messages (`NavigateTo`, `ShowXrefs`, `OpenGotoDialog`) to provide full functionality.

3. **Validate Addresses**: When jumping to addresses, validate they exist in your disassembly data.

4. **Focus Management**: Ensure the widget can receive focus for keyboard input: `widget.focus()`

5. **Performance**: For large disassembly outputs, consider paginating or limiting the number of displayed lines.

## Limitations

- **Click Support**: The widget uses keyboard navigation instead of mouse clicks due to Textual limitations.
- **Indirect Calls**: Indirect calls/jumps (e.g., `call rax`) are not marked as navigable.
- **Symbol Resolution**: The widget doesn't resolve symbols itself—ensure addresses are resolved before displaying.

## See Also

- [NavigationManager Documentation](../navigation/README.md)
- [AsmHighlighter Documentation](../syntax/README.md)
- [Textual Widgets Guide](https://textual.textualize.io/guide/widgets/)
