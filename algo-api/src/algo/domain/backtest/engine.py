from datetime import date
from dotenv import load_dotenv

from algo.domain.strategy import Strategy
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.timeframe import Timeframe

from algo.domain.backtest.report import BackTestReport
from algo.domain.backtest.backtest_run import BackTest
from algo.domain.backtest.historical_data import HistoricalData


class BacktestEngine:
    def __init__(self, historical_data_repository: HistoricalDataRepository):
        self.historical_data_repository = historical_data_repository

    def start(self, strategy: Strategy, start_date: date, end_date: date) -> BackTestReport:
        underlying_instrument_hd = self._get_underlying_historical_data(strategy, start_date, end_date)
        position_instrument_hd = self._get_position_historical_data(strategy, start_date, end_date)
        backtest = BackTest(strategy, underlying_instrument_hd, position_instrument_hd, start_date, end_date)
        report = backtest.run()
        return report

    def _get_underlying_historical_data(self, strategy: Strategy, start_date: date, end_date: date) -> HistoricalData:
        instrument = strategy.get_instrument()
        timeframe = Timeframe(strategy.get_timeframe())
        required_start_date = strategy.get_required_history_start_date(start_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        return historical_data
    
    def _get_position_historical_data(self, strategy:Strategy, start_date: date, end_date: date) -> HistoricalData:
        instrument = strategy.get_position_instrument().instrument
        timeframe = Timeframe(strategy.get_timeframe())
        historical_data = self.historical_data_repository.get_historical_data(instrument, start_date, end_date, timeframe)
        return historical_data