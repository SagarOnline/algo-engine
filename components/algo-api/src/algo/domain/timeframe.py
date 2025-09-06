from enum import Enum

class Timeframe(Enum):
    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    SIXTY_MINUTES = "60min"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
