import pytest
from algo.application.strategy_usecases import InstrumentDTO
from algo.domain.strategy.strategy import Instrument, Segment, Exchange, Expiry, Expiring, Type

def make_instrument():
    return Instrument(
        segment=Segment.FNO,
        exchange=Exchange.NSE,
        instrument_key="NSE_INDEX|Nifty 50",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.NEXT,
        atm=-50,
        type=Type.FUT
    )


def test_instrument_dto_fields():
    instr = make_instrument()
    dto = InstrumentDTO(instr)
    assert dto.segment == Segment.FNO.name
    assert dto.type == Type.FUT.name
    assert dto.exchange == Exchange.NSE.name
    assert dto.instrument_key == "NSE_INDEX|Nifty 50"
    assert dto.expiry == Expiry.MONTHLY.name
    assert dto.expiring == Expiring.NEXT.name
    assert dto.atm == -50

def test_instrument_dto_display_name():
    instr = make_instrument()
    dto = InstrumentDTO(instr)
    display = dto.get_display_name()
    assert "NSE_INDEX|Nifty 50, Exchange.NSE" not in display  # Should not show enum type
    assert "NSE_INDEX|Nifty 50" in display
    assert "with NEXT MONTHLY expiry" in display
    assert ", atm -50" in display

def test_instrument_dto_to_dict():
    instr = make_instrument()
    dto = InstrumentDTO(instr)
    d = dto.to_dict()
    assert d["segment"] == str(Segment.FNO.name)
    assert d["type"] == str(Type.FUT.name)
    assert d["exchange"] == str(Exchange.NSE.name)
    assert d["instrument_key"] == "NSE_INDEX|Nifty 50"
    assert d["expiry"] == str(Expiry.MONTHLY.name)
    assert d["expiring"] == str(Expiring.NEXT.name)
    assert d["atm"] == -50
    assert "display_name" in d
