# Caspoon TUI User Guide

Welcome to the Caspoon Terminal User Interface (TUI) guide! This document will help you master the interactive binary analysis experience.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Views and Navigation](#views-and-navigation)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Command Palette](#command-palette)
- [Multi-Panel Layout](#multi-panel-layout)
- [Common Workflows](#common-workflows)
- [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Launching the TUI

Start the TUI with a binary file:

```bash
caspoon /path/to/binary
```

Or start empty and load a file later:

```bash
caspoon
```

The TUI will open in your terminal with a clean, organized interface ready for analysis.

### First Steps

1. **Load a Binary**: Enter the path to your binary in the input field at the top and press Enter
2. **Wait for Analysis**: Caspoon will analyze the binary (progress shown in the footer)
3. **Explore**: Use tabs or number keys to navigate between different views
4. **Investigate**: Use filters, search, and the command palette to dig deeper

## Interface Overview

The Caspoon TUI is organized into several key areas:

```
┌─────────────────────────────────────────────────────┐
│ Input: /path/to/binary                   [File Path]│
├─────────────────────────────────────────────────────┤
│ [Overview] [Protections] [Strings] [Imports] [R2]   │ ← Tabs
├─────────────────────────────────────────────────────┤
│                                                     │
│                  Main Content Area                  │ ← Active View
│                                                     │
├─────────────────────────────────────────────────────┤
│ Ready | Ctrl+P: Commands | Ctrl+Q: Quit            │ ← Footer
└─────────────────────────────────────────────────────┘
```

### Layout Components

- **Input Bar**: Enter file paths to analyze binaries
- **Tab Bar**: Switch between different analysis views
- **Main Content**: Displays the active view's content
- **Footer**: Shows status, progress, and key shortcuts

### Optional Panels

The TUI supports a powerful multi-panel layout:

- **Sidebar** (Ctrl+B): Function explorer for quick navigation
- **Details Panel** (Ctrl+D): Detailed information about selections
- **Console** (Ctrl+J): Analysis logs and debugging output

## Views and Navigation

Caspoon provides multiple specialized views for different analysis aspects:

### 1. Overview (Tab 1)

Displays high-level binary information:

- **File Path**: Location of the analyzed binary
- **Architecture**: CPU architecture (x86_64, ARM, MIPS, etc.)
- **Bits**: 32-bit or 64-bit
- **File Type**: ELF, PE, Mach-O, etc.
- **Size**: File size in bytes
- **Entry Point**: Program entry address
- **Stripped**: Whether debug symbols are present

**Use Case**: Quick binary identification and metadata overview

### 2. Protections (Tab 2)

Shows security hardening features:

- **PIE** (Position Independent Executable): ASLR support
- **NX** (No-Execute): Stack execution protection
- **Canary**: Stack canary/cookie protection
- **RELRO** (Relocation Read-Only): GOT hardening (None/Partial/Full)

**Color Coding**:
- 🟢 **Green**: Protection enabled (good)
- 🔴 **Red**: Protection disabled (vulnerable)
- 🟡 **Yellow**: Partial protection

**Use Case**: Security assessment and exploitation difficulty evaluation

### 3. Strings (Tab 3)

Lists all printable strings found in the binary:

- **Filter**: Press `/` to search strings
- **Navigation**: Arrow keys to browse, Enter to select
- **Selection**: View context and location of selected string

**Features**:
- Case-insensitive filtering
- Real-time search as you type
- Offset and section information
- Large string support (truncated with indicator)

**Use Case**: Finding API keys, error messages, URLs, credentials, debug info

### 4. Imports/Exports (Tab 4)

Shows imported and exported functions:

**Imports** (left column):
- Functions the binary imports from libraries
- Reveals dependencies and capabilities
- Indicates libc functions, network APIs, file operations

**Exports** (right column):
- Functions the binary exports (if a library)
- Public API surface
- Potential entry points

**Use Case**: Understanding binary capabilities, API analysis, dependency mapping

### 5. R2 Analysis (Tab 5)

Advanced analysis powered by radare2:

- **Functions**: Detailed function analysis
- **Cross-references**: Function calls and references
- **Disassembly**: Assembly code view
- **Control Flow**: Program flow analysis

**Use Case**: Deep technical analysis, reverse engineering, vulnerability research

## Keyboard Shortcuts

Master these shortcuts for efficient navigation:

### Global Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+P` | Command Palette | Search and execute commands |
| `Ctrl+Q` | Quit | Exit the application |
| `F1` | Help | Show help screen |
| `Tab` | Next Widget | Focus next interactive element |
| `Shift+Tab` | Previous Widget | Focus previous element |

### View Navigation

| Shortcut | Action | Description |
|----------|--------|-------------|
| `1` | Overview | Switch to Overview tab |
| `2` | Protections | Switch to Protections tab |
| `3` | Strings | Switch to Strings tab |
| `4` | Imports/Exports | Switch to Imports/Exports tab |
| `5` | R2 Analysis | Switch to R2 Analysis tab |

### Panel Controls

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+B` | Toggle Sidebar | Show/hide function explorer |
| `Ctrl+D` | Toggle Details | Show/hide details panel |
| `Ctrl+J` | Toggle Console | Show/hide console output |

### View-Specific Shortcuts

| Shortcut | View | Action |
|----------|------|--------|
| `/` | Strings | Focus filter/search |
| `Escape` | Any | Clear filter/cancel action |
| `↑/↓` | Lists | Navigate up/down |
| `Enter` | Lists | Select item |
| `Page Up/Down` | Lists | Fast scroll |

## Command Palette

The Command Palette (Ctrl+P) provides quick access to all Caspoon actions through fuzzy search.

### Opening the Palette

Press `Ctrl+P` from anywhere in the TUI.

### Using the Palette

1. **Type to Search**: Start typing command names, categories, or keybindings
2. **Navigate**: Use arrow keys to browse results
3. **Execute**: Press Enter to run the selected command
4. **Cancel**: Press Escape to close without executing

### Search Examples

- Type `"strings"` → Find string-related commands
- Type `"toggle"` → Find all toggle commands
- Type `"ctrl+b"` → Find commands with Ctrl+B keybinding
- Type `"view"` → Find view-related commands

### Command Categories

Commands are organized into logical groups:

- **File**: Binary loading and file operations
- **View**: Tab and view switching
- **Navigation**: Moving through data
- **Panel**: Panel visibility controls
- **Analysis**: Analysis operations
- **Filter**: Search and filter operations

## Multi-Panel Layout

For advanced workflows, Caspoon supports a multi-panel layout with simultaneous views.

### Function Explorer Sidebar (Ctrl+B)

Shows a tree/list of all functions in the binary:

- **Navigate**: Arrow keys to browse functions
- **Select**: Enter to view function details
- **Filter**: Type to filter function list
- **Context**: Right panel shows selected function info

**Use Case**: Quick function navigation, API exploration

### Details Panel (Ctrl+D)

Displays detailed information about the current selection:

- **String Details**: Full string content, offset, section
- **Function Details**: Disassembly, size, calls, references
- **Import/Export Details**: Library, type, usage

**Use Case**: Deep dive into selected items without switching views

### Console Panel (Ctrl+J)

Shows analysis progress and debug output:

- **Logs**: Real-time analysis messages
- **Errors**: Debugging information
- **Progress**: Detailed operation status

**Use Case**: Troubleshooting, understanding analysis process

### Panel Workflows

**Workflow 1: Function Analysis**
1. Press `Ctrl+B` to open sidebar
2. Navigate to interesting function
3. Press Enter to load details
4. Press `Ctrl+D` to see disassembly
5. Press `Ctrl+J` to view analysis logs

**Workflow 2: String Investigation**
1. Go to Strings view (press `3`)
2. Press `/` and type search term
3. Select interesting string
4. Press `Ctrl+D` to see context
5. Use sidebar to find related functions

## Common Workflows

### Workflow 1: Quick Binary Assessment

**Goal**: Quickly understand a binary's purpose and security

```
1. Load binary → caspoon /path/to/binary
2. View Overview (1) → Check architecture, size, stripped status
3. View Protections (2) → Assess security hardening
4. View Imports (4) → Identify capabilities (network, file, crypto)
5. Search Strings (3, then /) → Look for URLs, paths, messages
```

**Time**: 2-3 minutes

### Workflow 2: Finding Sensitive Data

**Goal**: Locate API keys, passwords, or sensitive strings

```
1. Go to Strings view (3)
2. Apply filters:
   - Type "password" → Check results
   - Type "api" → Check API keys
   - Type "secret" → Check secrets
   - Type "key" → Check encryption keys
3. Select suspicious strings (Enter)
4. View context in details panel (Ctrl+D)
5. Cross-reference with functions (Ctrl+B)
```

**Time**: 5-10 minutes

### Workflow 3: Security Analysis

**Goal**: Assess exploitation difficulty and attack surface

```
1. View Protections (2) → Document enabled protections
2. View Imports (4) → Identify dangerous functions:
   - strcpy, sprintf → Buffer overflow candidates
   - system, exec → Command injection
   - malloc, free → Memory management
3. View Strings (3) → Search for:
   - Format strings ("%s", "%d")
   - Shell commands
   - File paths
4. Use R2 Analysis (5) → Examine vulnerable functions
```

**Time**: 15-30 minutes

### Workflow 4: Malware Triage

**Goal**: Quickly identify malicious behavior indicators

```
1. View Imports (4) → Check for:
   - Network functions (socket, connect)
   - Process functions (fork, exec)
   - File operations (fopen, read, write)
   - Crypto functions (encrypt, hash)
2. Search Strings (3):
   - IPs and domains → C2 servers
   - "http://" or "https://" → Network activity
   - File paths → Dropped files
   - Registry keys → Persistence (Windows)
3. View Protections (2) → Often disabled in malware
4. Examine suspicious functions with R2 (5)
```

**Time**: 10-20 minutes

## Tips and Tricks

### Efficiency Tips

1. **Use Number Keys**: Press `1-5` to instantly switch views without reaching for the mouse
2. **Memorize Ctrl Combos**: `Ctrl+P` (palette), `Ctrl+B` (sidebar), `Ctrl+D` (details) are your best friends
3. **Filter Early**: In Strings view, apply filters immediately to reduce noise
4. **Command Palette for Discovery**: Press `Ctrl+P` and type random words to discover features

### Analysis Tips

1. **Start with Imports**: Imports reveal capabilities faster than strings
2. **Cross-Reference**: Use multiple views—find string, check function, view disassembly
3. **Look for Patterns**: Suspicious strings often cluster near suspicious functions
4. **Check Entry Points**: Start analysis at main() or exported functions

### Performance Tips

1. **Filter Large String Lists**: Use `/` to filter before scrolling through thousands of strings
2. **Close Unused Panels**: Toggle off panels you're not actively using
3. **Use Pagination**: Navigate large lists with Page Up/Down instead of arrow keys

### Debugging Tips

1. **Console Output**: Press `Ctrl+J` if analysis seems stuck
2. **Progress Messages**: Watch the footer for analysis progress
3. **Error Recovery**: If something crashes, the TUI should remain responsive—try reloading

### Keyboard Maestro

Combine shortcuts for lightning-fast workflows:

- **`3` → `/` → `"password"` → `Enter`**: Jump to strings, filter, select first match
- **`Ctrl+B` → `Enter` → `Ctrl+D`**: Open sidebar, select first, view details
- **`Ctrl+P` → `"strings"` → `Enter`**: Command palette quick switch

### Hidden Features

- **Auto-Complete**: File path input supports tab completion
- **Fuzzy Search**: Command palette matches partial words
- **Quick Selection**: In lists, type letters to jump to entries
- **Context Awareness**: Some shortcuts change based on active view

## Troubleshooting

### Common Issues

**Q: Binary won't load**
- Check file path is correct
- Verify file permissions (must be readable)
- Ensure radare2 is installed

**Q: Analysis takes too long**
- Large binaries (>100MB) take time
- Press `Escape` to cancel analysis
- Close unused panels for better performance

**Q: Strings view is overwhelming**
- Use filter (`/`) to narrow results
- Try specific search terms ("http", "error", "password")
- Consider your analysis goal and filter accordingly

**Q: Nothing happens when I press keys**
- Ensure correct widget has focus
- Some keys only work in specific views
- Try pressing `Tab` to change focus

**Q: Display looks weird/corrupted**
- Try resizing terminal window
- Ensure terminal supports colors and box-drawing characters
- Use a modern terminal (kitty, alacritty, iTerm2, Windows Terminal)

### Getting Help

- **In-App Help**: Press `F1`
- **Documentation**: Check `docs/` folder
- **Issues**: Report bugs on GitHub
- **Community**: Join discussions for tips and tricks

## Next Steps

Now that you understand the TUI, try these advanced topics:

1. **Automation**: Learn to script Caspoon for batch analysis
2. **Custom Backends**: Integrate other analysis tools
3. **Export Results**: Save findings to reports
4. **Advanced R2**: Master radare2 integration

Happy analyzing! 🕵️
