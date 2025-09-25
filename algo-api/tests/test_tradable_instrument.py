import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, InstrumentType, PositionAction
from algo.domain.backtest.report import TradableInstrument

def make_instrument():
    return Instrument(type= InstrumentType.STOCK, exchange= "NSE", instrument_key= "NSE_TEST_INSTRUMENT" )

def test_add_position_creates_trade():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # Open a BUY
    tradable.add_position(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 1
    # Close with a SELL
    tradable.exit_position(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_any_position_open() is False
    assert len(tradable.positions) == 1
    position = tradable.positions[0]
    assert position.entry_price() == 100
    assert position.exit_price() == 110
    assert position.quantity == 1
    assert position.pnl() == 10

def test_add_position_multiple_open_positions():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # Open two BUYs
    tradable.add_position(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    tradable.add_position(datetime(2023,1,1,9,16), 101, PositionAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 2
    # Close one
    tradable.exit_position(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 2
    # Close the other
    tradable.exit_position(datetime(2023,1,1,9,31), 111, PositionAction.SELL, 1)
    assert tradable.is_any_position_open() is False
    assert len(tradable.positions) == 2

def test_is_trade_open_false_when_no_positions():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    assert tradable.is_any_position_open() is False

def test_is_trade_open_true_when_open_position():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.add_position(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    tradable.exit_position(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_any_position_open() is False
