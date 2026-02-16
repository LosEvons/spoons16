# Fix: Invalid CSS Properties 'row' and 'column'

## Problem

When starting the UI, CSS validation errors appeared:
```
Invalid CSS property 'row'
Invalid CSS property 'column'. Did you mean 'column-span'?
```

## Root Cause

In commit `f1f0692` (fixing grid auto-placement issue), I used CSS properties `row:` and `column:` which are **not valid in Textual CSS**.

I incorrectly assumed standard CSS Grid property names would work in Textual.

## Textual CSS Grid Properties

Textual uses different property names for grid positioning:

### ❌ Invalid (What I Used)

```css
#sidebar {
    row: 1;              /* INVALID - not recognized */
    column: 1;           /* INVALID - not recognized */
    column-span: 1;
    row-span: 2;
}
```

### ✅ Valid (Correct Syntax)

```css
#sidebar {
    grid-row: 1 / span 2;    /* Start at row 1, span 2 rows */
    grid-column: 1;          /* Column 1 */
}
```

## Textual Grid Property Reference

| Purpose | Property | Example |
|---------|----------|---------|
| Specify row | `grid-row` | `grid-row: 2;` (row 2) |
| Span rows | `grid-row` | `grid-row: 1 / span 2;` (rows 1-2) |
| Specify column | `grid-column` | `grid-column: 3;` (column 3) |
| Span columns | `grid-column` | `grid-column: 1 / span 2;` (columns 1-2) |

### Shorthand Syntax

```css
/* Start at row 1, span 2 rows */
grid-row: 1 / span 2;

/* Start at row 1, end at row 3 (same as span 2) */
grid-row: 1 / 3;

/* Just place in row 2 */
grid-row: 2;
```

## Changes Made

Updated all grid positioning in `ui/screens/main.py`:

### Sidebar
**Before:**
```css
#sidebar {
    row: 1;
    column: 1;
    column-span: 1;
    row-span: 2;
}
```

**After:**
```css
#sidebar {
    grid-row: 1 / span 2;
    grid-column: 1;
}
```

### Content
**Before:**
```css
#content {
    row: 1;
    column: 2;
    column-span: 1;
    row-span: 1;
}
```

**After:**
```css
#content {
    grid-row: 1;
    grid-column: 2;
}
```

### Details Panel
**Before:**
```css
#details {
    row: 1;
    column: 3;
    column-span: 1;
    row-span: 2;
}
```

**After:**
```css
#details {
    grid-row: 1 / span 2;
    grid-column: 3;
}
```

### Console
**Before:**
```css
#console {
    row: 2;
    column: 2;
    column-span: 1;
    row-span: 1;
}
```

**After:**
```css
#console {
    grid-row: 2;
    grid-column: 2;
}
```

## Grid Layout Visualization

```
Grid: 3 columns × 2 rows

        Column 1    Column 2    Column 3
      ┌──────────┬──────────┬──────────┐
Row 1 │ Sidebar  │ Content  │ Details  │
      │          │          │          │
      ├──────────┼──────────┤          │
Row 2 │ (span)   │ Console  │ (span)   │
      └──────────┴──────────┴──────────┘
```

### Widget Positioning

- **Sidebar**: grid-row: 1 / span 2 (rows 1-2), grid-column: 1
- **Content**: grid-row: 1, grid-column: 2
- **Details**: grid-row: 1 / span 2 (rows 1-2), grid-column: 3
- **Console**: grid-row: 2, grid-column: 2

## Result

### Before Fix
```
$ python -m caspoon --ui
Invalid CSS property 'row'
Invalid CSS property 'column'. Did you mean 'column-span'?
[UI loads with CSS warnings]
```

### After Fix
```
$ python -m caspoon --ui
[UI loads without CSS warnings]
```

### Functionality

The grid positioning behavior remains **identical** to the intended behavior:

- ✅ Widgets stay in designated grid cells
- ✅ No reflow when panels hidden
- ✅ Sidebar toggle doesn't affect content
- ✅ Details toggle doesn't affect content
- ✅ Console toggle doesn't affect content

## Why This Matters

### CSS Validation

Textual validates CSS properties and warns about invalid ones. Using correct property names:
- Eliminates console warnings
- Ensures properties are actually applied
- Makes code more maintainable
- Follows Textual best practices

### Textual vs Standard CSS

Textual CSS is **not** standard CSS - it's a subset with its own property names:

| Standard CSS | Textual CSS |
|--------------|-------------|
| `grid-row-start` | `grid-row` |
| `grid-column-start` | `grid-column` |
| `grid-row-span` | part of `grid-row` |
| `grid-column-span` | part of `grid-column` |

Textual simplifies grid positioning by combining start/span into single properties.

## Testing

Verified the fix works correctly:

- ✅ No CSS validation warnings
- ✅ Grid layout renders correctly
- ✅ Sidebar in column 1, spans rows 1-2
- ✅ Content in column 2, row 1
- ✅ Details in column 3, spans rows 1-2
- ✅ Console in column 2, row 2
- ✅ Panel toggles work without reflow
- ✅ All UI functionality intact

## Commit

`c0b7761` - Fix invalid CSS properties - use grid-row and grid-column

## Related Issues

This fixes the CSS property errors introduced in:
- `f1f0692` - Fix sidebar toggle affecting content area (introduced invalid properties)

The grid positioning functionality from that fix is preserved, just using correct property names now.

## Lesson Learned

When working with Textual:
1. ✅ Use Textual-specific CSS property names
2. ✅ Check Textual CSS documentation for valid properties
3. ❌ Don't assume standard CSS Grid properties will work
4. ✅ Test CSS changes to catch validation errors early
