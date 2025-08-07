from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    indicators: Dict[str, Any] = field(default_factory=dict)
