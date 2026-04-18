import pytest

from template_github_copilot.settings.azure_blob_storage import (
    AzureBlobStorageSettings,
    get_azure_blob_storage_settings,
)


def test_azure_blob_storage_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """AzureBlobStorageSettings should have empty-string defaults."""
    monkeypatch.delenv("AZURE_BLOB_STORAGE_ACCOUNT_URL", raising=False)
    monkeypatch.delenv("AZURE_BLOB_STORAGE_CONTAINER_NAME", raising=False)
    settings = AzureBlobStorageSettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert settings.azure_blob_storage_account_url == ""
    assert settings.azure_blob_storage_container_name == ""


def test_azure_blob_storage_settings_from_env(monkeypatch: pytest.MonkeyPatch):
    """AzureBlobStorageSettings should pick up values from env vars."""
    monkeypatch.setenv(
        "AZURE_BLOB_STORAGE_ACCOUNT_URL", "https://myaccount.blob.core.windows.net"
    )
    monkeypatch.setenv("AZURE_BLOB_STORAGE_CONTAINER_NAME", "my-container")
    settings = AzureBlobStorageSettings(_env_file=None)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]
    assert (
        settings.azure_blob_storage_account_url
        == "https://myaccount.blob.core.windows.net"
    )
    assert settings.azure_blob_storage_container_name == "my-container"


def test_get_azure_blob_storage_settings_cached():
    """get_azure_blob_storage_settings should return the same cached instance."""
    get_azure_blob_storage_settings.cache_clear()
    s1 = get_azure_blob_storage_settings()
    s2 = get_azure_blob_storage_settings()
    assert s1 is s2
