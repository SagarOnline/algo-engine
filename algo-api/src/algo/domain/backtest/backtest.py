from datetime import date
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.strategy import Strategy
from algo.domain.backtest.report import BackTestReport, BackTestReport, TradableInstrument
from algo.domain.backtest.historical_data import HistoricalData
class BackTest:

    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository, start_date: date, end_date: date):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository
        self.start_date = start_date
        self.end_date = end_date

    def run(self) -> BackTestReport:
        
        # tradable = TradableInstrument(self.strategy.get_instrument())
        # position = self.strategy.get_position_instrument()
        # for i in range(0, len(self.underlying_instrument_hd.data)):
        #     previous_candles = self.underlying_instrument_hd.data[:i+1]
        #     candle = self.underlying_instrument_hd.data[i]
        #     if candle['timestamp'].date() < self.start_date:
        #         continue
        #     tradable.process_stop_loss(candle['close'], candle['timestamp'])
        #     # Use hd for entry/exit logic, but use position_instrument_hd for execution
        #     if not tradable.is_any_position_open() and self.strategy.should_enter_trade(previous_candles):
        #         exec_candle = self.position_instrument_hd.getCandleBy(
        #             candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
        #         )
        #         if exec_candle is None:
        #             raise ValueError(f"No execution candle found for entry at timestamp {candle['timestamp']}")
        #         stop_loss_price = self.strategy.calculate_stop_loss_for(exec_candle["close"])
        #         tradable.add_position(exec_candle["timestamp"], exec_candle["close"], position.action, 1, stop_loss=stop_loss_price)
        #         continue
                
        #     if tradable.is_any_position_open() and self.strategy.should_exit_trade(previous_candles):
        #         exec_candle = self.position_instrument_hd.getCandleBy(
        #             candle['timestamp'].isoformat() if hasattr(candle['timestamp'], 'isoformat') else str(candle['timestamp'])
        #         )
        #         if exec_candle is None:
        #             raise ValueError(f"No execution candle found for exit at timestamp {candle['timestamp']}")
        #         tradable.exit_position(exec_candle["timestamp"], exec_candle["close"], position.get_close_action(), 1)

        return BackTestReport(self.strategy.get_display_name(), tradable, start_date=self.start_date, end_date=self.end_date)
