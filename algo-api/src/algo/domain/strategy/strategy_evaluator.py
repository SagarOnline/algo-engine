from datetime import date
import datetime
from typing import Any, Dict, Optional
from .strategy import Strategy, Instrument, PositionAction
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from .tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe


class TradeSignal:
    def __init__(self, instrument: Instrument, action: PositionAction, quantity: int, timestamp: datetime.datetime, timeframe: Timeframe):
        self.instrument = instrument
        self.action = action
        self.quantity = quantity
        self.timestamp = timestamp
        self.timeframe = timeframe

    def __repr__(self):
        return f"TradeSignal(instrument={self.instrument.instrument_key}, action={self.action}, quantity={self.quantity}, timestamp={self.timestamp}, timeframe={self.timeframe})"

class StrategyEvaluator:
    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository, tradable_instrument_repository: TradableInstrumentRepository):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository
        self.tradable_instrument_repository = tradable_instrument_repository

    def evaluate(self, candle: Dict[str, Any]) -> Optional[TradeSignal]:
        historical_data = self._get_historical_data(self.strategy, candle['timestamp'].date())
        strategy_timeframe = Timeframe(self.strategy.get_timeframe())
        tradable_instruments = self.tradable_instrument_repository.get_tradable_instruments(self.strategy.get_name())
        for tradable in tradable_instruments:
            should_enter_trade = self.strategy.should_enter_trade(historical_data.data)
            should_exit_trade = self.strategy.should_exit_trade(historical_data.data)
            enter = not tradable.is_any_position_open() and should_enter_trade
            exit = tradable.is_any_position_open() and should_exit_trade
            if enter:
                # Return a trade signal for entering a position
                position = self.strategy.get_position_instrument()
                timestamp = self._get_next_candle_timestamp(candle['timestamp'], strategy_timeframe)
                return TradeSignal(tradable.instrument, position.action, 1, timestamp, strategy_timeframe)
            if exit:
                # Return a trade signal for exiting a position
                position = self.strategy.get_position_instrument()
                timestamp = self._get_next_candle_timestamp(candle['timestamp'], strategy_timeframe)
                return TradeSignal(tradable.instrument, position.get_close_action(), 1, timestamp, strategy_timeframe)
        return None
    
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
