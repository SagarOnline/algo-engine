import pytest
from flask import Flask
from api.app import app as flask_app
import json

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_backtest_success(client, mocker):
    # Mock the use case to return a fake report
    mock_report = {'result': 'success', 'details': {}}
    mocker.patch('api.use_cases.run_backtest.RunBacktestUseCase.execute', return_value=mock_report)
    payload = {
        'strategy': {'type': 'dummy'},
        'start_date': '2024-01-01',
        'end_date': '2024-01-02'
    }
    response = client.post('/backtest', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    assert response.get_json() == mock_report

def test_backtest_invalid_input(client):
    response = client.post('/backtest', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_backtest_internal_error(client, mocker):
    mocker.patch('api.use_cases.run_backtest.RunBacktestUseCase.execute', side_effect=Exception('fail'))
    payload = {
        'strategy': {'type': 'dummy'},
        'start_date': '2024-01-01',
        'end_date': '2024-01-02'
    }
    response = client.post('/backtest', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 500
    assert 'error' in response.get_json()
