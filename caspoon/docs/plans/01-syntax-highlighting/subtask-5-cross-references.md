# Subtask 5: Cross-Reference Display

## Objective
Display cross-references (xrefs) for functions and addresses, showing where code is called from and what it calls.

## Scope
- Display "called from" (callers) for functions
- Display "calls to" (callees) for functions
- Show jump target references
- Provide xref panel or inline display

## Implementation

### 1. Xref Panel Widget (4 hours)
**Location**: `caspoon/ui/widgets/xref_panel.py`

```python
class XrefPanel(Static):
    """Display cross-references for selected address."""
    
    def update_xrefs(self, address: str, xref_data: Dict):
        """Update panel with xrefs for address."""
        # Callers (xrefs to this address)
        callers = xref_data.get('callers', [])
        
        # Callees (xrefs from this address)
        callees = xref_data.get('callees', [])
        
        # Format and display
        table = Table(title=f"Cross-References for {address}")
        table.add_column("Type")
        table.add_column("Address")
        table.add_column("Function")
        
        for caller in callers:
            table.add_row("Caller", caller['addr'], caller.get('name', ''))
        
        for callee in callees:
            table.add_row("Calls", callee['addr'], callee.get('name', ''))
        
        self.update(table)
```

### 2. Enhanced R2 Backend (3 hours)
Extract comprehensive xref data:

```python
def get_xrefs_for_function(r2, func_addr: str) -> Dict:
    """Get both incoming and outgoing xrefs."""
    # Xrefs TO this function (callers)
    callers_json = r2.cmd(f"axtj @ {func_addr}")
    callers = json.loads(callers_json) if callers_json.strip() else []
    
    # Xrefs FROM this function (callees)
    callees_json = r2.cmd(f"axfj @ {func_addr}")
    callees = json.loads(callees_json) if callees_json.strip() else []
    
    return {
        'callers': callers,
        'callees': callees
    }
```

### 3. Inline Xref Display (3 hours)
Show xref count inline with disassembly:

```text
0x400500:  mov    rax, [rbp-0x8]
0x400504:  call   sym.helper          ; xrefs: 3 calls to this
0x400509:  jne    0x400520            ; → 0x400520
```

### 4. Xref Navigation (2 hours)
Allow jumping to xref sources/targets.

## Estimated Time
**12 hours total**

## Success Criteria
- [ ] Xrefs are displayed for functions
- [ ] Both callers and callees are shown
- [ ] Xref panel is accessible from disassembly view
- [ ] Navigation to xref sources works

## Next Steps
Proceed to Subtask 6: Performance Optimization.
