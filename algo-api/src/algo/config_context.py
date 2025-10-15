import threading
import json
from algo.domain.config import Config
import os

_config = None
_config_lock = threading.Lock()


def load_config(config_path):
    """
    Loads the config from a JSON file and returns a Config object.
    """
    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    else:
        config_data = {}
    return Config.from_dict(config_data)

def get_config():
    global _config
    if _config is None:
        with _config_lock:
            if _config is None:
                load_config_path = os.getenv("CONFIG_JSON_PATH", "config/config.json")
                _config = load_config(load_config_path)
    return _config
