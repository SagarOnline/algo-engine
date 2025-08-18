from abc import ABC, abstractmethod
from typing import List, Optional, Union, Literal, Dict, Any
from datetime import date, timedelta
import math
from domain.indicators.registry import IndicatorRegistry
from domain.market import Candle
from enum import Enum
from domain.timeframe import Timeframe

class InstrumentType(Enum):
    FUTURE = "FUTURE"
    PE = "PE"
    CE = "CE"
    STOCK = "STOCK"

class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"

class Expiry(Enum):
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"

class Expiring(Enum):
    CURRENT = "CURRENT"
    NEXT = "NEXT"

class PositionAction(Enum):
    BUY = "BUY"
    SELL = "SELL"


class Instrument:
    def __init__(self, 
        type: InstrumentType,
        exchange: Exchange,
        instrument_key: str,
        expiry: Optional[Expiry] = None,
        expiring: Optional[Expiring] = None, 
        atm: Optional[int] = None
    ):
        self.type = InstrumentType(type)
        self.exchange = Exchange(exchange)
        self.instrument_key = instrument_key
        self.expiry = Expiry(expiry) if expiry else None
        self.expiring = Expiring(expiring) if expiring else None
        self.atm = atm


class Position:
    def __init__(self, action: PositionAction, instrument: Instrument):
        self.action = PositionAction(action)
        self.instrument = instrument

class Expression:
    def __init__(self, expr_type: str, params: Dict):
        self.type = expr_type  # e.g., "ema", "price"
        self.params = params   # e.g., {"period": 20, "price": "close"}

    def __repr__(self):
        return f"Expression(type={self.type}, params={self.params})"

    def evaluate(self, historical_data:List[Dict[str, Any]]) -> float:
        handler = IndicatorRegistry.get(self.type.lower())
        return handler(historical_data, self.params)

class Condition:
    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator  # e.g., ">", "<", "=="
        self.left = left
        self.right = right

    def __repr__(self):
        return (
            f"Condition(operator={self.operator}, "
            f"left={self.left}, right={self.right})"
        )

    def is_satisfied(self, historical_data:List[Dict[str, Any]]) -> bool:
        left_value = self.left.evaluate(historical_data)
        right_value = self.right.evaluate(historical_data)
        import math
        if math.isnan(left_value) or math.isnan(right_value):
            return False
        if self.operator == ">":
            return left_value > right_value
        elif self.operator == "<":
            return left_value < right_value
        elif self.operator == "==":
            return left_value == right_value
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")
    
class RuleSet:
    def __init__(self, logic: str, conditions: List[Condition]):
        self.logic = logic  # "AND" or "OR"
        self.conditions = conditions

    def __repr__(self):
        return f"RuleSet(logic={self.logic}, conditions={self.conditions})"

    def apply_on(self, historical_data:List[Dict[str, Any]]) -> bool:
        logic = self.logic.upper()
        results = [cond.is_satisfied(historical_data) for cond in self.conditions]
        return all(results) if logic == "AND" else any(results)
    


class Strategy(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_instrument(self) -> Instrument:
        pass

    @abstractmethod
    def get_timeframe(self) -> Timeframe:
        pass

    @abstractmethod
    def get_capital(self) -> int:
        pass

    @abstractmethod
    def get_entry_rules(self) -> RuleSet:
        pass

    @abstractmethod
    def get_exit_rules(self) -> RuleSet:
        pass

    @abstractmethod
    def get_position(self) -> Position:
        pass

    def get_required_history_start_date(self, start_date: date) -> date:
        entry_rules = self.get_entry_rules()
        exit_rules = self.get_exit_rules()

        all_expressions = []
        if entry_rules and entry_rules.conditions:
            for cond in entry_rules.conditions:
                all_expressions.append(cond.left)
                all_expressions.append(cond.right)
        
        if exit_rules and exit_rules.conditions:
            for cond in exit_rules.conditions:
                all_expressions.append(cond.left)
                all_expressions.append(cond.right)

        max_period = 0
        for expr in all_expressions:
            if "period" in expr.params:
                period = expr.params["period"]
                if isinstance(period, int) and period > max_period:
                    max_period = period
        
        if max_period == 0:
            return start_date

        timeframe = self.get_timeframe()
        timeframe_str = timeframe.value

        # Estimate calendar days needed for max_period candles
        # This is a rough estimation and might need to be adjusted based on market specifics
        calendar_days_buffer_multiplier = 1.5 # Buffer for weekends and holidays, 7/5 is 1.4, 1.5 is safer

        if timeframe_str.endswith('d'):
            days_needed = max_period
        elif timeframe_str.endswith('w'):
            days_needed = max_period * 7
        elif timeframe_str.endswith('min'):
            minutes = int(timeframe_str[:-3])
            # Assuming 375 trading minutes a day
            candles_per_day = 375 / minutes
            days_needed = math.ceil(max_period / candles_per_day)
        else:
            days_needed = 0 # Should not happen for valid timeframes

        calendar_days_needed = math.ceil(days_needed * calendar_days_buffer_multiplier)
        
        return start_date - timedelta(days=calendar_days_needed)

    def should_enter_trade(self, historical_data: List[Dict[str, Any]]) -> bool:
        entry_rules = self.get_entry_rules()
        return entry_rules.apply_on(historical_data)

    def should_exit_trade(self, historical_data: List[Dict[str, Any]]) -> bool:
        exit_rules = self.get_exit_rules()
        return exit_rules.apply_on(historical_data)

    # _evaluate_expression moved to Condition
    
