from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class MicrosoftFoundrySettings(BaseSettings):
    microsoft_foundry_project_endpoint: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_microsoft_foundry_settings() -> MicrosoftFoundrySettings:
    return MicrosoftFoundrySettings()
