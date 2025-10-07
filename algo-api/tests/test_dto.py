from datetime import date
import pytest
from algo.application.run_backtest_usecase import TradableDTO,PositionDTO, BackTestReportDTO
from algo.application.util import fmt_currency, fmt_datetime, fmt_percent
from algo.domain.backtest.report import BackTestReport
from algo.domain.strategy.strategy import Exchange, Instrument, InstrumentType, TradeAction

from datetime import datetime

from algo.domain.strategy.tradable_instrument import Position, PositionType, TradableInstrument

@pytest.fixture
def mock_tradable():
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    tradable.add_position(datetime(2025, 9, 12, 9, 15, 0), 100.0, TradeAction.BUY, 10)
    tradable.exit_position(datetime(2025, 9, 12, 15, 30, 0), 110.0, TradeAction.SELL, 10)
    return tradable

@pytest.fixture
def mock_backtest_report(mock_tradable):
    report = BackTestReport("test_strategy", mock_tradable, date(2025, 9, 1), date(2025, 9, 12))
    return report

def test_position_dto(mock_tradable):
    dto = PositionDTO(mock_tradable.positions[0])
    d = dto.to_dict()
    assert d['entry_price'] == fmt_currency(100.0)
    assert d['entry_time'] == fmt_datetime(datetime(2025, 9, 12, 9, 15, 0))
    assert d['exit_price'] == fmt_currency(110.0)
    assert d['exit_time'] == fmt_datetime(datetime(2025, 9, 12, 15, 30, 0))
    assert d['profit'] == fmt_currency(100.0)
    assert d['profit_percentage'] == fmt_percent(0.1)
    assert d['profit_points'] == 10.0
    assert d['quantity'] == 10

def test_tradable_dto(mock_tradable):
    dto = TradableDTO(mock_tradable)
    d = dto.to_dict()
    assert d['instrument']['instrument_key'] == 'NSE_INE869I01013'
    assert len(d['positions']) == 1

def test_backtest_report_dto(mock_backtest_report):
    dto = BackTestReportDTO(mock_backtest_report)
    d = dto.to_dict()
    summary = d['summary']
    assert isinstance(summary, dict)
    assert summary['start_date'] == '01-Sep-2025'
    assert summary['end_date'] == '12-Sep-2025'
    assert summary['strategy_name'] == 'test_strategy'
    assert summary['total_trades_count'] == 1
    assert summary['winning_trades_count'] == 1
    assert summary['losing_trades_count'] == 0
    assert summary['winning_streak'] == 1
    assert summary['max_gain'] == fmt_currency(100.0)
    assert d['tradable']['instrument']['instrument_key'] == 'NSE_INE869I01013'
    assert len(d['tradable']['positions']) == 1
    assert d['tradable']['positions'][0]['entry_price'] == fmt_currency(100.0)
