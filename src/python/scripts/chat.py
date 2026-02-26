import asyncio
import logging
from typing import Annotated

import typer
from dotenv import load_dotenv

from template_github_copilot.core import (
    create_copilot_client,
    create_event_handler,
    create_message_options,
    create_session_config,
)
from template_github_copilot.services.chat import ChatParallelOutput, ChatResult
from template_github_copilot.loggers import get_logger
from template_github_copilot.providers import AuthMethod, create_provider
from template_github_copilot.settings import get_project_settings

app = typer.Typer(
    add_completion=False,
    help="adhoc CLI",
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
def hello(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the person to greet",
        ),
    ] = "World",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)

    logger.debug(f"This is a debug message with name: {name}")
    logger.info(
        f"Settings from .env: {get_project_settings().model_dump_json(indent=2)}"
    )


@app.command()
def chat(
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
    set_verbose_logging(verbose)

    result = create_provider(AuthMethod.COPILOT)

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        session = await client.create_session(
            create_session_config(
                model=result.model,
                provider=result.provider,
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
def chat_loop(
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
    """Interactive chat loop with Copilot."""
    set_verbose_logging(verbose)

    result = create_provider(AuthMethod.COPILOT)

    async def main():
        client = create_copilot_client(cli_url)
        await client.start()

        session = await client.create_session(
            create_session_config(
                model=result.model,
                provider=result.provider,
            )
        )

        handler = create_event_handler(
            writer=logger.info,
        )
        session.on(handler)

        logger.info("Chat with Copilot (Ctrl+C to exit)\n")

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
def chat_parallel(
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
    """Send multiple prompts to Copilot in parallel (separate sessions) and output structured JSON."""
    set_verbose_logging(verbose)

    result = create_provider(AuthMethod.COPILOT)

    async def process_prompt(client, prompt: str) -> ChatResult:
        try:
            session = await client.create_session(
                create_session_config(
                    model=result.model,
                    provider=result.provider,
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
