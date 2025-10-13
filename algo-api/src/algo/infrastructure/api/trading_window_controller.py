"""
Example trading window controller showing service registry usage.
"""
from flask import Blueprint, jsonify, request
from datetime import date, datetime

from algo.infrastructure.services import get_trading_window_service

# Create blueprint for trading window endpoints
trading_window_bp = Blueprint('trading_window', __name__, url_prefix='/api/trading-window')


@trading_window_bp.route('/status', methods=['GET'])
def get_trading_window_status():
    """Get trading window service status."""
    try:
        service = get_trading_window_service()
        cache_stats = service.get_cache_stats()
        
        return jsonify({
            "status": "active",
            "cache_stats": cache_stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@trading_window_bp.route('/window/<exchange>/<segment>', methods=['GET'])
def get_trading_window(exchange: str, segment: str):
    """
    Get trading window for a specific date, exchange, and segment.
    
    Query parameters:
        date: Date in YYYY-MM-DD format (optional, defaults to today)
    """
    try:
        service = get_trading_window_service()
        
        # Parse date parameter
        date_str = request.args.get('date')
        if date_str:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            query_date = date.today()
        
        # Get trading window
        window = service.get_trading_window(query_date, exchange.upper(), segment.upper())
        
        if window is None:
            return jsonify({
                "error": f"No trading window found for {exchange}-{segment} on {query_date}"
            }), 404
        
        return jsonify(window.to_dict())
        
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_window_bp.route('/holidays/<exchange>/<segment>/<int:year>', methods=['GET'])
def get_holidays(exchange: str, segment: str, year: int):
    """Get all holidays for a specific exchange, segment, and year."""
    try:
        service = get_trading_window_service()
        holidays = service.get_holidays(year, exchange.upper(), segment.upper())
        
        return jsonify({
            "exchange": exchange.upper(),
            "segment": segment.upper(),
            "year": year,
            "holidays": [holiday.to_dict() for holiday in holidays]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_window_bp.route('/special-days/<exchange>/<segment>/<int:year>', methods=['GET'])
def get_special_trading_days(exchange: str, segment: str, year: int):
    """Get all special trading days for a specific exchange, segment, and year."""
    try:
        service = get_trading_window_service()
        special_days = service.get_special_trading_days(year, exchange.upper(), segment.upper())
        
        return jsonify({
            "exchange": exchange.upper(),
            "segment": segment.upper(),
            "year": year,
            "special_days": [day.to_dict() for day in special_days]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_window_bp.route('/exchanges-segments', methods=['GET'])
def get_available_exchanges_segments():
    """Get all available exchange-segment combinations."""
    try:
        service = get_trading_window_service()
        exchanges_segments = service.get_available_exchanges_segments()
        
        return jsonify({
            "exchanges_segments": [
                {"exchange": exchange, "segment": segment}
                for exchange, segment in exchanges_segments
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
