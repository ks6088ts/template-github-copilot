from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ByokSettings(BaseSettings):
    byok_provider_type: Literal["openai", "azure", "anthropic"] = "openai"
    byok_base_url: str = "https://<your-resource>.openai.azure.com/openai/v1/"
    byok_api_key: str = "<your-api-key>"
    byok_model: str = "gpt-5"
    byok_wire_api: Literal["completions", "responses"] = "responses"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_byok_settings() -> ByokSettings:
    return ByokSettings()
