import pytest
from datetime import date, datetime, timedelta
from algo.domain.strategy import Instrument, PositionAction, PositionInstrument, RiskManagement, StopLoss, StopLossType, Strategy
from algo.domain.backtest.report import BackTestReport, PositionType, TradableInstrument, Position
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.backtest_run import BackTest

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
        return PositionInstrument(PositionAction.BUY, self._instrument)
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
    return Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")

@pytest.fixture
def strategy(instrument):
    return DummyStrategy(instrument, entry_idx=0, exit_idx=2, stop_loss_in_points=5.0)

@pytest.fixture
def historical_data(candles):
    return DummyHistoricalData(candles)

@pytest.fixture
def backtest(strategy, historical_data):
    return BackTest(strategy, historical_data, historical_data, date(2025, 9, 17), date(2025, 9, 17))

def test_stop_loss_triggered(backtest):
    report = backtest.run()
    tradable = report.tradable
    assert len(tradable.positions) == 1
    pos = tradable.positions[0]
    assert not pos.is_open()
    assert pos.exit_price() == 95.0
    assert pos.exit_time() == datetime(2025, 9, 17, 9, 16)
