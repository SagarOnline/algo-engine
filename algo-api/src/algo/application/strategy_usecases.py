from typing import List
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.strategy import Instrument, Strategy


class InstrumentDTO:
    def __init__(self, instrument: Instrument):
        self._instrument = instrument
        self.type = instrument.type.name if instrument.type else None
        self.exchange = instrument.exchange.name if instrument.exchange else None
        self.instrument_key = instrument.instrument_key
        self.expiry = instrument.expiry.name if instrument.expiry else None
        self.expiring = instrument.expiring.name if instrument.expiring else None
        self.atm = instrument.atm
    
    def get_display_name(self):
        key = self.instrument_key
        exchange = self.exchange
        expiring = self.expiring
        expiry = self.expiry
        atm = self.atm
        parts = [f"{key}, {exchange}"]
        if expiring and expiry:
            parts.append(f", with {expiring} {expiry} expiry")
        if atm is not None:
            parts.append(f", atm {atm}")
        return "".join(parts)

    def to_dict(self):
        return {
            "type": self.type,
            "exchange": str(self.exchange),
            "instrument_key": str(self.instrument_key),
            "expiry": str(self.expiry),
            "expiring": str(self.expiring),
            "atm": self.atm,
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
