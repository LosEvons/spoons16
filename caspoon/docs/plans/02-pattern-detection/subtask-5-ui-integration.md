# Subtask 5: UI Integration

## Objective
Display detected patterns in the UI and integrate with the analysis pipeline.

## Implementation

### Pattern Recon Module (3 hours)
**Location**: `caspoon/recon/pattern_detection.py`

```python
class PatternDetectionRecon:
    name = "pattern_detection"
    
    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        # Load binary data
        with open(path, 'rb') as f:
            data = f.read()
        
        # Run pattern matching
        matcher = PatternMatcher()
        # Register all patterns
        matcher.register_pattern(AESPattern())
        matcher.register_pattern(AntiDebugPattern())
        # ... more patterns
        
        matches = matcher.search_binary(data, report)
        
        # Store in report
        report.raw_backend_data['patterns'] = {
            'matches': [m.__dict__ for m in matches],
            'summary': self._generate_summary(matches)
        }
        
        return report
```

### Patterns View Widget (4 hours)
**Location**: `caspoon/ui/views/patterns_view.py`

```python
class PatternsView(Static):
    def update_data(self, report: ExecutableReport) -> None:
        pattern_data = report.raw_backend_data.get('patterns', {})
        matches = pattern_data.get('matches', [])
        
        if not matches:
            self.update("No patterns detected.")
            return
        
        # Group by category
        by_category = self._group_by_category(matches)
        
        # Create tables for each category
        parts = []
        for category, items in by_category.items():
            table = Table(title=category.title())
            table.add_column("Pattern")
            table.add_column("Address")
            table.add_column("Confidence")
            table.add_column("Severity")
            
            for match in items:
                conf_style = self._get_confidence_style(match['confidence'])
                sev_style = self._get_severity_style(match['severity'])
                
                table.add_row(
                    match['pattern_name'],
                    hex(match['address']) if match['address'] else 'N/A',
                    f"[{conf_style}]{match['confidence']:.0%}[/]",
                    f"[{sev_style}]{match['severity']}[/]"
                )
            
            parts.append(table)
        
        self.update(Group(*parts))
```

### Add to UI App (2 hours)
Update `caspoon/ui/app.py`:
```python
with TabPane("Pattern Detection"):
    with ScrollableContainer():
        yield PatternsView(id="patterns_view")
```

### Register in Runner (1 hour)
Add pattern detection to recon pipeline in `core/runner.py`.

## Estimated Time: 10 hours

## Success Criteria
- [ ] Pattern detection runs in analysis pipeline
- [ ] Detected patterns are displayed in dedicated tab
- [ ] Patterns are grouped by category
- [ ] Color coding indicates severity/confidence
- [ ] UI provides useful forensic information
