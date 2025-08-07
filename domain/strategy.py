from abc import ABC, abstractmethod
from typing import List, Optional, Union,Literal
from dataclasses import dataclass
from domain.market import Candle
from typing import List,Dict

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
    def get_symbol(self) -> str:
        pass

    @abstractmethod
    def get_exchange(self) -> str:
        pass

    @abstractmethod
    def get_timeframe(self) -> str:
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

    
