"""Background analysis worker using QRunnable."""

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Signals emitted by AnalysisWorker."""

    progress = Signal(int, str)  # percent, message
    result = Signal(object)      # ExecutableReport
    error = Signal(str)          # error message
    finished = Signal()


class AnalysisWorker(QRunnable):
    """Runs ReconRunner in a background thread via QThreadPool.

    Emits progress updates at key stages and delivers the final
    ExecutableReport (or an error string) via signals.
    """

    def __init__(self, filepath: str, runner) -> None:
        super().__init__()
        self.filepath = filepath
        self.runner = runner
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        try:
            self.signals.progress.emit(5, "Initializing analysis...")
            self.signals.progress.emit(15, f"Loading: {self.filepath}")
            report = self.runner.run(self.filepath)
            self.signals.progress.emit(100, "Analysis complete")
            self.signals.result.emit(report)
        except Exception as e:
            self.signals.error.emit(
                f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            )
        finally:
            self.signals.finished.emit()
