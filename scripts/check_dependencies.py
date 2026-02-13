#!/usr/bin/env python3
"""
Dependency Management Helper Script

This script helps maintain the project's dependencies by:
1. Checking for outdated packages
2. Running security audits
3. Generating dependency reports
4. Validating version constraints

Usage:
    python scripts/check_dependencies.py [--check-outdated] [--security-audit] [--all]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=Path(__file__).parent.parent / "caspoon"
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return e


def check_outdated() -> bool:
    """Check for outdated packages."""
    print("🔍 Checking for outdated packages...")
    print("=" * 60)
    
    result = run_command(
        ["pip", "list", "--outdated", "--format=json"],
        check=False
    )
    
    if result.returncode != 0:
        print("❌ Failed to check for outdated packages")
        return False
    
    try:
        outdated = json.loads(result.stdout)
        if not outdated:
            print("✅ All packages are up to date!")
            return True
        
        print(f"📦 Found {len(outdated)} outdated package(s):\n")
        
        for pkg in outdated:
            name = pkg['name']
            current = pkg['version']
            latest = pkg['latest_version']
            pkg_type = pkg.get('latest_filetype', 'unknown')
            
            print(f"  • {name}")
            print(f"    Current: {current}")
            print(f"    Latest:  {latest}")
            print(f"    Type:    {pkg_type}")
            print()
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Failed to parse outdated packages output")
        return False


def security_audit() -> bool:
    """Run security audit using pip-audit."""
    print("🔒 Running security audit...")
    print("=" * 60)
    
    # Check if pip-audit is installed
    check_result = run_command(["pip", "show", "pip-audit"], check=False)
    if check_result.returncode != 0:
        print("⚠️  pip-audit not installed. Installing...")
        install_result = run_command(["pip", "install", "pip-audit"], check=False)
        if install_result.returncode != 0:
            print("❌ Failed to install pip-audit")
            return False
    
    # Run audit on core dependencies
    print("\n📋 Auditing core dependencies...")
    core_result = run_command(
        ["pip-audit", "--requirement", "requirements.txt", "--desc"],
        check=False
    )
    
    # Run audit on dev dependencies
    print("\n📋 Auditing dev dependencies...")
    dev_result = run_command(
        ["pip-audit", "--requirement", "requirements-dev.txt", "--desc"],
        check=False
    )
    
    if core_result.returncode == 0 and dev_result.returncode == 0:
        print("\n✅ No security vulnerabilities found!")
        return True
    else:
        print("\n⚠️  Security vulnerabilities detected!")
        print("Please review the output above and update affected packages.")
        return False


def check_conflicts() -> bool:
    """Check for dependency conflicts."""
    print("🔍 Checking for dependency conflicts...")
    print("=" * 60)
    
    result = run_command(["pip", "check"], check=False)
    
    if result.returncode == 0:
        print("✅ No dependency conflicts found!")
        return True
    else:
        print("❌ Dependency conflicts detected:")
        print(result.stdout)
        return False


def generate_report() -> bool:
    """Generate dependency report."""
    print("📊 Generating dependency report...")
    print("=" * 60)
    
    # Check if pipdeptree is installed
    check_result = run_command(["pip", "show", "pipdeptree"], check=False)
    if check_result.returncode != 0:
        print("⚠️  pipdeptree not installed. Installing...")
        install_result = run_command(["pip", "install", "pipdeptree"], check=False)
        if install_result.returncode != 0:
            print("❌ Failed to install pipdeptree")
            return False
    
    # Generate dependency tree
    result = run_command(["pipdeptree", "--warn", "silence"], check=False)
    
    if result.returncode == 0:
        print("\n📦 Dependency Tree:")
        print(result.stdout)
        return True
    else:
        print("❌ Failed to generate dependency tree")
        return False


def list_installed() -> bool:
    """List installed packages."""
    print("📋 Installed packages...")
    print("=" * 60)
    
    result = run_command(["pip", "list", "--format=columns"], check=False)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("❌ Failed to list installed packages")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Dependency Management Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/check_dependencies.py --all
  python scripts/check_dependencies.py --check-outdated --security-audit
  python scripts/check_dependencies.py --conflicts
        """
    )
    
    parser.add_argument(
        "--check-outdated",
        action="store_true",
        help="Check for outdated packages"
    )
    parser.add_argument(
        "--security-audit",
        action="store_true",
        help="Run security audit"
    )
    parser.add_argument(
        "--conflicts",
        action="store_true",
        help="Check for dependency conflicts"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate dependency report"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List installed packages"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks"
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 0
    
    # Track results
    results = {}
    
    print("\n" + "=" * 60)
    print("  🔧 CASPOON DEPENDENCY CHECKER")
    print("=" * 60 + "\n")
    
    # Run requested checks
    if args.all or args.conflicts:
        results['conflicts'] = check_conflicts()
        print()
    
    if args.all or args.check_outdated:
        results['outdated'] = check_outdated()
        print()
    
    if args.all or args.security_audit:
        results['security'] = security_audit()
        print()
    
    if args.all or args.report:
        results['report'] = generate_report()
        print()
    
    if args.list:
        results['list'] = list_installed()
        print()
    
    # Summary
    print("=" * 60)
    print("  📊 SUMMARY")
    print("=" * 60)
    
    failed = []
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check.capitalize()}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            failed.append(check)
    
    print("=" * 60)
    
    if failed:
        print(f"\n⚠️  {len(failed)} check(s) failed: {', '.join(failed)}")
        return 1
    else:
        print("\n✅ All checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
