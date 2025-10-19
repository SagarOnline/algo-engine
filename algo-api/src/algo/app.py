from flask import Flask
from flask_cors import CORS
from algo.infrastructure.api.backtest_controller import backtest_bp
from algo.infrastructure.api.strategy_controller import strategy_bp
from algo.infrastructure.service_configuration import register_all_services

app = Flask(__name__)
CORS(app)

# Register all services on application startup
register_all_services()

app.register_blueprint(backtest_bp)
app.register_blueprint(strategy_bp)

@app.route('/')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)
