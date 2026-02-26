from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseSettings):
    """Settings for the OAuth GitHub App integration and API server."""

    # GitHub OAuth App credentials
    # Create at: https://github.com/settings/applications/new
    github_client_id: str = ""
    github_client_secret: str = ""

    # Server configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # Copilot CLI server URL (the SDK communicates via this)
    copilot_cli_url: str = "localhost:3000"

    # Session secret for cookie signing
    session_secret: str = "change-me-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_oauth_settings() -> OAuthSettings:
    return OAuthSettings()
