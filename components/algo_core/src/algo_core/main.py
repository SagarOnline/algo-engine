
import os
from datetime import datetime, date
from dotenv import load_dotenv, find_dotenv
import json
from algo_core.domain.backtest.engine import BacktestEngine
from algo_core.infrastructure.json_backtest_report_repository import JsonBacktestReportRepository
from algo_core.infrastructure.jsonstrategy import JsonStrategy
from algo_core.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo_core.domain.indicators.exceptions import InvalidStrategyConfiguration

from algo_core.config_context import get_config
from algo_core.domain.config import HistoricalDataBackend
from algo_core.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository



def main():
    load_dotenv(find_dotenv())
    config = get_config()

    """
    Runs a backtest for a given strategy.
    """
    try:
        strategies_dir = config.backtest_engine.strategies_path
        strategy_path = f"{strategies_dir}/bullish_nifty.json"
        with open(strategy_path) as f:
            strategy_data = json.load(f)
        strategy = JsonStrategy(strategy_data)

        # Initialize historical data repository
        if config.backtest_engine.historical_data_backend == HistoricalDataBackend.PARQUET_FILES:
            historical_data_repository = ParquetHistoricalDataRepository()
        elif config.backtest_engine.historical_data_backend == HistoricalDataBackend.UPSTOX_API:
            historical_data_repository = UpstoxHistoricalDataRepository()
        else:
            raise ValueError("Unsupported historical data backend")
        # Initialize report repository
        report_repository = JsonBacktestReportRepository()

        # Initialize and run backtest engine
        engine = BacktestEngine(historical_data_repository, report_repository)
        start_date = "2025-08-01"
        end_date = "2025-08-14"
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        backtest_report = engine.start(strategy, start_date_obj, end_date_obj)
        print(backtest_report)
    except InvalidStrategyConfiguration as e:
        print(f"InvalidStrategyConfiguration: {e}")


if __name__ == "__main__":
    main()
