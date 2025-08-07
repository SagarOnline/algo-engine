from abc import ABC, abstractmethod
from typing import List, Optional, Union,Literal
from dataclasses import dataclass

@dataclass
class Indicator:
    name: str
    type: str
    params: dict

@dataclass
class Condition:
    condition: str
    left: Union[str, float]
    right: Union[str, float]

@dataclass
class RuleGroup:
    logic: Literal["AND", "OR"]
    conditions: List[Union['Condition', 'RuleGroup']]

@dataclass
class PositionSize:
    type: Literal["fixed", "percent"]
    value: float

@dataclass
class RiskManagement:
    capital: float
    order_type: str
    position_size: PositionSize
    stop_loss_percent: float
    take_profit_percent: float
    trailing_stop_loss_percent: Optional[float] = None

@dataclass
class ActiveTimeWindow:
    days: List[str]
    start_time: str
    end_time: str

@dataclass
class Metadata:
    created_by: str
    created_at: str

class Strategy(ABC):

    @abstractmethod
    def get_indicators(self) -> List[Indicator]:
        pass

    @abstractmethod
    def get_entry_rules(self) -> RuleGroup:
        pass

    @abstractmethod
    def get_exit_rules(self) -> RuleGroup:
        pass

    @abstractmethod
    def get_risk_management(self) -> RiskManagement:
        pass

    @abstractmethod
    def get_active_time_window(self) -> Optional[ActiveTimeWindow]:
        pass

    @abstractmethod
    def get_metadata(self) -> Metadata:
        pass
