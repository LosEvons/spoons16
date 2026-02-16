# Grid Positioning Fix - Sidebar Toggle Issue

## Problem

When toggling the left sidebar (Ctrl+B), the middle content area was also disappearing or becoming invisible.

## Root Cause

The grid layout was using **auto-placement** for widgets - they had `column-span` and `row-span` properties but no explicit `row` and `column` positions. 

When the sidebar was hidden using `display: none`, it was completely removed from the document flow. The CSS Grid auto-placement algorithm then treated the remaining widgets as if the sidebar never existed, causing them to reflow:

**Before hiding sidebar:**
```
| Sidebar (col 1) | Content (col 2)  | Details (col 3) |
|                 | Console (col 2)  |                 |
```

**After hiding sidebar (display: none) - with auto-placement:**
```
| Content (col 1) ??? | Console (col 1) ??? | Details (col 2) ??? |
```

The content and console moved to column 1, which had `grid-columns: 0` width when sidebar was hidden, effectively hiding them!

## Solution

Added **explicit grid positioning** using `row` and `column` properties:

```css
#sidebar {
    row: 1;
    column: 1;
    column-span: 1;
    row-span: 2;
}

#content {
    row: 1;
    column: 2;
    column-span: 1;
    row-span: 1;
}

#details {
    row: 1;
    column: 3;
    column-span: 1;
    row-span: 2;
}

#console {
    row: 2;
    column: 2;
    column-span: 1;
    row-span: 1;
}
```

## How It Works Now

With explicit positioning, widgets **always** stay in their designated grid cells:

**Sidebar visible:**
```
Grid: 1fr 2fr 1fr (25%, 50%, 25%)
| Sidebar (col 1) | Content (col 2)  | Details (col 3) |
| 25%             | Console (col 2)  | 25%             |
|                 | 50%              |                 |
```

**Sidebar hidden (display: none):**
```
Grid: 0 3fr 1fr (0%, 75%, 25%)
| [Sidebar hidden]| Content (col 2)  | Details (col 3) |
| (col 1, 0%)     | Console (col 2)  | 25%             |
|                 | 75%              |                 |
```

Even though sidebar is hidden, content and console remain in column 2 because of explicit positioning. Column 1 just becomes 0 width.

## Result

- ✅ Toggling sidebar (Ctrl+B) only affects sidebar visibility
- ✅ Content area always stays visible in column 2
- ✅ Console always stays visible in column 2
- ✅ Details panel always stays in column 3
- ✅ Grid column widths adjust correctly when panels hidden

## Technical Details

### CSS Grid Auto-Placement vs Explicit Positioning

**Auto-placement** (what we had):
- Widgets placed in order they appear in DOM
- Grid fills cells sequentially
- `display: none` elements skip placement
- Remaining elements reflow to fill grid

**Explicit positioning** (what we have now):
- Each widget has fixed `row` and `column`
- Grid respects positions regardless of DOM order
- `display: none` elements still "occupy" their cell (just invisible)
- No reflow when elements hidden

### Why This Matters

In Textual's CSS Grid:
- When a widget has `display: none`, it's removed from layout flow
- Auto-placement treats remaining widgets as if hidden widget doesn't exist
- With explicit positioning, grid cells remain allocated even if empty

## Files Changed

- `caspoon/ui/screens/main.py` - Added explicit `row` and `column` to all grid widgets

## Commit

`f1f0692` - Fix sidebar toggle affecting content area - use explicit grid positioning
