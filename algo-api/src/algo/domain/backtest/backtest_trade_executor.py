from datetime import datetime

from algo.domain.strategy.strategy import TradeAction, Strategy
from algo.domain.strategy.strategy_evaluator import TradeSignal, PositionAction
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.strategy.trade_executor import TradeExecutor
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.timeframe import Timeframe

class BackTestTradeExecutor(TradeExecutor):
    def __init__(self, tradable_instrument_repository: TradableInstrumentRepository, historical_data_repository: HistoricalDataRepository, strategy: Strategy):
        self.tradable_instrument_repository = tradable_instrument_repository
        self.historical_data_repository = historical_data_repository
        self.strategy = strategy

    def execute(self, trade_signal: TradeSignal) -> None:
        """Execute the given trade signal in a backtest environment."""
        tradable_instruments = self.tradable_instrument_repository.get_tradable_instruments(self.strategy.get_name())
        
        # Get the candle data for the trade signal using the timeframe from the signal
        historical_data = self.historical_data_repository.get_historical_data(
            trade_signal.instrument, 
            trade_signal.timestamp.date(), 
            trade_signal.timestamp.date(), 
            trade_signal.timeframe
        )
        
        # Find the specific candle at the trade signal timestamp
        candle = historical_data.getCandleBy(trade_signal.timestamp.isoformat())
        if candle is None:
            raise ValueError(f"No candle found for timestamp {trade_signal.timestamp}")
        
        execution_price = candle['open']
        execution_time = trade_signal.timestamp
        trigger_type = trade_signal.trigger_type
        
        # Find the matching tradable instrument
        for tradable in tradable_instruments:
            if tradable.instrument.instrument_key == trade_signal.instrument.instrument_key:
                # Add position or exit position based on position_action
                if trade_signal.position_action == PositionAction.ADD:
                    # Calculate stop loss using strategy
                    stop_loss = self.strategy.calculate_stop_loss_for(execution_price)
                    # Add new position with stop loss
                    tradable.add_position(execution_time, execution_price, trade_signal.action, trade_signal.quantity, stop_loss, trigger_type=trigger_type)
                elif trade_signal.position_action == PositionAction.EXIT:
                    # Exit existing position
                    tradable.exit_position(execution_time, execution_price, trade_signal.action, trade_signal.quantity, trigger_type=trigger_type)
                
                # Save the updated tradable instrument
                self.tradable_instrument_repository.save_tradable_instrument(self.strategy.get_name(), tradable)
                break