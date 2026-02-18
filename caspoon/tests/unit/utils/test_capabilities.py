"""Tests for capability detection."""

import sys
from unittest.mock import MagicMock, patch

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

    def test_check_pefile_when_available(self):
        """Test _check_pefile returns True when pefile is available."""
        caps = Capabilities()
        # Mock successful import
        with patch.dict(sys.modules, {"pefile": MagicMock()}):
            result = caps._check_pefile()
            assert result is True

    def test_check_capstone_when_available(self):
        """Test _check_capstone returns True when capstone is available."""
        caps = Capabilities()
        with patch.dict(sys.modules, {"capstone": MagicMock()}):
            result = caps._check_capstone()
            assert result is True

    def test_check_yara_when_available(self):
        """Test _check_yara returns True when yara is available."""
        caps = Capabilities()
        with patch.dict(sys.modules, {"yara": MagicMock()}):
            result = caps._check_yara()
            assert result is True

    def test_check_scipy_when_available(self):
        """Test _check_scipy returns True when scipy is available."""
        caps = Capabilities()
        with patch.dict(sys.modules, {"scipy": MagicMock()}):
            result = caps._check_scipy()
            assert result is True

    def test_check_networkx_when_available(self):
        """Test _check_networkx returns True when networkx is available."""
        caps = Capabilities()
        with patch.dict(sys.modules, {"networkx": MagicMock()}):
            result = caps._check_networkx()
            assert result is True

    def test_check_jinja2_when_available(self):
        """Test _check_jinja2 returns True when jinja2 is available."""
        caps = Capabilities()
        with patch.dict(sys.modules, {"jinja2": MagicMock()}):
            result = caps._check_jinja2()
            assert result is True

    def test_print_summary_all_features_installed(self, capsys):
        """Test print_summary when all features are installed."""
        caps = Capabilities()
        # Mock all capabilities as available
        caps._capabilities = {
            "windows_pe": True,
            "capstone": True,
            "yara": True,
            "advanced_math": True,
            "graphs": True,
            "reports": True,
        }

        caps.print_summary()

        captured = capsys.readouterr()
        assert "All optional features are installed!" in captured.out
        # Should not show installation instructions when all are available
        assert "To install missing features:" not in captured.out

    def test_print_summary_some_features_missing(self, capsys):
        """Test print_summary when some features are missing."""
        caps = Capabilities()
        # Mock some capabilities as missing
        caps._capabilities = {
            "windows_pe": False,
            "capstone": True,
            "yara": False,
            "advanced_math": True,
            "graphs": False,
            "reports": True,
        }

        caps.print_summary()

        captured = capsys.readouterr()
        # Should show installation instructions when some are missing
        assert "To install missing features:" in captured.out
        assert "pip install caspoon[all]" in captured.out
        assert "pip install caspoon[windows]" in captured.out

    def test_detect_all_populates_all_capabilities(self):
        """Test that _detect_all populates all expected capabilities."""
        caps = Capabilities()

        assert "radare2" in caps._capabilities
        assert "windows_pe" in caps._capabilities
        assert "capstone" in caps._capabilities
        assert "yara" in caps._capabilities
        assert "advanced_math" in caps._capabilities
        assert "graphs" in caps._capabilities
        assert "reports" in caps._capabilities
        assert len(caps._capabilities) == 7
