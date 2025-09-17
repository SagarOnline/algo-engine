import pytest
from datetime import datetime
from algo.domain.strategy import Instrument, PositionAction
from algo.domain.backtest.report import Position, PositionType

def make_position_long(entry_price=100.0, stop_loss=95.0):
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    return Position(instrument, PositionType.LONG, 1, entry_price, entry_time, stop_loss=stop_loss)

def make_position_short(entry_price=100.0, stop_loss=105.0):
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    return Position(instrument, PositionType.SHORT, 1, entry_price, entry_time, stop_loss=stop_loss)

def test_process_stop_loss_long_triggers():
    pos = make_position_long()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = pos.process_stop_loss(94.0, exit_time)
    assert triggered
    assert not pos.is_open()
    assert pos.exit_price() == 95.0
    assert pos.exit_time() == exit_time

def test_process_stop_loss_long_not_triggered():
    pos = make_position_long()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = pos.process_stop_loss(96.0, exit_time)
    assert not triggered
    assert pos.is_open()
    assert pos.exit_price() is None

def test_process_stop_loss_short_triggers():
    pos = make_position_short()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = pos.process_stop_loss(106.0, exit_time)
    assert triggered
    assert not pos.is_open()
    assert pos.exit_price() == 105.0
    assert pos.exit_time() == exit_time

def test_process_stop_loss_short_not_triggered():
    pos = make_position_short()
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = pos.process_stop_loss(104.0, exit_time)
    assert not triggered
    assert pos.is_open()
    assert pos.exit_price() is None

def test_process_stop_loss_no_stop_loss():
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    pos = Position(instrument, PositionType.LONG, 1, 100.0, entry_time)
    exit_time = datetime(2025, 9, 17, 15, 30)
    triggered = pos.process_stop_loss(94.0, exit_time)
    assert not triggered
    assert pos.is_open()
    assert pos.exit_price() is None
