from flask import Flask, request, g
from flask_cors import CORS
from algo.infrastructure.api.backtest_controller import backtest_bp
from algo.infrastructure.api.strategy_controller import strategy_bp
from algo.infrastructure.service_configuration import register_all_services
from algo.config_context import get_config
import logging
import time
import uuid


app = Flask(__name__)
CORS(app)

# Register all services on application startup
register_all_services()

app.register_blueprint(backtest_bp)
app.register_blueprint(strategy_bp)


# Flask middleware to log incoming requests (structured)
logger = logging.getLogger("algo.api")


@app.before_request
def _start_timer_and_request_id():
    g._start_time = time.time()
    # Generate a request ID for tracing
    g.request_id = str(uuid.uuid4())


@app.after_request
def _log_request(response):
    try:
        duration = None
        if hasattr(g, "_start_time"):
            duration = time.time() - g._start_time

        # Try to extract user/session info if available (customize as needed)
        user_id = None
        session_id = None
        # Example: from headers or cookies
        if "X-User-Id" in request.headers:
            user_id = request.headers.get("X-User-Id")
        if "session_id" in request.cookies:
            session_id = request.cookies.get("session_id")

        log_data = {
            "request_id": getattr(g, "request_id", None),
            "method": request.method,
            "path": request.path,
            "endpoint": request.endpoint,
            "status_code": response.status_code,
            "duration_ms": int((duration or 0) * 1000),
            "user_id": user_id,
            "session_id": session_id,
        }

        logger.info("request_complete", extra={"extra": log_data})
    except Exception:
        logger.exception("failed_to_log_request")
    return response


@app.route('/')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # ensure config is loaded which will configure logging
    try:
        get_config()
    except Exception:
        pass
    app.run(debug=True)
