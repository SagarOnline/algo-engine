import pytest
from algo.application.strategy_usecases import StrategyUseCase, StrategyNotFound, StrategyDetailsDTO
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.strategy.strategy import Exchange, Expiring, Expiry, Strategy, Instrument, Type

class DummyStrategy(Strategy):
    def get_name(self): return "test_strategy"
    def get_display_name(self): return "Test Strategy Display Name"
    def get_description(self): return "Test Description"
    def get_instrument(self): return Instrument(type=Type.FUT, exchange=Exchange.NSE, instrument_key="NIFTY23JUNFUT", expiry=Expiry.MONTHLY, expiring=Expiring.CURRENT)
    def get_timeframe(self): return "1d"
    def get_position_instrument(self): return []
    def get_capital(self): return 10000
    def get_entry_rules(self): return []
    def get_exit_rules(self): return []
    def get_risk_management(self): return None
    
class DummyRepository(StrategyRepository):
    def __init__(self, strategies):
        self._strategies = {s.get_name(): s for s in strategies}
    def list_strategies(self):
        return list(self._strategies.values())
    def get_strategy(self, name):
        if name in self._strategies:
            return self._strategies[name]
        raise ValueError("Not found")

def test_get_strategy_success():
    repo = DummyRepository([DummyStrategy()])
    usecase = StrategyUseCase(repo)
    result = usecase.get_strategy("test_strategy")
    assert isinstance(result, StrategyDetailsDTO)
    assert result.name == "test_strategy"
    assert result.display_name == "Test Strategy Display Name"

def test_get_strategy_not_found():
    repo = DummyRepository([])
    usecase = StrategyUseCase(repo)
    with pytest.raises(StrategyNotFound):
        usecase.get_strategy("missing_strategy")
