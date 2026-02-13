# Expected Test Outputs

This directory contains expected outputs from test binaries for comparison in golden tests.

## Golden Tests

Golden tests (also called regression tests) compare current analysis output against
known-good reference outputs. This helps detect unintended changes in analysis behavior.

## Usage

### Running Golden Tests

```bash
# Run all golden tests
pytest -m golden

# Skip golden tests
pytest -m "not golden"
```

### Creating/Updating Golden Files

When you first run golden tests, or when intentional changes are made to analysis output:

```bash
# Update all golden files with current output
pytest tests/integration/test_golden.py --update-golden

# Update specific golden test
pytest tests/integration/test_golden.py::TestGoldenOutputs::test_golden_test_hello_x64 --update-golden
```

## Golden Files

Each test binary has a corresponding `.json` file with expected output:

- `test_hello_x64.json` - Expected output for standard x64 binary
- `test_stripped.json` - Expected output for stripped binary
- `test_with_pie.json` - Expected output for PIE-enabled binary

## File Format

Golden files are JSON format with the following structure:

```json
{
  "path": "test_hello_x64",
  "arch": "x86_64",
  "bits": 64,
  "file_type": "ELF 64-bit LSB executable...",
  "stripped": false,
  "protections": {
    "pie": false,
    "nx": true,
    "canary": false,
    "relro": "partial"
  },
  "imports": ["printf", "..."],
  "exports": ["main", "..."],
  "strings_count": 42
}
```

## Best Practices

1. **Review changes**: When updating golden files, review the diff to ensure changes are intentional
2. **Version control**: Commit golden files to git to track analysis behavior over time
3. **Normalize output**: Golden test framework normalizes volatile fields (timestamps, absolute paths)
4. **Be lenient**: Don't be too strict on fields that naturally vary (e.g., exact string count)

## Regenerating All Golden Files

If you make intentional changes to the analysis pipeline:

```bash
# 1. Update golden files
pytest tests/integration/test_golden.py --update-golden

# 2. Review changes
git diff tests/fixtures/expected/

# 3. If changes look correct, commit them
git add tests/fixtures/expected/
git commit -m "Update golden test outputs for [reason]"
```
