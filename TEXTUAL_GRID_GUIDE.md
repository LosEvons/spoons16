# Textual Grid Layout: CSS Properties and Limitations

## The Problem

When trying to use standard CSS Grid positioning properties in Textual, you'll encounter these errors:

```
Invalid CSS property 'grid-row-start'. Did you mean 'grid-rows'?
Invalid CSS property 'grid-column-start'. Did you mean 'grid-columns'?
```

## Why This Happens

**Textual CSS ≠ Standard CSS Grid**

Textual implements its own CSS subset, which includes grid layout support but **does not include explicit grid item positioning properties** from standard CSS Grid.

## What Textual Grid DOES Support

### ✅ Valid Textual Grid Properties

#### Container Level (MainScreen)
```css
MainScreen {
    layout: grid;                    /* Enable grid layout */
    grid-size: 3 2;                  /* 3 columns × 2 rows */
    grid-columns: 1fr 2fr 1fr;       /* Column widths */
    grid-rows: 1fr auto;             /* Row heights */
}
```

#### Item Level (Child Widgets)
```css
#sidebar {
    row-span: 2;                     /* Span 2 rows */
    column-span: 1;                  /* Span 1 column */
}
```

### Supported Properties Reference

| Property | Level | Purpose | Example |
|----------|-------|---------|---------|
| `layout: grid` | Container | Enable grid layout | `layout: grid;` |
| `grid-size` | Container | Define grid dimensions | `grid-size: 3 2;` (3 cols × 2 rows) |
| `grid-columns` | Container | Column sizing | `grid-columns: 1fr 2fr 1fr;` |
| `grid-rows` | Container | Row sizing | `grid-rows: 1fr auto;` |
| `row-span` | Item | Rows to span | `row-span: 2;` |
| `column-span` | Item | Columns to span | `column-span: 3;` |

## What Textual Grid DOES NOT Support

### ❌ Invalid Properties (Standard CSS Grid)

```css
#widget {
    /* ❌ These DO NOT work in Textual */
    grid-row-start: 1;
    grid-row-end: 3;
    grid-column-start: 2;
    grid-column-end: 4;
    grid-row: 1 / 3;
    grid-column: 2 / 4;
    grid-row: 1 / span 2;
    grid-column: 2 / span 3;
    grid-area: sidebar;
    grid-template-areas: "header header" "sidebar content";
}
```

**None of these standard CSS Grid positioning properties work in Textual.**

## How Textual Grid Actually Works

### Auto-Placement Based on Widget Order

Textual uses **automatic grid placement** based on the order widgets are yielded in the `compose()` method.

```python
def compose(self) -> ComposeResult:
    """Widgets are placed in grid order."""
    yield Widget1(id="first")    # → Cell (1,1)
    yield Widget2(id="second")   # → Cell (1,2)
    yield Widget3(id="third")    # → Cell (1,3)
    yield Widget4(id="fourth")   # → Cell (2,1)
```

### Grid Placement Algorithm

1. **Start at cell (1,1)** (top-left)
2. **Place first widget**, respect its `column-span` and `row-span`
3. **Move to next available cell** (left-to-right, top-to-bottom)
4. **Repeat** for each widget in yield order

### Example: 3×2 Grid

```python
class MainScreen(Container):
    DEFAULT_CSS = """
    MainScreen {
        layout: grid;
        grid-size: 3 2;              # 3 columns, 2 rows
        grid-columns: 1fr 2fr 1fr;   # Column widths
        grid-rows: 1fr auto;         # Row heights
    }
    
    #sidebar {
        row-span: 2;                 # Spans 2 rows
        column-span: 1;              # Spans 1 column
    }
    """
    
    def compose(self) -> ComposeResult:
        # Order determines placement:
        yield Sidebar(id="sidebar")      # → (1,1), spans rows 1-2
        yield Content(id="content")      # → (2,1)
        yield Details(id="details")      # → (3,1), spans rows 1-2
        yield Console(id="console")      # → (2,2)
```

**Resulting Grid:**
```
        Col 1         Col 2         Col 3
      ┌───────────┬───────────┬───────────┐
Row 1 │  Sidebar  │  Content  │  Details  │
      │ (span 2)  │           │ (span 2)  │
      ├───────────┼───────────┤           │
Row 2 │           │  Console  │           │
      └───────────┴───────────┴───────────┘
```

## The Original Problem: Hiding Panels

### ❌ Broken Approach: `display: none`

```python
# This REMOVES the widget from the grid flow
sidebar.add_class("hidden")  # CSS: .hidden { display: none; }
```

**Problem:**
- Widget is removed from document flow
- Grid auto-placement recalculates
- Remaining widgets shift to fill the gap
- Content moves from column 2 to column 1
- Layout breaks

### ✅ Working Approach: Zero-Width Columns

```python
# This KEEPS the widget in the grid but collapses its space
self.add_class("sidebar-hidden")  # CSS: grid-columns: 0 3fr 1fr;
```

**Why this works:**
- Widget stays in grid flow at its original position
- Column 1 width becomes 0 (effectively invisible)
- No auto-placement recalculation
- Other widgets remain in their columns
- Layout stays stable

### Implementation

**CSS:**
```css
MainScreen {
    grid-columns: 1fr 2fr 1fr;  /* Default: all panels visible */
}

MainScreen.sidebar-hidden {
    grid-columns: 0 3fr 1fr;    /* Sidebar column = 0 width */
}

MainScreen.details-hidden {
    grid-columns: 1fr 2fr 0;    /* Details column = 0 width */
}

MainScreen.console-hidden {
    grid-rows: 1fr 0;           /* Console row = 0 height */
}
```

**Python:**
```python
def action_toggle_sidebar(self) -> None:
    """Toggle sidebar by changing grid layout, not hiding widget."""
    self.toggle_class("sidebar-hidden")  # Toggle MainScreen class
    # Widget stays in grid, column just becomes 0 width
```

## Complete Working Example

```python
from textual.containers import Container
from textual.app import ComposeResult

class MainScreen(Container):
    """Main screen with collapsible panels."""
    
    DEFAULT_CSS = """
    MainScreen {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 2fr 1fr;
        grid-rows: 1fr auto;
    }

    #sidebar {
        row-span: 2;
        column-span: 1;
    }

    #content {
        column-span: 1;
        row-span: 1;
    }

    #details {
        row-span: 2;
        column-span: 1;
    }

    #console {
        column-span: 1;
        row-span: 1;
    }

    /* Panel hiding: set column/row to 0, don't use display:none */
    MainScreen.sidebar-hidden {
        grid-columns: 0 3fr 1fr;
    }

    MainScreen.details-hidden {
        grid-columns: 1fr 2fr 0;
    }

    MainScreen.console-hidden {
        grid-rows: 1fr 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Yield widgets in grid order."""
        yield Sidebar(id="sidebar")      # (1,1) span 2 rows
        yield Content(id="content")      # (2,1)
        yield Details(id="details")      # (3,1) span 2 rows
        yield Console(id="console")      # (2,2)

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self.toggle_class("sidebar-hidden")
        # Sidebar stays in column 1, but column width becomes 0
```

## Key Takeaways

### ✅ DO:
- Use `row-span` and `column-span` for widget sizing
- Rely on widget yield order for positioning
- Hide panels by setting grid column/row to 0 width
- Keep widgets in the grid flow

### ❌ DON'T:
- Try to use `grid-row-start` or `grid-column-start`
- Use standard CSS Grid positioning syntax
- Hide widgets with `display: none` if you need stable positioning
- Assume standard CSS Grid features work in Textual

## Common Patterns

### Pattern 1: Sidebar Layout

```css
MainScreen {
    layout: grid;
    grid-size: 2 1;              /* 2 columns, 1 row */
    grid-columns: 1fr 3fr;       /* Sidebar 25%, Content 75% */
}
```

```python
def compose(self) -> ComposeResult:
    yield Sidebar()              # Column 1
    yield Content()              # Column 2
```

### Pattern 2: Header/Content/Footer

```css
MainScreen {
    layout: grid;
    grid-size: 1 3;              /* 1 column, 3 rows */
    grid-rows: auto 1fr auto;    /* Header auto, Content flex, Footer auto */
}
```

```python
def compose(self) -> ComposeResult:
    yield Header()               # Row 1
    yield Content()              # Row 2
    yield Footer()               # Row 3
```

### Pattern 3: Dashboard Grid

```css
MainScreen {
    layout: grid;
    grid-size: 2 2;              /* 2×2 grid */
    grid-columns: 1fr 1fr;       /* Equal columns */
    grid-rows: 1fr 1fr;          /* Equal rows */
}

#big-widget {
    column-span: 2;              /* Spans both columns */
}
```

```python
def compose(self) -> ComposeResult:
    yield BigWidget(id="big-widget")    # (1,1), spans 2 columns
    yield SmallWidget1()                # (1,2)
    yield SmallWidget2()                # (2,2)
```

## Debugging Tips

### Visualize Your Grid

Add borders to see grid cells:

```css
MainScreen > * {
    border: solid green;
}
```

### Check Widget Order

The order in `compose()` determines placement. If widgets appear in wrong cells, check yield order.

### Verify Grid Size

Ensure `grid-size` matches your intended layout:
- `grid-size: 3 2` = 3 columns × 2 rows = 6 cells
- You can yield fewer widgets than cells (extras stay empty)
- You can't yield more widgets than cells fit (extras overflow)

### Test Panel Toggling

When hiding panels:
1. ✅ Widget should stay in place
2. ✅ Its column/row should collapse to 0
3. ❌ Other widgets should NOT move

If widgets move, you're probably using `display: none` instead of grid column manipulation.

## Commit History

This solution evolved through multiple attempts:

1. ❌ `row: 1; column: 1;` - Invalid properties
2. ❌ `grid-row: 1 / span 2;` - Invalid `/` syntax  
3. ❌ `grid-row-start: 1;` - Property doesn't exist in Textual
4. ✅ `row-span: 2;` + grid column manipulation - **Works!**

## Further Reading

- Textual Documentation: https://textual.textualize.io/
- Textual CSS Reference: https://textual.textualize.io/styles/
- Grid Layout Guide: https://textual.textualize.io/guide/layout/#grid
- Textual Discord: Ask questions about grid layout

## Summary

**Textual's grid layout is simpler than CSS Grid:**
- ✅ Define grid structure on container
- ✅ Set span on items
- ✅ Let auto-placement handle positioning
- ❌ No explicit cell positioning
- ❌ No grid-template-areas
- ❌ No line-based placement

**For stable panel layouts:**
- Keep widgets in the grid flow
- Hide by setting column/row to 0 width
- Never use `display: none` for grid items you want to toggle

This approach works perfectly with Textual's grid system! 🎉
