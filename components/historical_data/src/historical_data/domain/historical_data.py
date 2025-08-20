from dataclasses import dataclass
from datetime import datetime

@dataclass
class Candle:
    """Represents a single candle in a price chart."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int
