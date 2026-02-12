from caspoon.core.runner import ReconRunner
import json
import sys

def main():
    if "--ui" in sys.argv:
        from caspoon.ui.app import CaspoonApp
        CaspoonApp().run()
        return

    if len(sys.argv) < 2:
        print("Usage: python -m caspoon <binary>  or  python -m caspoon --ui")
        return

    path = sys.argv[1]
    runner = ReconRunner()
    report = runner.run(path)
    #print(json.dumps(report.pretty(), indent=2))
    print(json.dumps(report.raw_backend_data.get("r2", {}), indent=2))