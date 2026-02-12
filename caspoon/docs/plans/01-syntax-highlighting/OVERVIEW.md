# Implementation Plan: Syntax Highlighting & Code Display Improvements

## Overview

This plan covers enhancements to the disassembly viewing experience in caspoon, focusing on syntax highlighting, interactive features, and improved code display. These improvements will make it easier for reverse engineers to understand and navigate disassembled code.

## Goals

1. Implement comprehensive syntax highlighting for assembly code
2. Add interactive navigation features for disassembly
3. Improve code readability through formatting and annotations
4. Support multiple architectures with appropriate highlighting schemes

## Architecture Impact

### Modified Components
- **UI Views**: Enhance `ui/views/r2_view.py` with new rendering capabilities
- **Backend**: Extend `backends/r2_analyzer.py` to extract additional metadata
- **Models**: Potentially add new data structures for highlighted/annotated code
- **New Modules**: Create syntax highlighting module in `ui/syntax/`

### New Components
- `ui/syntax/highlighter.py` - Core syntax highlighting engine
- `ui/syntax/schemes.py` - Architecture-specific color schemes
- `ui/syntax/annotator.py` - Code annotation system
- `ui/widgets/disasm_view.py` - Enhanced disassembly widget with interactivity

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
- **Syntax Highlighting**: Medium - Rich library provides primitives
- **Architecture Support**: Medium - Requires instruction classification per architecture
- **Interactive Features**: High - Requires custom Textual widgets
- **Performance**: Medium - Need to handle large disassembly outputs efficiently

### Estimated Effort
- Subtask 1 (Basic Highlighting): 2-3 days
- Subtask 2 (Architecture-Specific): 2-3 days
- Subtask 3 (Interactive Features): 3-5 days
- Subtask 4 (Optimization): 1-2 days
- **Total**: 8-13 days

## Success Criteria

1. Assembly instructions are color-coded by type (jumps, calls, data movement, etc.)
2. Registers, immediate values, and memory addresses are visually distinct
3. Users can navigate to function calls and jump targets
4. Cross-references are displayed for functions and addresses
5. Performance remains acceptable for functions with 500+ instructions
6. Support for at least x86, x86_64, and ARM architectures

## Implementation Phases

### Phase 1: Foundation (Subtasks 1-2)
Set up basic syntax highlighting infrastructure and implement core highlighting for x86/x64.

### Phase 2: Enhancement (Subtask 3)
Add architecture-specific support and improve highlighting accuracy.

### Phase 3: Interactivity (Subtasks 4-5)
Implement interactive navigation and cross-reference features.

### Phase 4: Polish (Subtask 6)
Optimize performance, add annotations, and refine user experience.

## Risk Assessment

### Technical Risks
- **Performance Degradation**: Large binaries may slow down with rich highlighting
  - *Mitigation*: Implement lazy loading and pagination
- **Architecture Coverage**: Different architectures have different instruction sets
  - *Mitigation*: Start with common architectures, use modular design for extensibility
- **Textual Limitations**: Complex interactive features may be challenging
  - *Mitigation*: Evaluate Textual capabilities early, have fallback plans

### Integration Risks
- **Radare2 API Changes**: r2pipe API may change
  - *Mitigation*: Abstract r2 interactions, version pin if necessary
- **Breaking Changes**: UI changes may disrupt existing workflows
  - *Mitigation*: Maintain backward compatibility, add features incrementally

## Dependencies on Other Plans

- **Point 2 (Pattern Detection)**: Pattern highlighting could leverage syntax highlighting infrastructure
- **Point 3 (Syscall Detection)**: API call highlighting will use similar mechanisms
- **UI Improvements (Point 9)**: Interactive features align with broader UI enhancements

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

1. [Basic Syntax Highlighting](subtask-1-basic-highlighting.md)
2. [Instruction Classification](subtask-2-instruction-classification.md)
3. [Architecture-Specific Schemes](subtask-3-architecture-schemes.md)
4. [Interactive Navigation](subtask-4-interactive-navigation.md)
5. [Cross-Reference Display](subtask-5-cross-references.md)
6. [Performance Optimization](subtask-6-performance.md)
