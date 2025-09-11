from typing import List
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.strategy import Instrument, Strategy


class InstrumentDTO:
    def __init__(self, instrument: Instrument):
        self._instrument = instrument

    def get_type(self):
        return self._instrument.type.name

    def get_exchange(self):
        return self._instrument.exchange.name

    def get_instrument_key(self):
        return getattr(self._instrument, 'instrument_key', None)

    def get_expiry(self):
        return self._instrument.expiry.name

    def get_expiring(self):
        return self._instrument.expiring.name

    def get_atm(self):
        return getattr(self._instrument, 'atm', None)
    
    def get_display_name(self):
        key = self.get_instrument_key()
        exchange = self.get_exchange()
        expiring = self.get_expiring()
        expiry = self.get_expiry()
        atm = self.get_atm()
        parts = [f"{key}, {exchange}"]
        if expiring and expiry:
            parts.append(f", with {expiring} {expiry} expiry")
        if atm is not None:
            parts.append(f", atm {atm}")
        return "".join(parts)

    def to_dict(self):
        return {
            "type": str(self.get_type()),
            "exchange": str(self.get_exchange()),
            "instrument_key": str(self.get_instrument_key()),
            "expiry": str(self.get_expiry()),
            "expiring": str(self.get_expiring()),
            "atm": self.get_atm(),
            "display_name": self.get_display_name()
        }


class StrategyDTO:
    def __init__(self, strategy: Strategy):
        self.name = strategy.get_name()
        self.display_name = strategy.get_display_name()
        self.description = strategy.get_description()
        self.instrument = InstrumentDTO(strategy.get_instrument())

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "instrument": self.instrument.to_dict() if hasattr(self.instrument, 'to_dict') else str(self.instrument)
        }

class PositionDTO:
    def __init__(self, position):
        self.action = position.action.name if position and hasattr(position.action, 'name') else str(position.action)
        self.instrument = InstrumentDTO(position.instrument)

    def to_dict(self):
        return {
            "action": self.action,
            "instrument": self.instrument.to_dict() if self.instrument else None
        }

class StrategyDetailsDTO:
    def __init__(self, strategy:Strategy):
        self.name = strategy.get_name()
        self.display_name = strategy.get_display_name()
        self.description = strategy.get_description()
        self.instrument = InstrumentDTO(strategy.get_instrument())
        self.timeframe = str(getattr(strategy.get_timeframe(), "value", strategy.get_timeframe()))
        position = strategy.get_position()
        if isinstance(position, list):
            self.positions = [PositionDTO(pos) for pos in position]
        else:
            self.positions = [PositionDTO(position)]

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "instrument": self.instrument.to_dict(),
            "timeframe": self.timeframe,
            "positions": [pos.to_dict() for pos in self.positions]
        }

class StrategyUseCase:
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def list_strategies(self) -> List[StrategyDTO]:
        strategies = self.strategy_repository.list_strategies()
        dtos = []
        for s in strategies:
            dtos.append(StrategyDTO(s))
        return dtos

    def get_strategy(self, strategy_name: str) -> 'StrategyDetailsDTO':
        try:
            strategy = self.strategy_repository.get_strategy(strategy_name)
        except ValueError:
            raise StrategyNotFound(f"Strategy '{strategy_name}' not found.")
        return StrategyDetailsDTO(strategy)

class StrategyNotFound(Exception):
    pass