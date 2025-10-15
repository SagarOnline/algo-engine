import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, TradeAction
from algo.domain.strategy.tradable_instrument import Position
from algo.domain.strategy.tradable_instrument import PositionType

def make_position_long(entry_price=100.0, stop_loss=95.0):
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    return Position(instrument, PositionType.LONG, 1, entry_price, entry_time, stop_loss=stop_loss)

def make_position_short(entry_price=100.0, stop_loss=105.0):
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    return Position(instrument, PositionType.SHORT, 1, entry_price, entry_time, stop_loss=stop_loss)

def test_should_trigger_stop_loss_long_position_triggers():
    """Test that should_trigger_stop_loss returns True for LONG position when price <= stop_loss."""
    pos = make_position_long(entry_price=100.0, stop_loss=95.0)
    
    # Price exactly at stop loss
    assert pos.has_stop_loss_hit(95.0) is True
    
    # Price below stop loss
    assert pos.has_stop_loss_hit(94.0) is True
    assert pos.has_stop_loss_hit(90.0) is True


def test_should_trigger_stop_loss_long_position_not_triggers():
    """Test that should_trigger_stop_loss returns False for LONG position when price > stop_loss."""
    pos = make_position_long(entry_price=100.0, stop_loss=95.0)
    
    # Price above stop loss
    assert pos.has_stop_loss_hit(96.0) is False
    assert pos.has_stop_loss_hit(100.0) is False
    assert pos.has_stop_loss_hit(105.0) is False


def test_should_trigger_stop_loss_short_position_triggers():
    """Test that should_trigger_stop_loss returns True for SHORT position when price >= stop_loss."""
    pos = make_position_short(entry_price=100.0, stop_loss=5.0)
    
    # Price exactly at stop loss
    assert pos.has_stop_loss_hit(105.0) is True
    
    # Price above stop loss
    assert pos.has_stop_loss_hit(106.0) is True
    assert pos.has_stop_loss_hit(110.0) is True


def test_should_trigger_stop_loss_short_position_not_triggers():
    """Test that should_trigger_stop_loss returns False for SHORT position when price < stop_loss."""
    pos = make_position_short(entry_price=100.0, stop_loss=105.0)
    
    # Price below stop loss
    assert pos.has_stop_loss_hit(104.0) is False
    assert pos.has_stop_loss_hit(100.0) is False
    assert pos.has_stop_loss_hit(95.0) is False


def test_should_trigger_stop_loss_no_stop_loss():
    """Test that should_trigger_stop_loss returns False when no stop_loss is set."""
    # LONG position without stop loss
    pos_long = make_position_long(entry_price=100.0, stop_loss=None)
    assert pos_long.has_stop_loss_hit(50.0) is False
    assert pos_long.has_stop_loss_hit(150.0) is False
    
    # SHORT position without stop loss
    pos_short = make_position_short(entry_price=100.0, stop_loss=None)
    assert pos_short.has_stop_loss_hit(50.0) is False
    assert pos_short.has_stop_loss_hit(150.0) is False


def test_should_trigger_stop_loss_closed_position():
    """Test that should_trigger_stop_loss returns False for closed positions."""
    pos = make_position_long(entry_price=100.0, stop_loss=95.0)
    
    # Close the position first
    exit_time = datetime(2025, 9, 17, 15, 30)
    pos.exit(110.0, exit_time)
    assert not pos.is_open()
    
    # Should not trigger stop loss on closed position
    assert pos.has_stop_loss_hit(90.0) is False
    assert pos.has_stop_loss_hit(94.0) is False


def test_should_trigger_stop_loss_edge_cases():
    """Test edge cases for should_trigger_stop_loss function."""
    # Test with very small price differences
    pos_long = make_position_long(entry_price=100.0, stop_loss=95.5)
    assert pos_long.has_stop_loss_hit(95.5) is True
    assert pos_long.has_stop_loss_hit(95.50001) is False
    assert pos_long.has_stop_loss_hit(95.49999) is True
    
    pos_short = make_position_short(entry_price=100.0, stop_loss=105.5)
    assert pos_short.has_stop_loss_hit(105.5) is True
    assert pos_short.has_stop_loss_hit(105.49999) is False
    assert pos_short.has_stop_loss_hit(105.50001) is True


def test_should_trigger_stop_loss_zero_stop_loss():
    """Test should_trigger_stop_loss with zero stop loss value."""
    # LONG position with zero stop loss
    pos_long = make_position_long(entry_price=100.0, stop_loss=0.0)
    assert pos_long.has_stop_loss_hit(0.0) is True
    assert pos_long.has_stop_loss_hit(-1.0) is True
    assert pos_long.has_stop_loss_hit(1.0) is False
    
    # SHORT position with zero stop loss (unusual but possible)
    pos_short = make_position_short(entry_price=100.0, stop_loss=0.0)
    assert pos_short.has_stop_loss_hit(0.0) is True
    assert pos_short.has_stop_loss_hit(1.0) is True
    assert pos_short.has_stop_loss_hit(-1.0) is False


def test_should_trigger_stop_loss_different_position_types():
    """Test should_trigger_stop_loss with different combinations of position types and prices."""
    # LONG position scenarios
    long_pos = make_position_long(entry_price=50.0, stop_loss=45.0)
    test_cases_long = [
        (44.0, True),   # Below stop loss
        (45.0, True),   # At stop loss
        (46.0, False),  # Above stop loss
        (50.0, False),  # At entry price
        (55.0, False),  # Above entry price
    ]
    
    for price, expected in test_cases_long:
        assert long_pos.has_stop_loss_hit(price) is expected, f"LONG: price {price} should return {expected}"
    
    # SHORT position scenarios
    short_pos = make_position_short(entry_price=50.0, stop_loss=55.0)
    test_cases_short = [
        (56.0, True),   # Above stop loss
        (55.0, True),   # At stop loss
        (54.0, False),  # Below stop loss
        (50.0, False),  # At entry price
        (45.0, False),  # Below entry price
    ]
    
    for price, expected in test_cases_short:
        assert short_pos.has_stop_loss_hit(price) is expected, f"SHORT: price {price} should return {expected}"
