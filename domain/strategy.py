from abc import ABC, abstractmethod
from typing import List, Optional, Union,Literal
from domain.indicators.registry import IndicatorRegistry
from domain.market import Candle
from typing import List,Dict,Any
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
        symbol: str,
        expiry: Optional[Expiry] = None,
        expiring: Optional[Expiring] = None, 
        atm: Optional[int] = None
    ):
        self.type = InstrumentType(type)
        self.exchange = Exchange(exchange)
        self.symbol = symbol
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
    
class RuleSet:
    def __init__(self, logic: str, conditions: List[Condition]):
        self.logic = logic  # "AND" or "OR"
        self.conditions = conditions

    def __repr__(self):
        return f"RuleSet(logic={self.logic}, conditions={self.conditions})"
    


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

    def should_enter_trade(self, candle: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> bool:
        entry_rules = self.get_entry_rules()
        logic = entry_rules.logic.upper()
        results = [
            self._evaluate_condition(cond, candle, historical_data)
            for cond in entry_rules.conditions
        ]
        return all(results) if logic == "AND" else any(results)
    
    def should_exit_trade(self, candle: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> bool:
        exit_rules = self.get_exit_rules()
        logic = exit_rules.logic.upper()
        results = [
            self._evaluate_condition(cond, candle, historical_data)
            for cond in exit_rules.conditions
        ]
        return all(results) if logic == "AND" else any(results)

    def _evaluate_condition(self, condition:Condition, candle, historical_data:List[Dict[str, Any]]) -> bool:
        left_value = self._evaluate_expression(condition.left, candle, historical_data)
        right_value = self._evaluate_expression(condition.right, candle, historical_data)

        if condition.operator == ">":
            return left_value > right_value
        elif condition.operator == "<":
            return left_value < right_value
        elif condition.operator == "==":
            return left_value == right_value
        else:
            raise ValueError(f"Unsupported operator: {condition.operator}")

    def _evaluate_expression(self, expression:Expression, candle, historical_data:List[Dict[str, Any]]) -> float:
        handler = IndicatorRegistry.get(expression.type.lower())
        return handler(candle, historical_data, expression.params)
    
