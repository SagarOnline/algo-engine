from flask import Flask
from flask_cors import CORS
from algo.infrastructure.api.backtest_controller import backtest_bp
from algo.infrastructure.api.strategy_controller import strategy_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(backtest_bp)
app.register_blueprint(strategy_bp)

@app.route('/')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)
