# Subtask 6: Performance Optimization

**Status**: 🔄 PARTIALLY IMPLEMENTED  
**Completion**: ~40% (basic limits exist, comprehensive optimization needed)  
**Dependencies**: ✅ Subtasks 1-3 complete, ✅ Plan 4 (TUI Redesign) complete

## Objective
Optimize syntax highlighting and rendering for large binaries without UI slowdown.

## Scope
- Lazy loading of disassembly
- Pagination for large outputs
- Caching of highlighted content
- Efficient rendering strategies
- Integration with async workers

## Performance Targets
- Highlight 1000 instructions in <100ms
- Smooth scrolling with 10,000+ line disassembly
- UI remains responsive during analysis ✅ (async workers implemented)
- Memory usage scales reasonably with binary size
- No noticeable lag when switching between functions

## Current State

### ✅ Already Implemented (Plan 4 TUI Redesign)
1. **Display Limits** in `r2_view.py`:
   - `MAX_FUNCTIONS = 50`
   - `MAX_DISASM_OPS = 100`
   - `MAX_STRINGS = 50`
   - Prevents UI from loading excessive data

2. **Async Workers** (`ui/workers/`):
   - Non-blocking analysis execution
   - Progress reporting
   - Cancellation support
   - Keeps UI responsive during analysis

3. **Reactive Architecture**:
   - Efficient state updates
   - Only re-renders what changes
   - Message-based event system

### ⏸️ Still Needed
1. **Lazy Loading**: Load disassembly on-demand as user scrolls
2. **Caching**: Cache highlighted instructions to avoid re-processing
3. **Pagination**: Proper pagination UI for navigating large functions
4. **Profiling**: Measure and optimize bottlenecks
5. **Streaming**: Stream large outputs instead of loading all at once
6. **Memory Management**: Clear caches when switching binaries

## Implementation

### 1. Highlight Caching with LRU (3 hours)
**Location**: `caspoon/ui/syntax/highlighter.py`

Add caching to avoid re-highlighting the same instructions:

```python
from functools import lru_cache

class AsmHighlighter:
    def __init__(self, ...):
        # ... existing init ...
        self._cache_enabled = True
        self._cache_size = 1000
    
    @lru_cache(maxsize=1000)
    def _highlight_instruction_cached(self, opcode: str, address: str) -> str:
        """Cached version that returns string representation."""
        text = self.highlight_instruction(opcode, address)
        return text.__rich__()  # Convert to string for caching
    
    def highlight_instruction(self, opcode: str, address: str = "") -> Text:
        """Main method - uses cache if enabled."""
        if self._cache_enabled:
            cached = self._highlight_instruction_cached(opcode, address)
            return Text.from_markup(cached)
        else:
            return self._highlight_instruction_impl(opcode, address)
    
    def clear_cache(self):
        """Clear highlight cache (call when switching binaries)."""
        self._highlight_instruction_cached.cache_clear()
```

### 2. Lazy/Paginated Disassembly View (4 hours)
**Location**: `caspoon/ui/views/r2_view.py` and/or new `lazy_disasm_view.py`

Implement pagination for large functions:

```python
class PaginatedDisasmView(InteractiveView):
    """Disassembly view with pagination support."""
    
    def __init__(self):
        super().__init__()
        self.page_size = 100  # instructions per page
        self.current_page = 0
        self.total_instructions = 0
    
    def render_page(self, page: int):
        """Render only the requested page of instructions."""
        start_idx = page * self.page_size
        end_idx = start_idx + self.page_size
        
        instructions = self.all_instructions[start_idx:end_idx]
        
        # Highlight only visible instructions
        highlighted = [
            self._highlighter.highlight_instruction(instr.opcode, instr.address)
            for instr in instructions
        ]
        
        self.update(highlighted)
    
    def on_key(self, event):
        """Handle pagination keys."""
        if event.key == "page_down":
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self.render_page(self.current_page)
        elif event.key == "page_up":
            if self.current_page > 0:
                self.current_page -= 1
                self.render_page(self.current_page)
```

### 3. Streaming Analysis Results (3 hours)
**Location**: `caspoon/ui/workers/analysis_worker.py`

Stream results as they're produced:

```python
async def analyze_with_streaming(self, path: str):
    """Analyze binary and stream results progressively."""
    # Start analysis
    report = await self.start_analysis(path)
    
    # Stream functions as they're discovered
    async for function in self.iter_functions():
        self.post_message(FunctionDiscovered(function))
        await asyncio.sleep(0)  # Yield control
    
    # Stream disassembly as it's generated
    async for instruction in self.iter_instructions(function):
        self.post_message(InstructionReady(instruction))
        await asyncio.sleep(0)
```

### 4. Memory Management (2 hours)
**Location**: `caspoon/ui/core/state.py`

Add cache management to AppState:

```python
class AppState:
    # ... existing code ...
    
    def clear_caches(self):
        """Clear all caches when switching binaries."""
        # Clear highlight cache
        if hasattr(self, '_highlighter'):
            self._highlighter.clear_cache()
        
        # Clear xref cache
        self.xref_cache.clear()
        
        # Clear navigation history
        self.navigation_history = []
        self.current_nav_index = -1
    
    def on_report_changed(self):
        """Called when executable report changes."""
        self.clear_caches()
```

### 5. Performance Profiling (2 hours)
**Location**: Create `scripts/profile_highlighting.py`

Measure actual performance:

```python
import time
from caspoon.ui.syntax import AsmHighlighter

def profile_highlighting():
    """Profile highlighting performance."""
    highlighter = AsmHighlighter()
    
    # Load test instructions
    test_instructions = load_test_data(1000)
    
    start = time.perf_counter()
    for instr in test_instructions:
        highlighted = highlighter.highlight_instruction(instr)
    elapsed = time.perf_counter() - start
    
    print(f"Highlighted 1000 instructions in {elapsed*1000:.2f}ms")
    print(f"Average: {elapsed/len(test_instructions)*1000:.2f}ms per instruction")
    
    assert elapsed < 0.1, f"Performance target not met: {elapsed:.2f}s > 0.1s"
```

### 6. Optimization Passes (2 hours)
Based on profiling results, optimize bottlenecks:

- **Regex Compilation**: Pre-compile all regex patterns
- **String Operations**: Minimize string concatenation
- **Rich Text Objects**: Reuse Text objects where possible
- **Operand Parsing**: Cache parsed operands
        self.viewport_size = 100  # lines visible at once
        self.buffer_size = 200    # lines to keep in memory
    
    def load_range(self, start_line: int, end_line: int):
        """Load and render only the visible range."""
        if (start_line, end_line) in self.cache:
            return self.cache[(start_line, end_line)]
        
        # Fetch from backend
        lines = self.fetch_disasm_lines(start_line, end_line)
        highlighted = [self.highlighter.highlight(line) for line in lines]
        
        self.cache[(start_line, end_line)] = highlighted
        return highlighted
```

## Implementation Steps

1. **Add highlight caching** (3 hours)
   - Implement LRU cache in AsmHighlighter
   - Add cache_clear() method
   - Test cache effectiveness

2. **Implement pagination** (4 hours)
   - Add pagination support to R2View or create PaginatedDisasmView
   - Add page navigation (PgUp/PgDn keys)
   - Display page indicators

3. **Add streaming support** (3 hours)
   - Modify analysis worker to stream results
   - Update views to handle streaming data
   - Test with large binaries

4. **Memory management** (2 hours)
   - Add cache clearing to AppState
   - Clear caches on binary switch
   - Monitor memory usage

5. **Performance profiling** (2 hours)
   - Create profiling script
   - Measure highlighting performance
   - Identify bottlenecks

6. **Optimization passes** (2 hours)
   - Optimize identified bottlenecks
   - Pre-compile regex patterns
   - Minimize object creation

7. **Testing** (2 hours)
   - Benchmark with large binaries
   - Test memory usage
   - Verify smooth UI experience

## Estimated Time
**18 hours total** → **16 hours revised** (async workers already done)
- Highlight caching: 3 hours
- Pagination: 4 hours
- Streaming: 3 hours (was background processing)
- Memory management: 2 hours
- Profiling: 2 hours
- Optimization: 2 hours

**NOTE**: Some work overlaps with existing limits (MAX_DISASM_OPS, etc.). Focus on caching, pagination, and profiling.

## Success Criteria
- [x] UI remains responsive during analysis (async workers)
- [ ] Large binaries (10MB+) load without freezing UI
- [ ] Highlighting 1000 instructions takes <100ms
- [ ] Scrolling is smooth with paginated disassembly
- [ ] Memory usage is reasonable (<500MB for large binaries)
- [ ] Cache size is bounded and manageable
- [ ] Switching binaries clears caches properly

## Integration with Existing Infrastructure

### Already Available from Plan 4
✅ **Async Workers**: Non-blocking analysis execution  
✅ **Progress Reporting**: Shows progress during analysis  
✅ **Cancellation**: Can cancel long-running operations  
✅ **Reactive Updates**: Efficient re-rendering

### New Optimizations Needed
⏸️ Highlight caching with LRU  
⏸️ Pagination for large disassembly  
⏸️ Streaming results (optional enhancement)  
⏸️ Memory management and cache clearing  
⏸️ Performance profiling and benchmarks

## Next Steps
After all subtasks (1-6) complete:
1. Integration testing across all features
2. Documentation updates
3. User guide for navigation features
4. Performance tuning based on real-world usage
