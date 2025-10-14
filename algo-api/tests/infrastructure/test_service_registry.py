"""
Tests for the service registry and service configuration.
"""
import pytest
from unittest.mock import patch, MagicMock

from algo.infrastructure.service_registry import ServiceRegistry, service_registry, register_service_instance, get_service
from algo.infrastructure.service_configuration import register_all_services
from algo.domain.services import get_trading_window_service
from algo.domain.trading.trading_window_service import TradingWindowService


class TestServiceRegistry:
    """Test cases for the ServiceRegistry class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear the registry before each test
        service_registry.clear_all()
    
    def test_singleton_behavior(self):
        """Test that ServiceRegistry is a singleton."""
        registry1 = ServiceRegistry()
        registry2 = ServiceRegistry()
        
        assert registry1 is registry2
        assert registry1 is service_registry
    
    def test_register_and_get_instance(self):
        """Test registering and retrieving services via direct instance."""
        
        class TestService:
            def __init__(self, value: str = "test"):
                self.value = value
        
        # Create and register instance
        instance = TestService("direct_instance")
        register_service_instance(TestService, instance)
        
        # Get service
        retrieved = get_service(TestService)
        assert retrieved is instance
        assert retrieved.value == "direct_instance"
        
        # Get service again (should return same instance)
        retrieved2 = get_service(TestService)
        assert retrieved is retrieved2
    
    def test_service_not_registered(self):
        """Test error when trying to get unregistered service."""
        
        class UnregisteredService:
            pass
        
        with pytest.raises(ValueError, match="Service type UnregisteredService is not registered"):
            get_service(UnregisteredService)
    
    def test_is_registered(self):
        """Test checking if service is registered."""
        
        class TestService:
            pass
        
        # Initially not registered
        assert not service_registry.is_registered(TestService)
        
        # Register instance
        register_service_instance(TestService, TestService())
        assert service_registry.is_registered(TestService)
    
    def test_get_registered_services(self):
        """Test getting information about registered services."""
        
        class Service1:
            pass
        
        class Service2:
            pass
        
        # Register services
        register_service_instance(Service1, Service1())
        service_registry.register_instance(Service2, Service2())
        
        # Check both services are registered
        assert service_registry.is_registered(Service1)
        assert service_registry.is_registered(Service2)


class TestServiceConfiguration:
    """Test cases for service configuration."""
    
    def setup_method(self):
        """Set up test environment."""
        service_registry.clear_all()
    
    @patch('algo.infrastructure.service_configuration.Path')
    @patch('algo.infrastructure.service_configuration.json.load')
    @patch('builtins.open')
    def test_register_all_services(self, mock_open, mock_json_load, mock_path):
        """Test registering all services."""
        # Mock configuration directory
        mock_config_dir = MagicMock()
        mock_config_dir.exists.return_value = True
        mock_config_dir.is_dir.return_value = True
        mock_config_dir.glob.return_value = []  # No config files
        
        mock_path.return_value = mock_config_dir
        
        # Register services
        register_all_services()
        
        # Check that TradingWindowService is registered
        assert service_registry.is_registered(TradingWindowService)
        
        # Check that we can get the service
        trading_service = get_service(TradingWindowService)
        assert isinstance(trading_service, TradingWindowService)


class TestServiceAccessors:
    """Test cases for service accessor utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        service_registry.clear_all()
    
    @patch('algo.infrastructure.service_configuration.Path')
    def test_get_trading_window_service(self, mock_path):
        """Test getting TradingWindowService via accessor."""
        # Mock configuration directory
        mock_config_dir = MagicMock()
        mock_config_dir.exists.return_value = True
        mock_config_dir.is_dir.return_value = True
        mock_config_dir.glob.return_value = []  # No config files
        
        mock_path.return_value = mock_config_dir
        
        # Register services
        register_all_services()
        
        # Get service via accessor
        service = get_trading_window_service()
        assert isinstance(service, TradingWindowService)
        
        # Should return same instance on subsequent calls
        service2 = get_trading_window_service()
        assert service is service2
    
    def test_get_trading_window_service_not_registered(self):
        """Test error when TradingWindowService is not registered."""
        with pytest.raises(ValueError, match="Service type TradingWindowService is not registered"):
            get_trading_window_service()


if __name__ == "__main__":
    pytest.main([__file__])
