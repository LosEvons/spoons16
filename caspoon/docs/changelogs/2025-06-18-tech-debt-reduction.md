# Tech Debt Reduction - TUI Removal & Complexity Reduction

**Date**: 2025-06-18
**Type**: Breaking Change / Cleanup

## Summary

Major technical debt reduction focusing on removing the Textual TUI, consolidating agent definitions, and simplifying the dependency surface.

## Changes

### Removed
- **Textual TUI** (`caspoon/ui/`): Entire TUI implementation, tests, and documentation deleted
- `--ui` CLI flag removed
- `textual` removed from core dependencies
- TUI-specific test fixtures and verification scripts removed
- TUI documentation and redesign plans removed

### Changed
- `_check_dependencies()` in `main.py` now only checks truly required deps (pyelftools, rich)
- `Radare2Backend.is_available()` now uses `shutil.which` instead of opening r2pipe sessions
- Agent definitions consolidated: shared rules moved to `copilot-instructions.md`, agent files trimmed to domain-specific guidance
- All documentation updated to remove TUI references

### Kept
- CLI/JSON analysis mode (primary interface)
- PySide6 Qt GUI (`--gui` flag)
- Core analysis pipeline (ReconRunner, recon modules)
- Radare2 backend integration (as optional dependency)

## Migration

Users who relied on `--ui` should use `--gui` for the Qt interface or the CLI for JSON output.
