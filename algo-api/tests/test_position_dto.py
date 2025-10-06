import pytest
from datetime import datetime
from algo.application.util import fmt_currency
from algo.domain.strategy.strategy import Instrument, TradeAction
from algo.domain.backtest.report import Position, PositionType
from algo.application.run_backtest_usecase import PositionDTO

def make_position(entry_price=None, entry_time=None, exit_price=None, exit_time=None):
    instrument = Instrument(type="STOCK", exchange="NSE", instrument_key="TCS")
    pos = Position(instrument, PositionType.LONG, 1, entry_price if entry_price is not None else 100.0, entry_time if entry_time is not None else datetime(2025, 9, 17, 9, 15))
    if exit_price is not None and exit_time is not None:
        pos.exit(exit_price, exit_time)
    return pos

def test_positiondto_exit_price_none():
    pos = make_position()
    dto = PositionDTO(pos)
    assert dto.exit_price == ""

def test_positiondto_exit_time_none():
    pos = make_position()
    dto = PositionDTO(pos)
    assert dto.exit_time == ""

def test_positiondto_all_fields_present():
    entry_time = datetime(2025, 9, 17, 9, 15)
    exit_time = datetime(2025, 9, 17, 15, 30)
    pos = make_position(entry_price=100.0, entry_time=entry_time, exit_price=110.0, exit_time=exit_time)
    dto = PositionDTO(pos)
    assert dto.entry_price == fmt_currency(100.0)
    assert dto.exit_price == fmt_currency(110.0)
    assert dto.entry_time != ""
    assert dto.exit_time != ""
