"""Tests for template_github_copilot.providers module."""

from unittest.mock import MagicMock, patch

import pytest

from template_github_copilot.providers import (
    AuthMethod,
    ProviderResult,
    _PROVIDER_BUILDERS,
    create_provider,
    register_provider,
)


# ---------------------------------------------------------------------------
# AuthMethod enum
# ---------------------------------------------------------------------------


def test_auth_method_values():
    """AuthMethod should expose the expected string values."""
    assert AuthMethod.COPILOT == "copilot"
    assert AuthMethod.API_KEY == "api_key"
    assert AuthMethod.ENTRA_ID == "entra_id"


# ---------------------------------------------------------------------------
# ProviderResult dataclass
# ---------------------------------------------------------------------------


def test_provider_result_defaults():
    """ProviderResult with no arguments should have None fields."""
    result = ProviderResult()
    assert result.provider is None
    assert result.model is None


def test_provider_result_frozen():
    """ProviderResult should be immutable."""
    result = ProviderResult()
    with pytest.raises(AttributeError):
        result.model = "gpt-5"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# create_provider – COPILOT (no provider)
# ---------------------------------------------------------------------------


def test_create_provider_copilot():
    """COPILOT auth should return empty ProviderResult."""
    result = create_provider(AuthMethod.COPILOT)
    assert result.provider is None
    assert result.model is None


def test_create_provider_default_is_copilot():
    """Default auth method should be COPILOT."""
    result = create_provider()
    assert result.provider is None
    assert result.model is None


# ---------------------------------------------------------------------------
# create_provider – API_KEY
# ---------------------------------------------------------------------------


def test_create_provider_api_key(monkeypatch: pytest.MonkeyPatch):
    """API_KEY auth should build a ProviderConfig with api_key."""
    monkeypatch.setenv("BYOK_PROVIDER_TYPE", "openai")
    monkeypatch.setenv("BYOK_BASE_URL", "https://example.com/v1/")
    monkeypatch.setenv("BYOK_API_KEY", "sk-test-key")
    monkeypatch.setenv("BYOK_MODEL", "gpt-5")
    monkeypatch.setenv("BYOK_WIRE_API", "responses")

    # Clear cached settings so monkeypatched env vars are picked up
    from template_github_copilot.settings.byok import get_byok_settings

    get_byok_settings.cache_clear()

    result = create_provider(AuthMethod.API_KEY)
    assert result.model == "gpt-5"
    assert result.provider is not None
    assert result.provider["type"] == "openai"
    assert result.provider["base_url"] == "https://example.com/v1/"
    assert result.provider["api_key"] == "sk-test-key"
    assert result.provider.get("wire_api") == "responses"


# ---------------------------------------------------------------------------
# create_provider – ENTRA_ID
# ---------------------------------------------------------------------------


def test_create_provider_entra_id(monkeypatch: pytest.MonkeyPatch):
    """ENTRA_ID auth should build a ProviderConfig with bearer_token."""
    monkeypatch.setenv("BYOK_PROVIDER_TYPE", "azure")
    monkeypatch.setenv("BYOK_BASE_URL", "https://azure.example.com/")
    monkeypatch.setenv("BYOK_API_KEY", "unused")
    monkeypatch.setenv("BYOK_MODEL", "gpt-5")
    monkeypatch.setenv("BYOK_WIRE_API", "completions")

    from template_github_copilot.settings.byok import get_byok_settings

    get_byok_settings.cache_clear()

    mock_credential = MagicMock()
    mock_credential.get_token.return_value = MagicMock(token="fake-bearer-token")

    with patch(
        "azure.identity.DefaultAzureCredential",
        return_value=mock_credential,
    ):
        result = create_provider(AuthMethod.ENTRA_ID)

    assert result.model == "gpt-5"
    assert result.provider is not None
    assert result.provider["type"] == "azure"
    assert result.provider["bearer_token"] == "fake-bearer-token"
    assert result.provider.get("wire_api") == "completions"


# ---------------------------------------------------------------------------
# create_provider – unknown auth method
# ---------------------------------------------------------------------------


def test_create_provider_unknown_raises():
    """An unknown auth method should raise ValueError."""
    with pytest.raises(ValueError, match="Unknown auth method"):
        create_provider("nonexistent")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# register_provider
# ---------------------------------------------------------------------------


def test_register_provider_custom():
    """register_provider should allow adding a custom builder."""
    custom_result = ProviderResult(model="custom-model")
    register_provider(AuthMethod.API_KEY, lambda: custom_result)

    try:
        result = create_provider(AuthMethod.API_KEY)
        assert result.model == "custom-model"
        assert result.provider is None
    finally:
        # Restore original builder
        from template_github_copilot.providers import _build_api_key_provider

        _PROVIDER_BUILDERS[AuthMethod.API_KEY] = _build_api_key_provider
