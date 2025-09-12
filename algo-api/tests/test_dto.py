import pytest
from algo.application.run_backtest_usecase import TradeDTO, TradableDTO, BackTestReportDTO
from algo.domain.strategy import Exchange, Instrument, InstrumentType

class MockTrade:
    def __init__(self):
        self.entry_price = 100.0
        self.entry_time = '2025-09-12T09:15:00'
        self.exit_price = 110.0
        self.exit_time = '2025-09-12T15:30:00'
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
        self.start_date = '2025-09-01'
        self.end_date = '2025-09-12'
        self.strategy_name = 'MockStrategy'
        self.tradable = MockTradableInstrument()
        self.winning_streak = 3
        self.losing_streak = 1
        self.max_gain = 200.0
        self.max_loss = -50.0
        self.total_pnl_points = 150.0
        self.total_pnl_percentage = 0.15
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
    assert d['entry_time'] == '2025-09-12T09:15:00'
    assert d['exit_price'] == 110.0
    assert d['exit_time'] == '2025-09-12T15:30:00'
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
    assert d['start_date'] == '01-Sep-2025'
    assert d['end_date'] == '12-Sep-2025'
    assert d['strategy_name'] == 'MockStrategy'
    assert d['total_trades_count'] == 1
    assert d['winning_trades_count'] == 1
    assert d['losing_trades_count'] == 0
    assert d['winning_streak'] == 3
    assert d['max_gain'] == 200.0
    assert d['tradable']['instrument']['instrument_key'] == 'NSE_INE869I01013'
    assert len(d['tradable']['trades']) == 1
    assert d['tradable']['trades'][0]['entry_price'] == 100.0
