import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, PositionAction
from algo.domain.backtest.report import Position, PositionType, TradableInstrument

def make_tradable_with_long_position(entry_price=100.0, stop_loss=95.0):
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    tradable = TradableInstrument(instrument)
    entry_time = datetime(2025, 9, 17, 9, 15)
    tradable.add_position(entry_time, entry_price, PositionAction.BUY, 1, stop_loss=stop_loss)
    return tradable

def make_tradable_with_short_position(entry_price=100.0, stop_loss=105.0):
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    tradable = TradableInstrument(instrument)
    entry_time = datetime(2025, 9, 17, 9, 15)
    tradable.add_position(entry_time, entry_price, PositionAction.SELL, 1, stop_loss=stop_loss)
    return tradable

def test_process_stop_loss_long_triggers():
    tradable = make_tradable_with_long_position()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = tradable.process_stop_loss(94.0, exit_time)
    assert triggered
    assert not tradable.positions[0].is_open()
    assert tradable.positions[0].exit_price() == 95.0
    assert tradable.positions[0].exit_time() == exit_time

def test_process_stop_loss_long_not_triggered():
    tradable = make_tradable_with_long_position()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = tradable.process_stop_loss(96.0, exit_time)
    assert not triggered
    assert tradable.positions[0].is_open()
    assert tradable.positions[0].exit_price() is None

def test_process_stop_loss_short_triggers():
    tradable = make_tradable_with_short_position()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = tradable.process_stop_loss(106.0, exit_time)
    assert triggered
    assert not tradable.positions[0].is_open()
    assert tradable.positions[0].exit_price() == 105.0
    assert tradable.positions[0].exit_time() == exit_time

def test_process_stop_loss_short_not_triggered():
    tradable = make_tradable_with_short_position()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = tradable.process_stop_loss(104.0, exit_time)
    assert not triggered
    assert tradable.positions[0].is_open()
    assert tradable.positions[0].exit_price() is None

def test_process_stop_loss_multiple_positions():
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    tradable = TradableInstrument(instrument)
    entry_time = datetime(2025, 9, 17, 9, 15)
    tradable.add_position(entry_time, 100.0, PositionAction.BUY, 1, stop_loss=95.0)
    
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = tradable.process_stop_loss(94.0, exit_time)
    assert triggered
    assert not tradable.positions[0].is_open()
    assert tradable.positions[0].exit_price() == 95.0
