import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Annotated, Literal

import typer
from dotenv import load_dotenv

from template_github_copilot.internals.azure_blob_storages import AzureBlobStorageClient
from template_github_copilot.loggers import get_logger
from template_github_copilot.providers import AuthMethod, create_provider
from template_github_copilot.services.reports import ReportOutput, run_parallel_chat
from template_github_copilot.settings.byok import ByokSettings

app = typer.Typer(
    add_completion=False,
)

logger = get_logger(__name__)

DEFAULT_SAS_EXPIRY_HOURS = 1


@app.callback()
def callback():
    """Report service CLI"""


def _configure_logging(verbose: bool) -> None:
    """Configure log levels based on the verbose flag."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)


def _resolve_blob_name(blob_name: str | None) -> str:
    """Return the given blob name, or generate a timestamped default."""
    if blob_name is not None:
        return blob_name
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"report_{timestamp}.json"


def _generate_report(
    cli_url: str,
    queries: list[str],
    system_prompt: str,
    auth_method: AuthMethod = AuthMethod.COPILOT,
    byok_settings: ByokSettings | None = None,
) -> ReportOutput:
    """Run parallel chat queries and return the aggregated report."""
    provider_result = create_provider(auth_method, byok_settings=byok_settings)

    async def _run() -> ReportOutput:
        return await run_parallel_chat(
            cli_url=cli_url,
            queries=queries,
            system_prompt=system_prompt,
            writer=logger.debug,
            provider=provider_result.provider,
            model=provider_result.model,
        )

    return asyncio.run(_run())


def _upload(
    client: AzureBlobStorageClient,
    report: ReportOutput,
    blob_name: str,
) -> None:
    """Upload the report JSON to Azure Blob Storage."""
    client.upload_blob(
        blob_name=blob_name,
        data=report.model_dump_json(indent=2).encode("utf-8"),
    )
    logger.info(
        f"Report uploaded to blob '{blob_name}' in container '{client.container_name}'"
    )


def _share(
    client: AzureBlobStorageClient,
    blob_name: str,
    expiry_hours: int,
) -> str:
    """Generate a time-limited SAS URL for the blob."""
    return client.generate_sas_url(
        blob_name=blob_name,
        expiry_hours=expiry_hours,
    )


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
    sas_expiry_hours: Annotated[
        int,
        typer.Option(
            "--sas-expiry-hours",
            envvar="SAS_EXPIRY_HOURS",
            help="Hours until the SAS URL expires",
        ),
    ] = DEFAULT_SAS_EXPIRY_HOURS,
    auth_method: Annotated[
        AuthMethod,
        typer.Option(
            "--auth-method",
            "-m",
            help="LLM provider authentication method (copilot, api_key, entra_id)",
        ),
    ] = AuthMethod.COPILOT,
    byok_provider_type: Annotated[
        Literal["openai", "azure", "anthropic"],
        typer.Option(
            "--byok-provider-type",
            envvar="BYOK_PROVIDER_TYPE",
            help="BYOK provider type (e.g. openai, azure, anthropic)",
        ),
    ] = "openai",
    byok_base_url: Annotated[
        str,
        typer.Option(
            "--byok-base-url",
            envvar="BYOK_BASE_URL",
            help="BYOK provider base URL",
        ),
    ] = "https://api.openai.com/v1/",
    byok_api_key: Annotated[
        str,
        typer.Option(
            "--byok-api-key",
            envvar="BYOK_API_KEY",
            help="BYOK provider API key",
        ),
    ] = "",
    byok_model: Annotated[
        str,
        typer.Option(
            "--byok-model",
            envvar="BYOK_MODEL",
            help="Model identifier for the BYOK provider",
        ),
    ] = "gpt-4o",
    byok_wire_api: Annotated[
        Literal["completions", "responses"],
        typer.Option(
            "--byok-wire-api",
            envvar="BYOK_WIRE_API",
            help="Wire API format (completions or responses)",
        ),
    ] = "responses",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Generate reports by sending multiple queries to Copilot in parallel and uploading results to Azure Blob Storage."""
    _configure_logging(verbose)

    query_list = [q.strip() for q in queries.split(",") if q.strip()]
    if not query_list:
        logger.error("No queries provided. Use comma-separated values for --queries.")
        raise typer.Exit(code=1)

    try:
        byok_settings: ByokSettings | None = None
        if auth_method in (AuthMethod.API_KEY, AuthMethod.ENTRA_ID):
            byok_settings = ByokSettings(
                byok_provider_type=byok_provider_type,
                byok_base_url=byok_base_url,
                byok_api_key=byok_api_key,
                byok_model=byok_model,
                byok_wire_api=byok_wire_api,
            )

        report = _generate_report(
            cli_url, query_list, system_prompt, auth_method, byok_settings
        )
        logger.info(f"Report generated: {report.succeeded}/{report.total} succeeded")

        azure_blob_storage_client = AzureBlobStorageClient(
            account_url=account_url,
            container_name=container_name,
        )
        resolved_name = _resolve_blob_name(blob_name)

        _upload(
            client=azure_blob_storage_client, report=report, blob_name=resolved_name
        )

        sas_url = _share(
            client=azure_blob_storage_client,
            blob_name=resolved_name,
            expiry_hours=sas_expiry_hours,
        )
        logger.info(f"SAS URL (expires in {sas_expiry_hours}h): {sas_url}")

        # Write SAS URL to GitHub Actions output if running in CI
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"sas_url={sas_url}\n")
            logger.info("SAS URL written to GITHUB_OUTPUT")

        typer.echo(report.model_dump_json(indent=2))
    except KeyboardInterrupt:
        logger.info("Bye!")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
