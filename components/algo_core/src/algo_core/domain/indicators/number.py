from typing import Dict, Any, List,Union
from algo_core.domain.indicators.registry import register_indicator
import pandas as pd

@register_indicator("number")
def indicator_number(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)
    return float(params.get("value", 0))
