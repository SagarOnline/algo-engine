import pytest
from datetime import datetime
from algo.domain.strategy.strategy import Instrument, InstrumentType, TradeAction
from algo.domain.strategy.tradable_instrument import TradableInstrument, TriggerType

def make_instrument():
    return Instrument(type= InstrumentType.STOCK, exchange= "NSE", instrument_key= "NSE_TEST_INSTRUMENT" )

def test_add_position_creates_trade():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # Open a BUY
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 1
    # Close with a SELL
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1)
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
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.add_position(datetime(2023,1,1,9,16), 101, TradeAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 2
    # Close one
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is True
    assert len(tradable.positions) == 2
    # Close the other
    tradable.exit_position(datetime(2023,1,1,9,31), 111, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is False
    assert len(tradable.positions) == 2

def test_is_trade_open_false_when_no_positions():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    assert tradable.is_any_position_open() is False

def test_is_trade_open_true_when_open_position():
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    assert tradable.is_any_position_open() is True
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is False

@pytest.fixture
def complex_tradable():
    """Create a TradableInstrument with multiple positions for comprehensive testing."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Position 1: Win +10 points
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    
    # Position 2: Loss -5 points  
    tradable.add_position(datetime(2023,1,2,9,15), 110, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 105, TradeAction.SELL, 1)
    
    # Position 3: Win +15 points
    tradable.add_position(datetime(2023,1,3,9,15), 105, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,3,10,0), 120, TradeAction.SELL, 1)
    
    # Position 4: Loss -8 points
    tradable.add_position(datetime(2023,1,4,9,15), 120, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,4,10,0), 112, TradeAction.SELL, 1)
    
    # Position 5: Win +20 points
    tradable.add_position(datetime(2023,1,5,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,5,10,0), 120, TradeAction.SELL, 1)
    
    return tradable


@pytest.fixture
def streak_tradable():
    """Create a TradableInstrument for testing winning/losing streaks."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Win, Win, Win, Loss, Loss, Win, Loss, Win, Win
    trades = [
        (100, 110),  # +10 Win
        (110, 120),  # +10 Win  
        (120, 130),  # +10 Win
        (130, 125),  # -5 Loss
        (125, 120),  # -5 Loss
        (120, 130),  # +10 Win
        (130, 125),  # -5 Loss
        (125, 135),  # +10 Win
        (135, 145),  # +10 Win
    ]
    
    for i, (entry, exit) in enumerate(trades):
        tradable.add_position(datetime(2023,1,i+1,9,15), entry, TradeAction.BUY, 1)
        tradable.exit_position(datetime(2023,1,i+1,10,0), exit, TradeAction.SELL, 1)
    
    return tradable


@pytest.fixture
def empty_tradable():
    """Create an empty TradableInstrument with no positions."""
    instr = make_instrument()
    return TradableInstrument(instr)


@pytest.fixture
def open_positions_tradable():
    """Create a TradableInstrument with both open and closed positions."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Closed position
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    
    # Open position
    tradable.add_position(datetime(2023,1,2,9,15), 110, TradeAction.BUY, 1)
    
    return tradable


def test_total_pnl_points(complex_tradable):
    """Test total_pnl_points calculation."""
    # +10 -5 +15 -8 +20 = +32 points
    assert complex_tradable.total_pnl_points() == 32


def test_total_pnl_points_empty(empty_tradable):
    """Test total_pnl_points with no positions."""
    assert empty_tradable.total_pnl_points() == 0


def test_total_pnl_points_open_positions(open_positions_tradable):
    """Test total_pnl_points excludes open positions."""
    # Only closed position contributes: +10 points
    assert open_positions_tradable.total_pnl_points() == 10


def test_total_pnl(complex_tradable):
    """Test total_pnl calculation (pnl_points * quantity)."""
    # +10 -5 +15 -8 +20 = +32 points, quantity=1 each
    assert complex_tradable.total_pnl() == 32


def test_total_pnl_empty(empty_tradable):
    """Test total_pnl with no positions."""
    assert empty_tradable.total_pnl() == 0


def test_total_pnl_percentage(complex_tradable):
    """Test total_pnl_percentage calculation."""
    # Total buy: 100 + 110 + 105 + 120 + 100 = 535
    # Total sell: 110 + 105 + 120 + 112 + 120 = 567
    # Percentage: (567-535)/535 = 32/535 ≈ 5.98%
    expected = (32 / 535) 
    assert complex_tradable.total_pnl_percentage() == pytest.approx(expected, rel=1e-3)


def test_total_pnl_percentage_empty(empty_tradable):
    """Test total_pnl_percentage with no positions."""
    assert empty_tradable.total_pnl_percentage() == 0


def test_winning_trades_count(complex_tradable):
    """Test winning_trades_count calculation."""
    # Wins: +10, +15, +20 = 3 wins
    assert complex_tradable.winning_trades_count() == 3


def test_winning_trades_count_empty(empty_tradable):
    """Test winning_trades_count with no positions."""
    assert empty_tradable.winning_trades_count() == 0


def test_losing_trades_count(complex_tradable):
    """Test losing_trades_count calculation."""
    # Losses: -5, -8 = 2 losses
    assert complex_tradable.losing_trades_count() == 2


def test_losing_trades_count_empty(empty_tradable):
    """Test losing_trades_count with no positions."""
    assert empty_tradable.losing_trades_count() == 0


def test_total_trades_count(complex_tradable):
    """Test total_trades_count calculation."""
    # Total closed positions: 5
    assert complex_tradable.total_trades_count() == 5


def test_total_trades_count_empty(empty_tradable):
    """Test total_trades_count with no positions."""
    assert empty_tradable.total_trades_count() == 0


def test_total_trades_count_open_positions(open_positions_tradable):
    """Test total_trades_count excludes open positions."""
    # Only 1 closed position
    assert open_positions_tradable.total_trades_count() == 1


def test_winning_streak(streak_tradable):
    """Test winning_streak calculation."""
    # Pattern: WWW L L W L WW (3 consecutive wins max)
    assert streak_tradable.winning_streak() == 3


def test_winning_streak_empty(empty_tradable):
    """Test winning_streak with no positions."""
    assert empty_tradable.winning_streak() == 0


def test_winning_streak_no_wins():
    """Test winning_streak with all losing trades."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # All losses
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 95, TradeAction.SELL, 1)
    
    assert tradable.winning_streak() == 0


def test_losing_streak(streak_tradable):
    """Test losing_streak calculation."""
    # Pattern: WWW LL W L WW (2 consecutive losses max)
    assert streak_tradable.losing_streak() == 2


def test_losing_streak_empty(empty_tradable):
    """Test losing_streak with no positions."""
    assert empty_tradable.losing_streak() == 0


def test_losing_streak_no_losses():
    """Test losing_streak with all winning trades."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # All wins
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    tradable.add_position(datetime(2023,1,2,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 120, TradeAction.SELL, 1)
    
    assert tradable.losing_streak() == 0


def test_max_gain(complex_tradable):
    """Test max_gain calculation."""
    # Gains: +10, +15, +20. Max = +20
    assert complex_tradable.max_gain() == 20


def test_max_gain_empty(empty_tradable):
    """Test max_gain with no positions."""
    assert empty_tradable.max_gain() == 0


def test_max_gain_no_gains():
    """Test max_gain with all losing trades."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # All losses
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 95, TradeAction.SELL, 1)
    tradable.add_position(datetime(2023,1,2,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 90, TradeAction.SELL, 1)
    
    assert tradable.max_gain() == 0


def test_max_loss(complex_tradable):
    """Test max_loss calculation."""
    # Losses: -5, -8. Min = -8
    assert complex_tradable.max_loss() == -8


def test_max_loss_empty(empty_tradable):
    """Test max_loss with no positions."""
    assert empty_tradable.max_loss() == 0


def test_max_loss_no_losses():
    """Test max_loss with all winning trades."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    # All wins
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    tradable.add_position(datetime(2023,1,2,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 120, TradeAction.SELL, 1)
    
    assert tradable.max_loss() == 0


def test_is_any_position_open_false_no_positions(empty_tradable):
    """Test is_any_position_open returns False when no positions exist."""
    assert empty_tradable.is_any_position_open() is False


def test_is_any_position_open_false_all_closed():
    """Test is_any_position_open returns False when all positions are closed."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    
    assert tradable.is_any_position_open() is False


def test_is_any_position_open_true_has_open_position(open_positions_tradable):
    """Test is_any_position_open returns True when at least one position is open."""
    assert open_positions_tradable.is_any_position_open() is True


def test_is_any_position_open_multiple_positions():
    """Test is_any_position_open with multiple positions (some open, some closed)."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Add multiple positions
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.add_position(datetime(2023,1,2,9,15), 105, TradeAction.BUY, 1)
    tradable.add_position(datetime(2023,1,3,9,15), 110, TradeAction.BUY, 1)
    
    # All open
    assert tradable.is_any_position_open() is True
    
    # Close one
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is True
    
    # Close another
    tradable.exit_position(datetime(2023,1,2,10,0), 115, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is True
    
    # Close last one
    tradable.exit_position(datetime(2023,1,3,10,0), 120, TradeAction.SELL, 1)
    assert tradable.is_any_position_open() is False


def test_short_position_calculations():
    """Test calculations work correctly for SHORT positions."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # SHORT position: SELL at 100, BUY back at 90 = +10 profit
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.SELL, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 90, TradeAction.BUY, 1)
    
    # SHORT position: SELL at 90, BUY back at 95 = -5 loss
    tradable.add_position(datetime(2023,1,2,9,15), 90, TradeAction.SELL, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 95, TradeAction.BUY, 1)
    
    assert tradable.total_pnl_points() == 5  # +10 -5
    assert tradable.total_pnl() == 5
    assert tradable.winning_trades_count() == 1
    assert tradable.losing_trades_count() == 1
    assert tradable.max_gain() == 10
    assert tradable.max_loss() == -5


def test_mixed_position_types():
    """Test calculations with mixed LONG and SHORT positions."""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # LONG: BUY at 100, SELL at 110 = +10
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,10,0), 110, TradeAction.SELL, 1)
    
    # SHORT: SELL at 110, BUY at 105 = +5  
    tradable.add_position(datetime(2023,1,2,9,15), 110, TradeAction.SELL, 1)
    tradable.exit_position(datetime(2023,1,2,10,0), 105, TradeAction.BUY, 1)
    
    assert tradable.total_pnl_points() == 15  # +10 +5
    assert tradable.winning_trades_count() == 2
    assert tradable.losing_trades_count() == 0
    assert tradable.max_gain() == 10  # Max individual gain


# Tests for trigger type functionality

def test_add_position_default_trigger_type():
    """Test that add_position defaults to ENTRY_RULES trigger type"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    
    position = tradable.positions[0]
    assert position.entry_trigger_type == TriggerType.ENTRY_RULES


def test_add_position_explicit_trigger_type():
    """Test that add_position accepts explicit trigger type"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Test ENTRY_RULES
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1, trigger_type=TriggerType.ENTRY_RULES)
    assert tradable.positions[0].entry_trigger_type == TriggerType.ENTRY_RULES
    
    # Test STOP_LOSS (unusual for entry but testing flexibility)
    tradable.add_position(datetime(2023,1,1,9,20), 105, TradeAction.SELL, 1, trigger_type=TriggerType.STOP_LOSS)
    assert tradable.positions[1].entry_trigger_type == TriggerType.STOP_LOSS


def test_exit_position_default_trigger_type():
    """Test that exit_position defaults to EXIT_RULES trigger type"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1)
    
    position = tradable.positions[0]
    assert position.exit_trigger_type == TriggerType.EXIT_RULES


def test_exit_position_explicit_trigger_type():
    """Test that exit_position accepts explicit trigger type"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Test EXIT_RULES
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1, trigger_type=TriggerType.EXIT_RULES)
    assert tradable.positions[0].exit_trigger_type == TriggerType.EXIT_RULES
    
    # Test STOP_LOSS
    tradable.add_position(datetime(2023,1,1,9,35), 105, TradeAction.BUY, 1)
    tradable.exit_position(datetime(2023,1,1,9,40), 95, TradeAction.SELL, 1, trigger_type=TriggerType.STOP_LOSS)
    assert tradable.positions[1].exit_trigger_type == TriggerType.STOP_LOSS


def test_trigger_type_workflow_complete():
    """Test complete workflow with different trigger types"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Entry with ENTRY_RULES, exit with EXIT_RULES
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1, trigger_type=TriggerType.ENTRY_RULES)
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1, trigger_type=TriggerType.EXIT_RULES)
    
    position1 = tradable.positions[0]
    assert position1.entry_trigger_type == TriggerType.ENTRY_RULES
    assert position1.exit_trigger_type == TriggerType.EXIT_RULES
    assert position1.pnl() == 10
    
    # Entry with ENTRY_RULES, exit with STOP_LOSS
    tradable.add_position(datetime(2023,1,1,9,35), 105, TradeAction.BUY, 1, trigger_type=TriggerType.ENTRY_RULES)
    tradable.exit_position(datetime(2023,1,1,9,40), 95, TradeAction.SELL, 1, trigger_type=TriggerType.STOP_LOSS)
    
    position2 = tradable.positions[1]
    assert position2.entry_trigger_type == TriggerType.ENTRY_RULES
    assert position2.exit_trigger_type == TriggerType.STOP_LOSS
    assert position2.pnl() == -10


def test_multiple_positions_different_trigger_types():
    """Test multiple positions with different trigger type combinations"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Position 1: ENTRY_RULES -> EXIT_RULES
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1, trigger_type=TriggerType.ENTRY_RULES)
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1, trigger_type=TriggerType.EXIT_RULES)
    
    # Position 2: ENTRY_RULES -> STOP_LOSS  
    tradable.add_position(datetime(2023,1,1,9,35), 105, TradeAction.BUY, 1, trigger_type=TriggerType.ENTRY_RULES)
    tradable.exit_position(datetime(2023,1,1,9,40), 95, TradeAction.SELL, 1, trigger_type=TriggerType.STOP_LOSS)
    
    # Position 3: STOP_LOSS -> EXIT_RULES (unusual but testing flexibility)
    tradable.add_position(datetime(2023,1,1,9,45), 90, TradeAction.BUY, 1, trigger_type=TriggerType.STOP_LOSS)
    tradable.exit_position(datetime(2023,1,1,9,50), 95, TradeAction.SELL, 1, trigger_type=TriggerType.EXIT_RULES)
    
    # Verify all positions have correct trigger types
    assert tradable.positions[0].entry_trigger_type == TriggerType.ENTRY_RULES
    assert tradable.positions[0].exit_trigger_type == TriggerType.EXIT_RULES
    
    assert tradable.positions[1].entry_trigger_type == TriggerType.ENTRY_RULES
    assert tradable.positions[1].exit_trigger_type == TriggerType.STOP_LOSS
    
    assert tradable.positions[2].entry_trigger_type == TriggerType.STOP_LOSS
    assert tradable.positions[2].exit_trigger_type == TriggerType.EXIT_RULES


def test_add_position_with_stop_loss_and_trigger_type():
    """Test add_position with both stop_loss and trigger_type parameters"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Add position with stop loss and explicit trigger type
    tradable.add_position(
        datetime(2023,1,1,9,15), 
        100, 
        TradeAction.BUY, 
        1, 
        stop_loss=95, 
        trigger_type=TriggerType.ENTRY_RULES
    )
    
    position = tradable.positions[0]
    assert position.entry_trigger_type == TriggerType.ENTRY_RULES
    assert position.stop_loss == 95
    assert position.exit_trigger_type is None  # Not exited yet


def test_exit_position_preserves_entry_trigger_type():
    """Test that exit_position preserves the entry trigger type"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Add position with specific entry trigger type
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 1, trigger_type=TriggerType.STOP_LOSS)
    
    # Exit with different trigger type
    tradable.exit_position(datetime(2023,1,1,9,30), 110, TradeAction.SELL, 1, trigger_type=TriggerType.EXIT_RULES)
    
    position = tradable.positions[0]
    # Entry trigger type should remain unchanged
    assert position.entry_trigger_type == TriggerType.STOP_LOSS
    # Exit trigger type should be set to new value
    assert position.exit_trigger_type == TriggerType.EXIT_RULES


def test_tradable_instrument_stop_loss_exit_uses_stop_loss_price():
    """Test that TradableInstrument exit with STOP_LOSS trigger uses stop loss offset calculation"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Add position with stop loss offset
    tradable.add_position(
        datetime(2023,1,1,9,15), 
        100, 
        TradeAction.BUY, 
        10, 
        stop_loss=95.0  # Stop loss offset of 5 points
    )
    
    # Exit with STOP_LOSS trigger - provided price should be ignored, calculated stop loss used
    tradable.exit_position(
        datetime(2023,1,1,9,30), 
        90.0,  # Market price (ignored)
        TradeAction.SELL, 
        10, 
        trigger_type=TriggerType.STOP_LOSS
    )
    
    position = tradable.positions[0]
    assert position.exit_price() == 95.0  # entry_price - stop_loss (100 - 5), not market price (90)
    assert position.exit_trigger_type == TriggerType.STOP_LOSS
    assert position.pnl() == -50.0  # (95 - 100) * 10


def test_tradable_instrument_exit_rules_uses_provided_price():
    """Test that TradableInstrument exit with EXIT_RULES uses provided price"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Add position with stop loss offset
    tradable.add_position(
        datetime(2023,1,1,9,15), 
        100, 
        TradeAction.BUY, 
        10, 
        stop_loss=5.0  # Stop loss offset
    )
    
    # Exit with EXIT_RULES trigger - provided price should be used
    tradable.exit_position(
        datetime(2023,1,1,9,30), 
        110.0,  # Target price
        TradeAction.SELL, 
        10, 
        trigger_type=TriggerType.EXIT_RULES
    )
    
    position = tradable.positions[0]
    assert position.exit_price() == 110.0  # Provided price, not stop loss calculation
    assert position.exit_trigger_type == TriggerType.EXIT_RULES
    assert position.pnl() == 100.0  # (110 - 100) * 10


def test_tradable_instrument_stop_loss_workflow_multiple_positions():
    """Test stop loss workflow with multiple positions using offset-based stop loss"""
    instr = make_instrument()
    tradable = TradableInstrument(instr)
    
    # Position 1: LONG with stop loss offset
    tradable.add_position(datetime(2023,1,1,9,15), 100, TradeAction.BUY, 10, stop_loss=95.0)
    
    # Position 2: SHORT with stop loss offset
    tradable.add_position(datetime(2023,1,1,9,20), 200, TradeAction.SELL, 5, stop_loss=210.0)
    
    # Exit LONG position with stop loss trigger
    tradable.exit_position(datetime(2023,1,1,9,30), 90.0, TradeAction.SELL, 10, trigger_type=TriggerType.STOP_LOSS)
    
    # Exit SHORT position with stop loss trigger  
    tradable.exit_position(datetime(2023,1,1,9,35), 220.0, TradeAction.BUY, 5, trigger_type=TriggerType.STOP_LOSS)
    
    # Verify both positions used calculated stop loss prices
    long_position = tradable.positions[0]
    short_position = tradable.positions[1]
    
    assert long_position.exit_price() == 95.0  # 100 - 5, not market price 90
    assert long_position.pnl() == -50.0  # (95 - 100) * 10
    
    assert short_position.exit_price() == 210.0  # 200 + 10, not market price 220
    assert short_position.pnl() == -50.0  # (200 - 210) * 5
    
    assert tradable.total_pnl() == -100.0  # Combined loss
