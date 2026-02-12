from caspoon.core.runner import ReconRunner
import json
import sys

def main():
  if len(sys.argv) < 2:
    print("Usage: python -m caspoon <binary>")
    sys.exit(1)

  path = sys.argv[1]
  runner = ReconRunner()
  report = runner.run(path)

  print(json.dumps(report.pretty(), indent=2))

if __name__ == "__main__":
  main()