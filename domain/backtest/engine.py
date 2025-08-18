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
    def __init__(self, historical_data_repository: HistoricalDataRepository, report_repository: BacktestReportRepository):
        self.historical_data_repository = historical_data_repository
        self.report_repository = report_repository

    def run(self, strategy: Strategy, start_date: date, end_date: date) -> BacktestReport:
        instrument = strategy.get_instrument()
        timeframe = Timeframe(strategy.get_timeframe())
        required_start_date = strategy.get_required_history_start_date(start_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        
        trades: List[Trade] = []
        in_trade = False
        entry_price = 0.0
        entry_time = None
        
        for i in range(0, len(historical_data)):
            previous_candles = historical_data[:i+1]
            # Ensure we only start trading from the requested start_date
            if previous_candles[i]['timestamp'].date() < start_date:
                continue

            if not in_trade:
                if strategy.should_enter_trade(previous_candles):
                    # Enter trade
                    entry_price = previous_candles[i]["close"]
                    entry_time = previous_candles[i]["timestamp"]
                    in_trade = True
            else:
                if strategy.should_exit_trade(previous_candles):
                    # Exit trade
                    exit_price = previous_candles[i]["close"]
                    exit_time = previous_candles[i]["timestamp"]
                    trades.append(Trade(instrument, entry_time, entry_price, exit_time, exit_price))
                    in_trade = False
        
        # Calculate results
        pnl = 0
        for trade in trades:
            pnl += trade.profit()
        
        report = BacktestReport(strategy.get_name(), pnl, trades)
        self.report_repository.save(report)

        return report