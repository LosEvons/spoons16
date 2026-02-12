
from .models import ExecutableReport
from ..recon.file_info import FileInfoRecon
from ..recon.protections import ProtectionsRecon
from ..recon.strings_mod import StringsRecon
from ..recon.imports_exports import ImportExportRecon

class ReconRunner:
    def __init__(self):
        self.steps = [
            FileInfoRecon(),
            ProtectionsRecon(),
            StringsRecon(),
            ImportExportRecon(),
        ]

    def run(self, path: str) -> ExecutableReport:
        report = ExecutableReport(path=path)

        for step in self.steps:
            print("DEBUG: Running: ", step.name)
            report = step.run(path, report)
            print("DEBUG: step returned: ", type(report))
