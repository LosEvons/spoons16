import subprocess
from ..core.models import ExecutableReport, ProtectionInfo

class ProtectionsRecon:
  name = "protections"

  def run(self, path: str, report: ExecutableReport) -> ExecutableReport:
    try:
      result = subprocess.run(
        ["checksec", "--file", path],
        capture_output=True,
        text=True
      ).stdout
    except FileNotFoundError:
      report.protections = ProtectionInfo(relro="checksec_not_found")
      return report

    pi = ProtectionInfo()

    pi.pie = "PIE enabled" in result
    pi.nx = "NX enabled" in result
    pi.canary = "Canary found" in result

    if "Full RELRO" in result:
      pi.relro = "full"
    elif "Partial RELRO" in result:
      pi.relro = "partial"
    else:
      pi.relro = "none"

    report.protections = pi
    return report
