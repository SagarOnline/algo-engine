from datetime import datetime
from algo_core.domain.market import Market
from algo_core.domain.backtest.trade import Trade
import pytest

def test_trade():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 110.0, 10)
    assert trade.profit() == 100.0
    
def test_profit_points():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 110.0, 10)
    assert trade.profit_points() == 10.0

def test_profit_percentage_positive():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 110.0, 10)
    assert trade.profit_percentage() == 10.0

def test_profit_percentage_negative():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 90.0, 10)
    assert trade.profit_percentage() == -10.0

def test_profit_percentage_zero_entry():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 0.0, datetime(2021, 1, 1, 9, 20, 0), 50.0, 10)
    assert trade.profit_percentage() == 0.0

def test_profit_percentage_zero_profit():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 100.0, 10)
    assert trade.profit_percentage() == 0.0
