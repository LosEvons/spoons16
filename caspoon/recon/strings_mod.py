import subprocess

class StringsRecon:
  name = "strings"

  def run(self, path: str, report):
    result = subprocess.run(
      ["strings", "-n", "4", path],
      capture_output=True, text=True
    ).stdout.splitlines()
    
    report.strings = result
    return report
