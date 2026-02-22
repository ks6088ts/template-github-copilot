from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureBlobStorageSettings(BaseSettings):
    azure_blob_storage_account_url: str = (
        "https://stazuredatastore.blob.core.windows.net"
    )
    azure_blob_storage_container_name: str = "test"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_azure_blob_storage_settings() -> AzureBlobStorageSettings:
    return AzureBlobStorageSettings()
