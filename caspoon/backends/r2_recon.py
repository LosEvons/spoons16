from typing import Optional
from ..core.models import ExecutableReport

def _try_import_r2pipe():
    try:
        import r2pipe
        return True
    except ImportError:
        return False


class R2BackendRecon:
    name = "r2_backend"

    def __init__(self):
        self.r2_available: bool = _try_import_r2pipe()

    def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
        if not self.r2_available:
            report.raw_backend_data["r2_error"] = "r2pipe not installed"
            return report

        from .r2_analyzer import analyze_with_r2

        try:
            data = analyze_with_r2(path)
            report.raw_backend_data["r2"] = data
        except Exception as e:
            report.raw_backend_data["r2_error"] = str(e)

        return report
