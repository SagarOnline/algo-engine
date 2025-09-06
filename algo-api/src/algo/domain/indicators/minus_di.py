import pandas as pd
import talib
from typing import Dict, Any, List, Union
from algo.domain.indicators.registry import register_indicator

@register_indicator("minus_di")
def indicator_minus_di(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate -DI (Negative Directional Indicator) value using TA-Lib."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in minus_di indicator")
    
    period = params.get("period", 14)  # Default = 14

    plus_di_series = talib.MINUS_DI(
        historical_data["high"].astype(float).values,
        historical_data["low"].astype(float).values,
        historical_data["close"].astype(float).values,
        timeperiod=period
    )

    return float(plus_di_series[-1])  # last +DI value
