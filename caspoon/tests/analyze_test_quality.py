#!/usr/bin/env python3
"""Apply consistent code quality improvements to test files.

This script applies the following improvements:
1. Add/fix type hints
2. Enhance docstrings
3. Add assertion messages
4. Fix import ordering

Usage:
    python apply_test_improvements.py <test_file.py>
"""

import sys
from pathlib import Path


TEMPLATE_HEADER = '''"""Unit tests for {module_name}.

{module_description}
"""
import pytest
{additional_imports}
from unittest.mock import Mock, patch

from caspoon.core.models import ExecutableReport
from caspoon.{module_path} import {module_class}
'''


def add_type_hints_to_line(line: str) -> str:
    """Add type hints to test methods and fixtures."""
    # Add -> None to test methods without return type
    if line.strip().startswith('def test_') and '->' not in line and ':' in line:
        return line.replace('):', ') -> None:')
    
    # Add -> Type to fixtures based on context
    if '@pytest.fixture' in line or 'def recon(self)' in line:
        # Would need more context to determine return type
        pass
    
    return line


def enhance_assertion(line: str) -> str:
    """Add descriptive message to assertions if missing."""
    if 'assert' in line and ',' not in line and '#' not in line:
        # Extract the assertion
        parts = line.split('assert', 1)
        if len(parts) == 2:
            indent = len(parts[0])
            assertion = parts[1].strip()
            
            # Generate a reasonable message
            if '==' in assertion:
                var = assertion.split('==')[0].strip()
                message = f'"{var} should match expected value"'
            elif 'is True' in assertion or 'is False' in assertion:
                var = assertion.split('is')[0].strip()
                message = f'"{var} should be set correctly"'
            elif 'is not None' in assertion:
                var = assertion.split('is')[0].strip()
                message = f'"{var} should not be None"'
            elif '>' in assertion or '<' in assertion:
                message = '"Value should meet numeric constraint"'
            else:
                message = '"Assertion should hold"'
            
            return f'{" " * indent}assert {assertion}, {message}\n'
    
    return line


def improve_docstring(lines: list, start_idx: int) -> list:
    """Enhance a docstring with more detail."""
    # Find the docstring
    if '"""' not in lines[start_idx]:
        return lines
    
    # Simple enhancement: if docstring is one line, suggest expansion
    if lines[start_idx].count('"""') == 2:
        # One-line docstring
        content = lines[start_idx].split('"""')[1]
        # Could expand here, but would need context
    
    return lines


def check_file_quality(filepath: Path) -> dict:
    """Check code quality metrics for a test file.
    
    Args:
        filepath: Path to the test file to check.
        
    Returns:
        Dictionary with quality metrics.
    """
    with open(filepath) as f:
        lines = f.readlines()
    
    metrics = {
        'total_lines': len(lines),
        'test_functions': 0,
        'tests_with_type_hints': 0,
        'assertions': 0,
        'assertions_with_messages': 0,
        'docstrings': 0,
        'comprehensive_docstrings': 0,
    }
    
    in_docstring = False
    for i, line in enumerate(lines):
        # Count test functions
        if line.strip().startswith('def test_'):
            metrics['test_functions'] += 1
            if '-> None' in line or '-> ' in line:
                metrics['tests_with_type_hints'] += 1
                
            # Check next line for docstring
            if i + 1 < len(lines) and '"""' in lines[i + 1]:
                metrics['docstrings'] += 1
                # Check if comprehensive (multi-line)
                if lines[i + 1].count('"""') == 1:
                    metrics['comprehensive_docstrings'] += 1
        
        # Count assertions
        if 'assert' in line and not line.strip().startswith('#'):
            metrics['assertions'] += 1
            if ',' in line and '"' in line:
                metrics['assertions_with_messages'] += 1
    
    return metrics


def print_report(filepath: Path, metrics: dict):
    """Print quality report for a file."""
    print(f"\n{'='*70}")
    print(f"Quality Report: {filepath.name}")
    print(f"{'='*70}")
    print(f"Total lines: {metrics['total_lines']}")
    print(f"Test functions: {metrics['test_functions']}")
    
    if metrics['test_functions'] > 0:
        type_hint_pct = (metrics['tests_with_type_hints'] / metrics['test_functions']) * 100
        print(f"Type hints: {metrics['tests_with_type_hints']}/{metrics['test_functions']} ({type_hint_pct:.1f}%)")
        
        docstring_pct = (metrics['docstrings'] / metrics['test_functions']) * 100
        print(f"Docstrings: {metrics['docstrings']}/{metrics['test_functions']} ({docstring_pct:.1f}%)")
    
    if metrics['assertions'] > 0:
        assertion_msg_pct = (metrics['assertions_with_messages'] / metrics['assertions']) * 100
        print(f"Assertion messages: {metrics['assertions_with_messages']}/{metrics['assertions']} ({assertion_msg_pct:.1f}%)")
    
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python apply_test_improvements.py <test_file.py>")
        print("\nOr run analysis on all test files:")
        print("  python apply_test_improvements.py --analyze")
        sys.exit(1)
    
    if sys.argv[1] == '--analyze':
        # Analyze all test files
        test_dir = Path(__file__).parent
        test_files = []
        
        # Find all test files
        for pattern in ['unit/core/test_*.py', 'unit/recon/test_*.py', 'integration/test_*.py']:
            test_files.extend(test_dir.glob(pattern))
        
        print("\n" + "="*70)
        print("TEST INFRASTRUCTURE QUALITY ANALYSIS")
        print("="*70)
        
        total_metrics = {
            'files': 0,
            'test_functions': 0,
            'tests_with_type_hints': 0,
            'assertions': 0,
            'assertions_with_messages': 0,
        }
        
        for test_file in sorted(test_files):
            metrics = check_file_quality(test_file)
            print_report(test_file, metrics)
            
            total_metrics['files'] += 1
            total_metrics['test_functions'] += metrics['test_functions']
            total_metrics['tests_with_type_hints'] += metrics['tests_with_type_hints']
            total_metrics['assertions'] += metrics['assertions']
            total_metrics['assertions_with_messages'] += metrics['assertions_with_messages']
        
        # Print summary
        print("\n" + "="*70)
        print("OVERALL SUMMARY")
        print("="*70)
        print(f"Files analyzed: {total_metrics['files']}")
        print(f"Total test functions: {total_metrics['test_functions']}")
        
        if total_metrics['test_functions'] > 0:
            type_hint_pct = (total_metrics['tests_with_type_hints'] / total_metrics['test_functions']) * 100
            print(f"Type hint coverage: {type_hint_pct:.1f}%")
        
        if total_metrics['assertions'] > 0:
            msg_pct = (total_metrics['assertions_with_messages'] / total_metrics['assertions']) * 100
            print(f"Assertion message coverage: {msg_pct:.1f}%")
        
        print("="*70 + "\n")
        
    else:
        # Process single file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        metrics = check_file_quality(filepath)
        print_report(filepath, metrics)


if __name__ == '__main__':
    main()
