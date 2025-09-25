from datetime import datetime

from algo.domain.strategy.strategy import PositionAction
from algo.domain.strategy.strategy_evaluator import TradeSignal
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.strategy.trade_executor import TradeExecutor
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.timeframe import Timeframe

class BackTestTradeExecutor(TradeExecutor):
    def __init__(self, tradable_instrument_repository: TradableInstrumentRepository, historical_data_repository: HistoricalDataRepository, strategy_name: str):
        self.tradable_instrument_repository = tradable_instrument_repository
        self.historical_data_repository = historical_data_repository
        self.strategy_name = strategy_name

    def execute(self, trade_signal: TradeSignal) -> None:
        """Execute the given trade signal in a backtest environment."""
        tradable_instruments = self.tradable_instrument_repository.get_tradable_instruments(self.strategy_name)
        
        # Get the candle data for the trade signal
        timeframe = Timeframe("5min")  # Default timeframe, should be passed from strategy
        historical_data = self.historical_data_repository.get_historical_data(
            trade_signal.instrument, 
            trade_signal.timestamp.date(), 
            trade_signal.timestamp.date(), 
            timeframe
        )
        
        # Find the specific candle at the trade signal timestamp
        candle = historical_data.getCandleBy(trade_signal.timestamp.isoformat())
        if candle is None:
            raise ValueError(f"No candle found for timestamp {trade_signal.timestamp}")
        
        execution_price = candle['close']
        execution_time = trade_signal.timestamp
        
        # Find the matching tradable instrument
        for tradable in tradable_instruments:
            if tradable.instrument.instrument_key == trade_signal.instrument.instrument_key:
                # Add position or exit position based on action
                if trade_signal.action == PositionAction.BUY:
                    # Add new position
                    tradable.add_position(execution_time, execution_price, trade_signal.action, trade_signal.quantity)
                elif trade_signal.action == PositionAction.SELL:
                    # Exit existing position
                    tradable.exit_position(execution_time, execution_price, trade_signal.action, trade_signal.quantity)
                
                # Save the updated tradable instrument
                self.tradable_instrument_repository.save_tradable_instrument(self.strategy_name, tradable)
                break