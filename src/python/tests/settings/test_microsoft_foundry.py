import pytest

from template_github_copilot.settings.microsoft_foundry import (
    MicrosoftFoundrySettings,
    get_microsoft_foundry_settings,
)


def test_microsoft_foundry_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """MicrosoftFoundrySettings should have empty-string default."""
    monkeypatch.delenv("MICROSOFT_FOUNDRY_PROJECT_ENDPOINT", raising=False)
    settings = MicrosoftFoundrySettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.microsoft_foundry_project_endpoint == ""


def test_microsoft_foundry_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """MicrosoftFoundrySettings should pick up value from env var."""
    monkeypatch.setenv(
        "MICROSOFT_FOUNDRY_PROJECT_ENDPOINT", "https://foundry.example.com"
    )
    settings = MicrosoftFoundrySettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.microsoft_foundry_project_endpoint == "https://foundry.example.com"


def test_get_microsoft_foundry_settings_cached():
    """get_microsoft_foundry_settings should return the same cached instance."""
    get_microsoft_foundry_settings.cache_clear()
    s1 = get_microsoft_foundry_settings()
    s2 = get_microsoft_foundry_settings()
    assert s1 is s2
