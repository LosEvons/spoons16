# Subtask 5: UI Integration

## Objective
Display syscall and API analysis results in the UI with filtering and categorization.

## Implementation

### API Detection Recon Module (3 hours)
**Location**: `caspoon/recon/api_detection.py`

```python
class APIDetectionRecon:
    name = "api_detection"
    
    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        # Get r2 data
        r2_data = report.raw_backend_data.get('r2', {})
        functions = r2_data.get('functions', [])
        imports = r2_data.get('imports', [])
        
        # Detect syscalls
        syscall_detector = SyscallDetector()
        syscalls = syscall_detector.detect_syscalls(
            r2_data.get('main_ops', []),
            report.arch
        )
        
        # Analyze API imports
        api_db = APIDatabase()
        api_calls = []
        for imp in imports:
            imp_name = imp.get('name', '')
            api_info = api_db.lookup(imp_name, self._detect_os(report))
            if api_info:
                api_calls.append(APICallInfo(
                    name=imp_name,
                    library=api_info['library'],
                    category=api_info['category'],
                    risk_level=api_info['risk_level'],
                    description=api_info['description'],
                    addresses=[]
                ))
        
        # Security analysis
        analyzer = SecurityAnalyzer()
        findings = analyzer.analyze_api_usage(api_calls)
        
        # Store results
        report.raw_backend_data['api_analysis'] = {
            'syscalls': [s.__dict__ for s in syscalls],
            'api_calls': [a.__dict__ for a in api_calls],
            'security_findings': [f.__dict__ for f in findings],
            'statistics': generate_api_statistics(api_calls),
            'capabilities': assess_capabilities(api_calls)
        }
        
        return report
```

### API View Widget (5 hours)
**Location**: `caspoon/ui/views/api_view.py`

```python
class APIView(Static):
    def update_data(self, report: ExecutableReport) -> None:
        api_data = report.raw_backend_data.get('api_analysis', {})
        
        if not api_data:
            self.update("No API analysis available.")
            return
        
        parts = []
        
        # Statistics summary
        stats = api_data.get('statistics', {})
        stats_table = self._create_stats_table(stats)
        parts.append(stats_table)
        
        # Capabilities
        capabilities = api_data.get('capabilities', [])
        if capabilities:
            parts.append(Text("\nDetected Capabilities:", style="bold cyan"))
            for cap in capabilities:
                parts.append(Text(f"  • {cap.replace('_', ' ').title()}"))
        
        # Security findings
        findings = api_data.get('security_findings', [])
        if findings:
            findings_table = self._create_findings_table(findings)
            parts.append(Text("\nSecurity Findings:", style="bold red"))
            parts.append(findings_table)
        
        # API calls by category
        api_calls = api_data.get('api_calls', [])
        by_category = self._group_by_category(api_calls)
        
        for category, apis in by_category.items():
            parts.append(Text(f"\n{category.title()} APIs:", style="bold"))
            api_table = Table()
            api_table.add_column("API Name")
            api_table.add_column("Library")
            api_table.add_column("Risk")
            api_table.add_column("Description")
            
            for api in apis:
                risk_style = self._get_risk_style(api['risk_level'])
                api_table.add_row(
                    api['name'],
                    api['library'],
                    f"[{risk_style}]{api['risk_level']}[/]",
                    api['description'][:50] + "..." if len(api['description']) > 50 
                        else api['description']
                )
            
            parts.append(api_table)
        
        # Syscalls
        syscalls = api_data.get('syscalls', [])
        if syscalls:
            parts.append(Text("\nDirect System Calls:", style="bold magenta"))
            syscall_table = self._create_syscall_table(syscalls)
            parts.append(syscall_table)
        
        self.update(Group(*parts))
    
    def _get_risk_style(self, risk_level: str) -> str:
        return {
            'low': 'green',
            'medium': 'yellow',
            'high': 'red'
        }.get(risk_level, 'white')
```

### Add to UI App (1 hour)
Update `caspoon/ui/app.py`:
```python
with TabPane("API / Syscalls"):
    with ScrollableContainer():
        yield APIView(id="api_view")
```

### Register in Runner (1 hour)
Add to recon pipeline in `core/runner.py`.

## Estimated Time: 10 hours

## Success Criteria
- [ ] API detection runs in analysis pipeline
- [ ] APIs are displayed grouped by category
- [ ] Security findings are prominently shown
- [ ] Syscalls are listed separately
- [ ] Risk levels are color-coded
- [ ] Statistics provide quick overview
- [ ] Capabilities are clearly listed
