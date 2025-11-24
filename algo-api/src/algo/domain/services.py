"""
Service accessor utilities for easy access to registered services.
"""
from typing import TypeVar

from algo.domain.service_registry import get_service
from algo.domain.trading.trading_window_service import TradingWindowService

T = TypeVar('T')


def get_trading_window_service() -> TradingWindowService:
    """
    Get the singleton TradingWindowService instance.
    
    Returns:
        The registered TradingWindowService instance
        
    Raises:
        ValueError: If TradingWindowService is not registered
    """
    return get_service(TradingWindowService)


# Example usage functions for other services can be added here
# def get_market_data_service() -> MarketDataService:
#     return get_service(MarketDataService)
#
# def get_order_service() -> OrderService:
#     return get_service(OrderService)
