# Subtask 1: Pattern Matching Engine

## Objective
Build a flexible pattern matching engine that can detect various code and data patterns in binaries.

## Implementation

### Core Engine (4 hours)
**Location**: `caspoon/patterns/engine.py`

```python
class PatternMatcher:
    def __init__(self):
        self.patterns = []
        self.confidence_threshold = 0.5
    
    def register_pattern(self, pattern: Pattern):
        """Register a pattern detector."""
        self.patterns.append(pattern)
    
    def search_binary(self, data: bytes, report: ExecutableReport) -> List[PatternMatch]:
        """Search for all registered patterns."""
        matches = []
        for pattern in self.patterns:
            results = pattern.match(data, report)
            matches.extend(results)
        return matches
```

### Pattern Base Class (2 hours)
```python
class Pattern(ABC):
    name: str
    category: str
    
    @abstractmethod
    def match(self, data: bytes, report: ExecutableReport) -> List[PatternMatch]:
        """Search for pattern and return matches."""
        pass
```

### Byte Pattern Matcher (3 hours)
Support for byte sequence patterns:
```python
class BytePattern(Pattern):
    def __init__(self, name: str, signature: bytes, category: str):
        self.name = name
        self.signature = signature
        self.category = category
    
    def match(self, data: bytes, report: ExecutableReport):
        matches = []
        offset = 0
        while True:
            pos = data.find(self.signature, offset)
            if pos == -1:
                break
            matches.append(PatternMatch(
                pattern_name=self.name,
                category=self.category,
                confidence=1.0,
                address=pos,
                description=f"Found {self.name} at offset {hex(pos)}"
            ))
            offset = pos + 1
        return matches
```

### Regex Pattern Matcher (2 hours)
Support for regex-based patterns.

## Estimated Time: 11 hours

## Success Criteria
- [ ] Pattern engine can register and execute multiple patterns
- [ ] Byte sequence matching works correctly
- [ ] Regex matching is supported
- [ ] Confidence scoring is implemented
- [ ] Performance is acceptable (<2 seconds for typical binary)
