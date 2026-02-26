"""CLI to launch the Copilot Chat API server (FastAPI + OAuth GitHub App)."""

import logging
from typing import Annotated

import typer
import uvicorn
from dotenv import load_dotenv

from template_github_copilot.loggers import get_logger
from template_github_copilot.settings.oauth import get_oauth_settings

app = typer.Typer(
    add_completion=False,
)

logger = get_logger(__name__)


@app.callback()
def callback():
    """Copilot Chat API server with OAuth GitHub App authentication"""


def set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


@app.command()
def serve(
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Bind address"),
    ] = "",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Bind port"),
    ] = 0,
    copilot_cli_url: Annotated[
        str,
        typer.Option("--copilot-cli-url", "-c", help="Copilot CLI server URL"),
    ] = "",
    reload: Annotated[
        bool,
        typer.Option("--reload", "-r", help="Enable auto-reload for development"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Start the Copilot Chat API server."""
    set_verbose_logging(verbose)

    settings = get_oauth_settings()

    # CLI flags override settings; fall back to env/dotenv values
    bind_host = host or settings.api_host
    bind_port = port or settings.api_port

    if copilot_cli_url:
        settings.copilot_cli_url = copilot_cli_url

    if not settings.github_client_id or not settings.github_client_secret:
        logger.warning(
            "GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET are not set. "
            "OAuth login will fail. Set them in .env or as environment variables."
        )

    logger.info(f"Starting server on {bind_host}:{bind_port}")
    logger.info(f"Copilot CLI URL: {settings.copilot_cli_url}")

    uvicorn.run(
        "template_github_copilot.services.apis.app:create_app",
        host=bind_host,
        port=bind_port,
        reload=reload,
        factory=True,
        log_level="debug" if verbose else "info",
    )


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
