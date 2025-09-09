from flask import Blueprint, jsonify
from algo.application.strategy_usecases import StrategyUseCase
from algo.infrastructure.json_strategy_repository import JsonStrategyRepository

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/api/strategies', methods=['GET'])
def list_strategies():
    try:
        use_case = StrategyUseCase(JsonStrategyRepository())
        dtos = use_case.list_strategies()
        result = [dto.to_dict() for dto in dtos]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
