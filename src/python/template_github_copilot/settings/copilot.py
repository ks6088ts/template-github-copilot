from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CopilotSettings(BaseSettings):
    """Settings for the GitHub Copilot SDK integration."""

    copilot_send_timeout: float = 300.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_copilot_settings() -> CopilotSettings:
    return CopilotSettings()
