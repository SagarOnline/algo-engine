from algo_core.application.run_backtest_usecase import RunBacktestUseCase
from algo_core.config_context import get_config
from algo_core.domain.config import HistoricalDataBackend
from algo_core.infrastructure.json_strategy_repository import JsonStrategyRepository
from algo_core.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo_core.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from flask import Blueprint, request, jsonify


backtest_bp = Blueprint('backtest', __name__)

def get_historical_data_repository():
    config = get_config()
    if config.backtest_engine.historical_data_backend == HistoricalDataBackend.UPSTOX_API:
        historical_data_repository = UpstoxHistoricalDataRepository()
    else:
         historical_data_repository = ParquetHistoricalDataRepository()
    return historical_data_repository

def get_strategy_repository():
    return JsonStrategyRepository()

@backtest_bp.route('/backtest', methods=['POST'])
def run_backtest():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400

        use_case = RunBacktestUseCase(
            get_historical_data_repository(),
            get_strategy_repository()
        )
        report = use_case.execute(data)
        return jsonify(report), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
