import logging
from typing import Annotated

import typer
from dotenv import load_dotenv

from template_github_copilot.internals.azure_blob_storages import AzureBlobStorageClient
from template_github_copilot.loggers import get_logger
from template_github_copilot.settings import get_azure_blob_storage_settings

app = typer.Typer(
    add_completion=False,
    help="blob CLI",
)

logger = get_logger(__name__)


def set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


@app.command()
def list_blobs(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """List blobs in the Azure Blob Storage container."""
    set_verbose_logging(verbose)

    settings = get_azure_blob_storage_settings()
    client = AzureBlobStorageClient(
        account_url=settings.azure_blob_storage_account_url,
        container_name=settings.azure_blob_storage_container_name,
    )
    blobs = client.list_blobs()
    logger.info(
        f"Blobs in container '{settings.azure_blob_storage_container_name}': {blobs}"
    )


@app.command()
def upload_blob(
    data_str: Annotated[
        str,
        typer.Option(
            "--data",
            "-d",
            help="The data to upload as a blob (string format)",
        ),
    ],
    blob_name: Annotated[
        str,
        typer.Option(
            "--blob-name",
            "-b",
            help="The name of the blob to create in Azure Blob Storage",
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Upload a string as a blob to Azure Blob Storage."""
    set_verbose_logging(verbose)

    settings = get_azure_blob_storage_settings()
    client = AzureBlobStorageClient(
        account_url=settings.azure_blob_storage_account_url,
        container_name=settings.azure_blob_storage_container_name,
    )
    client.upload_blob(blob_name=blob_name, data=data_str.encode("utf-8"))
    logger.info(
        f"Uploaded blob '{blob_name}' to container '{settings.azure_blob_storage_container_name}'"
    )


@app.command()
def generate_sas_url(
    blob_name: Annotated[
        str,
        typer.Option(
            "--blob-name",
            "-b",
            help="The name of the blob to generate a SAS URL for",
        ),
    ],
    expiry_days: Annotated[
        int,
        typer.Option(
            "--expiry-days",
            help="Number of days until the SAS token expires",
        ),
    ] = 0,
    expiry_hours: Annotated[
        int,
        typer.Option(
            "--expiry-hours",
            help="Number of hours until the SAS token expires",
        ),
    ] = 1,
    expiry_minutes: Annotated[
        int,
        typer.Option(
            "--expiry-minutes",
            help="Number of minutes until the SAS token expires",
        ),
    ] = 0,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Generate a time-limited SAS URL for a blob in Azure Blob Storage."""
    set_verbose_logging(verbose)

    if expiry_days == 0 and expiry_hours == 0 and expiry_minutes == 0:
        logger.error(
            "At least one of --expiry-days, --expiry-hours, or --expiry-minutes must be greater than 0"
        )
        raise typer.Exit(code=1)

    settings = get_azure_blob_storage_settings()
    client = AzureBlobStorageClient(
        account_url=settings.azure_blob_storage_account_url,
        container_name=settings.azure_blob_storage_container_name,
    )
    sas_url = client.generate_sas_url(
        blob_name=blob_name,
        expiry_days=expiry_days,
        expiry_hours=expiry_hours,
        expiry_minutes=expiry_minutes,
    )
    typer.echo(sas_url)


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
