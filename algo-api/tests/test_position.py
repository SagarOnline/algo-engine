import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, Type
from algo.domain.strategy.tradable_instrument import Position
from algo.domain.strategy.tradable_instrument import TriggerType
from algo.domain.strategy.tradable_instrument import PositionType

@pytest.fixture
def instrument():
    return Instrument(
        segment="EQ",
        exchange="NSE",
        instrument_key="TCS",
        type=Type.EQ
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


def test_position_zero_price_or_quantity_raises(instrument, entry_time):
    import pytest
    with pytest.raises(ValueError, match="Entry price cannot be zero."):
        Position(instrument, PositionType.LONG, 1, 0.0, entry_time)
    with pytest.raises(ValueError, match="Quantity cannot be zero."):
        Position(instrument, PositionType.LONG, 0, 100.0, entry_time)


def test_position_entry_trigger_type_default(instrument, entry_time):
    """Test that Position defaults to ENTRY_RULES for entry trigger type"""
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    assert pos.entry_trigger_type == TriggerType.ENTRY_RULES


def test_position_entry_trigger_type_explicit(instrument, entry_time):
    """Test that Position accepts explicit entry trigger type"""
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time, trigger_type=TriggerType.ENTRY_RULES)
    assert pos.entry_trigger_type == TriggerType.ENTRY_RULES
    
    pos_stop = Position(instrument, PositionType.SHORT, 5, 200.0, entry_time, trigger_type=TriggerType.STOP_LOSS)
    assert pos_stop.entry_trigger_type == TriggerType.STOP_LOSS


def test_position_exit_trigger_type_default(instrument, entry_time, exit_time):
    """Test that Position defaults to EXIT_RULES for exit trigger type"""
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    pos.exit(110.0, exit_time)
    assert pos.exit_trigger_type == TriggerType.EXIT_RULES


def test_position_exit_trigger_type_explicit(instrument, entry_time, exit_time):
    """Test that Position accepts explicit exit trigger type"""
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    pos.exit(110.0, exit_time, trigger_type=TriggerType.EXIT_RULES)
    assert pos.exit_trigger_type == TriggerType.EXIT_RULES
    
    pos_stop = Position(instrument, PositionType.SHORT, 5, 200.0, entry_time)
    pos_stop.exit(180.0, exit_time, trigger_type=TriggerType.STOP_LOSS)
    assert pos_stop.exit_trigger_type == TriggerType.STOP_LOSS


def test_position_exit_trigger_type_none_when_open(instrument, entry_time):
    """Test that Position has None exit trigger type when position is still open"""
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    assert pos.exit_trigger_type is None
    assert pos.is_open()


def test_position_trigger_types_workflow(instrument, entry_time, exit_time):
    """Test complete workflow with entry and exit trigger types"""
    # Create position with ENTRY_RULES trigger
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time, trigger_type=TriggerType.ENTRY_RULES)
    assert pos.entry_trigger_type == TriggerType.ENTRY_RULES
    assert pos.exit_trigger_type is None
    assert pos.is_open()
    
    # Exit position with STOP_LOSS trigger
    pos.exit(90.0, exit_time, trigger_type=TriggerType.STOP_LOSS)
    assert pos.entry_trigger_type == TriggerType.ENTRY_RULES
    assert pos.exit_trigger_type == TriggerType.STOP_LOSS
    assert not pos.is_open()
    assert pos.pnl() == -100.0  # Loss of 10 points * 10 quantity


def test_position_all_trigger_types(instrument, entry_time, exit_time):
    """Test Position with all available trigger types"""
    # Test ENTRY_RULES entry
    pos1 = Position(instrument, PositionType.LONG, 1, 100.0, entry_time, trigger_type=TriggerType.ENTRY_RULES)
    assert pos1.entry_trigger_type == TriggerType.ENTRY_RULES
    
    # Test EXIT_RULES exit
    pos1.exit(105.0, exit_time, trigger_type=TriggerType.EXIT_RULES)
    assert pos1.exit_trigger_type == TriggerType.EXIT_RULES
    
    # Test STOP_LOSS entry and exit
    pos2 = Position(instrument, PositionType.SHORT, 1, 200.0, entry_time, trigger_type=TriggerType.STOP_LOSS)
    assert pos2.entry_trigger_type == TriggerType.STOP_LOSS
    
    pos2.exit(195.0, exit_time, trigger_type=TriggerType.STOP_LOSS)
    assert pos2.exit_trigger_type == TriggerType.STOP_LOSS


def test_position_stop_loss_exit_uses_stop_loss_price():
    """Test that exit with STOP_LOSS trigger uses stop loss offset from entry price"""
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS", type=Type.EQ)
    entry_time = datetime(2025, 9, 17, 9, 15)
    exit_time = datetime(2025, 9, 17, 15, 30)
    
    # LONG position with stop loss offset of 5
    pos_long = Position(instrument, PositionType.LONG, 10, 100.0, entry_time, stop_loss=95.0)
    pos_long.exit(90.0, exit_time, trigger_type=TriggerType.STOP_LOSS)  # Provided 90, should use 100-5=95
    
    assert pos_long.exit_price() == 95.0  # Should use entry_price - stop_loss (100 - 5)
    assert pos_long.exit_trigger_type == TriggerType.STOP_LOSS
    assert pos_long.pnl() == -50.0  # (95 - 100) * 10 = -50
    
    # SHORT position with stop loss offset of 10
    pos_short = Position(instrument, PositionType.SHORT, 5, 200.0, entry_time, stop_loss=210.0)
    pos_short.exit(220.0, exit_time, trigger_type=TriggerType.STOP_LOSS)  # Provided 220, should use 200+10=210
    
    assert pos_short.exit_price() == 210.0  # Should use entry_price + stop_loss (200 + 10)
    assert pos_short.exit_trigger_type == TriggerType.STOP_LOSS
    assert pos_short.pnl() == -50.0  # (200 - 210) * 5 = -50


def test_position_exit_rules_uses_provided_price():
    """Test that exit with EXIT_RULES trigger uses provided exit price"""
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    exit_time = datetime(2025, 9, 17, 15, 30)
    
    # Position with stop loss offset but exiting with EXIT_RULES
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time, stop_loss=5.0)
    pos.exit(110.0, exit_time, trigger_type=TriggerType.EXIT_RULES)  # Should use provided 110
    
    assert pos.exit_price() == 110.0  # Should use provided price, not stop loss calculation
    assert pos.exit_trigger_type == TriggerType.EXIT_RULES
    assert pos.pnl() == 100.0  # (110 - 100) * 10 = 100


def test_position_stop_loss_exit_no_stop_loss_set():
    """Test that exit with STOP_LOSS trigger uses provided price when no stop loss is set"""
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    exit_time = datetime(2025, 9, 17, 15, 30)
    
    # Position without stop loss
    pos = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)  # No stop loss
    pos.exit(90.0, exit_time, trigger_type=TriggerType.STOP_LOSS)  # Should use provided 90
    
    assert pos.exit_price() == 90.0  # Should use provided price since no stop loss
    assert pos.exit_trigger_type == TriggerType.STOP_LOSS
    assert pos.pnl() == -100.0  # (90 - 100) * 10 = -100


def test_position_stop_loss_workflow_realistic():
    """Test realistic stop loss workflow with offset-based stop loss"""
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    exit_time = datetime(2025, 9, 17, 15, 30)
    
    # Create LONG position with 5% stop loss (50 points on 1000 entry)
    entry_price = 1000.0
    stop_loss = 950.0  # 5% of entry price
    pos = Position(instrument, PositionType.LONG, 100, entry_price, entry_time, stop_loss=stop_loss)
    
    # Market price drops and triggers stop loss
    market_price = 940.0  # Market went below stop loss level
    pos.exit(market_price, exit_time, trigger_type=TriggerType.STOP_LOSS)
    
    # Verify stop loss price is calculated as entry_price - offset
    assert pos.exit_price() == stop_loss  # 950, not market price (940)
    assert pos.pnl() == -5000.0  # (950 - 1000) * 100 = -5000
    assert pos.pnl_percentage() == -0.05  # -5%


def test_position_has_stop_loss_hit_with_offset():
    """Test has_stop_loss_hit method with offset-based stop loss"""
    instrument = Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")
    entry_time = datetime(2025, 9, 17, 9, 15)
    
    # LONG position with stop loss offset of 5 points
    pos_long = Position(instrument, PositionType.LONG, 10, 100.0, entry_time, stop_loss=95.0)
    
    # Test various prices
    assert pos_long.has_stop_loss_hit(96.0) == False  # Above stop loss level (100-5=95)
    assert pos_long.has_stop_loss_hit(95.0) == True   # At stop loss level
    assert pos_long.has_stop_loss_hit(94.0) == True   # Below stop loss level
    
    # SHORT position with stop loss offset of 10 points
    pos_short = Position(instrument, PositionType.SHORT, 5, 200.0, entry_time, stop_loss=210.0)
    
    # Test various prices
    assert pos_short.has_stop_loss_hit(209.0) == False  # Below stop loss level (200+10=210)
    assert pos_short.has_stop_loss_hit(210.0) == True   # At stop loss level
    assert pos_short.has_stop_loss_hit(211.0) == True   # Above stop loss level
    
    # Position without stop loss should never trigger
    pos_no_sl = Position(instrument, PositionType.LONG, 10, 100.0, entry_time)
    assert pos_no_sl.has_stop_loss_hit(50.0) == False
