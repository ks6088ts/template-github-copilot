import asyncio
import logging
from datetime import datetime, timezone
from typing import Annotated

import typer
from dotenv import load_dotenv

from template_github_copilot.core import ReportOutput, run_parallel_chat
from template_github_copilot.internals.azure_blob_storages import AzureBlobStorageClient
from template_github_copilot.loggers import get_logger

app = typer.Typer(
    add_completion=False,
    help="Report service CLI",
)

logger = get_logger(__name__)


def set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


def _upload_report(
    report: ReportOutput,
    account_url: str,
    container_name: str,
    blob_name: str | None = None,
) -> str:
    """Upload a report JSON to Azure Blob Storage.

    Args:
        report: The structured report output.
        account_url: Azure Blob Storage account URL.
        container_name: Azure Blob Storage container name.
        blob_name: Optional blob name. If not provided, a timestamped name is generated.

    Returns:
        The blob name used for the upload.
    """
    if blob_name is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        blob_name = f"report_{timestamp}.json"

    client = AzureBlobStorageClient(
        account_url=account_url,
        container_name=container_name,
    )
    client.upload_blob(
        blob_name=blob_name,
        data=report.model_dump_json(indent=2).encode("utf-8"),
    )
    return blob_name


@app.command()
def generate(
    system_prompt: Annotated[
        str,
        typer.Option(
            "--system-prompt",
            "-s",
            help="The system prompt to configure the assistant's behavior",
        ),
    ],
    queries: Annotated[
        str,
        typer.Option(
            "--queries",
            "-q",
            help="Comma-separated user queries (e.g. 'query1,query2,query3')",
        ),
    ],
    account_url: Annotated[
        str,
        typer.Option(
            "--account-url",
            "-a",
            help="Azure Blob Storage account URL (e.g. https://<account>.blob.core.windows.net)",
        ),
    ],
    container_name: Annotated[
        str,
        typer.Option(
            "--container-name",
            "-n",
            help="Azure Blob Storage container name",
        ),
    ],
    blob_name: Annotated[
        str | None,
        typer.Option(
            "--blob-name",
            "-b",
            help="Blob name for the report (default: report_<timestamp>.json)",
        ),
    ] = None,
    cli_url: Annotated[
        str,
        typer.Option(
            "--cli-url",
            "-c",
            help="The URL of the Copilot CLI server (e.g., localhost:3000)",
        ),
    ] = "localhost:3000",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Generate reports by sending multiple queries to Copilot in parallel and uploading results to Azure Blob Storage."""
    set_verbose_logging(verbose)

    query_list = [q.strip() for q in queries.split(",") if q.strip()]
    if not query_list:
        logger.error("No queries provided. Use comma-separated values for --queries.")
        raise typer.Exit(code=1)

    async def main() -> ReportOutput:
        return await run_parallel_chat(
            cli_url=cli_url,
            queries=query_list,
            system_prompt=system_prompt,
            writer=logger.debug,
        )

    try:
        report = asyncio.run(main())
        logger.info(f"Report generated: {report.succeeded}/{report.total} succeeded")

        uploaded_name = _upload_report(
            report=report,
            account_url=account_url,
            container_name=container_name,
            blob_name=blob_name,
        )
        logger.info(
            f"Report uploaded to blob '{uploaded_name}' in container '{container_name}'"
        )

        typer.echo(report.model_dump_json(indent=2))
    except KeyboardInterrupt:
        logger.info("Bye!")


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
