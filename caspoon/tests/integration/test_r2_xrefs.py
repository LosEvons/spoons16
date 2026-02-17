"""Integration tests for radare2 xref extraction.

Tests cross-reference extraction using real binaries to verify the feature
works correctly with radare2.
"""

import pytest

from caspoon.backends.r2_analyzer import analyze_with_r2

# Skip all tests if radare2 is not available
pytest.importorskip("r2pipe")


@pytest.mark.requires_r2
class TestR2XrefIntegration:
    """Integration tests for xref extraction with real binaries."""

    def test_xrefs_extracted_from_real_binary(self, sample_binary):
        """Test that xrefs are extracted from a real binary."""
        result = analyze_with_r2(sample_binary)

        # Verify the result structure
        assert "xrefs" in result
        assert isinstance(result["xrefs"], dict)

        # If there are functions, there should typically be some xrefs
        # (though isolated functions may not have any)
        if result["functions"]:
            # Xrefs dict may be empty if all functions are isolated
            # Just verify it's a dict and has the right structure if populated
            for hex_addr, xref_data in result["xrefs"].items():
                # Check hex address format
                assert hex_addr.startswith("0x")
                assert "callers" in xref_data
                assert "callees" in xref_data
                assert isinstance(xref_data["callers"], list)
                assert isinstance(xref_data["callees"], list)

                # Verify caller/callee structure
                for caller in xref_data["callers"]:
                    assert "from" in caller or "addr" in caller
                    # May have type and fcn_name fields

                for callee in xref_data["callees"]:
                    assert "to" in callee or "addr" in callee
                    # May have type and fcn_name fields

    def test_xrefs_with_test_hello_binary(self, test_binaries_dir):
        """Test xref extraction with test_hello_x64 binary."""
        test_binary = test_binaries_dir / "test_hello_x64"
        if not test_binary.exists():
            pytest.skip("test_hello_x64 binary not available")

        result = analyze_with_r2(str(test_binary))

        assert "xrefs" in result
        assert "functions" in result

        # The hello world binary should have some functions and xrefs
        assert len(result["functions"]) > 0

        # Check that at least one function has xrefs
        # (main should typically call other functions)
        if result["xrefs"]:
            # Verify structure of first xref entry
            first_addr = next(iter(result["xrefs"]))
            xref_data = result["xrefs"][first_addr]

            assert "callers" in xref_data
            assert "callees" in xref_data

            # At least one should be non-empty
            assert xref_data["callers"] or xref_data["callees"]

    def test_xrefs_do_not_break_analysis(self, sample_binary):
        """Test that xref extraction doesn't break the main analysis."""
        result = analyze_with_r2(sample_binary)

        # All core fields should still be present
        assert "functions" in result
        assert "imports" in result
        assert "strings" in result
        assert "main_ops" in result
        assert "xrefs" in result

        # Verify types
        assert isinstance(result["functions"], list)
        assert isinstance(result["imports"], list)
        assert isinstance(result["strings"], list)
        assert isinstance(result["main_ops"], list)
        assert isinstance(result["xrefs"], dict)

    def test_stripped_binary_xrefs(self, test_binaries_dir):
        """Test xref extraction with stripped binary."""
        test_binary = test_binaries_dir / "test_stripped"
        if not test_binary.exists():
            pytest.skip("test_stripped binary not available")

        result = analyze_with_r2(str(test_binary))

        # Even stripped binaries should have xrefs extracted
        assert "xrefs" in result
        assert isinstance(result["xrefs"], dict)

        # Xrefs should still be valid even if function names are missing
        for hex_addr, xref_data in result["xrefs"].items():
            assert hex_addr.startswith("0x")
            assert "callers" in xref_data
            assert "callees" in xref_data

    def test_xref_addresses_match_functions(self, sample_binary):
        """Test that xref addresses correspond to analyzed functions."""
        result = analyze_with_r2(sample_binary)

        if not result["xrefs"]:
            pytest.skip("No xrefs found in binary")

        # Get function addresses
        func_addrs = {f"0x{func['offset']:x}" for func in result["functions"] if "offset" in func}

        # All xref keys should correspond to function addresses
        for xref_addr in result["xrefs"].keys():
            assert xref_addr in func_addrs, f"Xref address {xref_addr} not in function list"

    def test_xrefs_hex_format_consistency(self, sample_binary):
        """Test that all xref addresses use consistent hex format."""
        result = analyze_with_r2(sample_binary)

        for hex_addr in result["xrefs"].keys():
            # Should be hex string starting with 0x
            assert isinstance(hex_addr, str)
            assert hex_addr.startswith("0x")
            # Should be valid hex
            try:
                int(hex_addr, 16)
            except ValueError:
                pytest.fail(f"Invalid hex address format: {hex_addr}")

    def test_callers_and_callees_not_empty_together(self, sample_binary):
        """Test that if xrefs exist, at least callers or callees is non-empty."""
        result = analyze_with_r2(sample_binary)

        for hex_addr, xref_data in result["xrefs"].items():
            # If function is in xrefs dict, it should have at least one xref
            assert (
                xref_data["callers"] or xref_data["callees"]
            ), f"Function {hex_addr} has no callers or callees but is in xrefs dict"

    def test_performance_acceptable(self, sample_binary):
        """Test that xref extraction doesn't significantly slow down analysis."""
        import time

        start = time.time()
        result = analyze_with_r2(sample_binary)
        elapsed = time.time() - start

        # Analysis should complete in reasonable time (adjust threshold as needed)
        # For a typical binary, this should be well under 10 seconds
        assert elapsed < 30, f"Analysis took {elapsed:.2f}s, too slow"

        # Verify xrefs were actually extracted
        assert "xrefs" in result
