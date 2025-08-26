# test_access_token.py
import os
import pytest
from algo_core.infrastructure.access_token import AccessToken


def test_singleton_instance():
    """AccessToken should always return the same instance."""
    token1 = AccessToken()
    token2 = AccessToken()
    assert token1 is token2


def test_env_variable(monkeypatch):
    """AccessToken should read token from environment variable on first initialization."""
    monkeypatch.setenv("BACKTEST_ENGINE.BROKER_API_ACCESS_TOKEN", "env_token")

    # Reset singleton before test
    AccessToken._instance = None

    token = AccessToken()
    assert token.get_token() == "env_token"


def test_set_and_get_token():
    """AccessToken should allow setting and getting token."""
    # Reset singleton before test
    AccessToken._instance = None

    token = AccessToken()
    token.set_token("custom_token")

    assert token.get_token() == "custom_token"


def test_multiple_calls_share_token():
    """All references should share the same token."""
    # Reset singleton before test
    AccessToken._instance = None

    token1 = AccessToken()
    token2 = AccessToken()

    token1.set_token("shared_token")
    assert token2.get_token() == "shared_token"


def test_no_env_var(monkeypatch):
    """If no env variable is set, token should be None."""
    monkeypatch.delenv("BACKTEST_ENGINE.BROKER_API_ACCESS_TOKEN", raising=False)

    # Reset singleton before test
    AccessToken._instance = None

    token = AccessToken()
    assert token.get_token() is None
