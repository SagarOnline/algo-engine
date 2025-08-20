from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Market:
    exchange: str
    instrument_key: str

    @classmethod
    def from_str(cls, market_str: str) -> "Market":
        parts = market_str.split("_")
        return Market(exchange=parts[0], instrument_key=parts[1])

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    indicators: Dict[str, Any] = field(default_factory=dict)
