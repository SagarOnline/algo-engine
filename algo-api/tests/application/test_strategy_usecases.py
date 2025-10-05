import pytest
from unittest.mock import Mock
from algo.domain.strategy.strategy import Instrument,InstrumentType,Exchange,Expiring, Expiry, PositionInstrument, PositionAction, Strategy
from algo.application.strategy_usecases import StrategyUseCase, StrategyDTO, InstrumentDTO

class DummyStrategy(Strategy):
    def __init__(self, strategy_name, display_name, description, instrument):
        self.strategy_name = strategy_name
        self.display_name = display_name
        self.description = description
        self.instrument = instrument

    def get_name(self):
        return self.strategy_name

    def get_display_name(self):
        return self.display_name

    def get_description(self):
        return self.description

    def get_instrument(self):
        return self.instrument

    def get_timeframe(self):
        return ""

    def get_capital(self):
        return ""

    def get_entry_rules(self):
        return ""

    def get_exit_rules(self):
        return ""

    def get_position_instrument(self):
        return PositionInstrument(action=PositionAction.BUY, instrument=self.get_instrument())

    def get_risk_management(self):
        return None
    
class DummyRepository:
    def list_strategies(self):
        return [
            DummyStrategy("strat1", "Strategy One", "Strategy One", Instrument(type=InstrumentType.FUTURE, exchange=Exchange.NSE, instrument_key="NIFTY23JUNFUT")),
            DummyStrategy("strat2", "Strategy Two", "SStrategy Two", Instrument(type=InstrumentType.FUTURE, exchange=Exchange.NSE, instrument_key="NIFTY23JUNFUT")),
        ]

def test_strategy_dto_to_dict():
    instr = Instrument(type=InstrumentType.FUTURE, exchange=Exchange.NSE, instrument_key="NIFTY23JUNFUT", expiry=Expiry.MONTHLY,expiring=Expiring.CURRENT)
    strategy = DummyStrategy("strat1", "Strategy One", "First strategy", instr)
    dto = StrategyDTO(strategy)
    result = dto.to_dict()
    assert result["name"] == "strat1"
    assert result["display_name"] == "Strategy One"
    assert result["description"] == "First strategy"
    assert isinstance(result["instrument"], dict) or isinstance(result["instrument"], str)

def test_list_strategies_maps_domain_to_dto():
    repo = DummyRepository()
    usecase = StrategyUseCase(repo)
    dtos = usecase.list_strategies()
    assert len(dtos) == 2
    assert dtos[0].name == "strat1"
    assert dtos[0].display_name == "Strategy One"
    assert dtos[0].description == "Strategy One"
    assert isinstance(dtos[0].instrument, InstrumentDTO)
