from datetime import date
import datetime
from typing import Any, Dict, Optional, List
from enum import Enum

from algo.domain.strategy.tradable_instrument import TradableInstrument, TriggerType
from .strategy import Strategy, Instrument, TradeAction
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from .tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe


class PositionAction(Enum):
    ADD = "ADD"
    EXIT = "EXIT"


class TradeSignal:
    def __init__(self, instrument: Instrument, action: TradeAction, quantity: int, timestamp: datetime.datetime, timeframe: Timeframe, position_action: PositionAction, trigger_type: TriggerType):
        self.instrument = instrument
        self.action = action
        self.quantity = quantity
        self.timestamp = timestamp
        self.timeframe = timeframe
        self.position_action = position_action
        self.trigger_type = trigger_type

    def __repr__(self):
        return f"TradeSignal(instrument={self.instrument.instrument_key}, action={self.action}, quantity={self.quantity}, timestamp={self.timestamp}, timeframe={self.timeframe}, position_action={self.position_action}, trigger_type={self.trigger_type})"

class StrategyEvaluator:
    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository, tradable_instrument_repository: TradableInstrumentRepository):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository
        self.tradable_instrument_repository = tradable_instrument_repository

    def evaluate(self, candle: Dict[str, Any]) -> List[TradeSignal]:
        """
        Evaluate the strategy for the given candle and return a list of trade signals.
        
        Args:
            candle: The current candle data
            
        Returns:
            List[TradeSignal]: List of trade signals generated, empty list if no signals
        """
        historical_data = self._get_historical_data(self.strategy, candle['timestamp'].date())
        strategy_timeframe = Timeframe(self.strategy.get_timeframe())
        tradable_instruments = self.tradable_instrument_repository.get_tradable_instruments(self.strategy.get_name())
        trade_signals = []
        
        for tradable in tradable_instruments:
            should_enter_trade = self.strategy.should_enter_trade(historical_data.data)
            should_exit_trade = self.strategy.should_exit_trade(historical_data.data)
            enter = not tradable.is_any_position_open() and should_enter_trade
            exit = tradable.is_any_position_open() and should_exit_trade
            
            # Check for stop loss hits on open positions
            stop_loss_signals = self._evaluate_for_stop_loss(candle, strategy_timeframe, tradable)
            if stop_loss_signals:
                trade_signals.extend(stop_loss_signals)
            elif enter:
                # Create a trade signal for entering a position
                position = self.strategy.get_position_instrument()
                timestamp = self._get_next_candle_timestamp(candle['timestamp'], strategy_timeframe)
                trade_signal = TradeSignal(tradable.instrument, position.action, 1, timestamp, strategy_timeframe, PositionAction.ADD, TriggerType.ENTRY_RULES)
                trade_signals.append(trade_signal)
                
            elif exit:
                # Create a trade signal for exiting a position
                position = self.strategy.get_position_instrument()
                timestamp = self._get_next_candle_timestamp(candle['timestamp'], strategy_timeframe)
                trade_signal = TradeSignal(tradable.instrument, position.get_close_action(), 1, timestamp, strategy_timeframe, PositionAction.EXIT, TriggerType.EXIT_RULES)
                trade_signals.append(trade_signal)
                
        return trade_signals

    def _evaluate_for_stop_loss(self, candle, strategy_timeframe, tradable: TradableInstrument) -> List[TradeSignal]:
        """
        Evaluate open positions for stop loss hits and return corresponding trade signals.
        
        Args:
            candle: The current candle data
            strategy_timeframe: The strategy's timeframe
            tradable: The TradableInstrument to check
            
        Returns:
            List[TradeSignal]: List of stop loss trade signals generated
        """
        stop_loss_signals = []
        
        if tradable.is_any_position_open():
            current_price = candle['close']  # Use candle's close price for stop loss check
            for position in tradable.positions:
                if position.is_open() and position.has_stop_loss_hit(current_price):
                    # Create stop loss exit signal
                    position_instrument = self.strategy.get_position_instrument()
                    timestamp = self._get_next_candle_timestamp(candle['timestamp'], strategy_timeframe)
                    stop_loss_signal = TradeSignal(
                        tradable.instrument, 
                        position_instrument.get_close_action(), 
                        position.quantity, 
                        timestamp, 
                        strategy_timeframe, 
                        PositionAction.EXIT, 
                        TriggerType.STOP_LOSS
                    )
                    stop_loss_signals.append(stop_loss_signal)
                    
        return stop_loss_signals
    
    def _get_historical_data(self, strategy: Strategy, end_date: date) -> HistoricalData:
        instrument = strategy.get_instrument()
        timeframe = Timeframe(strategy.get_timeframe())
        required_start_date = strategy.get_required_history_start_date(end_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        return historical_data

    def _get_next_candle_timestamp(self, timestamp, timeframe: Timeframe):
        # This is a placeholder function. The actual implementation would depend on the timeframe of the candles.
        # For example, if the timeframe is 1 minute, you would add one minute to the current timestamp.
        from datetime import timedelta
        if timeframe == Timeframe.ONE_MINUTE:
            return timestamp + timedelta(minutes=1)
        elif timeframe == Timeframe.FIVE_MINUTES:
            return timestamp + timedelta(minutes=5)
        elif timeframe == Timeframe.FIFTEEN_MINUTES:
            return timestamp + timedelta(minutes=15)
        elif timeframe == Timeframe.THIRTY_MINUTES:
            return timestamp + timedelta(minutes=30)
        elif timeframe == Timeframe.SIXTY_MINUTES:
            return timestamp + timedelta(hours=1)
        elif timeframe == Timeframe.ONE_DAY:
            return timestamp + timedelta(days=1)
        elif timeframe == Timeframe.ONE_WEEK:
            return timestamp + timedelta(weeks=1)
        return timestamp
