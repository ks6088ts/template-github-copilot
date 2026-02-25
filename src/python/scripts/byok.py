import asyncio
import logging
from typing import Annotated

import typer
from azure.identity import DefaultAzureCredential
from copilot.types import ProviderConfig
from dotenv import load_dotenv

from template_github_copilot.core import (
    create_copilot_client,
    create_event_handler,
    create_message_options,
    create_session_config,
)
from template_github_copilot.internals.chat import ChatParallelOutput, ChatResult
from template_github_copilot.loggers import get_logger
from template_github_copilot.settings import get_byok_settings

COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"

app = typer.Typer(
    add_completion=False,
    help="BYOK (Bring Your Own Key) CLI for API Key and Entra ID authentication",
)

logger = get_logger(__name__)


def set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


def _build_api_key_provider() -> ProviderConfig:
    """Build a ProviderConfig using a static API key from BYOK settings."""
    settings = get_byok_settings()
    provider = ProviderConfig(
        type=settings.byok_provider_type,
        base_url=settings.byok_base_url,
        api_key=settings.byok_api_key,
    )
    if settings.byok_wire_api:
        provider["wire_api"] = settings.byok_wire_api
    return provider


def _build_entra_id_provider() -> ProviderConfig:
    """Build a ProviderConfig using a short-lived Entra ID bearer token."""
    settings = get_byok_settings()
    credential = DefaultAzureCredential()
    token = credential.get_token(COGNITIVE_SERVICES_SCOPE).token
    provider = ProviderConfig(
        type=settings.byok_provider_type,
        base_url=settings.byok_base_url,
        bearer_token=token,
    )
    if settings.byok_wire_api:
        provider["wire_api"] = settings.byok_wire_api
    return provider


# --- API Key-based BYOK commands ---


@app.command()
def chat_api_key(
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            "-p",
            help="The prompt to use for the chat",
        ),
    ] = "Hello, Copilot!",
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
    """Send a single prompt using BYOK with a static API key."""
    set_verbose_logging(verbose)

    settings = get_byok_settings()
    provider = _build_api_key_provider()

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        session = await client.create_session(
            create_session_config(
                model=settings.byok_model,
                provider=provider,
            )
        )

        handler = create_event_handler(writer=logger.info)
        session.on(handler)

        reply = await session.send_and_wait(create_message_options(prompt))
        content = reply.data.content if reply else None
        logger.info(f"Assistant: {content or '(no response)'}")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


@app.command()
def chat_loop_api_key(
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
    """Interactive chat loop using BYOK with a static API key."""
    set_verbose_logging(verbose)

    settings = get_byok_settings()
    provider = _build_api_key_provider()

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        session = await client.create_session(
            create_session_config(
                model=settings.byok_model,
                provider=provider,
            )
        )

        handler = create_event_handler(writer=logger.info)
        session.on(handler)

        logger.info("Chat with Copilot via API Key BYOK (Ctrl+C to exit)\n")

        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            reply = await session.send_and_wait(create_message_options(user_input))
            content = reply.data.content if reply else None
            typer.echo(
                typer.style("Assistant: ", fg=typer.colors.GREEN, bold=True)
                + (content or "(no response)")
            )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


@app.command()
def chat_parallel_api_key(
    prompts: Annotated[
        list[str],
        typer.Option(
            "--prompt",
            "-p",
            help="Prompts to send in parallel (specify multiple times, e.g. -p 'Hello' -p 'Hi')",
        ),
    ],
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
    """Send multiple prompts in parallel using BYOK with a static API key."""
    set_verbose_logging(verbose)

    settings = get_byok_settings()
    provider = _build_api_key_provider()

    async def process_prompt(client, prompt: str) -> ChatResult:
        try:
            session = await client.create_session(
                create_session_config(
                    model=settings.byok_model,
                    provider=provider,
                )
            )
            handler = create_event_handler(writer=logger.debug)
            session.on(handler)

            reply = await session.send_and_wait(create_message_options(prompt))
            content = reply.data.content if reply else None
            return ChatResult(prompt=prompt, response=content)
        except Exception as e:
            return ChatResult(prompt=prompt, error=str(e))

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        tasks = [process_prompt(client, p) for p in prompts]
        results = await asyncio.gather(*tasks)

        succeeded = sum(1 for r in results if r.response is not None)
        output = ChatParallelOutput(
            results=list(results),
            total=len(results),
            succeeded=succeeded,
            failed=len(results) - succeeded,
        )
        typer.echo(output.model_dump_json(indent=2))

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


# --- Entra ID-based BYOK commands ---


@app.command()
def chat_entra_id(
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            "-p",
            help="The prompt to use for the chat",
        ),
    ] = "Hello, Copilot!",
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
    """Send a single prompt using BYOK with Entra ID (DefaultAzureCredential) bearer token."""
    set_verbose_logging(verbose)

    settings = get_byok_settings()
    provider = _build_entra_id_provider()

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        session = await client.create_session(
            create_session_config(
                model=settings.byok_model,
                provider=provider,
            )
        )

        handler = create_event_handler(writer=logger.info)
        session.on(handler)

        reply = await session.send_and_wait(create_message_options(prompt))
        content = reply.data.content if reply else None
        logger.info(f"Assistant: {content or '(no response)'}")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


@app.command()
def chat_loop_entra_id(
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
    """Interactive chat loop using BYOK with Entra ID bearer token.

    A fresh token is obtained for each new session. Since bearer tokens expire
    (~1 hour), the token is refreshed when a new session is created.
    """
    set_verbose_logging(verbose)

    settings = get_byok_settings()

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        # Obtain a fresh bearer token for the session
        provider = _build_entra_id_provider()
        session = await client.create_session(
            create_session_config(
                model=settings.byok_model,
                provider=provider,
            )
        )

        handler = create_event_handler(writer=logger.info)
        session.on(handler)

        logger.info("Chat with Copilot via Entra ID BYOK (Ctrl+C to exit)\n")

        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            reply = await session.send_and_wait(create_message_options(user_input))
            content = reply.data.content if reply else None
            typer.echo(
                typer.style("Assistant: ", fg=typer.colors.GREEN, bold=True)
                + (content or "(no response)")
            )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


@app.command()
def chat_parallel_entra_id(
    prompts: Annotated[
        list[str],
        typer.Option(
            "--prompt",
            "-p",
            help="Prompts to send in parallel (specify multiple times, e.g. -p 'Hello' -p 'Hi')",
        ),
    ],
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
    """Send multiple prompts in parallel using BYOK with Entra ID bearer token.

    A fresh bearer token is obtained once and shared across all parallel sessions.
    """
    set_verbose_logging(verbose)

    settings = get_byok_settings()
    provider = _build_entra_id_provider()

    async def process_prompt(client, prompt: str) -> ChatResult:
        try:
            session = await client.create_session(
                create_session_config(
                    model=settings.byok_model,
                    provider=provider,
                )
            )
            handler = create_event_handler(writer=logger.debug)
            session.on(handler)

            reply = await session.send_and_wait(create_message_options(prompt))
            content = reply.data.content if reply else None
            return ChatResult(prompt=prompt, response=content)
        except Exception as e:
            return ChatResult(prompt=prompt, error=str(e))

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        tasks = [process_prompt(client, p) for p in prompts]
        results = await asyncio.gather(*tasks)

        succeeded = sum(1 for r in results if r.response is not None)
        output = ChatParallelOutput(
            results=list(results),
            total=len(results),
            succeeded=succeeded,
            failed=len(results) - succeeded,
        )
        typer.echo(output.model_dump_json(indent=2))

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bye!")


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
