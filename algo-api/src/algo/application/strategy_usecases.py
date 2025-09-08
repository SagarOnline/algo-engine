from typing import List
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.strategy import Instrument

class StrategyDTO:
    def __init__(self, name: str, display_name: str, description: str, instrument: Instrument):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.instrument = instrument

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "instrument": self.instrument.to_dict() if hasattr(self.instrument, 'to_dict') else str(self.instrument)
        }

class StrategyUseCase:
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def list_strategies(self) -> List[StrategyDTO]:
        strategies = self.strategy_repository.list_strategies()
        dtos = []
        for s in strategies:
            # Use getter methods if available, fallback to attribute
            name = s.get_name()
            display_name = s.get_display_name()
            description = s.get_display_name()
            instrument = s.get_instrument()
            dto = StrategyDTO(
                name=name,
                display_name=display_name,
                description=description,
                instrument=instrument
            )
            dtos.append(dto)
        return dtos
