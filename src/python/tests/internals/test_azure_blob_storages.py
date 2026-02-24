"""Tests for template_github_copilot.internals.azure_blob_storages."""

from unittest.mock import MagicMock, patch

from template_github_copilot.internals.azure_blob_storages import AzureBlobStorageClient


@patch("template_github_copilot.internals.azure_blob_storages.DefaultAzureCredential")
@patch("template_github_copilot.internals.azure_blob_storages.BlobServiceClient")
class TestAzureBlobStorageClient:
    """Tests for AzureBlobStorageClient methods."""

    def _make_client(self, mock_blob_svc_cls, mock_cred_cls):
        mock_cred = MagicMock()
        mock_cred_cls.return_value = mock_cred
        mock_blob_svc = MagicMock()
        mock_blob_svc_cls.return_value = mock_blob_svc
        mock_container_client = MagicMock()
        mock_blob_svc.get_container_client.return_value = mock_container_client

        client = AzureBlobStorageClient(
            account_url="https://myaccount.blob.core.windows.net",
            container_name="test-container",
        )
        return client, mock_blob_svc, mock_container_client

    # -----------------------------------------------------------------------
    # __init__
    # -----------------------------------------------------------------------

    def test_init(self, mock_blob_svc_cls, mock_cred_cls):
        client, mock_blob_svc, mock_container = self._make_client(
            mock_blob_svc_cls, mock_cred_cls
        )
        assert client.account_url == "https://myaccount.blob.core.windows.net"
        assert client.container_name == "test-container"
        mock_blob_svc.get_container_client.assert_called_once_with("test-container")

    # -----------------------------------------------------------------------
    # create_container
    # -----------------------------------------------------------------------

    def test_create_container_success(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        client.create_container()
        mock_container.create_container.assert_called_once()

    def test_create_container_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_container.create_container.side_effect = Exception("already exists")
        # Should not raise
        client.create_container()

    # -----------------------------------------------------------------------
    # upload_blob
    # -----------------------------------------------------------------------

    def test_upload_blob_success(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client

        client.upload_blob("file.txt", b"data")

        mock_container.get_blob_client.assert_called_once_with("file.txt")
        mock_blob_client.upload_blob.assert_called_once_with(b"data", overwrite=True)

    def test_upload_blob_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.upload_blob.side_effect = Exception("upload failed")
        # Should not raise
        client.upload_blob("file.txt", b"data")

    # -----------------------------------------------------------------------
    # download_blob
    # -----------------------------------------------------------------------

    def test_download_blob_success(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_stream = MagicMock()
        mock_stream.readall.return_value = b"content"
        mock_blob_client.download_blob.return_value = mock_stream

        result = client.download_blob("file.txt")

        assert result == b"content"
        mock_container.get_blob_client.assert_called_once_with("file.txt")

    def test_download_blob_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.download_blob.side_effect = Exception("not found")

        result = client.download_blob("missing.txt")
        assert result is None

    # -----------------------------------------------------------------------
    # list_blobs
    # -----------------------------------------------------------------------

    def test_list_blobs_success(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        blob1 = MagicMock()
        blob1.name = "a.txt"
        blob2 = MagicMock()
        blob2.name = "b.txt"
        mock_container.list_blobs.return_value = [blob1, blob2]

        result = client.list_blobs()
        assert result == ["a.txt", "b.txt"]

    def test_list_blobs_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_container.list_blobs.side_effect = Exception("forbidden")

        result = client.list_blobs()
        assert result == []

    # -----------------------------------------------------------------------
    # delete_blob
    # -----------------------------------------------------------------------

    def test_delete_blob_success(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client

        client.delete_blob("file.txt")
        mock_blob_client.delete_blob.assert_called_once()

    def test_delete_blob_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.delete_blob.side_effect = Exception("not found")
        # Should not raise
        client.delete_blob("file.txt")

    # -----------------------------------------------------------------------
    # blob_exists
    # -----------------------------------------------------------------------

    def test_blob_exists_true(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.exists.return_value = True

        assert client.blob_exists("file.txt") is True

    def test_blob_exists_false(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.exists.return_value = False

        assert client.blob_exists("file.txt") is False

    def test_blob_exists_error(self, mock_blob_svc_cls, mock_cred_cls):
        client, _, mock_container = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.exists.side_effect = Exception("error")

        assert client.blob_exists("file.txt") is False

    # -----------------------------------------------------------------------
    # generate_sas_url
    # -----------------------------------------------------------------------

    @patch("template_github_copilot.internals.azure_blob_storages.generate_blob_sas")
    def test_generate_sas_url_defaults(
        self, mock_gen_sas, mock_blob_svc_cls, mock_cred_cls
    ):
        client, mock_blob_svc, _ = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_delegation_key = MagicMock()
        mock_blob_svc.get_user_delegation_key.return_value = mock_delegation_key
        mock_gen_sas.return_value = "sas_token_value"

        url = client.generate_sas_url("file.txt", expiry_hours=1)

        assert "sas_token_value" in url
        assert "file.txt" in url
        assert "test-container" in url
        mock_gen_sas.assert_called_once()

    @patch("template_github_copilot.internals.azure_blob_storages.generate_blob_sas")
    def test_generate_sas_url_custom_permissions(
        self, mock_gen_sas, mock_blob_svc_cls, mock_cred_cls
    ):
        client, mock_blob_svc, _ = self._make_client(mock_blob_svc_cls, mock_cred_cls)
        mock_delegation_key = MagicMock()
        mock_blob_svc.get_user_delegation_key.return_value = mock_delegation_key
        mock_gen_sas.return_value = "custom_sas"

        from azure.storage.blob import BlobSasPermissions

        perms = BlobSasPermissions(read=True, write=True)
        url = client.generate_sas_url(
            "data.bin",
            expiry_days=1,
            expiry_minutes=30,
            permission=perms,
        )

        assert "custom_sas" in url
        mock_gen_sas.assert_called_once()
        call_kwargs = mock_gen_sas.call_args[1]
        assert call_kwargs["permission"] is perms
        assert call_kwargs["account_name"] == "myaccount"
        assert call_kwargs["container_name"] == "test-container"
        assert call_kwargs["blob_name"] == "data.bin"
