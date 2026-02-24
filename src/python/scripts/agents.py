import logging
from typing import Annotated

import typer
from dotenv import load_dotenv

from template_github_copilot.internals.agents import (
    create_agent,
    create_project_client,
    delete_agent,
    get_agent,
    list_agents,
    run_agent,
)
from template_github_copilot.loggers import get_logger
from template_github_copilot.settings import get_microsoft_foundry_settings

app = typer.Typer(
    add_completion=False,
    help="Microsoft Foundry Agents CLI",
)

logger = get_logger(__name__)


def _default_endpoint() -> str:
    return get_microsoft_foundry_settings().microsoft_foundry_project_endpoint


def set_verbose_logging(
    verbose: bool,
    target_logger: logging.Logger = logger,
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        target_logger.setLevel(logging.DEBUG)


@app.command()
def create(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "my-agent",
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Model to use for the agent (e.g., gpt-4o)",
        ),
    ] = "gpt-4o",
    instructions: Annotated[
        str,
        typer.Option(
            "--instructions",
            "-i",
            help="System instructions for the agent",
        ),
    ] = "You are a helpful assistant.",
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Microsoft Foundry project endpoint",
        ),
    ] = "",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Create a new agent."""
    set_verbose_logging(verbose)

    ep = endpoint or _default_endpoint()
    client = create_project_client(ep)
    info = create_agent(client, model=model, name=name, instructions=instructions)
    typer.echo(info.model_dump_json(indent=2))


@app.command(name="get")
def get_cmd(
    agent_name: Annotated[
        str,
        typer.Option(
            "--agent-name",
            "-n",
            help="Name of the agent to retrieve",
        ),
    ],
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Microsoft Foundry project endpoint",
        ),
    ] = "",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Get an agent by name."""
    set_verbose_logging(verbose)

    ep = endpoint or _default_endpoint()
    client = create_project_client(ep)
    info = get_agent(client, agent_name=agent_name)
    typer.echo(info.model_dump_json(indent=2))


@app.command(name="list")
def list_cmd(
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Microsoft Foundry project endpoint",
        ),
    ] = "",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """List all agents."""
    set_verbose_logging(verbose)

    ep = endpoint or _default_endpoint()
    client = create_project_client(ep)
    output = list_agents(client)
    typer.echo(output.model_dump_json(indent=2))


@app.command()
def delete(
    agent_name: Annotated[
        str,
        typer.Option(
            "--agent-name",
            "-n",
            help="Name of the agent to delete",
        ),
    ],
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Microsoft Foundry project endpoint",
        ),
    ] = "",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Delete an agent by name."""
    set_verbose_logging(verbose)

    ep = endpoint or _default_endpoint()
    client = create_project_client(ep)
    delete_agent(client, agent_name=agent_name)
    logger.info(f"Agent {agent_name} deleted successfully.")


@app.command()
def run(
    agent_name: Annotated[
        str,
        typer.Option(
            "--agent-name",
            "-n",
            help="Name of the agent to run",
        ),
    ],
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            "-p",
            help="User message to send to the agent",
        ),
    ] = "Hello!",
    conversation_id: Annotated[
        str,
        typer.Option(
            "--conversation-id",
            "-c",
            help="Existing conversation ID for multi-turn chat",
        ),
    ] = "",
    endpoint: Annotated[
        str,
        typer.Option(
            "--endpoint",
            "-e",
            help="Microsoft Foundry project endpoint",
        ),
    ] = "",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    """Run an agent with a user message."""
    set_verbose_logging(verbose)

    ep = endpoint or _default_endpoint()
    client = create_project_client(ep)
    result = run_agent(
        client,
        agent_name=agent_name,
        user_message=prompt,
        conversation_id=conversation_id or None,
    )
    typer.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    load_dotenv(
        override=True,
        verbose=True,
    )
    app()
