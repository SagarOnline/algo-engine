from datetime import date
from typing import List
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.report import BackTestReport
from algo_core.domain.trade import Trade
from algo_core.domain.backtest.historical_data import HistoricalData

class BackTest:

    def __init__(self, strategy: Strategy, underlying_instrument_hd: HistoricalData, start_date: date, position_instrument_hd: HistoricalData = None):
        self.strategy = strategy
        self.underlying_instrument_hd = underlying_instrument_hd
        self.position_instrument_hd = position_instrument_hd if position_instrument_hd is not None else underlying_instrument_hd
        self.start_date = start_date

    def run(self) -> BackTestReport:
        instrument = self.strategy.get_instrument()
        trades = []
        in_trade = False
        entry_price = 0.0
        entry_time = None
        for i in range(0, len(self.underlying_instrument_hd.data)):
            previous_candles = self.underlying_instrument_hd.data[:i+1]
            candle = self.underlying_instrument_hd.data[i]
            if candle['timestamp'].date() < self.start_date:
                continue
            # Use hd for entry/exit logic, but use position_instrument_hd for execution
            if not in_trade:
                if self.strategy.should_enter_trade(previous_candles):
                    # Find execution candle in position_instrument_hd by timestamp
                    exec_candle = self.position_instrument_hd.getCandleBy(
                        candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
                    )
                    if exec_candle is None:
                        raise ValueError(f"No execution candle found for entry at timestamp {candle['timestamp']}")
                    entry_price = exec_candle["close"]
                    entry_time = exec_candle["timestamp"]
                    in_trade = True
            else:
                if self.strategy.should_exit_trade(previous_candles):
                    exec_candle = self.position_instrument_hd.getCandleBy(
                        candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
                    )
                    if exec_candle is None:
                        raise ValueError(f"No execution candle found for exit at timestamp {candle['timestamp']}")
                    exit_price = exec_candle["close"]
                    exit_time = exec_candle["timestamp"]
                    trades.append(Trade(instrument, entry_time, entry_price, exit_time, exit_price))
                    in_trade = False
        pnl = 0
        for trade in trades:
            pnl += trade.profit()
        return BackTestReport(self.strategy.get_name(), pnl, trades)
