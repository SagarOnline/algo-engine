import pytest
from datetime import date, datetime, timedelta
from algo.domain.strategy.strategy import Instrument, TradeAction, PositionInstrument, RiskManagement, StopLoss, StopLossType, Strategy
from algo.domain.backtest.historical_data import HistoricalData

class DummyStrategy(Strategy):
    def __init__(self, instrument, entry_idx=0, exit_idx=2, stop_loss_in_points=None):
        self._instrument = instrument
        self._entry_idx = entry_idx
        self._exit_idx = exit_idx
        self._stop_loss_in_points = stop_loss_in_points

    def get_name(self): return "Dummy"
    def get_display_name(self): return "Dummy"
    def get_description(self): return "Dummy"
    def get_instrument(self): return self._instrument
    def get_timeframe(self): return None
    def get_capital(self): return 10000
    def get_entry_rules(self): return None
    def get_exit_rules(self): return None
    
    def get_position_instrument(self):
        return PositionInstrument(TradeAction.BUY, self._instrument)
    def get_risk_management(self):
        return RiskManagement(StopLoss(self._stop_loss_in_points, StopLossType.POINTS)) if self._stop_loss_in_points else None
    def should_enter_trade(self, historical_data):
        return len(historical_data) == self._entry_idx + 1
    def should_exit_trade(self, historical_data):
        return len(historical_data) == self._exit_idx + 1

class DummyHistoricalData(HistoricalData):
    def __init__(self, candles):
        self.data = candles
    def getCandleBy(self, timestamp):
        for c in self.data:
            if c['timestamp'].isoformat() == timestamp:
                return c
        return None

@pytest.fixture
def candles():
    base_time = datetime(2025, 9, 17, 9, 15)
    return [
        {"timestamp": base_time, "close": 100.0},
        {"timestamp": base_time + timedelta(minutes=1), "close": 94.0},  # triggers stop loss
        {"timestamp": base_time + timedelta(minutes=2), "close": 110.0},
    ]

@pytest.fixture
def instrument():
    return Instrument(segment="EQ", exchange="NSE", instrument_key="TCS")

@pytest.fixture
def strategy(instrument):
    return DummyStrategy(instrument, entry_idx=0, exit_idx=2, stop_loss_in_points=5.0)

@pytest.fixture
def historical_data(candles):
    return DummyHistoricalData(candles)

