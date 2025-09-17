import pytest
from datetime import datetime
from algo.domain.strategy import Instrument, PositionAction
from algo.domain.backtest.report import Position, PositionType

@pytest.fixture
def instrument():
    return Instrument(
        type="STOCK",
        exchange="NSE",
        instrument_key="TCS"
    )

@pytest.fixture
def entry_time():
    return datetime(2025, 9, 17, 9, 15)

@pytest.fixture
def exit_time():
    return datetime(2025, 9, 17, 15, 30)

def test_long_position_pnl(instrument, entry_time, exit_time):
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    pos.exit(110.0, exit_time)
    assert pos.pnl_points() == 10.0
    assert pos.pnl() == 100.0
    assert not pos.is_open()
    assert pos.entry_price() == 100.0
    assert pos.exit_price() == 110.0
    assert pos.entry_time() == entry_time
    assert pos.exit_time() == exit_time

def test_short_position_pnl(instrument, entry_time, exit_time):
    pos = Position(instrument, PositionType.SHORT, 5, 200.0, entry_time)
    pos.exit(180.0, exit_time)
    assert pos.pnl_points() == 20.0
    assert pos.pnl() == 100.0
    assert not pos.is_open()

def test_open_position(instrument, entry_time):
    pos = Position(instrument, PositionType.LONG, 1, 50.0, entry_time)
    assert pos.is_open()
    assert pos.exit_price() is None
    assert pos.exit_time() is None
    assert pos.entry_price() == 50.0
    assert pos.entry_time() == entry_time

def test_open_position_pnl_zero(instrument, entry_time):
    pos = Position(instrument, PositionType.LONG, 1, 50.0, entry_time)
    assert pos.is_open()
    assert pos.pnl() == 0.0
    assert pos.pnl_points() == 0.0
    assert pos.pnl_percentage() == 0.0

def test_process_stop_loss_long(instrument, entry_time, exit_time):
    pos = Position(instrument, PositionType.LONG, 1, 100.0, entry_time, stop_loss=95.0)
    triggered = pos.process_stop_loss(94.0, exit_time)
    assert triggered
    assert not pos.is_open()
    assert pos.exit_price() == 94.0
    assert pos.exit_time() == exit_time

def test_process_stop_loss_short(instrument, entry_time, exit_time):
    pos = Position(instrument, PositionType.SHORT, 1, 100.0, entry_time, stop_loss=105.0)
    triggered = pos.process_stop_loss(106.0, exit_time)
    assert triggered
    assert not pos.is_open()
    assert pos.exit_price() == 106.0
    assert pos.exit_time() == exit_time

def test_no_stop_loss_trigger(instrument, entry_time, exit_time):
    pos = Position(instrument, PositionType.LONG, 1, 100.0, entry_time, stop_loss=95.0)
    triggered = pos.process_stop_loss(96.0, exit_time)
    assert not triggered
    assert pos.is_open()

def test_position_zero_price_or_quantity_raises(instrument, entry_time):
    import pytest
    with pytest.raises(ValueError, match="Entry price cannot be zero."):
        Position(instrument, PositionType.LONG, 1, 0.0, entry_time)
    with pytest.raises(ValueError, match="Quantity cannot be zero."):
        Position(instrument, PositionType.LONG, 0, 100.0, entry_time)
