"""Integration tests for R2BackendRecon with BackendManager."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from caspoon.backends.r2_recon import R2BackendRecon
from caspoon.backends.manager import BackendManager
from caspoon.backends.r2_backend import Radare2Backend
from caspoon.core.models import ExecutableReport


class TestR2BackendReconIntegration:
    """Test R2BackendRecon integration with BackendManager."""
    
    def test_r2_recon_instantiation(self):
        """Test R2BackendRecon can be instantiated."""
        recon = R2BackendRecon()
        assert recon is not None
        assert recon.name == "r2_backend"
        assert recon.manager is not None
        assert isinstance(recon.manager, BackendManager)
    
    def test_r2_recon_handles_unavailable_backend(self):
        """Test R2BackendRecon handles unavailable backend gracefully."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/tmp/test.bin")
        
        # Mock the manager to return None (backend not available)
        with patch.object(recon.manager, 'get_backend', return_value=None):
            result = recon.run("/tmp/test.bin", report)
            
            assert result is not None
            assert "r2_error" in result.raw_backend_data
            assert "not available" in result.raw_backend_data["r2_error"]
    
    def test_r2_recon_successful_analysis(self):
        """Test R2BackendRecon with successful backend analysis."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/tmp/test.bin")
        
        # Mock backend with successful analysis
        mock_backend = Mock(spec=Radare2Backend)
        mock_backend.analyze.return_value = {
            'functions': [
                {'name': 'main', 'offset': 0x1000},
                {'name': 'helper', 'offset': 0x2000}
            ],
            'imports': ['printf', 'malloc'],
            'strings': ['Hello World']
        }
        
        with patch.object(recon.manager, 'get_backend', return_value=mock_backend):
            result = recon.run("/tmp/test.bin", report)
            
            assert result is not None
            assert "r2" in result.raw_backend_data
            assert len(result.raw_backend_data["r2"]["functions"]) == 2
            assert "r2_error" not in result.raw_backend_data
            mock_backend.analyze.assert_called_once_with("/tmp/test.bin")
    
    def test_r2_recon_handles_file_not_found(self):
        """Test R2BackendRecon handles FileNotFoundError."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/nonexistent/file.bin")
        
        # Mock backend that raises FileNotFoundError
        mock_backend = Mock(spec=Radare2Backend)
        mock_backend.analyze.side_effect = FileNotFoundError("File not found")
        
        with patch.object(recon.manager, 'get_backend', return_value=mock_backend):
            result = recon.run("/nonexistent/file.bin", report)
            
            assert result is not None
            assert "r2_error" in result.raw_backend_data
            assert "File not found" in result.raw_backend_data["r2_error"]
    
    def test_r2_recon_handles_generic_exception(self):
        """Test R2BackendRecon handles generic exceptions."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/tmp/test.bin")
        
        # Mock backend that raises generic exception
        mock_backend = Mock(spec=Radare2Backend)
        mock_backend.analyze.side_effect = RuntimeError("Analysis failed")
        
        with patch.object(recon.manager, 'get_backend', return_value=mock_backend):
            result = recon.run("/tmp/test.bin", report)
            
            assert result is not None
            assert "r2_error" in result.raw_backend_data
            assert "Analysis failed" in result.raw_backend_data["r2_error"]
    
    def test_r2_recon_preserves_existing_report_data(self):
        """Test R2BackendRecon preserves existing report data."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/tmp/test.bin")
        report.raw_backend_data["existing_key"] = "existing_value"
        report.architecture = "x86_64"
        
        # Mock backend with successful analysis
        mock_backend = Mock(spec=Radare2Backend)
        mock_backend.analyze.return_value = {'functions': []}
        
        with patch.object(recon.manager, 'get_backend', return_value=mock_backend):
            result = recon.run("/tmp/test.bin", report)
            
            assert result is not None
            assert result.raw_backend_data["existing_key"] == "existing_value"
            assert result.architecture == "x86_64"
            assert "r2" in result.raw_backend_data
    
    def test_r2_recon_empty_analysis_result(self):
        """Test R2BackendRecon handles empty analysis results."""
        recon = R2BackendRecon()
        report = ExecutableReport(path="/tmp/test.bin")
        
        # Mock backend with empty analysis
        mock_backend = Mock(spec=Radare2Backend)
        mock_backend.analyze.return_value = {}
        
        with patch.object(recon.manager, 'get_backend', return_value=mock_backend):
            result = recon.run("/tmp/test.bin", report)
            
            assert result is not None
            assert "r2" in result.raw_backend_data
            assert result.raw_backend_data["r2"] == {}
            assert "r2_error" not in result.raw_backend_data


class TestBackendManagerIntegration:
    """Test BackendManager integration scenarios."""
    
    def test_manager_with_multiple_backends(self):
        """Test manager with multiple backend instances."""
        manager = BackendManager()
        
        # Should have at least Radare2Backend
        assert len(manager._backends) >= 1
        assert any(isinstance(b, Radare2Backend) for b in manager._backends)
    
    def test_manager_get_available_backends_filters_unavailable(self):
        """Test get_available_backends filters out unavailable backends."""
        manager = BackendManager()
        
        # Mock one backend as available, others as unavailable
        with patch.object(Radare2Backend, 'is_available', return_value=False):
            available = manager.get_available_backends()
            # When r2 is not available, should return empty list
            assert isinstance(available, list)
    
    def test_manager_get_backend_returns_first_available(self):
        """Test get_backend returns first available when no name specified."""
        manager = BackendManager()
        
        # Mock r2 as available
        with patch.object(Radare2Backend, 'is_available', return_value=True):
            backend = manager.get_backend()
            assert backend is not None
            assert isinstance(backend, Radare2Backend)
    
    def test_manager_get_backend_by_specific_name(self):
        """Test get_backend returns specific backend by name."""
        manager = BackendManager()
        
        with patch.object(Radare2Backend, 'is_available', return_value=True):
            backend = manager.get_backend("radare2")
            assert backend is not None
            assert backend.name == "radare2"
    
    def test_manager_preferred_backend_setting(self):
        """Test setting and using preferred backend."""
        manager = BackendManager()
        manager.set_preferred_backend("radare2")
        assert manager._preferred_backend == "radare2"
    
    def test_manager_logs_warning_for_unavailable_backend(self, caplog):
        """Test manager logs warning when requested backend unavailable."""
        import logging
        manager = BackendManager()
        
        with caplog.at_level(logging.WARNING):
            backend = manager.get_backend("nonexistent_backend")
            assert backend is None
            assert "not available" in caplog.text.lower()
    
    def test_manager_logs_error_for_no_backends(self, caplog):
        """Test manager logs error when no backends available."""
        import logging
        manager = BackendManager()
        
        # Mock all backends as unavailable
        with patch.object(Radare2Backend, 'is_available', return_value=False):
            with caplog.at_level(logging.ERROR):
                backend = manager.get_backend()
                assert backend is None


class TestR2BackendFunctionality:
    """Test R2Backend specific functionality."""
    
    def test_r2_backend_properties(self):
        """Test R2Backend exposes correct properties."""
        backend = Radare2Backend()
        
        assert backend.name == "radare2"
        
        caps = backend.capabilities
        assert caps.name == "radare2"
        assert caps.disassembly is True
        assert caps.analysis is True
        assert caps.functions is True
        assert caps.imports is True
        assert caps.strings is True
        assert caps.xrefs is True
    
    def test_r2_backend_is_available_checks_r2pipe(self):
        """Test is_available properly checks for r2pipe."""
        backend = Radare2Backend()
        
        # Should return boolean regardless of availability
        result = backend.is_available()
        assert isinstance(result, bool)
    
    def test_r2_backend_analyze_signature(self):
        """Test analyze method has correct signature."""
        backend = Radare2Backend()
        
        # Should have analyze method
        assert hasattr(backend, 'analyze')
        assert callable(backend.analyze)
