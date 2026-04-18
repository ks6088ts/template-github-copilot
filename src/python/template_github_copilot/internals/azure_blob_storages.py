from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    generate_blob_sas,
)

from template_github_copilot.loggers import get_logger

logger = get_logger(__name__)


class AzureBlobStorageClient:
    def __init__(
        self,
        account_url: str,
        container_name: str,
    ):
        self.account_url = account_url
        self.container_name = container_name
        self.credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=self.credential,
        )
        self.container_client: ContainerClient = (
            self.blob_service_client.get_container_client(container_name)
        )

    def create_container(self):
        """Create the container if it does not exist."""
        try:
            self.container_client.create_container()
            logger.info(f"Container '{self.container_name}' created successfully")
        except Exception as e:
            logger.error(f"Container creation failed: {e}")

    def upload_blob(self, blob_name: str, data: bytes):
        """Upload a blob to the container."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Blob '{blob_name}' uploaded successfully")
        except Exception as e:
            logger.error(f"Uploading blob failed: {e}")

    def download_blob(self, blob_name: str) -> bytes | None:
        """Download a blob from the container."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            download_stream = blob_client.download_blob()
            data: bytes = download_stream.readall()  # type: ignore[assignment]  # ty: ignore[invalid-assignment]
            logger.info(f"Blob '{blob_name}' downloaded successfully")
            return data
        except Exception as e:
            logger.error(f"Downloading blob failed: {e}")
            return None

    def list_blobs(self) -> list:
        """List all blobs in the container."""
        try:
            blobs = self.container_client.list_blobs()
            blob_list = [blob.name for blob in blobs]
            logger.debug(f"Listed {len(blob_list)} blobs")
            return blob_list
        except Exception as e:
            logger.error(f"Listing blobs failed: {e}")
            return []

    def delete_blob(self, blob_name: str):
        """Delete a blob from the container."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            logger.info(f"Blob '{blob_name}' deleted successfully")
        except Exception as e:
            logger.error(f"Deleting blob failed: {e}")

    def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists in the container."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Checking blob existence failed: {e}")
            return False

    def generate_sas_url(
        self,
        blob_name: str,
        expiry_hours: int = 0,
        expiry_minutes: int = 0,
        expiry_days: int = 0,
        permission: BlobSasPermissions | None = None,
    ) -> str:
        """Generate a SAS URL for a blob using a user delegation key.

        Args:
            blob_name: The name of the blob.
            expiry_hours: Hours until the SAS token expires.
            expiry_minutes: Minutes until the SAS token expires.
            expiry_days: Days until the SAS token expires.
            permission: The permissions for the SAS token. Defaults to read-only.

        Returns:
            The full SAS URL for the blob.
        """
        if permission is None:
            permission = BlobSasPermissions(read=True)

        now = datetime.now(timezone.utc)
        expiry_time = now + timedelta(
            days=expiry_days,
            hours=expiry_hours,
            minutes=expiry_minutes,
        )

        # User delegation key is valid for up to 7 days
        user_delegation_key = self.blob_service_client.get_user_delegation_key(
            key_start_time=now,
            key_expiry_time=expiry_time,
        )

        # Extract account name from the account URL
        # e.g. "https://myaccount.blob.core.windows.net" -> "myaccount"
        account_name = self.account_url.split("//")[1].split(".")[0]

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            user_delegation_key=user_delegation_key,
            permission=permission,
            expiry=expiry_time,
            start=now,
        )

        sas_url = f"{self.account_url}/{self.container_name}/{blob_name}?{sas_token}"
        logger.info(
            f"Generated SAS URL for blob '{blob_name}' (expires: {expiry_time.isoformat()})"
        )
        return sas_url
