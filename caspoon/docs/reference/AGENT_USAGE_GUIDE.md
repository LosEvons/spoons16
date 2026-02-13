# Agent System Usage Guide

**Quick Reference:** When and how to use the AI agents in the Caspoon project

---

## Quick Decision Tree

```
Need help with a task?
├─ Is it a large feature spanning multiple domains?
│  └─ YES → Use **architect** agent
│
├─ Do you need to write Python code?
│  └─ YES → Use **python-implementation** agent
│
├─ Do you need to design an algorithm or data structure?
│  └─ YES → Use **binary-analysis-design** agent
│
├─ Do you need to write or fix tests?
│  └─ YES → Use **testing-verification** agent
│
├─ Is it about CI/CD, GitHub Actions, or builds?
│  └─ YES → Use **cicd** agent
│
├─ Is it about CLI interface, TUI, or reports?
│  └─ YES → Use **cli-reporting** agent
│
└─ Is it about documentation?
   └─ YES → Use **docs** agent
```

---

## Agent Capabilities

### 1. Architect Agent (Orchestrator)
**When to use:**
- Planning new features that span multiple domains
- Coordinating work across multiple agents
- Making high-level architectural decisions
- Breaking down complex requirements

**Do NOT use for:**
- Simple bug fixes
- Straightforward implementation tasks
- Documentation-only changes

**Example invocations:**
```
"I want to add support for PE file format analysis"
→ Architect will plan the work and delegate to design, implementation, testing

"Help me design the architecture for a plugin system"
→ Architect will coordinate design and implementation agents
```

### 2. Python Implementation Agent
**When to use:**
- Writing new Python code
- Refactoring existing Python code
- Fixing Python bugs
- Implementing designs from the design agent

**Do NOT use for:**
- Designing algorithms (use binary-analysis-design)
- Writing tests primarily (use testing-verification)
- Documentation (use docs)

**Example invocations:**
```
"Implement the ELF section parser based on the design in docs/plans/..."
→ Implementation agent writes the Python code

"Refactor the ReconRunner to use async/await"
→ Implementation agent refactors code incrementally
```

**Works well with:**
- binary-analysis-design (receives designs from)
- testing-verification (coordinates on test code)

### 3. Binary Analysis Design Agent
**When to use:**
- Designing analysis algorithms
- Creating data structures and IR representations
- Planning analysis pipelines
- Evaluating trade-offs (precision vs performance)

**Do NOT use for:**
- Writing implementation code
- Testing code
- CLI/UX design

**Example invocations:**
```
"Design a data-flow analysis pass for detecting suspicious API usage"
→ Design agent creates algorithm and IR design

"How should we represent control flow graphs for multi-architecture support?"
→ Design agent proposes data structures and explains trade-offs
```

**Works well with:**
- python-implementation (hands off designs to)
- architect (receives high-level requirements from)

### 4. Testing & Verification Agent
**When to use:**
- Designing test strategies
- Writing test code
- Creating test fixtures
- Debugging test failures
- Improving test coverage

**Do NOT use for:**
- Production code implementation
- CI/CD configuration (use cicd)

**Example invocations:**
```
"Add integration tests for the radare2 backend"
→ Testing agent designs and implements tests

"Our coverage for imports_exports.py is only 60%, help improve it"
→ Testing agent identifies gaps and adds tests
```

**Works well with:**
- python-implementation (coordinates on test code)
- cicd (coordinates on CI test execution)

### 5. CI/CD Agent
**When to use:**
- Configuring GitHub Actions workflows
- Setting up quality gates
- Managing build pipelines
- Debugging CI failures
- Setting up security scanning

**Do NOT use for:**
- Writing application code
- Writing tests (use testing-verification)

**Example invocations:**
```
"Add a workflow to run tests on multiple Python versions"
→ CI/CD agent creates GitHub Actions workflow

"Our builds are slow, help optimize the CI pipeline"
→ CI/CD agent analyzes and improves workflow efficiency
```

**Works well with:**
- testing-verification (coordinates on test execution)
- docs (coordinates on documentation builds)

### 6. CLI & Reporting Agent
**When to use:**
- Designing command-line interfaces
- Creating TUI layouts and interactions
- Designing HTML report formats
- Improving user experience

**Do NOT use for:**
- Backend analysis logic (use binary-analysis-design)
- Test code (use testing-verification)

**Example invocations:**
```
"Design a better CLI for selecting analysis backends"
→ CLI agent proposes new CLI structure

"Create an HTML report template for showing security vulnerabilities"
→ CLI agent designs report layout
```

**Works well with:**
- python-implementation (hands off UI designs to)
- docs (coordinates on usage documentation)

### 7. Documentation Agent
**When to use:**
- Writing developer documentation
- Creating user guides
- Updating README files
- Maintaining changelog
- Writing architecture docs

**Do NOT use for:**
- Code comments (implementation agent does this)
- API documentation in docstrings (implementation agent)

**Example invocations:**
```
"Update the README to reflect the new plugin system"
→ Docs agent updates documentation

"Create a guide for extending Caspoon with new backends"
→ Docs agent writes comprehensive guide
```

**Works well with:**
- All agents (documents their work)

---

## Common Workflows

### Workflow 1: Adding a New Feature
**Scenario:** "Add support for Mach-O binary analysis"

**Recommended flow:**
1. **architect** - Plans the work, breaks it down
2. **binary-analysis-design** - Designs Mach-O parser and data structures
3. **python-implementation** - Implements the design
4. **testing-verification** - Creates tests for Mach-O support
5. **cicd** - Updates workflows if needed (e.g., macOS-specific tests)
6. **docs** - Documents the new feature

### Workflow 2: Fixing a Bug
**Scenario:** "String extraction is failing on ARM binaries"

**Recommended flow:**
1. **testing-verification** - Creates reproduction test
2. **python-implementation** - Fixes the bug
3. **testing-verification** - Verifies fix with tests

*(No need for architect unless the fix requires significant design changes)*

### Workflow 3: Improving User Experience
**Scenario:** "Make the TUI more responsive and add search"

**Recommended flow:**
1. **cli-reporting** - Designs UX improvements
2. **python-implementation** - Implements the UI changes
3. **testing-verification** - Adds UI tests
4. **docs** - Updates usage documentation

### Workflow 4: Refactoring
**Scenario:** "Refactor the recon module pattern for better extensibility"

**Recommended flow:**
1. **architect** - Plans refactoring strategy
2. **binary-analysis-design** - Designs new module interface
3. **python-implementation** - Refactors code incrementally
4. **testing-verification** - Updates tests, adds regression tests
5. **docs** - Updates architecture documentation

---

## Best Practices

### Do's ✅

1. **Be specific in your requests**
   - Good: "Add a flag to output results as YAML instead of JSON"
   - Bad: "Make the output better"

2. **Provide context**
   - Include relevant file paths
   - Mention related issues or PRs
   - Reference existing designs if applicable

3. **Start with the right agent**
   - Use the decision tree above
   - When in doubt, start with architect for planning

4. **Trust the agent's domain expertise**
   - Let implementation agent handle code style
   - Let design agent evaluate trade-offs
   - Let testing agent determine test strategy

5. **Iterate based on feedback**
   - Agents may ask clarifying questions
   - Provide additional context as needed

### Don'ts ❌

1. **Don't use multiple agents simultaneously for the same task**
   - Bad: Asking implementation AND design agent to "add a feature"
   - Good: Design first, then implement

2. **Don't skip the design phase for complex features**
   - Jumping straight to implementation can lead to rework
   - Use binary-analysis-design for non-trivial algorithms

3. **Don't mix concerns in a single request**
   - Bad: "Implement feature X and also fix the CI pipeline"
   - Good: Separate requests or use architect to coordinate

4. **Don't bypass testing**
   - Always include testing-verification for significant changes
   - Tests prevent regressions and document behavior

5. **Don't forget documentation**
   - User-facing changes need docs updates
   - Architectural changes need design docs

---

## Agent Coordination

### How Agents Work Together

Agents can call each other using their coordination protocols:

```markdown
**@python-implementation**: I need the IR design for basic blocks.
Can you check docs/plans/ or ask @binary-analysis-design?

**@binary-analysis-design**: The basic block IR should include:
- Start and end addresses
- List of instructions
- Successor blocks
- Predecessor blocks
See docs/plans/ir-design.md for details.

**@python-implementation**: Thanks! I'll implement based on that design.
```

### Escalation

If agents cannot resolve an issue:
1. **Agent-to-Agent:** Try direct coordination first
2. **To Architect:** Escalate design conflicts or unclear requirements
3. **To User:** Escalate if decisions require user input or preferences

---

## Tips for Effective Agent Usage

### 1. Provide Examples
```
Good: "Add a --verbose flag like the --json flag we already have"
Better: "Add a --verbose flag that prints progress to stderr, similar to --json"
```

### 2. Reference Existing Patterns
```
"Follow the same pattern as the strings_mod.py recon module"
```

### 3. Specify Constraints
```
"Keep backward compatibility with the existing CLI"
"Must work without external dependencies"
```

### 4. State Your Goals
```
"I want to improve test coverage" → testing-verification
"I want to improve code readability" → python-implementation
"I want to improve analysis accuracy" → binary-analysis-design
```

### 5. Break Down Large Tasks
```
Instead of: "Redesign the entire analysis pipeline"
Better:
1. "Design the new pipeline architecture" → binary-analysis-design
2. "Implement the pipeline runner" → python-implementation
3. "Add tests for the pipeline" → testing-verification
```

---

## Troubleshooting

### "I don't know which agent to use"
→ Start with **architect** - it will help plan and delegate

### "The agent didn't understand my request"
→ Provide more context, examples, or break down the request

### "I need multiple agents for my task"
→ Use **architect** to coordinate, or invoke them sequentially

### "The agent's output wasn't what I expected"
→ Provide feedback and iterate. Agents learn from clarification.

### "Can I work without agents?"
→ Yes! Agents are helpers, not requirements. Use them when beneficial.

---

## See Also

- [AGENT_SYSTEM_EVALUATION.md](AGENT_SYSTEM_EVALUATION.md) - Detailed analysis of agent system
- [OVERVIEW.md](OVERVIEW.md) - Caspoon architecture
- [TESTING.md](../guides/TESTING.md) - Testing guidelines
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - All documentation

---

**Questions?** Open an issue or check the agent definitions in `.github/agents/`
