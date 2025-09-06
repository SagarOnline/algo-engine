import pytest
from datetime import datetime, date
from algo.domain.backtest.report import BackTestReport, TradableInstrument
from algo.domain.strategy import PositionAction


class DummyInstrument:
    def __init__(self, name):
        self.name = name
    def __dict__(self):
        return {'name': self.name}



@pytest.fixture
def sample_tradable():
    instr = DummyInstrument('AAPL')
    tradable = TradableInstrument(instr)
    tradable.execute_order(datetime(2023,1,1,9,15), 100, PositionAction.BUY, 1) # buy 1 @100
    tradable.execute_order(datetime(2023,1,1,10,0), 110, PositionAction.SELL, 1) # buy 1 @110
        
    tradable.execute_order(datetime(2023,1,2,9,15), 110, PositionAction.BUY, 1) # buy 1 @100
    tradable.execute_order( datetime(2023,1,2,10,0), 105, PositionAction.SELL, 1) # buy 1 @110
        
    tradable.execute_order(datetime(2023,1,3,9,15), 105, PositionAction.BUY, 1) # buy 1 @100
    tradable.execute_order(datetime(2023,1,3,10,0), 120, PositionAction.SELL, 1) # buy 1 @110
        
    tradable.execute_order(datetime(2023,1,4,9,15), 120, PositionAction.BUY, 1) # buy 1 @100
    tradable.execute_order(datetime(2023,1,4,10,0), 115, PositionAction.SELL, 1) # buy 1 @110
        
    tradable.execute_order(datetime(2023,1,5,9,15), 115, PositionAction.BUY, 1) # buy 1 @100
    tradable.execute_order(datetime(2023,1,5,10,0), 130, PositionAction.SELL, 1) # buy 1 @110
    return tradable
    

def test_total_pnl_points(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.total_pnl_points() == 10 - 5 + 15 - 5 + 15

def test_total_pnl_percentage(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    total_invested = 100 + 110 + 105 + 120 + 115
    total_points = 10 - 5 + 15 - 5 + 15
    assert report.total_pnl_percentage() == pytest.approx((total_points/total_invested)*100)

def test_winning_trades_count(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.winning_trades_count() == 3

def test_losing_trades_count(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.losing_trades_count() == 2

def test_total_trades_count(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.total_trades_count() == 5

def test_winning_streak(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.winning_streak() == 1  # max consecutive wins is 1

def test_losing_streak(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.losing_streak() == 1  # max consecutive losses is 1

def test_max_gain(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.max_gain() == 15

def test_max_loss(sample_tradable):
    report = BackTestReport('strat', sample_tradable, date(2023,1,1), date(2023,1,5))
    assert report.max_loss() == -5
