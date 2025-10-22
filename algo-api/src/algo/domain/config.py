import os
from enum import Enum


def get_value(value: str, env_var: str, default: str) -> str:
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    elif value:
        return value
    else:
        return default


class HistoricalDataBackend(Enum):
    PARQUET_FILES = "PARQUET_FILES"
    UPSTOX_API = "UPSTOX_API"


class UpstoxConfig:
    def __init__(
        self,
        #  api_key: str, api_secret: str, redirect_uri: str,
        redirect_url: str,
    ):
        # self.api_key = api_key
        # self.api_secret = api_secret
        # self.redirect_uri = redirect_uri
        self.redirect_url = get_value(
            redirect_url, "BROKER_API.UPSTOX.REDIRECT_URL", ""
        )


class BrokerAPIConfig:
    def __init__(self, upstox_config: UpstoxConfig = None):
        self.upstox_config = upstox_config


class TradingWindowConfig:
    def __init__(self, config_dir: str):
        self.config_dir = get_value(
            config_dir, "TRADING_WINDOW_CONFIG.CONFIG_DIR", "./config/trading_window/"
        )


class InstrumentMappingConfig:
    def __init__(self, config_dir: str):
        self.config_dir = get_value(
            config_dir, "INSTRUMENT_MAPPING.CONFIG_DIR", "./config/instruments/"
        )


class BacktestEngineConfig:
    def __init__(
        self,
        historical_data_backend: HistoricalDataBackend,
        reports_dir: str,
        parquet_files_base_dir: str,
        strategy_json_config_dir: str,
    ):
        backend = get_value(
            historical_data_backend,
            "BACKTEST_ENGINE.HISTORICAL_DATA_BACKEND",
            HistoricalDataBackend.PARQUET_FILES.value,
        )

        self.historical_data_backend = HistoricalDataBackend[backend]

        self.reports_dir = get_value(
            reports_dir, "BACKTEST_ENGINE.REPORTS_DIR", os.getcwd()
        )

        self.parquet_files_base_dir = get_value(
            parquet_files_base_dir, "BACKTEST_ENGINE.PARQUET_FILES_BASE_DIR", os.getcwd()
        )

        self.strategy_json_config_dir = get_value(
            strategy_json_config_dir, "BACKTEST_ENGINE.STRATEGY_JSON_CONFIG_DIR", os.getcwd()
        )


class Config:
    def __init__(self, backtest_engine: BacktestEngineConfig, broker_api: dict, trading_window_config: TradingWindowConfig, instrument_mapping_config: InstrumentMappingConfig):
        self.backtest_engine = backtest_engine
        self.broker_api = broker_api
        self.trading_window_config = trading_window_config
        self.instrument_mapping_config = instrument_mapping_config

    @staticmethod
    def from_dict(config_dict):
        be = config_dict.get("backtest_engine", {})
        backtest_engine = BacktestEngineConfig(
            historical_data_backend=be.get("historical_data_backend", ""),
            reports_dir=be.get("reports_dir", ""),
            parquet_files_base_dir=be.get("parquet_files_base_dir", ""),
            strategy_json_config_dir=be.get("strategy_json_config_dir", ""),
        )
        broker_api = config_dict.get("broker_api", {})
        broker_api_config = BrokerAPIConfig(
            upstox_config=UpstoxConfig(
                redirect_url=broker_api.get("upstox", {}).get("redirect_url", "")
            )
        )
        
        # Add trading window configuration
        trading_window_dict = config_dict.get("trading_window_config", {})
        trading_window_config = TradingWindowConfig(
            config_dir=trading_window_dict.get("config_dir", "./config/trading_window/")
        )
        
        # Add instrument mapping configuration
        instrument_mapping_dict = config_dict.get("instrument_mapping", {})
        instrument_mapping_config = InstrumentMappingConfig(
            config_dir=instrument_mapping_dict.get("config_dir", "./config/instruments/")
        )
        
        return Config(backtest_engine=backtest_engine, broker_api=broker_api_config, trading_window_config=trading_window_config, instrument_mapping_config=instrument_mapping_config)
