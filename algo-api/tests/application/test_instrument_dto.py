import pytest
from algo.application.strategy_usecases import InstrumentDTO
from algo.domain.strategy import Instrument, InstrumentType, Exchange, Expiry, Expiring

def make_instrument():
    return Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NSE_INDEX|Nifty 50",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.NEXT,
        atm=-50
    )


def test_instrument_dto_fields():
    instr = make_instrument()
    dto = InstrumentDTO(instr)
    assert dto.get_type() == InstrumentType.FUTURE.name
    assert dto.get_exchange() == Exchange.NSE.name
    assert dto.get_instrument_key() == "NSE_INDEX|Nifty 50"
    assert dto.get_expiry() == Expiry.MONTHLY.name
    assert dto.get_expiring() == Expiring.NEXT.name
    assert dto.get_atm() == -50

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
    assert d["type"] == str(InstrumentType.FUTURE.name)
    assert d["exchange"] == str(Exchange.NSE.name)
    assert d["instrument_key"] == "NSE_INDEX|Nifty 50"
    assert d["expiry"] == str(Expiry.MONTHLY.name)
    assert d["expiring"] == str(Expiring.NEXT.name)
    assert d["atm"] == -50
    assert "display_name" in d
