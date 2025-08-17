import os
from datetime import datetime, date
from dotenv import load_dotenv
from datetime import date
import json
from domain.backtest.engine import BacktestEngine
from infrastructure.json_backtest_report_repository import JsonBacktestReportRepository
from infrastructure.jsonstrategy import JsonStrategy
from infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository


def main():
    load_dotenv()
    """
    Runs a backtest for a given strategy.
    """
    # Load strategy
    strategy_path = f"strategies/bullish_nifty.json"
    with open(strategy_path) as f:
        strategy_data = json.load(f)
    strategy = JsonStrategy(strategy_data)
    
    # Initialize historical data repository
    historical_data_repository = ParquetHistoricalDataRepository()

    # Initialize report repository
    report_repository = JsonBacktestReportRepository()

    # Initialize and run backtest engine
    engine = BacktestEngine(strategy, historical_data_repository, report_repository)
    start_date = "2025-08-01"
    end_date = "2025-08-14"
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    report = engine.run(start_date_obj, end_date_obj)


if __name__ == "__main__":
    main()
