
import os
from datetime import datetime, date
from dotenv import load_dotenv, find_dotenv
import json
from algo.application.run_backtest_usecase import BackTestReportDTO
from algo.domain.backtest.engine import BacktestEngine
from algo.infrastructure.upstox.cached_upstox_historical_data_repository import CachedUpstoxHistoricalDataRepository
from algo.infrastructure.json_backtest_report_repository import JsonBacktestReportRepository
from algo.infrastructure.jsonstrategy import JsonStrategy
from algo.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo.infrastructure.in_memory_tradable_instrument_repository import InMemoryTradableInstrumentRepository
from algo.domain.indicators.exceptions import InvalidStrategyConfiguration

from algo.config_context import get_config
from algo.domain.config import HistoricalDataBackend
from algo.infrastructure.upstox.upstox_historical_data_repository import UpstoxHistoricalDataRepository

from algo.infrastructure.json_strategy_repository import JsonStrategyRepository



def main():
    load_dotenv(find_dotenv())
    config = get_config()

    """
    Runs a backtest for a given strategy.
    """
    try:
        strategy_json_config_dir = config.backtest_engine.strategy_json_config_dir
        strategy_path = f"{strategy_json_config_dir}/bullish_nifty.json"
        with open(strategy_path) as f:
            strategy_data = json.load(f)
        strategy = JsonStrategy(strategy_data)

        # Initialize historical data repository
        if config.backtest_engine.historical_data_backend == HistoricalDataBackend.PARQUET_FILES:
            historical_data_repository = ParquetHistoricalDataRepository(config.backtest_engine.parquet_files_base_dir)
        elif config.backtest_engine.historical_data_backend == HistoricalDataBackend.UPSTOX_API:
            historical_data_repository = CachedUpstoxHistoricalDataRepository(UpstoxHistoricalDataRepository())
        else:
            raise ValueError("Unsupported historical data backend")

        # Initialize tradable instrument repository
        tradable_instrument_repository = InMemoryTradableInstrumentRepository()

        # Initialize and run backtest engine
        engine = BacktestEngine(historical_data_repository, tradable_instrument_repository)
        start_date = "2025-08-01"
        end_date = "2025-08-13"
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        backtest_report = engine.start(strategy, start_date_obj, end_date_obj)
        print(BackTestReportDTO(backtest_report).to_dict())
    except InvalidStrategyConfiguration as e:
        print(f"InvalidStrategyConfiguration: {e}")


if __name__ == "__main__":
    main()
