# Caspoon Documentation Index

Quick reference to find the documentation you need.

## 📚 For New Users

Start here to understand what Caspoon is and how to use it:

- **[README.md](../../../README.md)** - Project overview, quick start, and basic usage
- **[OVERVIEW.md](OVERVIEW.md)** - Detailed architecture and usage guide
- **[TUI User Guide](../guides/tui-user-guide.md)** - Interactive UI usage and features

## 🛠️ For Developers

Guidelines for developers and contributors:

- **[TESTING.md](../guides/TESTING.md)** - Comprehensive testing documentation
  - How to run tests
  - How to write tests
  - Test coverage requirements
  - Golden tests and best practices

- **[TESTING_GUIDE.md](../guides/TESTING_GUIDE.md)** - Quick test reference card

- **[DEPENDENCIES.md](../DEPENDENCIES.md)** - Dependency management
  - Core and optional dependencies
  - Version constraints philosophy
  - Lock files for reproducible builds
  - Troubleshooting

- **[CI_CD_TOOLS.md](CI_CD_TOOLS.md)** - CI/CD and security tools
  - Security scanning workflow
  - Dependency check script
  - Dependabot configuration

- **[CODE_QUALITY.md](CODE_QUALITY.md)** - Code quality standards and tools

## 📖 Architecture & Design

Deep dives into how Caspoon works:

- **[OVERVIEW.md](OVERVIEW.md)** - Architecture overview
  - Component layers
  - Directory structure
  - Recon module pattern
  - Extensibility guide
  
- **[plans/](../plans/)** - Design documents and feature roadmaps
  - [01-syntax-highlighting](../plans/01-syntax-highlighting/) - Assembly syntax highlighting
  - [02-pattern-detection](../plans/02-pattern-detection/) - Pattern detection engine
  - [03-syscall-api-detection](../plans/03-syscall-api-detection/) - System call and API analysis
  - [04-tui-redesign](../plans/04-tui-redesign/) - Terminal UI architecture

## 📝 Changelogs

Project history and completed work:

- **[INDEX.md](../changelogs/INDEX.md)** - Complete changelog index

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
├── LICENSE                            # License information
│
└── caspoon/
    ├── docs/
    │   ├── README.md                  # Documentation overview
    │   ├── DEPENDENCIES.md            # Dependency management
    │   │
    │   ├── guides/                    # User and developer guides
    │   │   ├── TESTING.md            # 👈 Complete testing guide
    │   │   ├── TESTING_GUIDE.md      # Quick test reference
    │   │   └── tui-user-guide.md     # TUI usage guide
    │   │
    │   ├── reference/                 # Technical reference
    │   │   ├── DOCUMENTATION_INDEX.md # 👈 This file
    │   │   ├── OVERVIEW.md           # 👈 Architecture deep dive
    │   │   ├── CI_CD_TOOLS.md        # CI/CD documentation
    │   │   └── CODE_QUALITY.md       # Code quality standards
    │   │
    │   ├── plans/                     # Design documents
    │   │   ├── 01-syntax-highlighting/
    │   │   ├── 02-pattern-detection/
    │   │   ├── 03-syscall-api-detection/
    │   │   └── 04-tui-redesign/
    │   │
    │   └── changelogs/                # Project changelog
    │       └── INDEX.md
    │
    └── tests/
        ├── README.md                  # Test suite overview
        ├── unit/                      # Unit tests
        ├── integration/               # Integration tests
        └── fixtures/                  # Test data
```

## 🎯 Where Should I Look?

### "I want to use Caspoon"
→ Start with **[README.md](../../../README.md)** then **[TUI User Guide](../guides/tui-user-guide.md)**

### "I want to understand how Caspoon works"
→ Read **[OVERVIEW.md](OVERVIEW.md)**

### "I want to add or run tests"
→ Read **[TESTING.md](../guides/TESTING.md)**

### "I need quick test commands"
→ See **[TESTING_GUIDE.md](../guides/TESTING_GUIDE.md)**

### "I want to understand the roadmap"
→ See **[plans/](../plans/)** and **[changelogs/INDEX.md](../changelogs/INDEX.md)**

---

<div align="center">

**Questions?** Open an issue or discussion on GitHub

**[⬆ Back to Top](#caspoon-documentation-index)**

</div>
