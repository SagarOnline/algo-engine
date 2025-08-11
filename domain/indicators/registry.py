from typing import Callable, Dict

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

def register_indicator(name: str):
    """Decorator for registering indicator functions."""
    def decorator(func: Callable):
        IndicatorRegistry.register(name, func)
        return func
    return decorator
