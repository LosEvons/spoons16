"""Unit tests for assembly syntax highlighter LRU caching."""

import pytest
from rich.text import Text

from caspoon.ui.syntax import AsmHighlighter, ColorScheme


class TestHighlighterCaching:
    """Tests for LRU cache functionality in the highlighter."""

    def test_cache_enabled_by_default(self):
        """Test that cache is enabled by default."""
        highlighter = AsmHighlighter()
        assert highlighter._cache_enabled is True
        assert highlighter._cache_size == 1000

    def test_cache_custom_size(self):
        """Test creating highlighter with custom cache size."""
        highlighter = AsmHighlighter(cache_size=500)
        assert highlighter._cache_size == 500
        
        # Verify the cache was created with correct size
        info = highlighter.get_cache_info()
        assert info['maxsize'] == 500

    def test_cache_hit_improves_performance(self):
        """Test that cache provides hits for repeated instructions."""
        highlighter = AsmHighlighter()
        
        # First call - should be a cache miss
        result1 = highlighter.highlight_instruction("mov rax, rbx")
        info = highlighter.get_cache_info()
        assert info['misses'] == 1
        assert info['hits'] == 0
        
        # Second call with same instruction - should be a cache hit
        result2 = highlighter.highlight_instruction("mov rax, rbx")
        info = highlighter.get_cache_info()
        assert info['misses'] == 1
        assert info['hits'] == 1
        
        # Results should be equivalent
        assert str(result1) == str(result2)
        assert result1.plain == result2.plain

    def test_cache_different_instructions(self):
        """Test that different instructions create different cache entries."""
        highlighter = AsmHighlighter()
        
        # Call with different instructions
        highlighter.highlight_instruction("mov rax, rbx")
        highlighter.highlight_instruction("push rbp")
        highlighter.highlight_instruction("pop rbp")
        
        info = highlighter.get_cache_info()
        assert info['misses'] == 3
        assert info['hits'] == 0
        assert info['size'] == 3

    def test_cache_with_addresses(self):
        """Test that addresses are included in cache key."""
        highlighter = AsmHighlighter()
        
        # Same instruction, different addresses - should be separate cache entries
        result1 = highlighter.highlight_instruction("mov rax, rbx", "0x1000")
        result2 = highlighter.highlight_instruction("mov rax, rbx", "0x2000")
        result3 = highlighter.highlight_instruction("mov rax, rbx", "0x1000")
        
        info = highlighter.get_cache_info()
        assert info['misses'] == 2  # Two unique (instruction, address) pairs
        assert info['hits'] == 1    # Third call matches first
        assert info['size'] == 2
        
        # Results should differ for different addresses
        assert str(result1) != str(result2)
        assert str(result1) == str(result3)

    def test_cache_clear(self):
        """Test clearing the cache."""
        highlighter = AsmHighlighter()
        
        # Populate cache
        for i in range(5):
            highlighter.highlight_instruction(f"mov r{i}, r{i+1}")
        
        info = highlighter.get_cache_info()
        assert info['size'] == 5
        assert info['misses'] == 5
        
        # Clear cache
        highlighter.clear_cache()
        
        info = highlighter.get_cache_info()
        assert info['size'] == 0
        assert info['hits'] == 0
        assert info['misses'] == 0

    def test_disable_cache(self):
        """Test disabling the cache."""
        highlighter = AsmHighlighter()
        
        # Disable cache
        highlighter.disable_cache()
        assert highlighter._cache_enabled is False
        
        # Call same instruction twice
        result1 = highlighter.highlight_instruction("mov rax, rbx")
        result2 = highlighter.highlight_instruction("mov rax, rbx")
        
        # Cache should not be used (no hits)
        info = highlighter.get_cache_info()
        assert info['hits'] == 0
        assert info['misses'] == 0
        
        # Results should still be equivalent
        assert str(result1) == str(result2)

    def test_enable_cache(self):
        """Test re-enabling the cache after disabling."""
        highlighter = AsmHighlighter()
        
        # Disable then re-enable
        highlighter.disable_cache()
        highlighter.enable_cache()
        
        assert highlighter._cache_enabled is True
        
        # Verify caching works
        highlighter.highlight_instruction("mov rax, rbx")
        highlighter.highlight_instruction("mov rax, rbx")
        
        info = highlighter.get_cache_info()
        assert info['hits'] == 1

    def test_enable_cache_with_new_size(self):
        """Test changing cache size when re-enabling."""
        highlighter = AsmHighlighter(cache_size=1000)
        
        # Change size
        highlighter.enable_cache(size=100)
        
        assert highlighter._cache_size == 100
        info = highlighter.get_cache_info()
        assert info['maxsize'] == 100

    def test_cache_eviction(self):
        """Test that cache evicts old entries when full."""
        # Create small cache
        highlighter = AsmHighlighter(cache_size=5)
        
        # Fill cache
        for i in range(5):
            highlighter.highlight_instruction(f"mov r{i}, r{i+1}")
        
        info = highlighter.get_cache_info()
        assert info['size'] == 5
        
        # Add one more - should evict oldest
        highlighter.highlight_instruction("push rbp")
        
        info = highlighter.get_cache_info()
        assert info['size'] == 5  # Still at max size
        assert info['misses'] == 6

    def test_cache_with_comments(self):
        """Test that comments are properly cached."""
        highlighter = AsmHighlighter()
        
        result1 = highlighter.highlight_instruction("mov rax, rbx ; load value")
        result2 = highlighter.highlight_instruction("mov rax, rbx ; load value")
        
        info = highlighter.get_cache_info()
        assert info['hits'] == 1
        assert str(result1) == str(result2)

    def test_cache_with_legacy_mode(self):
        """Test that caching works with legacy (non-operand-parsing) mode."""
        highlighter = AsmHighlighter(enable_operand_parsing=False)
        
        result1 = highlighter.highlight_instruction("mov rax, rbx")
        result2 = highlighter.highlight_instruction("mov rax, rbx")
        
        info = highlighter.get_cache_info()
        assert info['hits'] == 1
        assert str(result1) == str(result2)

    def test_cache_info_structure(self):
        """Test the structure of cache info dictionary."""
        highlighter = AsmHighlighter()
        
        info = highlighter.get_cache_info()
        
        assert 'hits' in info
        assert 'misses' in info
        assert 'size' in info
        assert 'maxsize' in info
        
        assert isinstance(info['hits'], int)
        assert isinstance(info['misses'], int)
        assert isinstance(info['size'], int)
        assert isinstance(info['maxsize'], int)

    def test_cache_with_complex_operands(self):
        """Test caching with complex memory operands."""
        highlighter = AsmHighlighter()
        
        instruction = "mov qword ptr [rbp-0x10], rax"
        
        result1 = highlighter.highlight_instruction(instruction)
        result2 = highlighter.highlight_instruction(instruction)
        result3 = highlighter.highlight_instruction(instruction)
        
        info = highlighter.get_cache_info()
        assert info['misses'] == 1
        assert info['hits'] == 2
        
        # All results should be identical
        assert str(result1) == str(result2) == str(result3)

    def test_cache_preserves_rich_formatting(self):
        """Test that cached results preserve Rich text formatting."""
        highlighter = AsmHighlighter()
        
        # Get fresh result
        result_fresh = highlighter.highlight_instruction("call printf", "0x1000")
        
        # Get cached result
        result_cached = highlighter.highlight_instruction("call printf", "0x1000")
        
        # Both should be Rich Text objects with formatting
        assert isinstance(result_fresh, Text)
        assert isinstance(result_cached, Text)
        
        # Content should be identical
        assert result_fresh.plain == result_cached.plain
        assert str(result_fresh) == str(result_cached)
        
        # Verify it actually hit the cache
        info = highlighter.get_cache_info()
        assert info['hits'] >= 1

    def test_multiple_highlighters_independent_caches(self):
        """Test that multiple highlighter instances have independent caches."""
        highlighter1 = AsmHighlighter()
        highlighter2 = AsmHighlighter()
        
        # Use first highlighter
        highlighter1.highlight_instruction("mov rax, rbx")
        highlighter1.highlight_instruction("mov rax, rbx")
        
        info1 = highlighter1.get_cache_info()
        info2 = highlighter2.get_cache_info()
        
        # First should have cache activity
        assert info1['hits'] == 1
        assert info1['misses'] == 1
        
        # Second should be empty
        assert info2['hits'] == 0
        assert info2['misses'] == 0

    def test_cache_verifies_hits(self):
        """Test that cache properly records hits for repeated calls."""
        highlighter = AsmHighlighter()
        highlighter.clear_cache()
        
        # Make 100 calls to the same instruction
        for _ in range(100):
            highlighter.highlight_instruction("mov rax, [rbp-0x10]")
        
        # Verify cache was actually used
        info = highlighter.get_cache_info()
        assert info['hits'] == 99  # First is miss, rest are hits
        assert info['misses'] == 1
        assert info['size'] == 1

    def test_cache_with_empty_instruction(self):
        """Test caching behavior with empty instructions."""
        highlighter = AsmHighlighter()
        
        result1 = highlighter.highlight_instruction("")
        result2 = highlighter.highlight_instruction("")
        
        info = highlighter.get_cache_info()
        assert info['hits'] == 1
        assert str(result1) == str(result2)

    def test_cache_with_whitespace_variations(self):
        """Test that whitespace variations create separate cache entries."""
        highlighter = AsmHighlighter()
        
        # Different whitespace should be different cache keys
        result1 = highlighter.highlight_instruction("mov  rax, rbx")
        result2 = highlighter.highlight_instruction("mov rax,rbx")
        result3 = highlighter.highlight_instruction("mov  rax, rbx")
        
        info = highlighter.get_cache_info()
        assert info['misses'] == 2
        assert info['hits'] == 1
        
        # First and third should match
        assert str(result1) == str(result3)
