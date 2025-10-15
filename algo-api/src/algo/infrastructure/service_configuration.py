"""
Service configuration and registration module.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

from algo.infrastructure.service_registry import register_service_instance
from algo.domain.trading.trading_window_service import TradingWindowService
from algo.config_context import get_config

logger = logging.getLogger(__name__)


def _create_trading_window_service() -> TradingWindowService:
    """
    Create TradingWindowService instance using application configuration.
    
    Returns:
        Configured TradingWindowService instance
    """
    # Get configuration using existing config context
    config = get_config()
    
    # Get config directory from configuration or use default
    if config and hasattr(config, 'trading_window_config') and config.trading_window_config:
        config_dir = config.trading_window_config.config_dir
    else:
        config_dir = "config/trading_window"
    
    config_path = Path(config_dir)
    
    # Load configuration data from files
    config_data_list = []
    
    if config_path.exists() and config_path.is_dir():
        json_files = list(config_path.glob("*.json"))
        
        for json_file in json_files:
            try:
                logger.debug(f"Loading trading window config from {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                config_data_list.append(config_data)
            except Exception as e:
                logger.error(f"Failed to load trading window config from {json_file}: {e}")
                # Continue loading other files
    
    if not config_data_list:
        logger.warning("No trading window configuration files found, using empty configuration")
    
    logger.info(f"Creating TradingWindowService with {len(config_data_list)} configuration files from {config_dir}")
    return TradingWindowService(config_data_list)


def register_all_services() -> None:
    """
    Register all application services with the service registry.
    
    This function should be called during application startup to ensure
    all services are properly registered and available for dependency injection.
    """
    logger.info("Starting service registration...")
    
    # Create and register TradingWindowService instance
    trading_window_service = _create_trading_window_service()
    register_service_instance(TradingWindowService, trading_window_service)
    logger.info("Registered TradingWindowService instance")
    
    # Add other service registrations here as needed
    # other_service = _create_other_service()
    # register_service_instance(OtherService, other_service)
    
    logger.info("Service registration completed")
