from datetime import datetime, date
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv

from algo_core.domain.strategy import Strategy
from algo_core.infrastructure.jsonstrategy import JsonStrategy
from algo_core.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo_core.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo_core.domain.timeframe import Timeframe

from algo_core.domain.backtest.report_repository import BacktestReportRepository
from algo_core.infrastructure.json_backtest_report_repository import JsonBacktestReportRepository

from algo_core.domain.backtest.report import BacktestReport
from algo_core.domain.trade import Trade
from algo_core.domain.market import Market
from algo_core.domain.backtest.backtest_run import BacktestRun


class BacktestEngine:
    def __init__(self, historical_data_repository: HistoricalDataRepository, report_repository: BacktestReportRepository):
        self.historical_data_repository = historical_data_repository
        self.report_repository = report_repository

    def run(self, strategy: Strategy, start_date: date, end_date: date) -> BacktestReport:
        historical_data = self._get_historical_data(strategy, start_date, end_date)
        backtest_run = BacktestRun(strategy, historical_data, start_date)
        report = backtest_run.start()
        self.report_repository.save(report)
        return report

    def _get_historical_data(self, strategy, start_date, end_date):
        instrument = strategy.get_instrument()
        timeframe = Timeframe(strategy.get_timeframe())
        required_start_date = strategy.get_required_history_start_date(start_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        return historical_data