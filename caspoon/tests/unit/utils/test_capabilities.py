"""Tests for capability detection."""

import pytest

from caspoon.utils.capabilities import Capabilities, get_capabilities


class TestCapabilities:
    """Test the Capabilities class."""

    def test_init(self):
        """Test that Capabilities initializes successfully."""
        caps = Capabilities()
        assert caps is not None
        assert isinstance(caps._capabilities, dict)

    def test_get_all(self):
        """Test get_all returns all capabilities."""
        caps = Capabilities()
        all_caps = caps.get_all()

        assert isinstance(all_caps, dict)
        # Check that expected capabilities are present
        expected_keys = [
            "windows_pe",
            "capstone",
            "yara",
            "advanced_math",
            "graphs",
            "reports",
        ]
        for key in expected_keys:
            assert key in all_caps
            assert isinstance(all_caps[key], bool)

    def test_has(self):
        """Test has method for checking specific capabilities."""
        caps = Capabilities()

        # Test with valid capabilities
        result = caps.has("windows_pe")
        assert isinstance(result, bool)

        result = caps.has("capstone")
        assert isinstance(result, bool)

        # Test with invalid capability
        result = caps.has("nonexistent_feature")
        assert result is False

    def test_get_missing(self):
        """Test get_missing returns list of missing capabilities."""
        caps = Capabilities()
        missing = caps.get_missing()

        assert isinstance(missing, list)
        # All items in missing should be valid capability names
        all_caps = caps.get_all()
        for item in missing:
            assert item in all_caps
            assert all_caps[item] is False

    def test_print_summary(self, capsys):
        """Test print_summary produces output."""
        caps = Capabilities()
        caps.print_summary()

        captured = capsys.readouterr()
        assert "Caspoon Optional Features:" in captured.out
        # Should contain at least some capability names
        assert any(
            cap in captured.out
            for cap in ["windows_pe", "capstone", "yara", "advanced_math", "graphs", "reports"]
        )

    def test_singleton(self):
        """Test that get_capabilities returns the same instance."""
        caps1 = get_capabilities()
        caps2 = get_capabilities()

        assert caps1 is caps2

    def test_detection_doesnt_crash(self):
        """Test that detection methods don't crash even if imports fail."""
        caps = Capabilities()

        # All detection should complete without exceptions
        assert caps._check_pefile() in (True, False)
        assert caps._check_capstone() in (True, False)
        assert caps._check_yara() in (True, False)
        assert caps._check_scipy() in (True, False)
        assert caps._check_networkx() in (True, False)
        assert caps._check_jinja2() in (True, False)

    def test_core_dependencies_dont_affect_capabilities(self):
        """Test that missing optional deps don't break core functionality."""
        caps = Capabilities()
        all_caps = caps.get_all()

        # Should always return results, even if some are False
        assert len(all_caps) > 0
        assert all(isinstance(v, bool) for v in all_caps.values())
