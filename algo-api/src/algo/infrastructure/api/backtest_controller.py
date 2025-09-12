from algo.application.run_backtest_usecase import RunBacktestUseCase
from algo.config_context import get_config
from algo.domain.config import HistoricalDataBackend
from algo.infrastructure.json_strategy_repository import JsonStrategyRepository
from algo.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from flask import Blueprint, request, jsonify

from algo.application.run_backtest_usecase import RunBacktestInput


backtest_bp = Blueprint('backtest', __name__)

def get_historical_data_repository():
    config = get_config()
    if config.backtest_engine.historical_data_backend == HistoricalDataBackend.UPSTOX_API:
        historical_data_repository = UpstoxHistoricalDataRepository()
    else:
         historical_data_repository = ParquetHistoricalDataRepository(config.backtest_engine.parquet_files_base_dir)
    return historical_data_repository

def get_strategy_repository():
    return JsonStrategyRepository()

@backtest_bp.route('/api/backtest', methods=['POST'])
def run_backtest():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400

        use_case = RunBacktestUseCase(
            get_historical_data_repository(),
            get_strategy_repository()
        )
        input_data = RunBacktestInput(
            strategy_name=data.get("strategy_name"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date")
        )
        report = use_case.execute(input_data)
        print(report)
        return jsonify(report), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
