from algo.application.strategy_usecases import InstrumentDTO
from algo.application.util import fmt_currency, fmt_percent
from algo.domain.backtest.engine import BacktestEngine
from algo.domain.strategy import Strategy
from datetime import date
from typing import Optional
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.backtest.report import BackTestReport, TradableInstrument
from algo.domain.backtest.trade import Trade

class RunBacktestInput:
    def __init__(self, strategy_name: str, start_date: str, end_date: str):
        self.strategy_name = strategy_name
        self.start_date = start_date
        self.end_date = end_date
        
class TradableDTO:
    def __init__(self, tradable: TradableInstrument):
        self.instrument = InstrumentDTO(tradable.instrument)
        self.trades = [TradeDTO(t) for t in tradable.trades]

    def to_dict(self):
        return {
            "instrument": self.instrument.to_dict(),
            "trades": [t.to_dict() for t in self.trades],
        }

class TradeDTO:
    def __init__(self, trade: Trade):
        self.entry_price = trade.entry_price
        self.entry_time = trade.entry_time
        self.exit_price = trade.exit_price
        self.exit_time = trade.exit_time
        self.profit = trade.profit()
        self.profit_percentage = trade.profit_percentage()
        self.profit_points = trade.profit_points()
        self.quantity = trade.quantity

    def to_dict(self):
        return {
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time,
            "profit": self.profit,
            "profit_percentage": self.profit_percentage,
            "profit_points": self.profit_points,
            "quantity": self.quantity,
        }

class BackTestReportSummaryDTO:
    def __init__(self, report: BackTestReport):
        self.start_date = report.start_date.strftime("%d-%b-%Y")
        self.end_date = report.end_date.strftime("%d-%b-%Y")
        self.strategy_name = report.strategy_name
        self.total_trades_count = report.total_trades_count()
        self.winning_trades_count = report.winning_trades_count()
        self.losing_trades_count = report.losing_trades_count()
        self.winning_streak = report.winning_streak()
        self.losing_streak = report.losing_streak()
        self.max_gain = fmt_currency(report.max_gain())
        self.max_loss = fmt_currency(report.max_loss())
        self.total_pnl_points = fmt_currency(report.total_pnl_points())
        self.total_pnl_percentage = fmt_percent(report.total_pnl_percentage())

    def to_dict(self):
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "strategy_name": self.strategy_name,
            "total_trades_count": self.total_trades_count,
            "winning_trades_count": self.winning_trades_count,
            "losing_trades_count": self.losing_trades_count,
            "winning_streak": self.winning_streak,
            "losing_streak": self.losing_streak,
            "max_gain": self.max_gain,
            "max_loss": self.max_loss,
            "total_pnl_points": self.total_pnl_points,
            "total_pnl_percentage": self.total_pnl_percentage,
        }
class BackTestReportDTO:
    def __init__(self, report: BackTestReport):
        self.summary = BackTestReportSummaryDTO(report)
        self.tradable = TradableDTO(report.tradable)

    def to_dict(self):
        return {
            "summary": self.summary.to_dict(),
            "tradable": self.tradable.to_dict(),
        }

class RunBacktestUseCase:
    def __init__(self, historical_data_repository: HistoricalDataRepository, strategy_repository: StrategyRepository):
        self.engine = BacktestEngine(historical_data_repository)
        self.strategy_repository = strategy_repository

    def execute(self, input_data: 'RunBacktestInput') -> dict:
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
        return BackTestReportDTO(report).to_dict()
