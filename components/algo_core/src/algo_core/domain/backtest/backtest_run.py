from datetime import date
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.report import BackTestReport
from algo_core.domain.backtest.historical_data import HistoricalData
from algo_core.domain.backtest.report import TradableInstrument
class BackTest:

    def __init__(self, strategy: Strategy, underlying_instrument_hd: HistoricalData, position_instrument_hd: HistoricalData, start_date: date, end_date: date):
        self.strategy = strategy
        self.underlying_instrument_hd = underlying_instrument_hd
        self.position_instrument_hd = position_instrument_hd if position_instrument_hd is not None else underlying_instrument_hd
        self.start_date = start_date
        self.end_date = end_date

    def run(self) -> BackTestReport:
        
        tradable = TradableInstrument(self.strategy.get_instrument())
        position = self.strategy.get_position()
        for i in range(0, len(self.underlying_instrument_hd.data)):
            previous_candles = self.underlying_instrument_hd.data[:i+1]
            candle = self.underlying_instrument_hd.data[i]
            if candle['timestamp'].date() < self.start_date:
                continue
            # Use hd for entry/exit logic, but use position_instrument_hd for execution
            if not tradable.is_trade_open() and self.strategy.should_enter_trade(previous_candles):
                exec_candle = self.position_instrument_hd.getCandleBy(
                    candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
                )
                if exec_candle is None:
                    raise ValueError(f"No execution candle found for entry at timestamp {candle['timestamp']}")
                tradable.execute_order(exec_candle["timestamp"], exec_candle["close"], position.action, 1)
                continue
                
            if tradable.is_trade_open() and self.strategy.should_exit_trade(previous_candles):
                exec_candle = self.position_instrument_hd.getCandleBy(
                    candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
                )
                if exec_candle is None:
                    raise ValueError(f"No execution candle found for exit at timestamp {candle['timestamp']}")
                tradable.execute_order(exec_candle["timestamp"], exec_candle["close"], position.get_close_action(), 1)

        return BackTestReport(self.strategy.get_name(), tradable, start_date=self.start_date, end_date=self.end_date)
