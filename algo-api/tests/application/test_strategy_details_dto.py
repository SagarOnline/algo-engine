import pytest
from algo.application.strategy_usecases import StrategyDetailsDTO, InstrumentDTO, PositionDTO
from algo.domain.strategy import Instrument, InstrumentType, Exchange, Expiry, Expiring, Position

class DummyStrategy:
    def get_name(self):
        return "bullish_nifty"
    def get_display_name(self):
        return "Bullish Nifty"
    def get_description(self):
        return "Bullish Nifty Strategy with EMA crossover"
    
    def get_instrument(self):
        return Instrument(
            type=InstrumentType.FUTURE,
            exchange=Exchange.NSE,
            instrument_key="NSE_INDEX|Nifty 50",
            expiry=Expiry.MONTHLY,
            expiring=Expiring.NEXT,
            atm=-50
        )
    def get_timeframe(self):
        class TF:
            value = "15min"
        return TF()
    def get_position(self):
        return Position("BUY", self.get_instrument())

def test_strategy_details_dto_fields():
    strat = DummyStrategy()
    dto = StrategyDetailsDTO(strat)
    assert dto.name == "bullish_nifty"
    assert dto.display_name == "Bullish Nifty"
    assert isinstance(dto.instrument, InstrumentDTO)
    assert dto.timeframe == "15min"
    assert len(dto.positions) == 1
    assert isinstance(dto.positions[0], PositionDTO)
    assert dto.positions[0].action == "BUY"

def test_strategy_details_dto_to_dict():
    strat = DummyStrategy()
    dto = StrategyDetailsDTO(strat)
    d = dto.to_dict()
    assert d["name"] == "bullish_nifty"
    assert d["display_name"] == "Bullish Nifty"
    assert d["description"] == "Bullish Nifty Strategy with EMA crossover"
    assert d["instrument"]["instrument_key"] == "NSE_INDEX|Nifty 50"
    assert d["timeframe"] == "15min"
    assert isinstance(d["positions"], list)
    assert d["positions"][0]["action"] == "BUY"
    assert "instrument" in d["positions"][0]
