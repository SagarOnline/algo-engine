import pytest
from datetime import datetime
from algo_core.domain.backtest.historical_data import HistoricalData

def test_getCandleBy_returns_candle_when_exists():
    data = [
        {"timestamp": "2023-01-01T09:15:00", "close": 100},
        {"timestamp": "2023-01-01T09:30:00", "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T09:30:00")
    assert result == {"timestamp": "2023-01-01T09:30:00", "close": 110}

def test_getCandleBy_returns_candle_when_exists_datetime():
    data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T09:30:00")
    assert result == {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110}

def test_getCandleBy_returns_none_when_not_exists():
    data = [
        {"timestamp": "2023-01-01T09:15:00", "close": 100},
        {"timestamp": "2023-01-01T09:30:00", "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T10:00:00")
    assert result is None
