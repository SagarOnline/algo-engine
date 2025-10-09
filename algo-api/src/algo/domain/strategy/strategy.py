from abc import ABC, abstractmethod
from typing import List, Optional, Union, Literal, Dict, Any
from datetime import date, datetime, timedelta
import math
from algo.domain.indicators.registry import IndicatorRegistry
from algo.domain.market import Candle
from enum import Enum
from algo.domain.timeframe import Timeframe

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

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"

class StopLossType(Enum):
    POINTS = "POINTS"
    PERCENTAGE = "PERCENTAGE"

class StopLoss:
    def __init__(self, value: float, type: StopLossType):
        self.value = value
        self.type = type

class RiskManagement:
    def __init__(self, stop_loss: StopLoss):
        self.stop_loss = stop_loss
        
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
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "exchange": self.exchange.value,
            "instrument_key": self.instrument_key,
            "expiry": self.expiry.value if self.expiry else None,
            "expiring": self.expiring.value if self.expiring else None,
            "atm": self.atm
        }
        

    def __eq__(self, other):
        if not isinstance(other, Instrument):
            return False
        return (
            self.type == other.type and
            self.exchange == other.exchange and
            self.instrument_key == other.instrument_key and
            self.expiry == other.expiry and
            self.expiring == other.expiring and
            self.atm == other.atm
        )


class PositionInstrument:
    def __init__(self, action: TradeAction, instrument: Instrument):
        self.action = TradeAction(action)
        self.instrument = instrument
        
    def get_close_action(self) -> TradeAction:
        return TradeAction.SELL if self.action == TradeAction.BUY else TradeAction.BUY

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
    def get_maximum_period_value(self) -> int:
        max_period = 0
        for cond in self.conditions:
            for expr in [cond.left, cond.right]:
                if "period" in expr.params:
                    period = expr.params["period"]
                    if isinstance(period, int) and period > max_period:
                        max_period = period
        return max_period
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
    def get_display_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
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
    def get_position_instrument(self) -> PositionInstrument:
        pass

    @abstractmethod
    def get_risk_management(self) -> Optional[RiskManagement]:
        pass

    def get_required_history_start_date(self, end_datetime: datetime) -> datetime:
        entry_rules = self.get_entry_rules()
        exit_rules = self.get_exit_rules()
        period_multiplier = 5 # Multiplier to ensure enough data for indicators
        entry_max = entry_rules.get_maximum_period_value()* period_multiplier if entry_rules else 0
        exit_max = exit_rules.get_maximum_period_value()* period_multiplier if exit_rules else 0
        max_period = max(entry_max, exit_max)

        if max_period == 0:
            return end_datetime

        timeframe = self.get_timeframe()
        timeframe_str = timeframe.value

        # Estimate calendar days needed for max_period candles
        # This is a rough estimation and might need to be adjusted based on market specifics
        calendar_days_buffer_multiplier = 1.5 # Buffer for weekends and holidays, 7/5 is 1.4, 1.5 is safer

        if timeframe_str.endswith('d'):
            days_needed = max_period
            calendar_days_needed = math.ceil(days_needed * calendar_days_buffer_multiplier)
        elif timeframe_str.endswith('w'):
            days_needed = max_period * 7
            calendar_days_needed = math.ceil(days_needed * calendar_days_buffer_multiplier)
        elif timeframe_str.endswith('min'):
            minutes = int(timeframe_str[:-3])
            # Assuming 375 trading minutes a day
            candles_per_day = 375 / minutes
            days_needed = math.ceil(max_period / candles_per_day)
            # Add buffer and ONE extra day to account for end_datetime possibly being mid-session
            calendar_days_needed = math.ceil(days_needed * calendar_days_buffer_multiplier) + 1
        else:
            calendar_days_needed = 0 # Should not happen for valid timeframes

        return end_datetime - timedelta(days=calendar_days_needed)

    def should_enter_trade(self, historical_data: List[Dict[str, Any]]) -> bool:
        entry_rules = self.get_entry_rules()
        return entry_rules.apply_on(historical_data)

    def should_exit_trade(self, historical_data: List[Dict[str, Any]]) -> bool:
        exit_rules = self.get_exit_rules()
        return exit_rules.apply_on(historical_data)

    def calculate_stop_loss_for(self, price: float) -> Optional[float]:
        risk_management = self.get_risk_management()
        if not risk_management or not risk_management.stop_loss:
            return None
        stop_loss = risk_management.stop_loss
        if stop_loss.type == StopLossType.POINTS:
            return price - stop_loss.value
        elif stop_loss.type == StopLossType.PERCENTAGE:
            return price * (1 - stop_loss.value / 100)
        else:
            return None
