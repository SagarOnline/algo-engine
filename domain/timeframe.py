from enum import Enum

class Timeframe(Enum):
    ONE_MINUTE = "1MIN"
    TWO_MINUTES = "2MIN"
    FIVE_MINUTES = "5MIN"
    TEN_MINUTES = "10MIN"
    FIFTEEN_MINUTES = "15MIN"
    THIRTY_MINUTES = "30MIN"
    ONE_HOUR = "1HR"
    TWO_HOURS = "2HR"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1MO"
