from algo_core.domain.backtest.engine import BacktestEngine
from algo_core.domain.strategy import Strategy
from datetime import date

from algo_core.domain.strategy_repository import StrategyRepository
from algo_core.domain.backtest.historical_data_repository import HistoricalDataRepository

class RunBacktestUseCase:
    def __init__(self, historical_data_repository: HistoricalDataRepository, strategy_repository: StrategyRepository):
        self.engine = BacktestEngine(historical_data_repository)
        self.strategy_repository = strategy_repository

    def execute(self, data: dict):
        try:
            # Validate and parse input
            strategy_name = data.get('strategy_name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            if not strategy_name or not start_date or not end_date:
                raise ValueError('Missing required fields: strategy, start_date, end_date')
            strategy = self.strategy_repository.get_strategy(strategy_name)
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            report = self.engine.start(strategy, start, end)
            return report.to_dict()
        except Exception as e:
            raise e
