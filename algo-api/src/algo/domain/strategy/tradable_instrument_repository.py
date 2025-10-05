from abc import ABC, abstractmethod
from typing import List
from algo.domain.backtest.report import TradableInstrument

class TradableInstrumentRepository(ABC):
    @abstractmethod
    def get_tradable_instruments(self, strategy_name) -> List[TradableInstrument]:
        """Return list of TradableInstrument for the given strategy name."""
        pass

    @abstractmethod
    def save_tradable_instrument(self, strategy_name, tradable_instrument: TradableInstrument) -> None:
        """Save a TradableInstrument for the given strategy name."""
        pass
