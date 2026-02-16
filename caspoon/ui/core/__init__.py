"""Core TUI architecture components.

This package provides the foundational components for the TUI redesign:
- State management (AppState, data models)
- Message system (event-driven communication)
- Action registry (command and keybinding management)
- Base widget classes (BaseView, InteractiveView, TableView, TreeView)
"""

from .actions import Action, ActionRegistry
from .base import BaseView, InteractiveView, TableView, TreeNode, TreeView
from .messages import (
    AnalysisComplete,
    AnalysisError,
    AnalysisProgress,
    CloseBinary,
    ExecuteCommand,
    JumpToAddress,
    OpenBinary,
    SelectFunction,
    ShowCommandPalette,
    StartAnalysis,
    SwitchTab,
    TogglePanel,
)
from .models import AnalysisResults, BinaryInfo, UIState, UserPreferences
from .state import AppState

__all__ = [
    # State management
    "AppState",
    "BinaryInfo",
    "AnalysisResults",
    "UIState",
    "UserPreferences",
    # Actions
    "Action",
    "ActionRegistry",
    # Base widgets
    "BaseView",
    "InteractiveView",
    "TableView",
    "TreeView",
    "TreeNode",
    # Messages - Analysis
    "StartAnalysis",
    "AnalysisProgress",
    "AnalysisComplete",
    "AnalysisError",
    # Messages - Navigation
    "SelectFunction",
    "JumpToAddress",
    "SwitchTab",
    # Messages - UI
    "TogglePanel",
    "ShowCommandPalette",
    "ExecuteCommand",
    # Messages - File
    "OpenBinary",
    "CloseBinary",
]
