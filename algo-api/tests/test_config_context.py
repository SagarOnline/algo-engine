# import os
# import threading
# import tempfile
# import json
# import pytest
# from algo.config_context import  get_config, load_config, _config, _config_lock
# from algo.domain.config import Config


# def setup_module(module):
#     # Reset the singleton before each test module
#     global _config
#     with _config_lock:
#         _config = None

# def teardown_module(module):
#     # Reset the singleton after each test module
#     global _config
#     with _config_lock:
#         _config = None

# def test_get_config_loads_once(monkeypatch):
#     # Create a temporary config file
#     config_dict = {
#         "backtest_engine": {
#             "strategies_path": "strategies",
#             "reports_path": "report"
#         }
#     }
#     with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
#         json.dump(config_dict, tmp)
#         tmp_path = tmp.name

#     monkeypatch.setenv("CONFIG_JSON_PATH", tmp_path)
#     # Reset singleton
#     global _config
#     with _config_lock:
#         _config = None
#     config1 = get_config()
#     config2 = get_config()
#     assert config1 is config2  # Singleton
#     assert config1.backtest_engine.strategies_path == "strategies"
#     assert config1.backtest_engine.reports_path == "report"
#     os.remove(tmp_path)

# def test_get_config_thread_safety(monkeypatch):
#     # Test that get_config is thread-safe and only loads once
#     config_dict = {
#         "backtest_engine": {
#             "strategies_path": "s",
#             "reports_path": "r"
#         }
#     }
#     with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
#         json.dump(config_dict, tmp)
#         tmp_path = tmp.name
#     monkeypatch.setenv("CONFIG_JSON_PATH", tmp_path)
#     global _config
#     with _config_lock:
#         _config = None
#     results = []
#     def worker():
#         results.append(get_config())
#     threads = [threading.Thread(target=worker) for _ in range(5)]
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()
#     assert all(r is results[0] for r in results)
#     os.remove(tmp_path)
