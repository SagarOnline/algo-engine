import pytest
from datetime import datetime
from algo_core.domain.backtest.report import BackTestReport
from types import SimpleNamespace

class DummyInstrument:
    def __init__(self, name):
        self.name = name
    def __dict__(self):
        return {'name': self.name}

class DummyTrade:
    def __init__(self, instrument, entry_time, entry_price, exit_time, exit_price):
        self.instrument = instrument
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.exit_time = exit_time
        self.exit_price = exit_price
    def profit(self):
        return self.exit_price - self.entry_price

@pytest.fixture
def sample_trades():
    instr = DummyInstrument('AAPL')
    return [
        DummyTrade(instr, datetime(2023,1,1,9,15), 100, datetime(2023,1,1,10,0), 110),  # win
        DummyTrade(instr, datetime(2023,1,2,9,15), 110, datetime(2023,1,2,10,0), 105),  # loss
        DummyTrade(instr, datetime(2023,1,3,9,15), 105, datetime(2023,1,3,10,0), 120),  # win
        DummyTrade(instr, datetime(2023,1,4,9,15), 120, datetime(2023,1,4,10,0), 115),  # loss
        DummyTrade(instr, datetime(2023,1,5,9,15), 115, datetime(2023,1,5,10,0), 130),  # win
    ]

def test_positions(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    pos = report.positions()
    assert len(pos) == 5
    assert pos[0]['entry_price'] == 100
    assert pos[0]['exit_price'] == 110
    assert pos[0]['profit_points'] == 10
    assert pos[1]['profit_points'] == -5
    assert pos[2]['profit_pct'] == pytest.approx((15/105)*100)

def test_total_pnl_points(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.total_pnl_points() == 10 - 5 + 15 - 5 + 15

def test_total_pnl_percentage(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    total_invested = 100 + 110 + 105 + 120 + 115
    total_points = 10 - 5 + 15 - 5 + 15
    assert report.total_pnl_percentage() == pytest.approx((total_points/total_invested)*100)

def test_winning_trades_count(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.winning_trades_count() == 3

def test_losing_trades_count(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.losing_trades_count() == 2

def test_total_trades_count(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.total_trades_count() == 5

def test_winning_streak(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.winning_streak() == 1  # max consecutive wins is 1

def test_losing_streak(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.losing_streak() == 1  # max consecutive losses is 1

def test_max_gain(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.max_gain() == 15

def test_max_loss(sample_trades):
    report = BackTestReport('strat', 0, sample_trades)
    assert report.max_loss() == -5
