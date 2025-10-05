from typing import List, Dict
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.backtest.report import TradableInstrument

class InMemoryTradableInstrumentRepository(TradableInstrumentRepository):
    def __init__(self):
        self._storage: Dict[str, List[TradableInstrument]] = {}

    def get_tradable_instruments(self, strategy_name: str) -> List[TradableInstrument]:
        """Return list of TradableInstrument for the given strategy name."""
        return self._storage.get(strategy_name, [])

    def save_tradable_instrument(self, strategy_name: str, tradable_instrument: TradableInstrument) -> None:
        """Save a TradableInstrument for the given strategy name."""
        if strategy_name not in self._storage:
            self._storage[strategy_name] = []
        
        # Check if this instrument already exists for this strategy
        existing_instruments = self._storage[strategy_name]
        for i, existing in enumerate(existing_instruments):
            if existing.instrument.instrument_key == tradable_instrument.instrument.instrument_key:
                # Replace existing instrument
                existing_instruments[i] = tradable_instrument
                return
        
        # If not found, add as new instrument
        existing_instruments.append(tradable_instrument)
