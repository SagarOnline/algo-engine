from typing import Callable, Dict, List

class IndicatorRegistry:
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable):
        cls._registry[name] = func

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._registry:
            raise ValueError(f"Indicator '{name}' not registered")
        return cls._registry[name]
    
    @classmethod
    def list_indicators(cls) -> List[str]:
        """Return a list of all registered indicator names."""
        return list(cls._registry.keys())

def register_indicator(name: str):
    """Decorator for registering indicator functions."""
    def decorator(func: Callable):
        IndicatorRegistry.register(name, func)
        return func
    return decorator

def get_indicator(name: str) -> Callable:
    """Get a registered indicator by name."""
    return IndicatorRegistry.get(name)

def list_indicators() -> List[str]:
    """List all registered indicator names."""
    return IndicatorRegistry.list_indicators()
