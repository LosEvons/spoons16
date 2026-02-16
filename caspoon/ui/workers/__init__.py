"""Async worker patterns.

This package contains worker classes for async operations:
- Analysis workers (background analysis execution)
- File I/O workers (async file operations)
- Search workers (async search and filtering)
"""

from .analysis import AnalysisWorker
from .base import Worker, WorkerState

__all__ = ["Worker", "WorkerState", "AnalysisWorker"]
