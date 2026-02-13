# Agent Coordination Protocol

**Standard coordination guidelines for all Caspoon AI agents**

This document defines how agents communicate and coordinate with each other.

---

## Coordination Protocol

### When You Need Input From Another Agent

1. **Document what you need and why**
   - Be specific about the information or help required
   - Explain how it blocks or enables your work

2. **State what decisions you've deferred**
   - Clearly mark areas awaiting input
   - Provide your preliminary thoughts if applicable

3. **Tag the request appropriately**
   - `@agent-name` for direct requests
   - Example: "@binary-analysis-design: Need IR design for ARM instructions"

### When Another Agent Needs Your Input

1. **Respond to questions directly**
   - Address the specific question asked
   - Provide concrete, actionable information

2. **Provide context for your recommendations**
   - Explain reasoning behind suggestions
   - Reference relevant documentation or designs

3. **Note any constraints or assumptions**
   - State limitations or prerequisites
   - Highlight areas of uncertainty

### Escalation Path

- **Minor questions:** Direct agent-to-agent coordination
- **Design conflicts:** Escalate to architect agent
- **Blocked work:** Escalate to user for decision
- **Missing information:** Request clarification from user

---

## Agent Communication Templates

### Request Template
```markdown
**Request for @[agent-name]:**

**Context:** [Brief description of your current task]

**Need:** [Specific information or help needed]

**Blocking:** [What this blocks/enables]

**Preliminary thoughts:** [Optional: your initial ideas]
```

### Response Template
```markdown
**Response to @[agent-name]:**

**Answer:** [Direct response to question]

**Reasoning:** [Why this is recommended]

**Constraints:** [Limitations or assumptions]

**References:** [Links to docs/code/designs]
```

### Escalation Template
```markdown
**Escalation to @architect / user:**

**Issue:** [What needs resolution]

**Attempted:** [What has been tried]

**Options:** [Possible paths forward]

**Recommendation:** [Suggested approach if any]
```

---

## Handoff Checklist

When handing work to another agent:

- [ ] Provide complete context
- [ ] Reference relevant files and documentation
- [ ] State what has been decided/completed
- [ ] Note open questions or assumptions
- [ ] Specify success criteria

---

## Cross-Agent Workflows

### Design → Implementation
**Design agent provides:**
- Data structure specifications
- Algorithm descriptions
- Trade-off analysis
- Expected behavior

**Implementation agent confirms:**
- Feasibility within constraints
- Additional requirements needed
- Implementation timeline estimate

### Implementation → Testing
**Implementation agent provides:**
- Code changes made
- Expected behavior
- Edge cases identified
- Suggested test scenarios

**Testing agent confirms:**
- Test coverage plan
- Additional scenarios needed
- Testing approach

### Any Agent → Documentation
**Source agent provides:**
- What changed (code/design/process)
- Why it changed
- Impact on users/developers
- Examples if applicable

**Docs agent confirms:**
- Which docs need updates
- Documentation plan
- Review process

---

## Conflict Resolution

### Design Disagreements
1. Both agents state their positions
2. Identify core disagreement point
3. Architect agent makes final decision
4. Document the decision and rationale

### Implementation Blockers
1. Implementation agent documents the blocker
2. Relevant agent provides clarification or design change
3. If unresolved, escalate to architect or user

### Priority Conflicts
1. Architect agent sets priorities
2. Agents work in priority order
3. Lower priority work is deferred, not abandoned

---

## Quality Gates

Each agent should verify before handoff:

- **Design Agent:**
  - [ ] Design is complete and unambiguous
  - [ ] Trade-offs are documented
  - [ ] Examples are provided

- **Implementation Agent:**
  - [ ] Code follows project conventions
  - [ ] Changes are minimal and focused
  - [ ] Inline documentation is adequate

- **Testing Agent:**
  - [ ] Tests cover new functionality
  - [ ] Tests check edge cases
  - [ ] Tests are maintainable

- **CI/CD Agent:**
  - [ ] Workflows are idempotent
  - [ ] Error messages are clear
  - [ ] Security best practices followed

- **CLI/Reporting Agent:**
  - [ ] User experience is tested
  - [ ] Help text is clear
  - [ ] Examples are provided

- **Documentation Agent:**
  - [ ] Documentation is accurate
  - [ ] Links are valid
  - [ ] Examples are tested

---

## Context Sharing Format

When sharing work-in-progress context:

```markdown
## Agent Context: [Agent Name]

**Task:** [Brief description]

**Status:** [In Progress / Blocked / Complete]

**Dependencies:** 
- [What we need from other agents]
- [External dependencies]

**Blockers:** 
- [Current impediments]
- [Information needed]

**Decisions Made:** 
- [Key choices and rationale]

**Open Questions:**
- [Unresolved items]

**Next Steps:** 
- [Immediate actions]
- [Future work]
```

---

## Best Practices

### Communication
- **Be explicit:** Don't assume other agents have context
- **Be concise:** Respect token limits and reading time
- **Be specific:** Vague requests lead to vague answers

### Coordination
- **Early and often:** Coordinate before getting blocked
- **Async-friendly:** Don't wait for synchronous responses
- **Document decisions:** Write down what was decided and why

### Quality
- **Verify handoffs:** Confirm the receiving agent has what they need
- **Check your work:** Validate outputs before passing on
- **Iterate quickly:** Small corrections are better than perfect first attempts

---

## Examples

### Good Coordination

```markdown
**@binary-analysis-design**: I'm implementing the ARM disassembly support.
I need clarification on the instruction IR format for ARM-specific features
like conditional execution. Should these be separate fields in the
Instruction class or encoded in the mnemonic?

**Current implementation:** caspoon/backends/r2_analyzer.py:156

**Blocked on:** IR design decision

**@python-implementation**: Good question. Based on the design in
docs/plans/ir-design.md, conditional execution should be a separate
`condition` field on the Instruction class. This allows analysis passes
to reason about conditions independently of the instruction semantics.

Example:
```python
Instruction(
    address=0x1000,
    mnemonic="mov",
    condition="eq",  # ARM conditional execution
    operands=[...]
)
```

**Reasoning:** Separation of concerns - analysis passes that care about
conditions can check this field, others can ignore it.

**References:** docs/plans/ir-design.md section 3.2
```

### Poor Coordination (Don't do this)

```markdown
**@python-implementation**: Need help with ARM stuff

**@binary-analysis-design**: What specifically?

**@python-implementation**: The implementation

**@binary-analysis-design**: Of what?
```

Problems:
- Too vague
- No context
- No specific question
- Wastes multiple exchanges

---

## Updates and Maintenance

This coordination protocol should be updated when:
- New agents are added
- Coordination patterns emerge
- Pain points are identified
- Better practices are discovered

**Owner:** Architect agent
**Last updated:** 2026-02-13
