# Subtask 4: Security Analysis

## Objective
Analyze API usage for security implications and suspicious patterns.

## Implementation

### Suspicious Pattern Detector (4 hours)
**Location**: `caspoon/api/security_analyzer.py`

```python
class SecurityAnalyzer:
    def analyze_api_usage(self, api_calls: List[APICallInfo]) -> List[SecurityFinding]:
        """Analyze APIs for security concerns."""
        findings = []
        
        # Check for process injection
        findings.extend(self._check_process_injection(api_calls))
        
        # Check for persistence mechanisms
        findings.extend(self._check_persistence(api_calls))
        
        # Check for anti-analysis
        findings.extend(self._check_anti_analysis(api_calls))
        
        # Check for data exfiltration
        findings.extend(self._check_exfiltration(api_calls))
        
        return findings
    
    def _check_process_injection(self, apis):
        """Detect process injection patterns."""
        api_names = [api.name for api in apis]
        
        # Classic injection
        if all(a in api_names for a in ['OpenProcess', 'VirtualAllocEx', 
                                          'WriteProcessMemory', 'CreateRemoteThread']):
            return [SecurityFinding(
                severity='high',
                category='process_injection',
                description='Classic process injection pattern detected',
                evidence=['OpenProcess', 'VirtualAllocEx', 'WriteProcessMemory', 
                         'CreateRemoteThread']
            )]
        
        return []
    
    def _check_persistence(self, apis):
        """Detect persistence mechanisms."""
        findings = []
        api_names = [api.name for api in apis]
        
        # Registry persistence
        if 'RegSetValueEx' in api_names:
            for api in apis:
                if api.name == 'RegSetValueEx':
                    findings.append(SecurityFinding(
                        severity='medium',
                        category='persistence',
                        description='Registry modification for potential persistence',
                        evidence=[f'RegSetValueEx at {hex(api.addresses[0]) if api.addresses else "unknown"}']
                    ))
        
        return findings
    
    def _check_anti_analysis(self, apis):
        """Detect anti-analysis techniques."""
        anti_analysis_apis = [
            'IsDebuggerPresent', 'CheckRemoteDebuggerPresent',
            'NtQueryInformationProcess', 'ptrace'
        ]
        
        findings = []
        for api in apis:
            if api.name in anti_analysis_apis:
                findings.append(SecurityFinding(
                    severity='high',
                    category='anti_analysis',
                    description=f'Anti-debugging API detected: {api.name}',
                    evidence=[api.name]
                ))
        
        return findings
```

### MITRE ATT&CK Mapping (3 hours)
```python
class MITREMapper:
    # Map APIs to MITRE ATT&CK techniques
    API_TO_MITRE = {
        'CreateRemoteThread': ['T1055.001'],  # Process Injection: DLL Injection
        'WriteProcessMemory': ['T1055'],      # Process Injection
        'RegSetValueEx': ['T1547.001'],       # Registry Run Keys
        'CreateProcess': ['T1106'],           # Native API
        'socket': ['T1071'],                  # Application Layer Protocol
    }
    
    def map_to_mitre(self, api_calls: List[APICallInfo]) -> Dict[str, List[str]]:
        """Map detected APIs to MITRE ATT&CK techniques."""
        techniques = {}
        
        for api in api_calls:
            if api.name in self.API_TO_MITRE:
                for technique in self.API_TO_MITRE[api.name]:
                    if technique not in techniques:
                        techniques[technique] = []
                    techniques[technique].append(api.name)
        
        return techniques
```

### Capability Assessment (2 hours)
```python
def assess_capabilities(api_calls: List[APICallInfo]) -> List[str]:
    """Determine binary capabilities based on API usage."""
    capabilities = set()
    
    categories = [api.category for api in api_calls]
    
    if 'network' in categories:
        capabilities.add('network_communication')
    if 'file' in categories:
        capabilities.add('file_operations')
    if 'process' in categories:
        capabilities.add('process_manipulation')
    if 'registry' in categories:
        capabilities.add('registry_access')
    if 'crypto' in categories:
        capabilities.add('cryptography')
    
    # More specific capabilities
    api_names = [api.name for api in api_calls]
    if any(a in api_names for a in ['CreateRemoteThread', 'WriteProcessMemory']):
        capabilities.add('code_injection')
    if 'ptrace' in api_names or 'IsDebuggerPresent' in api_names:
        capabilities.add('anti_debugging')
    
    return list(capabilities)
```

## Estimated Time: 9 hours

## Success Criteria
- [ ] Detects process injection patterns
- [ ] Identifies persistence mechanisms
- [ ] Flags anti-analysis techniques
- [ ] Maps APIs to MITRE ATT&CK
- [ ] Provides capability assessment
- [ ] Generates actionable security findings
