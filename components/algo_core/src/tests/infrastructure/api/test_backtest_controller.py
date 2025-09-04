import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from algo_core.infrastructure.api.backtest_controller import backtest_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(backtest_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_run_backtest_success(client):
    mock_report = {'result': 'success'}
    with patch('algo_core.infrastructure.api.backtest_controller.RunBacktestUseCase') as MockUseCase:
        instance = MockUseCase.return_value
        instance.execute.return_value = mock_report
        payload = {
            'strategy_name': 'test_strategy',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
        response = client.post('/api/backtest', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.get_json() == mock_report

def test_run_backtest_invalid_json(client):
    response = client.post('/api/backtest', data='not a json', content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_run_backtest_value_error(client):
    with patch('algo_core.infrastructure.api.backtest_controller.RunBacktestUseCase') as MockUseCase:
        instance = MockUseCase.return_value
        instance.execute.side_effect = ValueError('Invalid input')
        payload = {
            'strategy_name': 'test_strategy',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
        response = client.post('/api/backtest', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Invalid input'

def test_run_backtest_internal_error(client):
    with patch('algo_core.infrastructure.api.backtest_controller.RunBacktestUseCase') as MockUseCase:
        instance = MockUseCase.return_value
        instance.execute.side_effect = Exception('Something went wrong')
        payload = {
            'strategy_name': 'test_strategy',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
        response = client.post('/api/backtest', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
        assert 'details' in data

def test_run_backtest_rejects_non_json_content_type(client):
    payload = 'strategy_name=test_strategy&start_date=2023-01-01&end_date=2023-01-31'
    response = client.post('/api/backtest', data=payload, content_type='application/x-www-form-urlencoded')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
