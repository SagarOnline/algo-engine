from flask import Blueprint, jsonify
from algo.application.strategy_usecases import StrategyUseCase
from algo.infrastructure.json_strategy_repository import JsonStrategyRepository

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/api/strategy', methods=['GET'])
def list_strategies():
    try:
        use_case = StrategyUseCase(JsonStrategyRepository())
        dtos = use_case.list_strategies()
        result = [dto.to_dict() for dto in dtos]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@strategy_bp.route('/api/strategy/<string:name>', methods=['GET'])
def get_strategy_details(name):
    try:
        use_case = StrategyUseCase(JsonStrategyRepository())
        details = use_case.get_strategy(name)
        return jsonify(details.to_dict()), 200
    except Exception as e:
        if hasattr(e, '__class__') and e.__class__.__name__ == 'StrategyNotFound':
            return jsonify({'error': f"Strategy '{name}' not found."}), 404
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
