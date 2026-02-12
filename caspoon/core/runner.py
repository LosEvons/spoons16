from .models import ExecutableReport
from ..recon.file_info import FileInfoRecon
from ..recon.protections import ProtectionsRecon
from ..recon.strings_mod import StringsRecon
from ..recon.imports_exports import ImportExportRecon
from ..backends.r2_recon import R2BackendRecon

class ReconRunner:
  def __init__(self):
    self.steps = [
      FileInfoRecon(),
      ProtectionsRecon(),
      StringsRecon(),
      ImportExportRecon(),
      R2BackendRecon(),
    ]

  def run(self, path: str) -> ExecutableReport:
    report = ExecutableReport(path=path)

    for step in self.steps:
      print(f"[DEBUG]: Running step {step.name}")
      report = step.run(path, report)
    return report