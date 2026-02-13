# Caspoon Documentation Index

Quick reference to find the documentation you need.

## 📚 For New Users

Start here to understand what Caspoon is and how to use it:

- **[README.md](README.md)** - Project overview, quick start, and basic usage
- **[caspoon/docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md)** - Detailed architecture and usage guide

## 🛠️ For Contributors

Guidelines for contributors:

- **[TESTING.md](TESTING.md)** - Comprehensive testing documentation
  - How to run tests
  - How to write tests
  - Test coverage requirements
  - Golden tests and best practices

- **[caspoon/docs/DEPENDENCIES.md](caspoon/docs/DEPENDENCIES.md)** - Dependency management
  - Core and optional dependencies
  - Version constraints philosophy
  - Lock files for reproducible builds
  - Troubleshooting

- **[caspoon/docs/reference/CI_CD_TOOLS.md](caspoon/docs/reference/CI_CD_TOOLS.md)** - CI/CD and security tools
  - Security scanning workflow
  - Dependency check script
  - Dependabot configuration

## 🧪 Testing Documentation

| Document | Audience | Purpose |
|----------|----------|---------|
| **[TESTING.md](TESTING.md)** | All developers | Comprehensive testing guide (start here) |
| **[caspoon/TESTING_GUIDE.md](caspoon/TESTING_GUIDE.md)** | Developers | Quick reference card |
| **[caspoon/tests/README.md](caspoon/tests/README.md)** | Developers | Test suite overview and statistics |
| **[caspoon/TEST_REVIEW.md](caspoon/TEST_REVIEW.md)** | Maintainers | Detailed testing strategy and review |
| **[caspoon/TESTING_COMPLETE.md](caspoon/TESTING_COMPLETE.md)** | Maintainers | Final implementation summary |

## 📖 Architecture & Design

Deep dives into how Caspoon works:

- **[caspoon/docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md)** - Architecture overview
  - Component layers
  - Directory structure
  - Recon module pattern
  - Extensibility guide
  
- **[caspoon/docs/plans/](caspoon/docs/plans/)** - Design documents and roadmap

### AI Agent System

- **[AGENT_SYSTEM_EVALUATION.md](caspoon/docs/reference/AGENT_SYSTEM_EVALUATION.md)** - Analysis and improvement plan for the AI agent system
- **[AGENT_USAGE_GUIDE.md](caspoon/docs/reference/AGENT_USAGE_GUIDE.md)** - How to effectively use the specialized AI agents
- **[AGENT_COORDINATION.md](caspoon/docs/reference/AGENT_COORDINATION.md)** - Agent coordination protocols and communication patterns

## 🚀 Quick Start Cheat Sheet

```bash
# Install
pip install -e ".[dev]"

# Run analysis
caspoon /path/to/binary

# Run interactive UI
caspoon --ui

# Run tests
pytest -m "not slow"

# Check coverage
pytest --cov=caspoon --cov-report=html
```

## 🗺️ Documentation Structure

```
spoons16/
├── README.md                          # 👈 Start here (project overview)
├── TESTING.md                         # 👈 Complete testing guide
├── DOCUMENTATION_INDEX.md             # This file
│
└── caspoon/
    ├── docs/
    │   ├── OVERVIEW.md               # 👈 Architecture deep dive
    │   └── plans/                    # Design documents
    │
    ├── TESTING_GUIDE.md              # Quick test reference
    ├── TEST_REVIEW.md                # Testing strategy (maintainers)
    ├── TESTING_COMPLETE.md           # Implementation summary
    │
    └── tests/
        ├── README.md                 # Test suite overview
        ├── unit/                     # Unit tests
        ├── integration/              # Integration tests
        └── fixtures/                 # Test data
```

## 🎯 Where Should I Look?

### "I want to use Caspoon"
→ Start with **[README.md](README.md)**

### "I want to understand how Caspoon works"
→ Read **[caspoon/docs/OVERVIEW.md](caspoon/docs/OVERVIEW.md)**

### "I want to add or run tests"
→ Read **[TESTING.md](TESTING.md)**

### "I need quick test commands"
→ See **[caspoon/TESTING_GUIDE.md](caspoon/TESTING_GUIDE.md)**

### "I want to understand test coverage"
→ See **[TESTING.md#test-coverage](TESTING.md#test-coverage)**

---

<div align="center">

**Questions?** Open an issue or discussion on GitHub

**[⬆ Back to Top](#caspoon-documentation-index)**

</div>
