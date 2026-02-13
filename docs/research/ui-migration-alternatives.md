# UI Framework Migration Research: Alternatives to Textual

**Date:** February 2026  
**Current Framework:** Textual (v0.40.0+)  
**Purpose:** Evaluate alternatives to Textual for Caspoon's Terminal UI with focus on stability, testability, and AI agent friendliness

---

## Executive Summary

After thorough research of Python UI frameworks, this document evaluates alternatives to Textual for the Caspoon binary analysis toolkit. The analysis focuses on three key criteria:
1. **Stability and Maturity**: Established frameworks with long-term support
2. **Testability**: Ease of writing and maintaining automated tests
3. **AI Agent Friendliness**: Clear APIs, good documentation, and predictable behavior

### Key Findings

**Recommended Option:** **Keep Textual** with improved testing infrastructure

**Reasoning:**
- Textual has significantly matured since its early days and is now production-ready
- Built-in testing support specifically designed for TUI applications
- Modern async architecture aligns with current Python best practices
- Can be served as web application without code changes
- Active development and strong community support

**Alternative Options** (if migration is required):
1. **Gradio** - For simple web-based UIs with minimal code
2. **Flask + htmx** - For custom web UIs with full control
3. **prompt_toolkit** - For staying in terminal but with lower-level control

---

## Current State Analysis

### Textual Usage in Caspoon

**Dependencies:**
```python
textual>=0.40.0,<1.0.0     # TUI framework
rich>=13.0.0,<15.0.0       # Text rendering (also used by Textual)
```

**UI Components (8 files):**
- `ui/app.py` - Main application (CaspoonApp)
- `ui/screens.py` - Screen layouts
- `ui/views/overview.py` - Overview tab
- `ui/views/protections.py` - Security protections tab
- `ui/views/strings_view.py` - Strings analysis tab
- `ui/views/imports_exports.py` - Import/Export symbols tab
- `ui/views/r2_view.py` - Radare2 analysis tab
- `ui/syntax/` - Custom syntax highlighting (7 files)

**Current Testing:**
- 8 UI-related test files
- UI tests excluded from coverage (see pyproject.toml line 108)
- Uses pytest with pytest-asyncio for async support

**Key Features Used:**
- Tabbed interface (TabbedContent, TabPane)
- Input widgets with validation
- ScrollableContainer for large data
- Rich table integration
- Custom widgets (Static subclasses)
- Status bar via Footer

---

## Option 1: Keep Textual (Recommended)

### Overview
Textual is a modern Python TUI framework created by Will McGugan (creator of Rich). Despite being relatively new (2021), it has rapidly matured into a production-ready framework.

### Pros

**Maturity & Adoption:**
- Active development with 25k+ GitHub stars
- Used by major projects (including tools from AWS, DataDog)
- Version 0.40+ is stable with clear semantic versioning
- Large Discord community (1000+ members) for support
- Excellent documentation with examples

**Testing Infrastructure:**
- Built-in testing support via `textual.pilot` for automated testing
- Async test support with pytest-asyncio (already used)
- Snapshot testing capabilities
- DOM inspection for verifying UI state
- Can test without rendering (headless mode)

**AI Agent Friendliness:**
- Clear, well-documented API with type hints
- Predictable component lifecycle
- CSS-like styling is familiar to web developers
- Rich error messages and debugging tools
- `textual-dev` provides inspector and console for debugging

**Technical Advantages:**
- Modern async/await architecture
- Can serve as web application via `textual serve` without code changes
- Excellent performance with virtual DOM
- Built on Rich (already a dependency)
- Reactive data binding simplifies state management

**Migration Cost:**
- **Zero** - already implemented

### Cons

**Perceived Immaturity:**
- Pre-1.0 version number (but API is stable)
- Some breaking changes possible before 1.0
- Newer framework means less battle-testing than urwid

**Complexity:**
- Learning curve for CSS-like styling
- Async nature can be tricky for simple use cases
- More abstraction than lower-level alternatives

### Testing Example
```python
from textual.pilot import Pilot
from caspoon.ui.app import CaspoonApp

async def test_app_loads():
    app = CaspoonApp()
    async with app.run_test() as pilot:
        # Verify UI components exist
        assert pilot.app.query_one("#path_input")
        assert pilot.app.query_one("#overview")
        
        # Simulate user input
        await pilot.click("#path_input")
        await pilot.press("tab")  # Navigate to next element

# This pattern is straightforward for AI agents to understand and replicate
```

### Recommendation Score: 9/10
**Best choice if:** You want to keep existing code and improve testability  
**Avoid if:** You absolutely need 1.0+ version or have legacy Python (<3.8) requirements

---

## Option 2: Urwid

### Overview
The oldest and most mature Python TUI library (2004+). Powers tools like `wicd`, `pudb`, and various system administration tools.

### Pros

**Maturity:**
- 20+ years of development
- Stable API that rarely breaks
- Proven in production across many projects
- Python 3.9+ support

**Testing:**
- Can create widgets without rendering
- Direct widget state inspection
- Synchronous by default (simpler testing in some cases)

**Reliability:**
- Well-understood limitations and workarounds
- Extensive battle-testing
- Conservative update policy reduces breakage

### Cons

**Outdated Architecture:**
- Callback-based event system (not async/await)
- More verbose API compared to modern frameworks
- Less intuitive widget composition
- Manual layout calculations often needed

**Documentation:**
- Documentation is comprehensive but dated
- Examples use older Python patterns
- Less active community support

**AI Agent Challenges:**
- Callback spaghetti harder to reason about
- More boilerplate code required
- Layout system requires manual calculations

**Migration Cost:**
- **High** - Complete rewrite of UI layer
- Different paradigm (callback vs async)
- Need to rebuild all custom components
- ~2-3 weeks development time

### Testing Example
```python
import urwid

def test_overview():
    # More manual setup required
    text = urwid.Text("Hello")
    assert text.get_text()[0] == "Hello"
    
    # But direct widget access is straightforward
    pile = urwid.Pile([text])
    assert len(pile.contents) == 1
```

### Recommendation Score: 5/10
**Best choice if:** You need maximum stability and don't care about modern features  
**Avoid if:** You want async support or modern Python patterns

---

## Option 3: prompt_toolkit

### Overview
A lower-level library focused on building interactive command-line applications. Powers `ptpython`, `ipython`, and many CLI tools.

### Pros

**Maturity:**
- 10+ years development
- Stable API (v3.0+)
- Used in major projects (IPython, pgcli, mycli)

**Control:**
- Full control over rendering
- Excellent key binding support
- Powerful completion engine
- Both sync and async support

**Testing:**
- Can create components without terminal
- Good separation of concerns
- Pytest compatible

### Cons

**Lower-Level:**
- More code needed for basic UI
- Manual layout management
- No built-in tabbed interface
- Requires more expertise

**Not a Full TUI Framework:**
- Focused on prompts and line editing
- Building complex layouts is tedious
- Missing many widgets (tables, trees, etc.)

**Migration Cost:**
- **Very High** - Near-complete rewrite
- Need to build custom widgets for tabs, tables, etc.
- ~4-6 weeks development time
- Significant ongoing maintenance burden

### Recommendation Score: 3/10
**Best choice if:** You're building a CLI with prompts, not a full TUI  
**Avoid if:** You need complex layouts like Caspoon does

---

## Option 4: Gradio (Web-Based)

### Overview
Modern Python library for creating simple web UIs with minimal code. Primarily used for ML model demos but suitable for any data display.

### Pros

**Simplicity:**
- Minimal code for functional UI
- Automatic layout and styling
- Built-in themes
- Live reload during development

**Testing:**
- Standard web testing (Selenium, Playwright)
- Well-understood testing patterns
- AI agents familiar with web testing

**Deployment:**
- Easy to share (web link)
- No terminal required
- Mobile-friendly

**AI Agent Friendly:**
- Very simple API
- Clear documentation
- Predictable behavior

### Cons

**Web Dependency:**
- Requires browser
- Not a terminal application
- Network dependency (local server)

**Limited Customization:**
- Opinionated layouts
- Hard to match current tab-based design
- Less control over appearance

**Migration Cost:**
- **Medium** - Rewrite UI layer but simpler code
- ~1-2 weeks development
- Need to adapt data flow for web paradigm

### Testing Example
```python
import gradio as gr

def test_interface():
    def analyze(path):
        return {"arch": "x86_64", "bits": 64}
    
    interface = gr.Interface(fn=analyze, inputs="text", outputs="json")
    # Standard web testing tools apply
```

### Recommendation Score: 6/10
**Best choice if:** You want simplest possible UI and web is acceptable  
**Avoid if:** Terminal interface is a requirement

---

## Option 5: Flask/FastAPI + htmx (Web-Based)

### Overview
Build a custom web UI with Python backend and htmx for dynamic updates without full JavaScript framework.

### Pros

**Full Control:**
- Complete customization of appearance
- Modern web stack (htmx is trending)
- Professional appearance
- Can match existing tab layout exactly

**Testing:**
- Flask/FastAPI have excellent test support
- Standard web testing patterns
- Both unit and integration testing straightforward

**Future-Proof:**
- Web technologies are not going away
- Easy to add features (auth, sharing, etc.)
- Mobile support built-in

**AI Agent Friendly:**
- Web testing is well-understood
- Clear request/response model
- Many examples available

### Cons

**Complexity:**
- Need HTML/CSS knowledge
- More moving parts (backend + frontend)
- Deployment more complex than single binary

**Migration Cost:**
- **Very High** - Complete rewrite
- Need to learn htmx patterns
- Create HTML templates
- ~3-4 weeks development time

**Loss of Terminal Identity:**
- No longer a terminal tool
- Requires browser
- Changes project character

### Recommendation Score: 7/10
**Best choice if:** You want professional web UI and are willing to invest time  
**Avoid if:** Terminal interface is core to project identity

---

## Option 6: Other Options (Brief Survey)

### blessed
- Mature (based on blessings)
- Lower-level than Textual but higher than curses
- Limited widgets
- **Score: 4/10** - Less capable than alternatives

### asciimatics
- Animation focus (not ideal for data display)
- Good for games/demos
- Less suitable for serious applications
- **Score: 3/10** - Wrong use case

### npyscreen
- Built on curses
- Not actively maintained
- Outdated patterns
- **Score: 2/10** - Avoid

### PyQt/PySide (Qt for Python)
- Full desktop GUI (not terminal)
- Very mature but heavy dependency
- **Score: N/A** - Different category

### Streamlit
- Similar to Gradio but more opinionated
- Great for data science dashboards
- **Score: 6/10** - Similar to Gradio pros/cons

---

## Testing Comparison Matrix

| Framework | Unit Testing | Integration Testing | UI Testing | Headless Mode | AI Agent Ease |
|-----------|--------------|---------------------|------------|---------------|---------------|
| **Textual** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **Urwid** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ✅ Yes | ⭐⭐⭐ |
| **prompt_toolkit** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ✅ Yes | ⭐⭐⭐ |
| **Gradio** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Browser | ⭐⭐⭐⭐ |
| **Flask+htmx** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Browser | ⭐⭐⭐⭐ |

---

## Recommendations

### Primary Recommendation: Keep Textual ✅

**Action Items:**
1. **Improve Test Coverage**
   - Add unit tests for each view component
   - Use `textual.pilot` for integration tests
   - Test user interactions (click, type, navigate)
   - Remove UI from coverage exclusion once tested

2. **Documentation Improvements**
   - Document component architecture
   - Add inline examples for each view
   - Create testing guide for contributors

3. **Leverage Built-in Features**
   - Use snapshot testing for regression prevention
   - Implement validation patterns
   - Use command palette for advanced features

4. **Future-Proof**
   - Pin to stable 0.4x series
   - Monitor 1.0 release for migration
   - Consider web serving feature for demos

### Alternative Path 1: If Web UI Desired

**Gradio** for quick implementation (1-2 weeks):
```python
import gradio as gr
from caspoon.core.runner import ReconRunner

def analyze_binary(file):
    runner = ReconRunner()
    report = runner.run(file.name)
    return report.to_json()

interface = gr.Interface(
    fn=analyze_binary,
    inputs=gr.File(label="Binary File"),
    outputs=gr.JSON(label="Analysis Report"),
    title="Caspoon Binary Analysis"
)
interface.launch()
```

### Alternative Path 2: If Maximum Control Needed

**Flask + htmx** for production web app (3-4 weeks):
- Full professional appearance
- Complete customization
- Standard web testing

---

## Migration Effort Comparison

| Framework | Code Rewrite | New Concepts | Timeline | Risk |
|-----------|--------------|--------------|----------|------|
| **Keep Textual** | 0% | Testing only | 1 week | Low ⚠️ |
| **Gradio** | 80% | Web paradigm | 2 weeks | Medium ⚠️⚠️ |
| **Urwid** | 100% | Callbacks | 3 weeks | Medium ⚠️⚠️ |
| **Flask+htmx** | 100% | Web stack | 4 weeks | High ⚠️⚠️⚠️ |
| **prompt_toolkit** | 100% | Low-level | 6 weeks | Very High ⚠️⚠️⚠️⚠️ |

---

## Conclusion

**Recommendation: Stay with Textual and invest in testing infrastructure.**

**Rationale:**
1. **Textual is more mature than perceived** - The v0.40+ series is stable and production-ready
2. **Excellent testing support** - Built-in tools designed specifically for TUI testing
3. **AI agent friendly** - Clean API, type hints, good documentation, predictable behavior
4. **Zero migration cost** - Keep existing working code
5. **Future flexibility** - Can serve as web app if needed without code changes
6. **Active ecosystem** - Large community, regular updates, responsive maintainers

**If you must migrate:**
- **For simplicity:** Choose Gradio (web-based, minimal code)
- **For control:** Choose Flask + htmx (web-based, maximum customization)
- **For terminal:** Urwid is the only real alternative (but outdated patterns)

**Next Steps:**
1. Implement comprehensive Textual tests using `textual.pilot`
2. Document testing patterns for future contributors
3. Monitor Textual 1.0 release (likely Q2 2026)
4. Reassess if issues arise during AI agent development

---

## References

- Textual Documentation: https://textual.textualize.io/
- Textual Testing Guide: https://textual.textualize.io/guide/testing/
- Urwid Documentation: http://urwid.org/
- prompt_toolkit Documentation: https://python-prompt-toolkit.readthedocs.io/
- Gradio Documentation: https://gradio.app/
- htmx Documentation: https://htmx.org/

---

**Document Version:** 1.0  
**Last Updated:** February 13, 2026
