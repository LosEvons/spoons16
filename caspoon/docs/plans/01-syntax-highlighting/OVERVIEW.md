# Implementation Plan: Syntax Highlighting & Code Display Improvements

## Current Status

**Progress**: 5 of 6 subtasks complete (83%)  
**Last Updated**: 2026-02-17 (Subtask 6 complete)

### ✅ Completed Subtasks
1. **Subtask 1: Basic Highlighting** - ✅ COMPLETE (2026-02-13)
2. **Subtask 2: Instruction Classification** - ✅ COMPLETE (2026-02-13)
3. **Subtask 3: Architecture-Specific Schemes** - ✅ COMPLETE (2026-02-13)
4. **Subtask 4: Interactive Navigation** - ✅ COMPLETE (2026-02-17)
5. **Subtask 6: Performance Optimization** - ✅ COMPLETE (2026-02-17)

### ⏸️ Remaining Subtasks
5. **Subtask 5: Cross-Reference Display** - ⏸️ NOT STARTED (core xref functionality complete in #4, optional enhancements only)

### Key Changes Since Original Plan
- ✅ **Plan 4 (TUI Redesign) completed** - New reactive architecture with async workers
- ✅ **Command palette implemented** - Ctrl+P for keyboard-driven workflows
- ✅ **Multi-panel layout** - Sidebar, main view, details panel, console
- ✅ **InteractiveView base** - Built-in selection and keyboard navigation support
- ✅ **Async workers** - Non-blocking analysis with progress reporting
- ✅ **Performance optimization** - LRU caching, profiling, memory management

## Overview

This plan covers enhancements to the disassembly viewing experience in caspoon, focusing on syntax highlighting, interactive features, and improved code display. These improvements will make it easier for reverse engineers to understand and navigate disassembled code.

## Goals

1. Implement comprehensive syntax highlighting for assembly code
2. Add interactive navigation features for disassembly
3. Improve code readability through formatting and annotations
4. Support multiple architectures with appropriate highlighting schemes

## Architecture Impact

### Modified Components
- **UI Views**: ✅ Enhanced `ui/views/r2_view.py` with syntax highlighting and architecture detection
- **Backend**: ✅ Radare2 integration (`backends/r2_analyzer.py`) - xref extraction complete
- **Models**: Using existing ExecutableReport structure
- **New Modules**: ✅ Created syntax highlighting module in `ui/syntax/`

### Completed Components
✅ `ui/syntax/highlighter.py` - Core syntax highlighting engine  
✅ `ui/syntax/schemes.py` - Architecture-specific color schemes  
✅ `ui/syntax/instructions.py` - x86/x64 instruction database (354 instructions)  
✅ `ui/syntax/instructions_arm.py` - ARM/ARM64 instructions (446 instructions)  
✅ `ui/syntax/instructions_mips.py` - MIPS instructions (381 instructions)  
✅ `ui/syntax/arch_detector.py` - Architecture detection from reports  
✅ `ui/syntax/arch_manager.py` - Classifier management  
✅ `ui/syntax/operand_parser.py` - Operand parsing and classification  
✅ `ui/views/r2_view.py` - Integrated syntax highlighting with architecture support  

### Components from Plan 4 (TUI Redesign) to Leverage
✅ `ui/core/state.py` - AppState with reactive properties  
✅ `ui/core/messages.py` - Message system (includes JumpToAddress)  
✅ `ui/core/base.py` - BaseView and InteractiveView  
✅ `ui/widgets/command_palette.py` - Command palette (Ctrl+P)  
✅ `ui/widgets/details_panel.py` - Details panel for contextual info  
✅ `ui/widgets/function_explorer.py` - Function tree in sidebar  
✅ `ui/workers/analysis_worker.py` - Async analysis execution  

### Pending Components (Subtask 5)
⏸️ Optional cross-reference enhancements (inline annotations, filtering)

### Completed in Subtask 4
✅ Navigation history in AppState  
✅ Xref extraction and display  
✅ Interactive disassembly navigation

## Technical Dependencies

### Required Libraries
- **Textual**: Already available, provides widget framework
- **Rich**: Already available, provides syntax highlighting primitives
- **Pygments** (optional): For additional syntax highlighting capabilities
- **capstone** (optional): For instruction parsing and classification

### Radare2 Integration
- Leverage existing r2pipe integration
- Extract additional metadata: instruction types, cross-references, comments
- Use r2 commands: `pdc` (decompiled code), `pdf` (function disassembly with metadata)

## Complexity Assessment

### Difficulty: Medium-High
- **Syntax Highlighting**: ✅ COMPLETE - Rich library integration successful
- **Architecture Support**: ✅ COMPLETE - x86/x64, ARM, MIPS all supported
- **Interactive Features**: ✅ COMPLETE - New TUI architecture simplified implementation
- **Performance**: ✅ COMPLETE - LRU caching, profiling, memory management implemented

### Estimated Effort (Revised)
- ✅ Subtask 1 (Basic Highlighting): 2-3 days → DONE
- ✅ Subtask 2 (Instruction Classification): 2-3 days → DONE
- ✅ Subtask 3 (Architecture-Specific): 2-3 days → DONE
- ✅ Subtask 4 (Interactive Navigation): 2-3 days → DONE (2 days)
- ⏸️ Subtask 5 (Cross-Reference Display): 1-2 days → May be skipped (core complete in #4)
- ✅ Subtask 6 (Performance Optimization): 2-3 days → DONE (1 day)
- **Completed**: 10-14 days
- **Remaining**: 0-2 days (Subtask 5 optional)
- **Total**: 10-16 days (original estimate: 8-13 days)

## Success Criteria

### Completed Criteria ✅
1. ✅ Assembly instructions are color-coded by type (jumps, calls, data movement, etc.)
2. ✅ Registers, immediate values, and memory addresses are visually distinct
3. ✅ Support for x86, x86_64, ARM, ARM64, MIPS, and MIPS64 architectures
4. ✅ Architecture is automatically detected from binary metadata
5. ✅ UI remains responsive during analysis (async workers)
6. ✅ Users can navigate to function calls and jump targets
7. ✅ Cross-references are displayed for functions and addresses
8. ✅ Performance remains acceptable for functions with 500+ instructions
9. ✅ Highlighting is cached to avoid re-computation

### Remaining Criteria ⏸️
10. ✅ Memory usage is bounded for large binaries (LRU cache with configurable limits)

## Implementation Phases

### ✅ Phase 1: Foundation (Subtasks 1-2) - COMPLETE
Set up basic syntax highlighting infrastructure and implement core highlighting for x86/x64.

**Status**: ✅ Complete (2026-02-13)  
**Delivered**:
- AsmHighlighter class with instruction classification
- Operand parsing (registers, immediates, memory, symbols)
- x86/x64 instruction database (354 instructions)
- Integration with r2_view
- Comprehensive test suite

### ✅ Phase 2: Enhancement (Subtask 3) - COMPLETE
Add architecture-specific support and improve highlighting accuracy.

**Status**: ✅ Complete (2026-02-13)  
**Delivered**:
- ARM/ARM64 instruction database (446 instructions)
- MIPS/MIPS64 instruction database (381 instructions)
- Architecture detection and automatic classifier selection
- 163 tests with 100% coverage

### ✅ Phase 3: Interactivity (Subtask 4) - COMPLETE
Implement interactive navigation and cross-reference features.

**Status**: ✅ Complete (2026-02-17)  
**Delivered**:
- Navigation history system with back/forward/bookmarks (3700+ lines)
- Xref extraction from radare2 (refs to/from)
- Interactive disassembly navigation with click/keyboard
- Xref display in details panel with inline indicators
- Navigation commands in command palette
- LRU cache for syntax highlighting
- 991 tests passing (965 unit + 26 integration)

### ✅ Phase 4: Polish (Subtask 6) - COMPLETE
Optimize performance, add caching, and refine user experience.

**Status**: ✅ Complete (2026-02-17)  
**Delivered**: 
- LRU caching with configurable size limits
- Performance profiling script with detailed metrics
- Memory management with cache clearing
- Comprehensive profiling revealing cache overhead insights

## Risk Assessment

### Technical Risks

#### ✅ RESOLVED: Performance Degradation
**Original Risk**: Large binaries may slow down with rich highlighting

**Mitigation Implemented**:
- ✅ Display limits (MAX_DISASM_OPS = 100)
- ✅ Async workers keep UI responsive
- ⏸️ Still needed: Caching and pagination (Subtask 6)

#### ✅ RESOLVED: Architecture Coverage
**Original Risk**: Different architectures have different instruction sets

**Mitigation Implemented**:
- ✅ Modular design with architecture-specific databases
- ✅ x86/x64, ARM, MIPS all supported
- ✅ Easy to extend with new architectures

#### ✅ RESOLVED: Textual Limitations
**Original Risk**: Complex interactive features may be challenging

**Mitigation Implemented**:
- ✅ Plan 4 provided InteractiveView base class
- ✅ Command palette for keyboard-driven navigation
- ✅ Details panel for contextual information
- ✅ Message-based architecture for events

### Integration Risks

#### ✅ LOW RISK: Radare2 API Changes
**Mitigation**: 
- r2pipe API is stable
- Backend abstraction layer isolates changes
- Can add fallbacks if needed

#### ✅ LOW RISK: Breaking Changes
**Mitigation**:
- All changes have been backward compatible
- New features are additive
- Existing workflows unchanged

## Dependencies on Other Plans

### Completed Dependencies ✅
- ✅ **Plan 4 (TUI Redesign)**: Provides reactive architecture, command palette, multi-panel layout, async workers
- ✅ **Subtasks 1-3**: Core highlighting infrastructure complete

### Active Dependencies ⏸️
- ⏸️ **Subtask 4 completion** required before Subtask 5 (xref display may overlap)
- ⏸️ **r2_analyzer.py enhancements** needed for xref extraction (Subtasks 4-5)

### Future Enhancements 🔮
After completion of remaining subtasks:
- **Point 2 (Pattern Detection)**: Could leverage syntax highlighting for pattern visualization
- **Point 3 (Syscall Detection)**: API call highlighting can use similar classification
- **Decompiler Support**: Extend to highlight decompiled code (r2's `pdc` output)
- **Custom Color Schemes**: User-configurable color palettes
- **Export Features**: HTML/PDF export with highlighting

## Future Enhancements

After core implementation, consider:
- Decompiler output highlighting (using r2's `pdc` command)
- Inline hex display alongside disassembly
- Customizable color schemes
- Export highlighted code as HTML or PDF
- Integration with external editors

## References

- [Rich Documentation - Syntax Highlighting](https://rich.readthedocs.io/en/latest/syntax.html)
- [Textual Documentation - Custom Widgets](https://textual.textualize.io/guide/widgets/)
- [Radare2 Commands Reference](https://book.rada.re/first_steps/commandline_flags.html)
- [Capstone Disassembly Framework](http://www.capstone-engine.org/)

## Subtasks

### ✅ Completed
1. [✅ Basic Syntax Highlighting](subtask-1-basic-highlighting.md) - Complete (2026-02-13)
2. [✅ Instruction Classification](subtask-2-instruction-classification.md) - Complete (2026-02-13)
3. [✅ Architecture-Specific Schemes](subtask-3-architecture-schemes.md) - Complete (2026-02-13)
4. [✅ Interactive Navigation](subtask-4-interactive-navigation.md) - Complete (2026-02-17)

### ⏸️ Remaining
5. [⏸️ Cross-Reference Display](subtask-5-cross-references.md) - Core functionality complete in #4, evaluate if additional work needed
6. [✅ Performance Optimization](subtask-6-performance.md) - ✅ COMPLETE (2026-02-17)

## Recent Changes

### 2026-02-17: Subtask 6 Complete

**Subtask 6 (Performance Optimization)** is now complete with all critical optimization steps implemented:

1. **LRU Caching**:
   - Implemented `functools.lru_cache` on `highlight_instruction()` method
   - Configurable cache size (default: 1000 entries)
   - `clear_cache()` method for memory management
   - Significant performance improvement for repeated highlighting

2. **Performance Profiling Script**:
   - Created `scripts/profile_highlighting.py` with comprehensive metrics
   - Measures instructions/second, cache hit rates, memory usage
   - Profiles with various cache sizes (0, 100, 500, 1000, 2000)
   - Detailed output showing performance characteristics

3. **Memory Management**:
   - Cache clearing on binary switch
   - Integration with AppState lifecycle
   - Bounded memory usage via cache size limits
   - Proper cleanup mechanisms

**Key Findings**:
- Profiling revealed significant cache overhead for small workloads
- Cache most effective with ≥500 entries for typical functions
- Memory usage scales predictably with cache size
- Highlight performance meets <100ms target for 1000 instructions

**Impact**: Plan 1 now 83% complete (5 of 6 subtasks). Only Subtask 5 (optional enhancements) remains.

### 2026-02-17: Subtask 4 Complete

**Subtask 4 (Interactive Navigation)** is now complete with all 8 steps implemented:

1. **Navigation History System** (3700+ lines):
   - NavigationHistory class with back/forward stacks
   - Bookmark system with named locations
   - History serialization and restoration
   - Integration with AppState

2. **Xref Extraction**:
   - Enhanced r2_analyzer.py to extract cross-references
   - Support for calls, jumps, data refs, strings
   - Bidirectional xrefs (to and from)

3. **Interactive R2View**:
   - Click and keyboard navigation
   - Address selection and highlighting
   - Navigation to xref targets

4. **Details Panel Xrefs**:
   - Display xrefs to/from current address
   - Inline xref indicators in disassembly
   - Keyboard shortcuts for navigation

5. **Command Palette Integration**:
   - Navigation commands (back, forward, bookmarks)
   - Jump to address command

6. **LRU Cache**:
   - Syntax highlighting cache implemented
   - Configurable cache size
   - Performance improvement for repeated views

**Testing**: 991 tests passing (965 unit + 26 integration)  
**Coverage**: Comprehensive test coverage for all new features  
**Impact**: Performance criterion met, Subtask 6 now ~60% complete

### 2026-02-16: Plan Review

This plan was reviewed and updated to reflect:

1. **Completed Work (Subtasks 1-3)**:
   - All marked as complete with completion dates
   - Success criteria updated to show what was achieved
   - Implementation summaries added

2. **New TUI Architecture Integration (Plan 4)**:
   - Updated subtasks 4-5 to leverage new reactive TUI
   - Removed references to obsolete custom widgets
   - Aligned with command palette, details panel, and InteractiveView
   - Simplified implementation approach using existing infrastructure

3. **Current State Assessment**:
   - Subtask 6 marked as partially complete (~40%)
   - Display limits and async workers already implemented
   - Remaining work: caching, pagination, profiling

4. **Reduced Complexity**:
   - Interactive features simplified by new TUI (was HIGH, now MEDIUM)
   - Estimated time reduced for subtasks 4-5 due to available infrastructure
   - Clear dependencies and integration points identified

## Next Actions

To complete Plan 1:

1. **✅ Subtask 6 Complete** (2026-02-17):
   - All 3 critical steps implemented and tested
   - LRU caching with configurable limits
   - Performance profiling script with detailed metrics
   - Memory management and cache clearing
   - All success criteria met

2. **Evaluate Plan 1 Completion**:
   - 5 of 6 subtasks complete (83%)
   - All critical functionality implemented
   - Only Subtask 5 (optional enhancements) remains
   - **Decision needed**: Is Plan 1 complete enough for production use?

3. **Optional: Subtask 5** (Cross-Reference Display):
   - Core xref functionality already complete in Subtask 4
   - Optional enhancements only:
     - Inline xref count annotations
     - Xref type filtering
     - Advanced sorting options
   - **Recommendation**: Skip for now, revisit based on user feedback

## References
