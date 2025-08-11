import pandas as pd
import pandas_ta as ta
from typing import Dict, Any, List, Union
from .registry import register_indicator

@register_indicator("ema")
def indicator_ema(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate EMA value using pandas_ta."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    period = params.get("period", 20)
    price_col = params.get("price", "close")

    ema_series = ta.ema(historical_data[price_col], length=period)
    return float(ema_series.iloc[-1])  # last EMA value
