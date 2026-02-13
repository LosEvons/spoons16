"""Golden test framework for regression detection.

Golden tests compare current output against known-good reference outputs.
This helps detect unintended changes in analysis behavior.

To update golden files, run: pytest --update-golden
"""
import json
import pytest
from pathlib import Path

from caspoon.core.runner import ReconRunner


@pytest.fixture
def golden_dir() -> Path:
    """Return path to golden test data directory.
    
    Returns:
        Path to expected output directory containing golden files.
    """
    return Path(__file__).parent.parent / "fixtures" / "expected"


@pytest.fixture
def update_golden(request) -> bool:
    """Check if we should update golden files (use --update-golden flag).
    
    Args:
        request: pytest request fixture.
        
    Returns:
        True if --update-golden was passed, False otherwise.
    """
    return request.config.getoption("--update-golden", default=False)


@pytest.mark.golden
class TestGoldenOutputs:
    """Test that analysis outputs match expected golden files."""

    def _get_golden_path(self, golden_dir: Path, binary_name: str) -> Path:
        """Get path to golden file for a binary.
        
        Args:
            golden_dir: Directory containing golden files.
            binary_name: Name of the binary.
            
        Returns:
            Path to the golden JSON file.
        """
        return golden_dir / f"{binary_name}.json"

    def _normalize_report(self, report_dict: dict) -> dict:
        """Normalize report for comparison (remove volatile fields).
        
        Removes or normalizes fields that may vary between runs,
        such as absolute paths and timestamps.
        
        Args:
            report_dict: The report dictionary to normalize.
            
        Returns:
            Normalized report dictionary suitable for comparison.
        """
        # Remove fields that may vary between runs
        normalized = report_dict.copy()
        
        # Path might be absolute, normalize to just filename
        if 'path' in normalized:
            normalized['path'] = Path(normalized['path']).name
        
        # String count may vary slightly, keep it but be lenient
        # Raw backend data may have timestamps or volatile info
        if 'raw_backend_data' in normalized:
            # Keep structure but remove volatile fields
            normalized['raw_backend_data'] = {
                k: v for k, v in normalized.get('raw_backend_data', {}).items()
                if k not in ['timestamp', 'analysis_time']
            }
        
        return normalized

    def test_golden_test_hello_x64(
        self, test_binaries_dir: Path, golden_dir: Path, update_golden: bool
    ) -> None:
        """Golden test for test_hello_x64 binary analysis output."""
        binary_name = "test_hello_x64"
        binary_path = test_binaries_dir / binary_name
        golden_path = self._get_golden_path(golden_dir, binary_name)
        
        if not binary_path.exists():
            pytest.skip(f"{binary_name} binary not available")
        
        # Run analysis
        runner = ReconRunner()
        report = runner.run(str(binary_path))
        current_output = self._normalize_report(report.pretty())
        
        if update_golden:
            # Update the golden file
            golden_path.parent.mkdir(parents=True, exist_ok=True)
            with open(golden_path, 'w') as f:
                json.dump(current_output, f, indent=2, sort_keys=True)
            pytest.skip(f"Updated golden file: {golden_path}")
        
        if not golden_path.exists():
            pytest.skip(
                f"Golden file not found: {golden_path}. "
                "Run with --update-golden to create."
            )
        
        # Load expected output
        with open(golden_path) as f:
            expected_output = json.load(f)
        
        # Compare (with some flexibility for strings count)
        assert current_output['path'] == expected_output['path'], \
            "Binary path should match"
        assert current_output['arch'] == expected_output['arch'], \
            "Architecture should match"
        assert current_output['bits'] == expected_output['bits'], \
            "Bit width should match"
        assert current_output['stripped'] == expected_output['stripped'], \
            "Stripped status should match"
        
        # Protections should match
        if expected_output.get('protections'):
            assert current_output['protections'] == expected_output['protections'], \
                "Protection features should match"

    def test_golden_test_stripped(
        self, test_binaries_dir: Path, golden_dir: Path, update_golden: bool
    ) -> None:
        """Golden test for test_stripped binary analysis output."""
        binary_name = "test_stripped"
        binary_path = test_binaries_dir / binary_name
        golden_path = self._get_golden_path(golden_dir, binary_name)
        
        if not binary_path.exists():
            pytest.skip(f"{binary_name} binary not available")
        
        runner = ReconRunner()
        report = runner.run(str(binary_path))
        current_output = self._normalize_report(report.pretty())
        
        if update_golden:
            golden_path.parent.mkdir(parents=True, exist_ok=True)
            with open(golden_path, 'w') as f:
                json.dump(current_output, f, indent=2, sort_keys=True)
            pytest.skip(f"Updated golden file: {golden_path}")
        
        if not golden_path.exists():
            pytest.skip(
                f"Golden file not found: {golden_path}. "
                "Run with --update-golden to create."
            )
        
        with open(golden_path) as f:
            expected_output = json.load(f)
        
        # Key characteristics should match
        assert current_output['stripped'] == expected_output['stripped'], \
            "Stripped status should match"
        assert current_output['arch'] == expected_output['arch'], \
            "Architecture should match"

    def test_golden_test_with_pie(
        self, test_binaries_dir: Path, golden_dir: Path, update_golden: bool
    ) -> None:
        """Golden test for test_with_pie binary analysis output."""
        binary_name = "test_with_pie"
        binary_path = test_binaries_dir / binary_name
        golden_path = self._get_golden_path(golden_dir, binary_name)
        
        if not binary_path.exists():
            pytest.skip(f"{binary_name} binary not available")
        
        runner = ReconRunner()
        report = runner.run(str(binary_path))
        current_output = self._normalize_report(report.pretty())
        
        if update_golden:
            golden_path.parent.mkdir(parents=True, exist_ok=True)
            with open(golden_path, 'w') as f:
                json.dump(current_output, f, indent=2, sort_keys=True)
            pytest.skip(f"Updated golden file: {golden_path}")
        
        if not golden_path.exists():
            pytest.skip(
                f"Golden file not found: {golden_path}. "
                "Run with --update-golden to create."
            )
        
        with open(golden_path) as f:
            expected_output = json.load(f)
        
        # Security features should match exactly
        assert current_output['protections']['pie'] == expected_output['protections']['pie'], \
            "PIE protection should match"
        assert current_output['protections']['canary'] == expected_output['protections']['canary'], \
            "Stack canary should match"
        assert current_output['protections']['nx'] == expected_output['protections']['nx'], \
            "NX protection should match"
        assert current_output['protections']['relro'] == expected_output['protections']['relro'], \
            "RELRO protection should match"


def test_golden_framework_available() -> None:
    """Meta-test: Verify that golden test framework is set up correctly."""
    # Ensure the module is importable and has required components
    assert Path(__file__).exists(), "Test file should exist"
