from datetime import datetime
from domain.market import Market
from domain.trade import Trade
import pytest

def test_trade():
    market = Market.from_str("NSE_RELIANCE")
    trade = Trade(market, datetime(2021, 1, 1, 9, 15, 0), 100.0, datetime(2021, 1, 1, 9, 20, 0), 110.0)
    assert trade.profit() == 10.0
