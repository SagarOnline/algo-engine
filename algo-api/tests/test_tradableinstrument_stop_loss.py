import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, TradeAction
from algo.domain.strategy.tradable_instrument import TradableInstrument
from algo.domain.strategy.tradable_instrument import Position, PositionType

def make_tradable_with_long_position(entry_price=100.0, stop_loss=95.0):
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    tradable = TradableInstrument(instrument)
    entry_time = datetime(2025, 9, 17, 9, 15)
    tradable.add_position(entry_time, entry_price, TradeAction.BUY, 1, stop_loss=stop_loss)
    return tradable

def make_tradable_with_short_position(entry_price=100.0, stop_loss=105.0):
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    tradable = TradableInstrument(instrument)
    entry_time = datetime(2025, 9, 17, 9, 15)
    tradable.add_position(entry_time, entry_price, TradeAction.SELL, 1, stop_loss=stop_loss)
    return tradable
