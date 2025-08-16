from datetime import datetime, date
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv

from domain.strategy import Strategy
from infrastructure.jsonstrategy import JsonStrategy
from domain.backtest.historical_data_repository import HistoricalDataRepository
from infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from domain.timeframe import Timeframe


from domain.backtest.report_repository import BacktestReportRepository
from infrastructure.json_backtest_report_repository import JsonBacktestReportRepository

from domain.backtest.report import BacktestReport
from domain.trade import Trade
from domain.market import Market


class BacktestEngine:
    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository, report_repository: BacktestReportRepository):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository
        self.report_repository = report_repository

    def run(self, start_date: date, end_date: date) -> BacktestReport:
        instrument = self.strategy.get_instrument()
        timeframe = Timeframe(self.strategy.get_timeframe())
        required_start_date = self.strategy.get_required_history_start_date(start_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        
        trades: List[Trade] = []
        in_trade = False
        entry_price = 0.0
        entry_time = None
        
        for i in range(1, len(historical_data)):
            current_candle = historical_data[i]
            previous_candles = historical_data[:i]
            
            # Ensure we only start trading from the requested start_date
            if current_candle['timestamp'].date() < start_date:
                continue

            if not in_trade:
                if self.strategy.should_enter_trade(current_candle, previous_candles):
                    # Enter trade
                    entry_price = current_candle["close"]
                    entry_time = current_candle["timestamp"]
                    in_trade = True
            else:
                if self.strategy.should_exit_trade(current_candle, previous_candles):
                    # Exit trade
                    exit_price = current_candle["close"]
                    exit_time = current_candle["timestamp"]
                    trades.append(Trade(instrument, entry_time, entry_price, exit_time, exit_price))
                    in_trade = False
        
        # Calculate results
        pnl = 0
        for trade in trades:
            pnl += trade.profit()
        
        report = BacktestReport(self.strategy.get_name(), pnl, trades)
        self.report_repository.save(report)

        return report


def backtest(strategy_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Runs a backtest for a given strategy.
    """
    # Load strategy
    strategy_path = f"infrastructure/strategies/{strategy_name}.json"
    with open(strategy_path) as f:
        strategy_data = json.load(f)
    strategy = JsonStrategy(strategy_data)
    
    # Initialize historical data repository
    historical_data_repository = ParquetHistoricalDataRepository()

    # Initialize report repository
    report_repository = JsonBacktestReportRepository()

    # Initialize and run backtest engine
    engine = BacktestEngine(strategy, historical_data_repository, report_repository)
    
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    report = engine.run(start_date_obj, end_date_obj)
    
    return report.to_dict()
