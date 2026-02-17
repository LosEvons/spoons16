"""Centralized widget ID constants.

All widget IDs used in the TUI are defined here as constants. Both source code
and tests should reference these constants instead of using string literals,
so that renaming an ID is a single-point change.
"""

# Main screen panels
SIDEBAR = "sidebar"
CONTENT = "content"
DETAILS = "details"
CONSOLE = "console"

# Input
PATH_INPUT = "path_input"

# Tabs
TABS = "tabs"
OVERVIEW_TAB = "overview-tab"
PROTECTIONS_TAB = "protections-tab"
STRINGS_TAB = "strings-tab"
IMPORTS_TAB = "imports-tab"
R2_TAB = "r2-tab"

# Views
OVERVIEW_VIEW = "overview"
PROTECTIONS_VIEW = "protections"
STRINGS_VIEW = "strings_view"
IMPORTS_EXPORTS_VIEW = "imp_exp"
R2_VIEW = "r2_view"

# Command palette
COMMAND_PALETTE = "command_palette"
COMMAND_SEARCH = "search"
COMMAND_RESULTS = "results"

# Console internals
CONSOLE_LOG = "console_log"

# Sidebar internals
FUNCTION_EXPLORER = "function_explorer"
FUNCTION_FILTER = "function_filter"

# Details panel internals
DETAILS_CONTENT = "details_content"
