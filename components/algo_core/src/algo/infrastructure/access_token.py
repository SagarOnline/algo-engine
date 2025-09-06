import os

class AccessToken:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AccessToken, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.access_token = os.environ.get('BACKTEST_ENGINE.BROKER_API_ACCESS_TOKEN', None)
        self._initialized = True

    def set_token(self, token):
        self.access_token = token

    def get_token(self):
        return self.access_token
