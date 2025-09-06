import pandas as pd
import talib
from typing import Dict, Any, List, Union
from algo.domain.indicators.registry import register_indicator

@register_indicator("adx")
def indicator_adx(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate ADX value using TA-Lib."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in adx indicator")
    
    period = params.get("period", 14)  # Default ADX period = 14

    # TA-Lib expects NumPy arrays
    adx_series = talib.ADX(
        historical_data["high"].astype(float).values,
        historical_data["low"].astype(float).values,
        historical_data["close"].astype(float).values,
        timeperiod=period
    )

    return float(adx_series[-1])  # last ADX value
