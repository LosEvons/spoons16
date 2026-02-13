# Subtask 2: API Database

## Objective
Build comprehensive databases of Windows and POSIX APIs with categorization and risk assessment.

## Implementation

### Windows API Database (4 hours)
**Location**: `caspoon/api/windows_api.py`

```python
WINDOWS_API_DB = {
    # File Operations
    'CreateFileA': {
        'category': 'file',
        'library': 'kernel32.dll',
        'risk_level': 'medium',
        'description': 'Creates or opens a file',
        'tags': ['file', 'io']
    },
    'ReadFile': {
        'category': 'file',
        'library': 'kernel32.dll',
        'risk_level': 'low',
        'description': 'Reads data from file',
        'tags': ['file', 'io', 'read']
    },
    'WriteFile': {
        'category': 'file',
        'library': 'kernel32.dll',
        'risk_level': 'medium',
        'description': 'Writes data to file',
        'tags': ['file', 'io', 'write']
    },
    
    # Process Operations
    'CreateProcessA': {
        'category': 'process',
        'library': 'kernel32.dll',
        'risk_level': 'high',
        'description': 'Creates a new process',
        'tags': ['process', 'execution']
    },
    'OpenProcess': {
        'category': 'process',
        'library': 'kernel32.dll',
        'risk_level': 'high',
        'description': 'Opens existing process',
        'tags': ['process', 'injection']
    },
    
    # Memory Operations
    'VirtualAlloc': {
        'category': 'memory',
        'library': 'kernel32.dll',
        'risk_level': 'medium',
        'description': 'Allocates memory',
        'tags': ['memory', 'allocation']
    },
    'VirtualProtect': {
        'category': 'memory',
        'library': 'kernel32.dll',
        'risk_level': 'high',
        'description': 'Changes memory protection',
        'tags': ['memory', 'protection', 'injection']
    },
    
    # Network Operations
    'WSAStartup': {
        'category': 'network',
        'library': 'ws2_32.dll',
        'risk_level': 'low',
        'description': 'Initializes Winsock',
        'tags': ['network', 'init']
    },
    'connect': {
        'category': 'network',
        'library': 'ws2_32.dll',
        'risk_level': 'medium',
        'description': 'Connects to remote socket',
        'tags': ['network', 'connection']
    },
    
    # Registry Operations
    'RegOpenKeyExA': {
        'category': 'registry',
        'library': 'advapi32.dll',
        'risk_level': 'medium',
        'description': 'Opens registry key',
        'tags': ['registry', 'read']
    },
    'RegSetValueExA': {
        'category': 'registry',
        'library': 'advapi32.dll',
        'risk_level': 'high',
        'description': 'Sets registry value',
        'tags': ['registry', 'write', 'persistence']
    },
}
```

### POSIX API Database (3 hours)
**Location**: `caspoon/api/posix_api.py`

```python
POSIX_API_DB = {
    'open': {
        'category': 'file',
        'library': 'libc',
        'risk_level': 'medium',
        'description': 'Opens file',
        'tags': ['file', 'io']
    },
    'socket': {
        'category': 'network',
        'library': 'libc',
        'risk_level': 'medium',
        'description': 'Creates socket',
        'tags': ['network', 'socket']
    },
    'fork': {
        'category': 'process',
        'library': 'libc',
        'risk_level': 'medium',
        'description': 'Forks process',
        'tags': ['process', 'fork']
    },
    'execve': {
        'category': 'process',
        'library': 'libc',
        'risk_level': 'high',
        'description': 'Executes program',
        'tags': ['process', 'execution']
    },
    'ptrace': {
        'category': 'debug',
        'library': 'libc',
        'risk_level': 'high',
        'description': 'Process trace (debugging)',
        'tags': ['debug', 'anti-analysis']
    },
}
```

### Database Query Interface (2 hours)
```python
class APIDatabase:
    def __init__(self):
        self.windows_db = WINDOWS_API_DB
        self.posix_db = POSIX_API_DB
    
    def lookup(self, api_name: str, os_type: str) -> Optional[Dict]:
        """Look up API information."""
        db = self.windows_db if os_type == 'windows' else self.posix_db
        return db.get(api_name)
    
    def search_by_category(self, category: str, os_type: str) -> List[str]:
        """Find all APIs in a category."""
        db = self.windows_db if os_type == 'windows' else self.posix_db
        return [name for name, info in db.items() 
                if info['category'] == category]
```

## Estimated Time: 9 hours

## Success Criteria
- [ ] Database covers 100+ common Windows APIs
- [ ] Database covers 50+ POSIX APIs
- [ ] Each API has category and risk level
- [ ] Query interface is efficient
- [ ] Database is easily extensible
