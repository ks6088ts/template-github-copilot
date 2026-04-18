"""Unified LLM provider factory.

This module consolidates provider construction logic so that scripts only need
to specify *which* authentication method to use, rather than building
``ProviderConfig`` objects by hand.

Supported authentication methods
--------------------------------
* **github_copilot** – Default GitHub Copilot backend (no ``ProviderConfig`` needed).
* **api_key** – Static API key read from ``ByokSettings``.
* **foundry_entra_id** – Microsoft Foundry OpenAI API authenticated via
  Azure Entra ID (``DefaultAzureCredential``).

Usage
-----
::

    from template_github_copilot.providers import AuthMethod, create_provider

    result = create_provider(AuthMethod.API_KEY)
    session_config = create_session_config(
        model=result.model,
        provider=result.provider,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from collections.abc import Callable
from typing import TYPE_CHECKING

from copilot.session import ProviderConfig

if TYPE_CHECKING:
    from template_github_copilot.settings.byok import ByokSettings

COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


class AuthMethod(StrEnum):
    """Supported LLM provider authentication methods."""

    GITHUB_COPILOT = "github_copilot"
    API_KEY = "api_key"
    FOUNDRY_ENTRA_ID = "foundry_entra_id"


@dataclass(frozen=True)
class ProviderResult:
    """Return value of :func:`create_provider`.

    Attributes:
        provider: A ``ProviderConfig`` for BYOK modes, or ``None`` when using
            the default Copilot backend.
        model: The model identifier to use (e.g. ``"gpt-5"``), or ``None``
            when relying on the Copilot default.
    """

    provider: ProviderConfig | None = None
    model: str | None = None


def _build_api_key_provider(
    byok_settings: "ByokSettings | None" = None,
) -> ProviderResult:
    """Build a :class:`ProviderResult` using a static API key."""
    if byok_settings is None:
        from template_github_copilot.settings import get_byok_settings

        byok_settings = get_byok_settings()
    settings = byok_settings
    provider = ProviderConfig(
        type=settings.byok_provider_type,
        base_url=settings.byok_base_url,
        api_key=settings.byok_api_key,
    )
    if settings.byok_wire_api:
        provider["wire_api"] = settings.byok_wire_api
    return ProviderResult(provider=provider, model=settings.byok_model)


def _build_entra_id_provider(
    byok_settings: "ByokSettings | None" = None,
) -> ProviderResult:
    """Build a :class:`ProviderResult` using a Microsoft Foundry Entra ID bearer token."""
    from azure.identity import DefaultAzureCredential

    if byok_settings is None:
        from template_github_copilot.settings import get_byok_settings

        byok_settings = get_byok_settings()
    settings = byok_settings
    credential = DefaultAzureCredential()
    token = credential.get_token(COGNITIVE_SERVICES_SCOPE).token
    provider = ProviderConfig(
        type=settings.byok_provider_type,
        base_url=settings.byok_base_url,
        bearer_token=token,
    )
    if settings.byok_wire_api:
        provider["wire_api"] = settings.byok_wire_api
    return ProviderResult(provider=provider, model=settings.byok_model)


# ---------------------------------------------------------------------------
# Factory registry – maps AuthMethod → builder callable
# ---------------------------------------------------------------------------

_PROVIDER_BUILDERS: dict[AuthMethod, Callable[..., ProviderResult]] = {
    AuthMethod.API_KEY: _build_api_key_provider,
    AuthMethod.FOUNDRY_ENTRA_ID: _build_entra_id_provider,
}


def create_provider(
    auth_method: AuthMethod = AuthMethod.GITHUB_COPILOT,
    byok_settings: "ByokSettings | None" = None,
) -> ProviderResult:
    """Create an LLM provider configuration for the given authentication method.

    Args:
        auth_method: The authentication strategy to use.
        byok_settings: Optional :class:`ByokSettings` to use instead of
            reading from the environment.  Ignored when *auth_method* is
            ``COPILOT``.

    Returns:
        A :class:`ProviderResult` containing the ``ProviderConfig`` (if any)
        and the target model name.

    Raises:
        ValueError: If *auth_method* is not a recognised :class:`AuthMethod`.
    """
    if auth_method == AuthMethod.GITHUB_COPILOT:
        return ProviderResult()

    builder = _PROVIDER_BUILDERS.get(auth_method)
    if builder is None:
        raise ValueError(
            f"Unknown auth method: {auth_method!r}. "
            f"Supported methods: {', '.join(m.value for m in AuthMethod)}"
        )
    try:
        return builder(byok_settings=byok_settings)
    except TypeError:
        # Custom-registered builders may not accept byok_settings
        return builder()


def register_provider(
    auth_method: AuthMethod,
    builder: Callable[..., ProviderResult],
) -> None:
    """Register (or override) a provider builder for a given auth method.

    This can be used by downstream code or plugins to extend the set of
    supported providers without modifying this module.

    Args:
        auth_method: The authentication method key.
        builder: A zero-argument callable that returns a :class:`ProviderResult`.
    """
    _PROVIDER_BUILDERS[auth_method] = builder
