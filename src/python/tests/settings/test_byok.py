import pytest

from template_github_copilot.settings.byok import (
    ByokSettings,
    get_byok_settings,
)


def test_byok_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """ByokSettings should have sensible defaults."""
    monkeypatch.delenv("BYOK_PROVIDER_TYPE", raising=False)
    monkeypatch.delenv("BYOK_BASE_URL", raising=False)
    monkeypatch.delenv("BYOK_API_KEY", raising=False)
    monkeypatch.delenv("BYOK_MODEL", raising=False)
    monkeypatch.delenv("BYOK_WIRE_API", raising=False)
    settings = ByokSettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.byok_provider_type == "openai"
    assert settings.byok_model == "gpt-5"
    assert settings.byok_wire_api == "responses"


def test_byok_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """ByokSettings should pick up values from environment variables."""
    monkeypatch.setenv("BYOK_PROVIDER_TYPE", "azure")
    monkeypatch.setenv(
        "BYOK_BASE_URL", "https://my-resource.openai.azure.com/openai/v1/"
    )
    monkeypatch.setenv("BYOK_API_KEY", "test-key-123")
    monkeypatch.setenv("BYOK_MODEL", "gpt-5")
    monkeypatch.setenv("BYOK_WIRE_API", "completions")
    settings = ByokSettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.byok_provider_type == "azure"
    assert settings.byok_base_url == "https://my-resource.openai.azure.com/openai/v1/"
    assert settings.byok_api_key == "test-key-123"
    assert settings.byok_model == "gpt-5"
    assert settings.byok_wire_api == "completions"


def test_get_byok_settings_cached():
    """get_byok_settings should return the same cached instance."""
    get_byok_settings.cache_clear()
    s1 = get_byok_settings()
    s2 = get_byok_settings()
    assert s1 is s2
