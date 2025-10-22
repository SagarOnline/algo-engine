import pytest
from algo.domain.instrument.instrument import Exchange, Expiring, Expiry, Type
from algo.domain.instrument.instrument import Instrument

def test_instrument_equality_basic():
    inst1 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    inst2 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    assert inst1 == inst2

def test_instrument_equality_with_all_fields():
    inst1 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.CURRENT,
        atm=0,
        type=Type.PE
    )
    inst2 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY,
        expiring=Expiring.CURRENT,
        atm=0,
        type=Type.PE
    )
    assert inst1 == inst2

def test_instrument_inequality_type():
    inst1 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    inst2 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.EQ
    )
    assert inst1 != inst2

def test_instrument_inequality_exchange():
    inst1 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    inst2 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    assert inst1 != inst2

def test_instrument_inequality_instrument_key():
    inst1 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    inst2 = Instrument(
        exchange=Exchange.NSE,
        instrument_key="BANKNIFTY23JUNFUT",
        type=Type.FUT
    )
    assert inst1 != inst2

def test_instrument_inequality_expiry():
    inst1 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.MONTHLY,
        type=Type.PE
    )
    inst2 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiry=Expiry.WEEKLY,
        type=Type.PE
    )
    assert inst1 != inst2

def test_instrument_inequality_expiring():
    inst1 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiring=Expiring.CURRENT,
        type=Type.PE
    )
    inst2 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        expiring=Expiring.NEXT1,
        type=Type.PE
    )
    assert inst1 != inst2

def test_instrument_inequality_atm():
    inst1 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        atm=0,
        type=Type.PE
    )
    inst2 = Instrument(
        exchange=Exchange.BSE,
        instrument_key="BANKNIFTY23JUN18000PE",
        atm=1,
        type=Type.PE
    )
    assert inst1 != inst2

def test_instrument_not_equal_to_other_type():
    inst = Instrument(
        exchange=Exchange.NSE,
        instrument_key="NIFTY23JUNFUT",
        type=Type.FUT
    )
    assert inst != "not an instrument"
