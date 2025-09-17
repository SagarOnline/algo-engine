import pytest
from algo.domain.strategy import Strategy, RiskManagement, StopLoss, StopLossType

class DummyStrategy(Strategy):
    def __init__(self, stop_loss_type=None, stop_loss_value=None):
        self._risk_management = None
        if stop_loss_type and stop_loss_value is not None:
            self._risk_management = RiskManagement(StopLoss(stop_loss_value, stop_loss_type))
    def get_name(self): return "Dummy"
    def get_display_name(self): return "Dummy"
    def get_description(self): return "Dummy"
    def get_instrument(self): return None
    def get_timeframe(self): return None
    def get_capital(self): return 0
    def get_entry_rules(self): return None
    def get_exit_rules(self): return None
    def get_position_instrument(self): return None
    def get_risk_management(self): return self._risk_management
    def should_enter_trade(self, historical_data): return False
    def should_exit_trade(self, historical_data): return False

@pytest.mark.parametrize("stop_loss_type, stop_loss_value, price, expected", [
    (StopLossType.POINTS, 10, 100, 90),
    (StopLossType.PERCENTAGE, 10, 100, 90),
    (StopLossType.POINTS, 5, 50, 45),
    (StopLossType.PERCENTAGE, 20, 200, 160),
])
def test_calculate_stop_loss_for_valid(stop_loss_type, stop_loss_value, price, expected):
    strategy = DummyStrategy(stop_loss_type, stop_loss_value)
    result = strategy.calculate_stop_loss_for(price)
    assert result == expected

def test_calculate_stop_loss_for_none_risk_management():
    strategy = DummyStrategy()
    assert strategy.calculate_stop_loss_for(100) is None

def test_calculate_stop_loss_for_none_stop_loss():
    class DummyStrategyNoStopLoss(DummyStrategy):
        def get_risk_management(self):
            return RiskManagement(None)
    strategy = DummyStrategyNoStopLoss()
    assert strategy.calculate_stop_loss_for(100) is None
