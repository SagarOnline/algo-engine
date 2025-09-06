import pytest
from datetime import datetime
from algo.domain.strategy import Instrument, InstrumentType, PositionAction
from algo.domain.backtest.report import TradableInstrument

def make_instrument():
    return Instrument(type= InstrumentType.STOCK, exchange= "NSE", instrument_key= "NSE_TEST_INSTRUMENT" )

def test_execute_order_creates_trade_and_closes_position():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # Open a BUY
    tradable.execute_order(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    assert tradable.is_trade_open() is True
    assert len(tradable.trades) == 0
    # Close with a SELL
    tradable.execute_order(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_trade_open() is False
    assert len(tradable.trades) == 1
    trade = tradable.trades[0]
    assert trade.entry_price == 100
    assert trade.exit_price == 110
    assert trade.quantity == 1
    assert trade.profit() == 10

def test_execute_order_multiple_open_positions():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # Open two BUYs
    tradable.execute_order(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    tradable.execute_order(datetime(2023,1,1,9,16), 101, PositionAction.BUY, 1)
    assert tradable.is_trade_open() is True
    assert len(tradable.trades) == 0
    # Close one
    tradable.execute_order(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_trade_open() is True
    assert len(tradable.trades) == 1
    # Close the other
    tradable.execute_order(datetime(2023,1,1,9,31), 111, PositionAction.SELL, 1)
    assert tradable.is_trade_open() is False
    assert len(tradable.trades) == 2

def test_is_trade_open_false_when_no_positions():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    assert tradable.is_trade_open() is False

def test_is_trade_open_true_when_open_position():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.execute_order(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1)
    assert tradable.is_trade_open() is True
    tradable.execute_order(datetime(2023,1,1,9,30), 110, PositionAction.SELL, 1)
    assert tradable.is_trade_open() is False
