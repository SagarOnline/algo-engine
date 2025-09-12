import pytest
from flask import Flask
from algo.infrastructure.api.strategy_controller import strategy_bp

class DummyUseCase:
    def list_strategies(self):
        class DummyDTO:
            def to_dict(self):
                return {"name": "strat1", "display_name": "Strategy One", "description": "desc", "instrument": {}}
        return [DummyDTO()]

    def get_strategy(self, name):
        class DummyDTO:
            def to_dict(self):
                return {"name": name, "display_name": "Test Strategy", "description": "Simple Test Strategy", "instrument": {}}
        return DummyDTO()

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(strategy_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_strategies_success(monkeypatch, client):
    monkeypatch.setattr("algo.infrastructure.api.strategy_controller.StrategyUseCase", lambda repo: DummyUseCase())
    response = client.get("/api/strategy")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["name"] == "strat1"
    assert data[0]["display_name"] == "Strategy One"

def test_list_strategies_error(monkeypatch, client):
    class ErrorUseCase:
        def list_strategies(self):
            raise Exception("fail")
    monkeypatch.setattr("algo.infrastructure.api.strategy_controller.StrategyUseCase", lambda repo: ErrorUseCase())
    response = client.get("/api/strategy")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data

def test_get_strategy_details_success(client, monkeypatch):
    # Patch StrategyUseCase.get_strategy to return a dummy DTO
    monkeypatch.setattr("algo.infrastructure.api.strategy_controller.StrategyUseCase", lambda repo: DummyUseCase())
    response = client.get('/api/strategy/test_strategy')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'test_strategy'
    assert data['display_name'] == 'Test Strategy'

def test_get_strategy_details_not_found(client, monkeypatch):
    # Patch StrategyUseCase.get_strategy to raise StrategyNotFound
    class StrategyNotFound(Exception): pass
    class NotFoundUseCase(DummyUseCase):
        def get_strategy(self, name):
            raise StrategyNotFound()
    monkeypatch.setattr("algo.infrastructure.api.strategy_controller.StrategyUseCase", lambda repo: NotFoundUseCase())
    response = client.get('/api/strategy/missing_strategy')
    assert response.status_code == 404
    data = response.get_json()
    assert "not found" in data['error'].lower()

def test_get_strategy_details_internal_error(client, monkeypatch):
    # Patch StrategyUseCase.get_strategy to raise generic Exception
    class SomeExceptionUseCase(DummyUseCase):
        def get_strategy(self, name):
            raise Exception("Internal Error")
    monkeypatch.setattr("algo.infrastructure.api.strategy_controller.StrategyUseCase", lambda repo: SomeExceptionUseCase())
    response = client.get('/api/strategy/error_strategy')
    assert response.status_code == 500
    data = response.get_json()
    assert "internal server error" in data['error'].lower()
