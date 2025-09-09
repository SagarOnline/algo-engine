import pytest
from flask import Flask
from algo.infrastructure.api.strategy_controller import strategy_bp

class DummyUseCase:
    def list_strategies(self):
        class DummyDTO:
            def to_dict(self):
                return {"name": "strat1", "display_name": "Strategy One", "description": "desc", "instrument": {}}
        return [DummyDTO()]

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
    response = client.get("/api/strategies")
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
    response = client.get("/api/strategies")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
