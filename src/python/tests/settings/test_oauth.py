import pytest

from template_github_copilot.settings.oauth import (
    OAuthSettings,
    get_oauth_settings,
)


def test_oauth_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """OAuthSettings should have sensible defaults."""
    monkeypatch.delenv("GITHUB_CLIENT_ID", raising=False)
    monkeypatch.delenv("GITHUB_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("API_HOST", raising=False)
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.delenv("COPILOT_CLI_URL", raising=False)
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    settings = OAuthSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.github_client_id == ""
    assert settings.github_client_secret == ""
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.copilot_cli_url == "localhost:3000"
    assert settings.session_secret == "change-me-in-production"


def test_oauth_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """OAuthSettings should pick up values from environment variables."""
    monkeypatch.setenv("GITHUB_CLIENT_ID", "Ov23liXXXXX")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "secret123")
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("API_PORT", "9999")
    monkeypatch.setenv("COPILOT_CLI_URL", "localhost:4000")
    monkeypatch.setenv("SESSION_SECRET", "my-session-secret")
    settings = OAuthSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.github_client_id == "Ov23liXXXXX"
    assert settings.github_client_secret == "secret123"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 9999
    assert settings.copilot_cli_url == "localhost:4000"
    assert settings.session_secret == "my-session-secret"


def test_get_oauth_settings_cached():
    """get_oauth_settings should return the same cached instance."""
    get_oauth_settings.cache_clear()
    s1 = get_oauth_settings()
    s2 = get_oauth_settings()
    assert s1 is s2
