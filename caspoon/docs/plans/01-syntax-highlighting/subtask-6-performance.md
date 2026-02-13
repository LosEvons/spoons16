# Subtask 6: Performance Optimization

## Objective
Optimize syntax highlighting and rendering for large binaries without UI slowdown.

## Scope
- Lazy loading of disassembly
- Pagination for large outputs
- Caching of highlighted content
- Efficient rendering strategies

## Performance Targets
- Highlight 1000 instructions in <100ms
- Smooth scrolling with 10,000+ line disassembly
- UI remains responsive during analysis
- Memory usage scales reasonably with binary size

## Implementation

### 1. Lazy Loading (4 hours)
**Location**: `caspoon/ui/widgets/lazy_disasm.py`

Load disassembly on-demand:
```python
class LazyDisasmView(Static):
    def __init__(self):
        self.cache = {}
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

### 2. Pagination (3 hours)
Implement pagination for function lists and disassembly:
- Page size: 50-100 instructions
- Previous/Next navigation
- Jump to page functionality

### 3. Caching Strategy (3 hours)
**Location**: `caspoon/ui/cache/highlight_cache.py`

```python
from functools import lru_cache

class HighlightCache:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self._cache = {}
    
    @lru_cache(maxsize=1000)
    def get_highlighted(self, instruction: str) -> Text:
        """Get cached highlighted instruction."""
        return self.highlighter.highlight(instruction)
```

### 4. Efficient Rendering (3 hours)
Optimize Rich Text object creation:
- Reuse Text objects where possible
- Batch rendering operations
- Minimize style changes

### 5. Background Processing (3 hours)
Use async operations for heavy analysis:
```python
async def analyze_in_background(self, path: str):
    """Analyze binary asynchronously."""
    # Run analysis in thread pool
    report = await asyncio.to_thread(self.runner.run, path)
    self.display_report(report)
```

### 6. Memory Management (2 hours)
Implement limits and cleanup:
- Clear old cache entries
- Limit total cached content
- Release resources when switching binaries

## Testing Strategy

### Performance Benchmarks
Create benchmarks in `tests/performance/`:
```python
def benchmark_highlight_1000_instructions():
    highlighter = AsmHighlighter()
    instructions = load_test_instructions(1000)
    
    start = time.time()
    for instr in instructions:
        highlighter.highlight(instr)
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # < 100ms for 1000 instructions
```

### Load Testing
- Test with 10MB+ binaries
- Test with 1000+ functions
- Monitor memory usage
- Profile rendering performance

### Stress Testing
- Rapid navigation between functions
- Scrolling through large disassembly
- Switching between multiple binaries

## Optimization Strategies

### Strategy 1: Incremental Rendering
Render only visible portion of content.

### Strategy 2: Memoization
Cache classification results for instructions.

### Strategy 3: Batch Operations
Process multiple instructions at once.

### Strategy 4: Async Loading
Load data asynchronously to keep UI responsive.

## Monitoring

Add performance metrics:
```python
import time

class PerformanceMonitor:
    def measure_highlight_time(func):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        logger.debug(f"Highlighting took {elapsed*1000:.2f}ms")
        return result
```

## Estimated Time
**18 hours total**
- Lazy loading: 4 hours
- Pagination: 3 hours
- Caching: 3 hours
- Efficient rendering: 3 hours
- Background processing: 3 hours
- Memory management: 2 hours

## Success Criteria
- [ ] Large binaries (10MB+) load without freezing UI
- [ ] Highlighting 1000 instructions takes <100ms
- [ ] Scrolling is smooth with 10,000+ lines
- [ ] Memory usage is reasonable (<500MB for large binaries)
- [ ] UI remains responsive during analysis
- [ ] Cache size is bounded and manageable

## Trade-offs

### Completeness vs. Speed
Show partial results quickly rather than waiting for complete analysis.

### Memory vs. Speed
Cache more for speed, but manage memory carefully.

### Accuracy vs. Performance
May need to simplify some highlighting rules for performance.

## Next Steps
After all subtasks complete, integration testing and documentation updates.
