"""
Service registry for managing singleton services across the application.
"""
import logging
from typing import Dict, Type, TypeVar, Optional
from threading import Lock

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceRegistry:
    """
    Thread-safe singleton service registry for dependency injection.
    
    This registry manages singleton instances of services throughout the application lifecycle.
    """
    
    _instance: Optional['ServiceRegistry'] = None
    _lock = Lock()
    
    def __new__(cls) -> 'ServiceRegistry':
        """Ensure only one instance of ServiceRegistry exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the service registry."""
        if not hasattr(self, '_initialized'):
            self._services: Dict[Type[T], T] = {}
            self._service_lock = Lock()
            self._initialized = True
            logger.info("ServiceRegistry initialized")
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Register a specific instance for a service type.
        
        Args:
            service_type: The type/class of the service
            instance: The singleton instance to register
        """
        with self._service_lock:
            self._services[service_type] = instance
            logger.debug(f"Registered instance for service type: {service_type.__name__}")
    
    def get_service(self, service_type: Type[T]) -> T:
        """
        Get a singleton instance of the specified service type.
        
        Args:
            service_type: The type/class of the service to retrieve
            
        Returns:
            The singleton instance of the service
            
        Raises:
            ValueError: If the service type is not registered
        """
        with self._service_lock:
            if service_type in self._services:
                return self._services[service_type]
            
            raise ValueError(f"Service type {service_type.__name__} is not registered")
    
    def is_registered(self, service_type: Type[T]) -> bool:
        """
        Check if a service type is registered.
        
        Args:
            service_type: The type/class to check
            
        Returns:
            True if the service type is registered, False otherwise
        """
        with self._service_lock:
            return service_type in self._services
    
    def clear_all(self) -> None:
        """
        Clear all registered services.
        
        Warning: This method is primarily for testing purposes.
        """
        with self._service_lock:
            self._services.clear()
            logger.warning("All services cleared from registry")


# Global service registry instance
service_registry = ServiceRegistry()


def register_service_instance(service_type: Type[T], instance: T) -> None:
    """
    Convenience function to register a service instance.
    
    Args:
        service_type: The type/class of the service
        instance: The singleton instance to register
    """
    service_registry.register_instance(service_type, instance)


def get_service(service_type: Type[T]) -> T:
    """
    Convenience function to get a service instance.
    
    Args:
        service_type: The type/class of the service to retrieve
        
    Returns:
        The singleton instance of the service
    """
    return service_registry.get_service(service_type)
