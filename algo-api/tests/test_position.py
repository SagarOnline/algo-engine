import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument
from algo.domain.strategy.tradable_instrument import Position
from algo.domain.strategy.tradable_instrument import TriggerType
from algo.domain.strategy.tradable_instrument import PositionType

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
