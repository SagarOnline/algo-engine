from algo.domain.backtest.engine import BacktestEngine
from algo.domain.strategy import Strategy
from datetime import date
from typing import Optional
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository

class RunBacktestInput:
    def __init__(self, strategy_name: str, start_date: str, end_date: str):
        self.strategy_name = strategy_name
        self.start_date = start_date
        self.end_date = end_date

class RunBacktestUseCase:
    def __init__(self, historical_data_repository: HistoricalDataRepository, strategy_repository: StrategyRepository):
        self.engine = BacktestEngine(historical_data_repository)
        self.strategy_repository = strategy_repository

    def execute(self, input_data: 'RunBacktestInput'):
        # Validate input fields
        if not input_data.strategy_name or not input_data.start_date or not input_data.end_date:
            raise ValueError('Missing required fields: strategy_name, start_date, end_date')
        # Validate date formats
        try:
            start = date.fromisoformat(input_data.start_date)
        except Exception:
            raise ValueError('Invalid start_date format, must be YYYY-MM-DD')
        try:
            end = date.fromisoformat(input_data.end_date)
        except Exception:
            raise ValueError('Invalid end_date format, must be YYYY-MM-DD')
        if start > end:
            raise ValueError('start_date cannot be later than end_date')
        strategy = self.strategy_repository.get_strategy(input_data.strategy_name)
        report = self.engine.start(strategy, start, end)
        return report.to_dict()
