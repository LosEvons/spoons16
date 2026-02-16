# Subtask 5: Cross-Reference Display

**Status**: ⏸️ NOT STARTED (⚠️ May be partially completed by Subtask 4)  
**Dependencies**: ✅ Subtasks 1-3 complete, ✅ Plan 4 (TUI Redesign) complete, ⏸️ Subtask 4 (Interactive Navigation)  
**Note**: Much of this subtask's functionality overlaps with Subtask 4's details panel work

## Objective
Display cross-references (xrefs) for functions and addresses, showing where code is called from and what it calls.

## Scope
- Display "called from" (callers) for functions
- Display "calls to" (callees) for functions
- Show jump target references
- Provide xref panel or inline display
- Integration with new details panel and reactive TUI

## Implementation

**NOTE**: This subtask is largely superseded by Subtask 4's details panel integration. Consider whether additional work is needed beyond Subtask 4.

### 1. Enhanced Xref Display in Details Panel (2 hours)
**Location**: `caspoon/ui/widgets/details_panel.py`

*If not fully implemented in Subtask 4*, enhance the details panel xref display:

```python
class DetailsPanel(Static):
    """Display contextual information including xrefs."""
    
    def show_xrefs(self, address: str, xref_data: dict):
        """Display comprehensive cross-references."""
        parts = []
        
        # Callers section
        callers = xref_data.get('callers', [])
        if callers:
            parts.append(Text("Called From:", style="bold cyan"))
            for caller in callers:
                from_addr = caller.get('from', 'unknown')
                fcn_name = caller.get('fcn_name', '<unknown>')
                xref_type = caller.get('type', 'call')
                parts.append(Text(f"  {from_addr} ({xref_type}) - {fcn_name}"))
        
        # Callees section
        callees = xref_data.get('callees', [])
        if callees:
            parts.append(Text("\nCalls To:", style="bold magenta"))
            for callee in callees:
                to_addr = callee.get('to', 'unknown')
                fcn_name = callee.get('fcn_name', '<unknown>')
                xref_type = callee.get('type', 'call')
                parts.append(Text(f"  {to_addr} ({xref_type}) - {fcn_name}"))
        
        # Jump targets
        jumps = xref_data.get('jumps', [])
        if jumps:
            parts.append(Text("\nJump Targets:", style="bold yellow"))
            for jump in jumps:
                target = jump.get('target', 'unknown')
                parts.append(Text(f"  → {target}"))
        
        group = Group(*parts)
        panel = Panel(group, title="Cross-References", border_style="cyan")
        self.update(panel)
```

### 2. Inline Xref Annotations (3 hours)
**Location**: `caspoon/ui/views/r2_view.py`

Add inline xref counts to disassembly display:

```python
def _format_instruction_with_xrefs(self, op: dict, xrefs: dict) -> Text:
    """Format instruction with inline xref annotations."""
    offset = hex(op.get("offset", 0))
    opcode = op.get("opcode", "")
    
    # Get syntax highlighted instruction
    highlighted = self._highlighter.highlight_instruction(opcode, offset)
    
    # Check if this address has xrefs
    if offset in xrefs:
        xref_data = xrefs[offset]
        caller_count = len(xref_data.get('callers', []))
        callee_count = len(xref_data.get('callees', []))
        
        # Add xref annotation
        if caller_count > 0:
            highlighted.append(f"  ; ← {caller_count} caller(s)", style="dim cyan")
        if callee_count > 0:
            highlighted.append(f"  ; → {callee_count} callee(s)", style="dim magenta")
    
    return highlighted
```

### 3. Xref Filtering and Sorting (2 hours)
**Location**: `caspoon/ui/widgets/details_panel.py`

Add ability to filter xrefs by type:

```python
def show_xrefs(self, address: str, xref_data: dict, filter_type: str = "all"):
    """Display cross-references with optional filtering.
    
    Args:
        address: The address to show xrefs for
        xref_data: The xref data dictionary
        filter_type: "all", "calls", "jumps", "data"
    """
    # Filter based on type
    if filter_type == "calls":
        # Show only call xrefs
        pass
    elif filter_type == "jumps":
        # Show only jump xrefs
        pass
    # ... etc
```

### 4. Xref Navigation Integration (1 hour)
**Location**: `caspoon/ui/widgets/details_panel.py`

Make xref entries in the details panel navigable:

```python
# When user presses Enter on an xref entry, navigate to that address
def on_key(self, event):
    if event.key == "enter":
        selected_xref = self.get_selected_xref()
        if selected_xref:
            self.post_message(JumpToAddress(selected_xref.address))
```

## Estimated Time
**12 hours total** → **8 hours revised** (most work done in Subtask 4)
- Enhanced xref display: 2 hours (if needed beyond Subtask 4)
- Inline xref annotations: 3 hours
- Xref filtering/sorting: 2 hours
- Xref navigation: 1 hour (most done in Subtask 4)

**NOTE**: If Subtask 4 fully implements xref display in details panel, this subtask may reduce to only 5-6 hours for inline annotations and enhancements.

## Success Criteria
- [ ] Xrefs are displayed for functions in details panel
- [ ] Both callers and callees are shown
- [ ] Inline xref counts are visible in disassembly
- [ ] Navigation to xref sources works (from details panel)
- [ ] Xref display distinguishes between calls, jumps, and data refs
- [ ] Performance is acceptable even with many xrefs

## Integration with Subtask 4

**Overlap Areas**:
- ✅ Xref extraction from r2 backend (done in Subtask 4)
- ✅ Basic xref display in details panel (done in Subtask 4)
- ✅ Xref navigation (done in Subtask 4)

**Unique to Subtask 5**:
- ⏸️ Inline xref count annotations in disassembly
- ⏸️ Xref type filtering (calls vs jumps vs data)
- ⏸️ Xref sorting and advanced display options
- ⏸️ Jump target visualization

## Recommended Approach

**Option 1**: Merge with Subtask 4
- Complete Subtask 4 first
- Evaluate if separate Subtask 5 work is needed
- If basic xref display is sufficient, mark this subtask as complete

**Option 2**: Implement as Enhancement
- Treat this subtask as "Advanced Xref Features"
- Focus on inline annotations and filtering
- Keep details panel work in Subtask 4

**Recommendation**: Option 2 - Keep subtasks separate but coordinate implementation to avoid duplication.

## Next Steps
After completion, proceed to Subtask 6: Performance Optimization.
