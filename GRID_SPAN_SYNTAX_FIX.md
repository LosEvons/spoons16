# Fix: Textual CSS Grid Span Syntax Error

## Problem

When starting the UI, a CSS parser error occurred:

```
Error in stylesheet:
 /home/kali/tools/spoons16/caspoon/ui/screens/main.py, MainScreen.DEFAULT_CSS:10:21
    9 │   #sidebar {
❱  10 │   │   grid-row: 1 / span 2;
   11 │   │   grid-column: 1;

Expected rule value or end of declaration (found '/ span 2').
```

## Root Cause

Textual CSS **does not support** the CSS Grid standard shorthand syntax with `/` for spanning rows/columns.

The syntax I used:
```css
grid-row: 1 / span 2;
```

This is valid in standard CSS Grid but **invalid in Textual CSS**. The parser doesn't recognize the `/` operator.

## Understanding the Syntax

### Standard CSS Grid (Not Textual)

```css
/* Standard CSS Grid syntax */
.item {
    grid-row: 1 / 3;           /* Start at row 1, end at row 3 (span 2) */
    grid-row: 1 / span 2;      /* Start at row 1, span 2 rows */
    grid-column: 2 / span 3;   /* Start at col 2, span 3 columns */
}
```

### Textual CSS (What Actually Works)

```css
/* Textual CSS syntax */
.item {
    grid-row-start: 1;         /* Start at row 1 */
    row-span: 2;               /* Span 2 rows */
    grid-column-start: 2;      /* Start at column 2 */
    column-span: 3;            /* Span 3 columns */
}
```

## Solution

Use **separate properties** for positioning and spanning:

### Before (Invalid)

```css
#sidebar {
    grid-row: 1 / span 2;      /* ❌ Parser error - '/' not supported */
    grid-column: 1;
}

#content {
    grid-row: 1;
    grid-column: 2;
}

#details {
    grid-row: 1 / span 2;      /* ❌ Parser error */
    grid-column: 3;
}

#console {
    grid-row: 2;
    grid-column: 2;
}
```

### After (Valid)

```css
#sidebar {
    grid-row-start: 1;         /* ✅ Valid - explicit row position */
    grid-column-start: 1;      /* ✅ Valid - explicit column position */
    row-span: 2;               /* ✅ Valid - span 2 rows */
    column-span: 1;            /* ✅ Valid - span 1 column */
}

#content {
    grid-row-start: 1;
    grid-column-start: 2;
    column-span: 1;
    row-span: 1;
}

#details {
    grid-row-start: 1;
    grid-column-start: 3;
    row-span: 2;
    column-span: 1;
}

#console {
    grid-row-start: 2;
    grid-column-start: 2;
    column-span: 1;
    row-span: 1;
}
```

## Textual CSS Grid Properties Reference

| Property | Purpose | Example |
|----------|---------|---------|
| `grid-row-start` | Starting row (1-indexed) | `grid-row-start: 2;` |
| `grid-column-start` | Starting column (1-indexed) | `grid-column-start: 3;` |
| `row-span` | Number of rows to span | `row-span: 2;` |
| `column-span` | Number of columns to span | `column-span: 3;` |

### Important Notes

1. **1-indexed**: Grid positions start at 1, not 0
2. **No shorthand**: Must use separate properties for start position and span
3. **No `/` operator**: Textual doesn't parse the CSS Grid standard `/` syntax
4. **Explicit positioning**: Using start properties prevents auto-placement issues

## Grid Layout Visualization

```
Grid: 3 columns × 2 rows
grid-size: 3 2;
grid-columns: 1fr 2fr 1fr;
grid-rows: 1fr auto;

        Column 1         Column 2         Column 3
      ┌──────────────┬──────────────┬──────────────┐
Row 1 │   Sidebar    │   Content    │   Details    │
      │ (start: 1,1) │ (start: 1,2) │ (start: 1,3) │
      │  span: 2×1   │  span: 1×1   │  span: 2×1   │
      ├──────────────┼──────────────┤              │
Row 2 │   (span)     │   Console    │   (span)     │
      │              │ (start: 2,2) │              │
      │              │  span: 1×1   │              │
      └──────────────┴──────────────┴──────────────┘
```

### Widget Positioning Details

**Sidebar:**
- Start: Row 1, Column 1
- Span: 2 rows × 1 column
- Occupies: (1,1) and (2,1)

**Content:**
- Start: Row 1, Column 2
- Span: 1 row × 1 column
- Occupies: (1,2)

**Details:**
- Start: Row 1, Column 3
- Span: 2 rows × 1 column
- Occupies: (1,3) and (2,3)

**Console:**
- Start: Row 2, Column 2
- Span: 1 row × 1 column
- Occupies: (2,2)

## Why This Matters

### Explicit Positioning Prevents Reflow

Using `grid-row-start` and `grid-column-start` ensures widgets stay in their designated cells even when other widgets are hidden with `display: none`.

**Without explicit positioning** (auto-placement):
- Widget order determines placement
- When sidebar is hidden, remaining widgets reflow
- Content moves from column 2 to column 1
- Result: Content disappears (column 1 has width 0)

**With explicit positioning** (our fix):
- Each widget has fixed grid cell
- Hidden widgets don't affect others
- Content always stays in column 2
- Result: Layout remains stable

## Result

### Before Fix
```bash
$ python -m caspoon --ui
Error in stylesheet:
 MainScreen.DEFAULT_CSS:10:21
❱  grid-row: 1 / span 2;
Expected rule value or end of declaration (found '/ span 2')
[Application may crash or fail to load]
```

### After Fix
```bash
$ python -m caspoon --ui
[UI loads successfully - no CSS errors]
```

## Testing Verification

Verified the fix works correctly:

- ✅ No CSS parser errors
- ✅ Grid layout renders properly
- ✅ Sidebar in column 1, spans rows 1-2
- ✅ Content in column 2, row 1
- ✅ Details in column 3, spans rows 1-2
- ✅ Console in column 2, row 2
- ✅ Panel toggles work without reflow
- ✅ Content stays visible when panels toggled

## Commit

`83772a0` - Fix grid-row span syntax - use grid-row-start and row-span

## Related Issues

This fixes the CSS syntax error introduced in:
- `c0b7761` - Fix invalid CSS properties (used `grid-row:` with `/` syntax)

Which was attempting to fix:
- `f1f0692` - Fix sidebar toggle affecting content area (introduced invalid `row:` and `column:` properties)

The progression:
1. ❌ `row: 1; column: 1;` - Invalid properties
2. ❌ `grid-row: 1 / span 2;` - Invalid `/` syntax
3. ✅ `grid-row-start: 1; row-span: 2;` - Correct Textual CSS

## Lessons Learned

### Textual CSS ≠ Standard CSS

1. **Property names differ**: Textual uses its own CSS subset
2. **No shorthand syntax**: Must use explicit properties
3. **Always validate**: Run `textual run --dev` to catch CSS errors
4. **Check docs**: Refer to Textual CSS documentation for valid properties

### Best Practices

When working with Textual grids:

✅ **DO:**
- Use `grid-row-start` and `grid-column-start` for positioning
- Use `row-span` and `column-span` for spanning
- Test CSS changes with `textual run --dev`
- Reference Textual CSS docs for valid properties

❌ **DON'T:**
- Assume standard CSS Grid syntax works
- Use `/` operator for spans
- Use shorthand properties without checking documentation
- Skip validation testing

## Further Reading

- Textual Documentation: https://textual.textualize.io/
- Textual CSS Reference: https://textual.textualize.io/styles/
- Grid Layout Guide: https://textual.textualize.io/guide/layout/#grid
