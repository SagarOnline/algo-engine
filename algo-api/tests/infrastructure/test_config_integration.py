"""
Tests for configuration integration with service registry.
"""
import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from algo.domain.config import Config, TradingWindowConfig, SpecialDayConfig, BacktestEngineConfig, BrokerAPIConfig, UpstoxConfig
from algo.config_context import get_config, load_config
from algo.infrastructure.service_configuration import register_all_services
from algo.infrastructure.service_registry import service_registry, get_service
from algo.domain.trading.trading_window_service import TradingWindowService


class TestTradingWindowConfig:
    """Test cases for TradingWindowConfig class."""
    
    def test_trading_window_config_creation(self):
        """Test creating TradingWindowConfig with custom directory."""
        config = TradingWindowConfig(config_dir="./custom/trading_window/")
        assert config.config_dir == "./custom/trading_window/"
    
    def test_trading_window_config_with_env_var(self):
        """Test TradingWindowConfig with environment variable."""
        with patch.dict('os.environ', {'TRADING_WINDOW_CONFIG.CONFIG_DIR': '/env/trading_window/'}):
            config = TradingWindowConfig(config_dir="./default/")
            assert config.config_dir == "/env/trading_window/"
    
    def test_trading_window_config_default(self):
        """Test TradingWindowConfig with default value."""
        config = TradingWindowConfig(config_dir="")
        assert config.config_dir == "./config/trading_window/"


class TestConfigFromDict:
    """Test cases for Config.from_dict with trading window configuration."""
    
    def test_config_from_dict_with_trading_window(self):
        """Test creating Config from dictionary with trading window config."""
        config_dict = {
            "backtest_engine": {
                "historical_data_backend": "PARQUET_FILES",
                "reports_dir": "./reports",
                "parquet_files_base_dir": "./data",
                "strategy_json_config_dir": "./strategies"
            },
            "broker_api": {
                "upstox": {
                    "redirect_url": "http://localhost:5000/callback"
                }
            },
            "special_day_config": {
                "config_dir": "./config/special_day/"
            },
            "trading_window_config": {
                "config_dir": "./config/trading_window/"
            }
        }
        
        config = Config.from_dict(config_dict)
        
        assert isinstance(config.trading_window_config, TradingWindowConfig)
        assert config.trading_window_config.config_dir == "./config/trading_window/"
        assert isinstance(config.special_day_config, SpecialDayConfig)
        assert config.special_day_config.config_dir == "./config/special_day/"
    
    def test_config_from_dict_without_trading_window(self):
        """Test creating Config from dictionary without trading window config."""
        config_dict = {
            "backtest_engine": {
                "historical_data_backend": "PARQUET_FILES",
                "reports_dir": "./reports",
                "parquet_files_base_dir": "./data",
                "strategy_json_config_dir": "./strategies"
            },
            "broker_api": {},
            "special_day_config": {
                "config_dir": "./config/special_day/"
            }
        }
        
        config = Config.from_dict(config_dict)
        
        assert isinstance(config.trading_window_config, TradingWindowConfig)
        assert config.trading_window_config.config_dir == "./config/trading_window/"  # Default value


class TestConfigContext:
    """Test cases for config_context integration."""
    
    def test_load_config_from_file(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "backtest_engine": {
                "historical_data_backend": "PARQUET_FILES",
                "reports_dir": "./reports",
                "parquet_files_base_dir": "./data",
                "strategy_json_config_dir": "./strategies"
            },
            "broker_api": {
                "upstox": {
                    "redirect_url": "http://localhost:5000/callback"
                }
            },
            "special_day_config": {
                "config_dir": "./config/special_day/"
            },
            "trading_window_config": {
                "config_dir": "./config/trading_window/"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file_path = f.name
        
        try:
            config = load_config(config_file_path)
            
            assert isinstance(config, Config)
            assert config.trading_window_config.config_dir == "./config/trading_window/"
            
        finally:
            Path(config_file_path).unlink()
    
    def test_load_config_file_not_found(self):
        """Test error when configuration file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("/non/existent/config.json")
    
    def test_load_config_invalid_json(self):
        """Test error when configuration file has invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json")
            config_file_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_config(config_file_path)
        finally:
            Path(config_file_path).unlink()


class TestServiceConfigurationIntegration:
    """Test cases for service configuration integration with Config."""
    
    def setup_method(self):
        """Set up test environment."""
        service_registry.clear_all()
        # Clear config context global variable
        import algo.config_context
        algo.config_context._config = None
    
    def test_register_services_with_config(self):
        """Test service registration with configuration."""
        config_data = {
            "trading_window_config": {
                "config_dir": "./test/trading_window/"
            },
            "backtest_engine": {
                "historical_data_backend": "PARQUET_FILES",
                "reports_dir": "./reports",
                "parquet_files_base_dir": "./data",
                "strategy_json_config_dir": "./strategies"
            },
            "broker_api": {},
            "special_day_config": {
                "config_dir": "./config/special_day/"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file_path = f.name
        
        try:
            with patch.dict(os.environ, {'CONFIG_JSON_PATH': config_file_path}):
                with patch('algo.infrastructure.service_configuration.Path') as mock_path:
                    # Mock directory and files
                    mock_config_dir = MagicMock()
                    mock_config_dir.exists.return_value = True
                    mock_config_dir.is_dir.return_value = True
                    mock_config_dir.glob.return_value = []  # No config files
                    
                    mock_path.return_value = mock_config_dir
                    
                    # Register services
                    register_all_services()
                    
                    # Verify service is registered
                    assert service_registry.is_registered(TradingWindowService)
                    
                    # Verify config directory was used
                    mock_path.assert_called_with("./test/trading_window/")
        finally:
            Path(config_file_path).unlink()
    
    def test_register_services_without_config(self):
        """Test service registration without configuration (uses defaults)."""
        with patch('algo.infrastructure.service_configuration.Path') as mock_path:
            # Mock directory and files
            mock_config_dir = MagicMock()
            mock_config_dir.exists.return_value = True
            mock_config_dir.is_dir.return_value = True
            mock_config_dir.glob.return_value = []  # No config files
            
            mock_path.return_value = mock_config_dir
            
            # Clear environment variable and config
            with patch.dict(os.environ, {}, clear=True):
                with patch('algo.config_context.load_config') as mock_load_config:
                    # Mock empty config loading
                    mock_config = MagicMock()
                    mock_config.trading_window_config = None
                    mock_load_config.return_value = mock_config
                    
                    # Register services
                    register_all_services()
                    
                    # Verify service is registered
                    assert service_registry.is_registered(TradingWindowService)
                    
                    # Verify default directory was used
                    mock_path.assert_called_with("config/trading_window")


if __name__ == "__main__":
    pytest.main([__file__])
