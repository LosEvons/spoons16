"""Data models for TUI state management.

This module defines immutable dataclasses for UI-specific data structures.
These models are used by AppState to maintain reactive application state.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BinaryInfo:
    """Binary metadata.

    Attributes:
        path: Full path to the binary file
        architecture: CPU architecture (e.g., x86_64, ARM, MIPS)
        bits: Bit width (32 or 64), 0 if unknown
        file_type: File type description from format detection
        stripped: Whether debug symbols are stripped
        file_size: Size of binary in bytes
        entry_point: Entry point address (hex string or None)
    """

    path: str
    architecture: str = "unknown"
    bits: int = 0
    file_type: str = "unknown"
    stripped: bool = False
    file_size: int = 0
    entry_point: str | None = None


@dataclass(frozen=True)
class AnalysisResults:
    """Analysis results from binary reconnaissance.

    Attributes:
        functions: List of function names or FunctionInfo objects
        strings: List of extracted strings from binary
        imports: List of imported function names
        exports: List of exported function names
        sections: List of section names or section data
        protections: Security protections dictionary (PIE, NX, Canary, RELRO)
        disassembly: Disassembly data (format depends on backend)
    """

    functions: list[Any] = field(default_factory=list)
    strings: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    sections: list[Any] = field(default_factory=list)
    protections: dict[str, Any] = field(default_factory=dict)
    disassembly: Any | None = None


@dataclass
class UIState:
    """Current UI state.

    Note: This is mutable to allow incremental updates during analysis.

    Attributes:
        is_analyzing: Whether analysis is currently in progress
        analysis_progress: Progress percentage (0.0 to 100.0)
        analysis_message: Current analysis status message
        selected_function: Currently selected function name
        selected_address: Currently selected address (hex string or None)
        active_tab: Currently active tab ID (e.g., "functions", "strings")
        panels_visible: Dictionary of panel visibility states
    """

    is_analyzing: bool = False
    analysis_progress: float = 0.0
    analysis_message: str = ""
    selected_function: str | None = None
    selected_address: str | None = None
    active_tab: str = "functions"
    panels_visible: dict[str, bool] = field(
        default_factory=lambda: {
            "sidebar": True,
            "details": True,
            "bottom": False,
        }
    )


@dataclass
class UserPreferences:
    """User preferences and settings.

    Attributes:
        theme: Color theme name (e.g., "dark", "light", "monokai")
        show_addresses: Whether to show memory addresses in views
        auto_analyze: Whether to automatically start analysis on file open
        max_strings: Maximum number of strings to display
        show_line_numbers: Whether to show line numbers in code views
        font_size: Preferred font size (for terminal-aware displays)
    """

    theme: str = "dark"
    show_addresses: bool = True
    auto_analyze: bool = True
    max_strings: int = 1000
    show_line_numbers: bool = True
    font_size: int = 12
