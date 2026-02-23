import logging
from typing import Annotated

import httpx
import typer
from dotenv import load_dotenv

from template_github_copilot.loggers import get_logger

app = typer.Typer(
    add_completion=False,
    help="Slack incoming webhook CLI",
)

logger = get_logger(__name__)


@app.callback()
def callback():
    """Slack incoming webhook CLI"""


def _set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


def _send_slack_message(webhook_url: str, text: str) -> httpx.Response:
    """Send a message to Slack via incoming webhook.

    Args:
        webhook_url: The Slack incoming webhook URL.
        text: The message text to send.

    Returns:
        The HTTP response from Slack.

    Raises:
        httpx.HTTPStatusError: If the request fails.
    """
    response = httpx.post(
        webhook_url,
        json={"text": text},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response


@app.command()
def send(
    webhook_url: Annotated[
        str,
        typer.Option(
            "--webhook-url",
            "-w",
            help="Slack incoming webhook URL",
            envvar="SLACK_WEBHOOK_URL",
        ),
    ],
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            help="Message text to send to Slack",
        ),
    ] = "Hello from template-github-copilot!",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Send a message to Slack via incoming webhook."""
    _set_verbose_logging(verbose)

    logger.debug(f"Sending message to Slack: {message}")
    try:
        response = _send_slack_message(webhook_url, message)
        logger.info(f"Message sent successfully (status={response.status_code})")
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Failed to send message: {e.response.status_code} {e.response.text}"
        )
        raise typer.Exit(code=1)
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
