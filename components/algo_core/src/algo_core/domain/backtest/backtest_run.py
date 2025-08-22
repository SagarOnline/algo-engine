from datetime import date
from typing import List
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.report import BackTestReport
from algo_core.domain.trade import Trade
from algo_core.domain.backtest.historical_data import HistoricalData

class BackTest:

    def __init__(self, strategy: Strategy, hd: HistoricalData, start_date: date):
        self.strategy = strategy
        self.hd = hd
        self.start_date = start_date

    def run(self) -> BackTestReport:
        instrument = self.strategy.get_instrument()
        trades = []
        in_trade = False
        entry_price = 0.0
        entry_time = None
        for i in range(0, len(self.hd.data)):
            previous_candles = self.hd.data[:i+1]
            if previous_candles[i]['timestamp'].date() < self.start_date:
                continue
            if not in_trade:
                if self.strategy.should_enter_trade(previous_candles):
                    entry_price = previous_candles[i]["close"]
                    entry_time = previous_candles[i]["timestamp"]
                    in_trade = True
            else:
                if self.strategy.should_exit_trade(previous_candles):
                    exit_price = previous_candles[i]["close"]
                    exit_time = previous_candles[i]["timestamp"]
                    trades.append(Trade(instrument, entry_time, entry_price, exit_time, exit_price))
                    in_trade = False
        pnl = 0
        for trade in trades:
            pnl += trade.profit()
        return BackTestReport(self.strategy.get_name(), pnl, trades)
