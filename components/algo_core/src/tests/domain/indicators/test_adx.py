import pytest
import pandas as pd
from algo.domain.indicators.adx import indicator_adx

def test_indicator_adx_with_dataframe():
    df = pd.DataFrame([
        {"high": 10, "low": 5, "close": 7},
        {"high": 12, "low": 6, "close": 9},
        {"high": 14, "low": 7, "close": 11},
        {"high": 16, "low": 8, "close": 13},
        {"high": 18, "low": 9, "close": 15},
        {"high": 20, "low": 10, "close": 17},
        {"high": 22, "low": 11, "close": 19},
        {"high": 24, "low": 12, "close": 21},
        {"high": 26, "low": 13, "close": 23},
        {"high": 28, "low": 14, "close": 25},
        {"high": 30, "low": 15, "close": 27},
        {"high": 32, "low": 16, "close": 29},
        {"high": 34, "low": 17, "close": 31},
        {"high": 36, "low": 18, "close": 33},
        {"high": 38, "low": 19, "close": 35},
    ])
    params = {"period": 14}
    result = indicator_adx(df, params)
    assert isinstance(result, float)

def test_indicator_adx_with_list_of_dicts():
    data = [
        {"high": 10, "low": 5, "close": 7},
        {"high": 12, "low": 6, "close": 9},
        {"high": 14, "low": 7, "close": 11},
        {"high": 16, "low": 8, "close": 13},
        {"high": 18, "low": 9, "close": 15},
        {"high": 20, "low": 10, "close": 17},
        {"high": 22, "low": 11, "close": 19},
        {"high": 24, "low": 12, "close": 21},
        {"high": 26, "low": 13, "close": 23},
        {"high": 28, "low": 14, "close": 25},
        {"high": 30, "low": 15, "close": 27},
        {"high": 32, "low": 16, "close": 29},
        {"high": 34, "low": 17, "close": 31},
        {"high": 36, "low": 18, "close": 33},
        {"high": 38, "low": 19, "close": 35},
    ]
    params = {"period": 14}
    result = indicator_adx(data, params)
    assert isinstance(result, float)

def test_indicator_adx_with_no_historical_data():
    df = pd.DataFrame([])
    params = {"period": 14}
    with pytest.raises(RuntimeError, match="historical_data is empty in adx indicator"):
        indicator_adx(df, params)

def test_indicator_adx_with_default_params():
    df = pd.DataFrame([
        {"high": 10, "low": 5, "close": 7},
        {"high": 12, "low": 6, "close": 9},
        {"high": 14, "low": 7, "close": 11},
        {"high": 16, "low": 8, "close": 13},
        {"high": 18, "low": 9, "close": 15},
        {"high": 20, "low": 10, "close": 17},
        {"high": 22, "low": 11, "close": 19},
        {"high": 24, "low": 12, "close": 21},
        {"high": 26, "low": 13, "close": 23},
        {"high": 28, "low": 14, "close": 25},
        {"high": 30, "low": 15, "close": 27},
        {"high": 32, "low": 16, "close": 29},
        {"high": 34, "low": 17, "close": 31},
        {"high": 36, "low": 18, "close": 33},
        {"high": 38, "low": 19, "close": 35},
    ])
    # No params provided, should use defaults
    result = indicator_adx(df, {})
    assert isinstance(result, float)
