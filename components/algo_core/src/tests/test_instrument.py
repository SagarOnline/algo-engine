import pytest
from algo.domain.strategy import Instrument, InstrumentType, Exchange, Expiry, Expiring

def test_instrument_equality_basic():
    inst1 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    inst2 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    assert inst1 == inst2

def test_instrument_equality_with_all_fields():
    inst1 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.CURRENT,
        atm=0
    )
    inst2 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.CURRENT,
        atm=0
    )
    assert inst1 == inst2

def test_instrument_inequality_type():
    inst1 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    inst2 = Instrument(
        type=InstrumentType.STOCK,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    assert inst1 != inst2

def test_instrument_inequality_exchange():
    inst1 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    inst2 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.BSE,
        instrument_key="NIFTY23JUNFUT"
    )
    assert inst1 != inst2

def test_instrument_inequality_instrument_key():
    inst1 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    inst2 = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="BANKNIFTY23JUNFUT"
    )
    assert inst1 != inst2

def test_instrument_inequality_expiry():
    inst1 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY
    )
    inst2 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.WEEKLY
    )
    assert inst1 != inst2

def test_instrument_inequality_expiring():
    inst1 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiring=Expiring.CURRENT
    )
    inst2 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiring=Expiring.NEXT
    )
    assert inst1 != inst2

def test_instrument_inequality_atm():
    inst1 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        atm=0
    )
    inst2 = Instrument(
        type=InstrumentType.PE,
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        atm=1
    )
    assert inst1 != inst2

def test_instrument_not_equal_to_other_type():
    inst = Instrument(
        type=InstrumentType.FUTURE,
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT"
    )
    assert inst != "not an instrument"
