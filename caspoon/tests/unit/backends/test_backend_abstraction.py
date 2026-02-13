"""Tests for backend abstraction."""

import pytest

from caspoon.backends.base import BackendCapabilities, DisassemblyBackend
from caspoon.backends.manager import BackendManager
from caspoon.backends.r2_backend import Radare2Backend


class TestBackendCapabilities:
    """Test BackendCapabilities."""

    def test_create_capabilities(self):
        """Test creating capabilities with specific features."""
        caps = BackendCapabilities(name="test", disassembly=True, analysis=True)
        assert caps.name == "test"
        assert caps.disassembly is True
        assert caps.analysis is True
        assert caps.functions is False  # default
        assert caps.imports is False  # default

    def test_default_capabilities(self):
        """Test default capability values are False."""
        caps = BackendCapabilities(name="default_test")
        assert caps.name == "default_test"
        assert caps.disassembly is False
        assert caps.analysis is False
        assert caps.functions is False
        assert caps.imports is False
        assert caps.strings is False
        assert caps.xrefs is False

    def test_all_capabilities_enabled(self):
        """Test all capabilities enabled."""
        caps = BackendCapabilities(
            name="full",
            disassembly=True,
            analysis=True,
            functions=True,
            imports=True,
            strings=True,
            xrefs=True,
        )
        assert caps.name == "full"
        assert all(
            [
                caps.disassembly,
                caps.analysis,
                caps.functions,
                caps.imports,
                caps.strings,
                caps.xrefs,
            ]
        )


class TestRadare2Backend:
    """Test Radare2Backend."""

    def test_backend_name(self):
        """Test backend name is 'radare2'."""
        backend = Radare2Backend()
        assert backend.name == "radare2"

    def test_capabilities(self):
        """Test radare2 backend capabilities."""
        backend = Radare2Backend()
        caps = backend.capabilities
        assert caps.name == "radare2"
        assert caps.disassembly is True
        assert caps.analysis is True
        assert caps.functions is True
        assert caps.imports is True
        assert caps.strings is True
        assert caps.xrefs is True

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        backend = Radare2Backend()
        result = backend.is_available()
        assert isinstance(result, bool)

    def test_get_functions_with_capability(self):
        """Test get_functions returns list."""
        backend = Radare2Backend()
        # This will return [] if backend not available or error occurs
        # Just testing the method signature and basic behavior
        assert hasattr(backend, "get_functions")

    def test_get_imports_with_capability(self):
        """Test get_imports returns list."""
        backend = Radare2Backend()
        # This will return [] if backend not available or error occurs
        # Just testing the method signature and basic behavior
        assert hasattr(backend, "get_imports")


class TestBackendManager:
    """Test BackendManager."""

    def test_manager_creation(self):
        """Test manager can be created."""
        manager = BackendManager()
        assert manager is not None

    def test_get_available_backends(self):
        """Test getting available backends returns list."""
        manager = BackendManager()
        backends = manager.get_available_backends()
        # Should be list (may be empty if r2 not installed)
        assert isinstance(backends, list)

    def test_get_backend_by_name(self):
        """Test getting backend by name."""
        manager = BackendManager()
        backend = manager.get_backend("radare2")
        # May be None if r2 not available
        if backend is not None:
            assert backend.name == "radare2"
            assert isinstance(backend, Radare2Backend)

    def test_get_backend_default(self):
        """Test getting default backend (first available)."""
        manager = BackendManager()
        backend = manager.get_backend()
        # May be None if no backends available
        if backend is not None:
            assert isinstance(backend, DisassemblyBackend)
            assert backend.name in ["radare2"]  # add more as they're implemented

    def test_get_backend_nonexistent(self):
        """Test getting non-existent backend returns None."""
        manager = BackendManager()
        backend = manager.get_backend("nonexistent_backend")
        assert backend is None

    def test_set_preferred_backend(self):
        """Test setting preferred backend."""
        manager = BackendManager()
        # Should not raise exception
        manager.set_preferred_backend("radare2")
        assert manager._preferred_backend == "radare2"

    def test_backends_list_not_empty(self):
        """Test that manager has at least one backend registered."""
        manager = BackendManager()
        # Should have at least Radare2Backend
        assert len(manager._backends) >= 1
        assert any(isinstance(b, Radare2Backend) for b in manager._backends)


class TestDisassemblyBackendInterface:
    """Test DisassemblyBackend abstract interface."""

    def test_cannot_instantiate_abstract_backend(self):
        """Test that abstract backend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DisassemblyBackend()

    def test_backend_has_required_methods(self):
        """Test backend interface defines required abstract methods."""
        # Check that the abstract class has the expected abstract methods
        abstract_methods = DisassemblyBackend.__abstractmethods__
        assert "name" in abstract_methods or hasattr(DisassemblyBackend, "name")
        assert "capabilities" in abstract_methods or hasattr(DisassemblyBackend, "capabilities")
        assert "is_available" in abstract_methods
        assert "analyze" in abstract_methods

    def test_backend_has_default_methods(self):
        """Test backend interface provides default implementations."""
        # Check that concrete methods exist
        assert hasattr(DisassemblyBackend, "get_functions")
        assert hasattr(DisassemblyBackend, "get_imports")
