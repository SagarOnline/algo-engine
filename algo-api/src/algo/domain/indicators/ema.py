import pandas as pd
import talib
from typing import Dict, Any, List, Union
from algo.domain.indicators.registry import register_indicator

@register_indicator("ema")
def indicator_ema(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate EMA value using TA-Lib."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in ema indicator")
    
    period = params.get("period", 20)
    price_col = params.get("price", "close")

    # TA-Lib expects a NumPy array
    ema_series = talib.EMA(historical_data[price_col].astype(float).values, timeperiod=period)

    return float(ema_series[-1])  # last EMA value
