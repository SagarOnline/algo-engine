from datetime import date
import pytest
from algo.application.run_backtest_usecase import TradeDTO, TradableDTO, BackTestReportDTO
from algo.application.util import fmt_currency, fmt_datetime
from algo.domain.strategy import Exchange, Instrument, InstrumentType

from datetime import datetime

class MockTrade:
    def __init__(self):
        self.entry_price = 100.0
        self.entry_time = datetime(2025, 9, 12, 9, 15, 0)
        self.exit_price = 110.0
        self.exit_time = datetime(2025, 9, 12, 15, 30, 0)
        self.quantity = 10
    def profit(self):
        return 100.0
    def profit_percentage(self):
        return 0.10
    def profit_points(self):
        return 10.0

class MockTradableInstrument:
    def __init__(self):
        self.instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
        self.trades = [MockTrade()]

class MockBackTestReport:
    def __init__(self):
        self.start_date = date(2025, 9, 1)
        self.end_date = date(2025, 9, 12)
        self.strategy_name = 'MockStrategy'
        self.tradable = MockTradableInstrument()
    def winning_streak(self):
        return 3
    def losing_streak(self):
        return 1
    def max_gain(self):
        return 200.0
    def max_loss(self):
        return -50.0
    def total_pnl_points(self):
        return 150.0
    def total_pnl_percentage(self):
        return 0.15
    def total_trades_count(self):
        return 1
    def winning_trades_count(self):
        return 1
    def losing_trades_count(self):
        return 0

def test_trade_dto():
    trade = MockTrade()
    dto = TradeDTO(trade)
    d = dto.to_dict()
    assert d['entry_price'] == 100.0
    assert d['entry_time'] == fmt_datetime(datetime(2025, 9, 12, 9, 15, 0))
    assert d['exit_price'] == 110.0
    assert d['exit_time'] == fmt_datetime(datetime(2025, 9, 12, 15, 30, 0))
    assert d['profit'] == 100.0
    assert d['profit_percentage'] == 0.10
    assert d['profit_points'] == 10.0
    assert d['quantity'] == 10

def test_tradable_dto():
    tradable = MockTradableInstrument()
    dto = TradableDTO(tradable)
    d = dto.to_dict()
    assert d['instrument'] == 'MOCK_INSTRUMENT' or isinstance(d['instrument'], dict)
    assert len(d['trades']) == 1

def test_backtest_report_dto():
    report = MockBackTestReport()
    dto = BackTestReportDTO(report)
    d = dto.to_dict()
    summary = d['summary']
    assert isinstance(summary, dict)
    assert summary['start_date'] == '01-Sep-2025'
    assert summary['end_date'] == '12-Sep-2025'
    assert summary['strategy_name'] == 'MockStrategy'
    assert summary['total_trades_count'] == 1
    assert summary['winning_trades_count'] == 1
    assert summary['losing_trades_count'] == 0
    assert summary['winning_streak'] == 3
    assert summary['max_gain'] == fmt_currency(200.0)
    assert d['tradable']['instrument']['instrument_key'] == 'NSE_INE869I01013'
    assert len(d['tradable']['trades']) == 1
    assert d['tradable']['trades'][0]['entry_price'] == 100.0
