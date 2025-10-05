from datetime import date
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.strategy import Strategy
from algo.domain.backtest.report import BackTestReport, TradableInstrument
from algo.domain.strategy.strategy_evaluator import StrategyEvaluator
from algo.domain.backtest.backtest_trade_executor import BackTestTradeExecutor
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe

class BackTest:

    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository, 
                 tradable_instrument_repository: TradableInstrumentRepository, start_date: date, end_date: date):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository
        self.tradable_instrument_repository = tradable_instrument_repository
        self.start_date = start_date
        self.end_date = end_date

    def run(self) -> BackTestReport:
        """
        Run the backtest using StrategyEvaluator and BackTestTradeExecutor.
        
        Returns:
            BackTestReport: The backtest results
        """
        # Create and save TradableInstrument for the strategy's PositionInstrument
        position_instrument = self.strategy.get_position_instrument()
        tradable_instrument = TradableInstrument(position_instrument)
        self.tradable_instrument_repository.save_tradable_instrument(
            self.strategy.get_name(), 
            tradable_instrument
        )
        
        # Initialize components
        strategy_evaluator = StrategyEvaluator(
            self.strategy, 
            self.historical_data_repository, 
            self.tradable_instrument_repository
        )
        
        trade_executor = BackTestTradeExecutor(
            self.tradable_instrument_repository,
            self.historical_data_repository,
            self.strategy.get_name()
        )
        

        
        # Get historical data for the underlying instrument over the entire backtest period
        underlying_instrument = self.strategy.get_instrument()
        timeframe = Timeframe(self.strategy.get_timeframe())
        
        # Get extended historical data to ensure strategy has enough history for evaluation
        extended_start_date = self.strategy.get_required_history_start_date(self.start_date)
        historical_data = self.historical_data_repository.get_historical_data(
            underlying_instrument, 
            extended_start_date, 
            self.end_date, 
            timeframe
        )
        
        # Process each candle in the historical data
        for i, candle in enumerate(historical_data.data):
            candle_date = candle['timestamp'].date()
            
            # Skip candles before the backtest start date
            if candle_date < self.start_date:
                continue
                
            # Skip candles after the backtest end date
            if candle_date > self.end_date:
                break
                
            # Evaluate strategy to generate trade signals
            trade_signal = strategy_evaluator.evaluate(candle)
            
            # Execute trade signal if generated
            if trade_signal is not None:
                trade_executor.execute(trade_signal)
        
        # Get the final state of the tradable instrument (it should exist since we created it at the start)
        tradables = self.tradable_instrument_repository.get_tradable_instruments(self.strategy.get_name())
        tradable = tradables[0]  # We know it exists since we created it at the beginning

        # Create and return the backtest report
        return BackTestReport(
            self.strategy.get_display_name(), 
            tradable, 
            start_date=self.start_date, 
            end_date=self.end_date
        )
