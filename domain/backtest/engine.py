from datetime import datetime, date
from typing import Dict, Any, List
import json

from domain.strategy import Strategy
from infrastructure.jsonstrategy import JsonStrategy
from domain.backtest.historical_data_repository import HistoricalDataRepository
from infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from domain.timeframe import Timeframe


class BacktestEngine:
    def __init__(self, strategy: Strategy, historical_data_repository: HistoricalDataRepository):
        self.strategy = strategy
        self.historical_data_repository = historical_data_repository

    def run(self, start_date: date, end_date: date) -> Dict[str, Any]:
        instrument = self.strategy.get_instrument()
        timeframe_str = self.strategy.get_timeframe()
        timeframe = Timeframe(timeframe_str)

        required_start_date = self.strategy.get_required_history_start_date(start_date)
        historical_data = self.historical_data_repository.get_historical_data(instrument, required_start_date, end_date, timeframe)
        
        trades = []
        in_trade = False
        
        for i in range(1, len(historical_data)):
            current_candle = historical_data[i]
            previous_candles = historical_data[:i]
            
            # Ensure we only start trading from the requested start_date
            if current_candle['timestamp'].date() < start_date:
                continue

            if not in_trade:
                if self.strategy.should_enter_trade(current_candle, previous_candles):
                    # Enter trade
                    entry_price = current_candle["close"]
                    trades.append({"entry_price": entry_price, "entry_time": current_candle["timestamp"]})
                    in_trade = True
            else:
                if self.strategy.should_exit_trade(current_candle, previous_candles):
                    # Exit trade
                    exit_price = current_candle["close"]
                    trades[-1]["exit_price"] = exit_price
                    trades[-1]["exit_time"] = current_candle["timestamp"]
                    in_trade = False
        
        # Calculate results
        pnl = 0
        for trade in trades:
            if "exit_price" in trade:
                pnl += trade["exit_price"] - trade["entry_price"]
        
        return {
            "strategy": self.strategy.get_name(),
            "pnl": pnl,
            "trades": trades
        }


def backtest(strategy_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Runs a backtest for a given strategy.
    """
    # Load strategy
    strategy_path = f"infrastructure/strategies/{strategy_name}.json"
    with open(strategy_path) as f:
        strategy_data = json.load(f)
    strategy = JsonStrategy(strategy_data)
    
    # Initialize historical data repository
    historical_data_repository = ParquetHistoricalDataRepository()

    # Initialize and run backtest engine
    engine = BacktestEngine(strategy, historical_data_repository)
    
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    results = engine.run(start_date_obj, end_date_obj)
    
    return results
