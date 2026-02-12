import subprocess
from ..core.models import ExecutableReport


class FileInfoRecon:
  name = "file_info"

  def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
    result = subprocess.run(
      ["file", path],
      capture_output=True, text=True
    ).stdout.strip()

    report.file_type = result

    # crude heuristics, refine later
    report.arch = "x86_64" if "64-bit" in result else "x86"
    report.bits = 64 if "64-bit" in result else 32
    report.stripped = "not stripped" not in result

    return report
