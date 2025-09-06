import pytest
import pandas as pd
from algo.domain.indicators.rsi import indicator_rsi

def test_indicator_rsi_with_dataframe():
    df = pd.DataFrame([
        {"close": 10},
        {"close": 12},
        {"close": 14},
        {"close": 16},
        {"close": 18},
        {"close": 20},
    ])
    params = {"period": 3, "price": "close"}
    result = indicator_rsi(df, params)
    assert isinstance(result, float)

def test_indicator_rsi_with_list_of_dicts():
    data = [
        {"close": 10},
        {"close": 12},
        {"close": 14},
        {"close": 16},
        {"close": 18},
        {"close": 20},
    ]
    params = {"period": 3, "price": "close"}
    result = indicator_rsi(data, params)
    assert isinstance(result, float)

def test_indicator_rsi_with_no_historical_data():
    df = pd.DataFrame([])
    params = {"period": 3, "price": "close"}
    with pytest.raises(RuntimeError, match="historical_data is empty in rsi indicator"):
        indicator_rsi(df, params)

def test_indicator_rsi_with_default_params():
    df = pd.DataFrame([
        {"close": 1}, {"close": 2}, {"close": 3}, {"close": 4}, {"close": 5},
        {"close": 6}, {"close": 7}, {"close": 8}, {"close": 9}, {"close": 10}
    ])
    # No params provided, should use defaults
    result = indicator_rsi(df, {})
    assert isinstance(result, float)
