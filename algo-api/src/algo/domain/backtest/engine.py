from datetime import date
from dotenv import load_dotenv

from algo.domain.strategy.strategy import Strategy
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe

from algo.domain.backtest.report import BackTestReport
from algo.domain.backtest.backtest import BackTest
from algo.domain.backtest.historical_data import HistoricalData


class BacktestEngine:
    def __init__(self, historical_data_repository: HistoricalDataRepository, 
                 tradable_instrument_repository: TradableInstrumentRepository):
        self.historical_data_repository = historical_data_repository
        self.tradable_instrument_repository = tradable_instrument_repository

    def start(self, strategy: Strategy, start_date: date, end_date: date) -> BackTestReport:
        """
        Start backtest using the enhanced BackTest class with StrategyEvaluator and BackTestTradeExecutor.
        
        Args:
            strategy: The trading strategy to backtest
            start_date: Start date for the backtest period
            end_date: End date for the backtest period
            
        Returns:
            BackTestReport: The backtest results
        """
        backtest = BackTest(
            strategy=strategy,
            historical_data_repository=self.historical_data_repository,
            tradable_instrument_repository=self.tradable_instrument_repository,
            start_date=start_date,
            end_date=end_date
        )

        report = backtest.run()
        return report