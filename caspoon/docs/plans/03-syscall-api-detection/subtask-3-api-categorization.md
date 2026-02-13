# Subtask 3: API Categorization

## Objective
Categorize detected APIs and syscalls by functionality and security relevance.

## Implementation

### Categorization Engine (3 hours)
**Location**: `caspoon/api/categorizer.py`

```python
class APICategori categorizer:
    CATEGORIES = [
        'file',        # File I/O operations
        'network',     # Network operations
        'process',     # Process management
        'memory',      # Memory operations
        'registry',    # Windows registry
        'crypto',      # Cryptography
        'debug',       # Debugging/tracing
        'system',      # System information
        'ui',          # User interface
        'other'        # Uncategorized
    ]
    
    def categorize_api(self, api_name: str, api_info: Dict) -> str:
        """Categorize an API call."""
        if api_info:
            return api_info.get('category', 'other')
        
        # Fallback: heuristic categorization
        return self._heuristic_categorize(api_name)
    
    def _heuristic_categorize(self, api_name: str) -> str:
        """Categorize by name pattern."""
        name_lower = api_name.lower()
        
        if any(k in name_lower for k in ['file', 'read', 'write', 'open', 'close']):
            return 'file'
        elif any(k in name_lower for k in ['socket', 'send', 'recv', 'connect', 'bind']):
            return 'network'
        elif any(k in name_lower for k in ['process', 'thread', 'fork', 'exec']):
            return 'process'
        # ... more patterns
        
        return 'other'
```

### Risk Assessment (3 hours)
```python
class RiskAssessor:
    # High-risk APIs that could indicate malicious behavior
    HIGH_RISK_APIS = [
        'CreateRemoteThread', 'WriteProcessMemory', 'VirtualAllocEx',
        'SetWindowsHookEx', 'RegSetValueEx', 'WinExec', 'ShellExecute',
        'execve', 'system', 'ptrace', 'mprotect'
    ]
    
    MEDIUM_RISK_APIS = [
        'CreateProcess', 'OpenProcess', 'VirtualProtect', 'socket',
        'CreateFile', 'RegOpenKey', 'LoadLibrary'
    ]
    
    def assess_risk(self, api_name: str, context: Dict = None) -> str:
        """Assess risk level of API usage."""
        if api_name in self.HIGH_RISK_APIS:
            return 'high'
        elif api_name in self.MEDIUM_RISK_APIS:
            return 'medium'
        else:
            return 'low'
    
    def assess_combination_risk(self, apis: List[str]) -> List[str]:
        """Detect risky API combinations."""
        warnings = []
        
        # Process injection pattern
        if all(api in apis for api in ['VirtualAllocEx', 'WriteProcessMemory', 'CreateRemoteThread']):
            warnings.append("Process injection pattern detected")
        
        # Code injection pattern
        if 'VirtualProtect' in apis and 'WriteFile' in apis:
            warnings.append("Potential code injection")
        
        # Persistence pattern
        if any(reg in apis for reg in ['RegSetValueEx', 'RegCreateKeyEx']):
            if 'CreateFile' in apis or 'CreateProcess' in apis:
                warnings.append("Potential persistence mechanism")
        
        return warnings
```

### Statistics Generator (2 hours)
```python
def generate_api_statistics(api_calls: List[APICallInfo]) -> Dict:
    """Generate statistics about API usage."""
    stats = {
        'total_apis': len(api_calls),
        'by_category': {},
        'by_risk': {'low': 0, 'medium': 0, 'high': 0},
        'by_library': {},
        'unique_apis': len(set(api.name for api in api_calls))
    }
    
    for api in api_calls:
        # Category stats
        stats['by_category'][api.category] = \
            stats['by_category'].get(api.category, 0) + 1
        
        # Risk stats
        stats['by_risk'][api.risk_level] += 1
        
        # Library stats
        stats['by_library'][api.library] = \
            stats['by_library'].get(api.library, 0) + 1
    
    return stats
```

## Estimated Time: 8 hours

## Success Criteria
- [ ] All detected APIs are categorized
- [ ] Risk levels are assigned accurately
- [ ] Dangerous API combinations are detected
- [ ] Statistics provide useful insights
- [ ] Unknown APIs are handled gracefully
