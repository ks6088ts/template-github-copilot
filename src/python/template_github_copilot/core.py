import asyncio
from collections.abc import Callable
from typing import Any

import typer
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.types import (
    CopilotClientOptions,
    MessageOptions,
    PermissionRequest,
    PermissionRequestResult,
    SessionConfig,
    SystemMessageAppendConfig,
    SystemMessageConfig,
    SystemMessageReplaceConfig,
    Tool,
)
from pydantic import BaseModel, Field

from template_github_copilot.internals.tools import get_custom_tools

# Type alias for the writer function used by the event handler
WriterFunc = Callable[[str], Any]


class ChatResult(BaseModel):
    """Result of a single chat prompt."""

    prompt: str = Field(..., description="The original prompt sent to Copilot.")
    response: str | None = Field(
        None, description="The response content from Copilot, or None if no response."
    )
    error: str | None = Field(None, description="Error message if the request failed.")


class ChatParallelOutput(BaseModel):
    """Structured output for the chat_parallel command."""

    results: list[ChatResult] = Field(
        ..., description="List of results for each prompt."
    )
    total: int = Field(..., description="Total number of prompts processed.")
    succeeded: int = Field(
        ..., description="Number of prompts that received a response."
    )
    failed: int = Field(
        ..., description="Number of prompts that failed or had no response."
    )


class ReportResult(BaseModel):
    """Result of a single report query."""

    query: str = Field(..., description="The original user query.")
    response: str | None = Field(
        None, description="The response content from Copilot, or None if no response."
    )
    error: str | None = Field(None, description="Error message if the request failed.")


class ReportOutput(BaseModel):
    """Structured output for the report service."""

    system_prompt: str = Field(..., description="The system prompt used.")
    results: list[ReportResult] = Field(
        ..., description="List of results for each query."
    )
    total: int = Field(..., description="Total number of queries processed.")
    succeeded: int = Field(
        ..., description="Number of queries that received a response."
    )
    failed: int = Field(
        ..., description="Number of queries that failed or had no response."
    )


def _default_writer(message: str) -> None:
    """Default writer that prints to stdout."""
    print(message)


def _get_system_message() -> SystemMessageConfig:
    """Example function to provide a default system message for the session config."""
    return SystemMessageAppendConfig(content="You are a helpful assistant.")


def write_status(
    label: str, color: str, message: str, writer: WriterFunc = _default_writer
) -> None:
    """Write a colored status message using the provided writer function."""
    writer(typer.style(f"[{label}]", fg=color) + f" {message}")


def approve_all(
    request: PermissionRequest, context: dict[str, str]
) -> PermissionRequestResult:
    """Permission handler that approves all requests."""
    return PermissionRequestResult(kind="approved", rules=[])


def create_event_handler(
    writer: WriterFunc = _default_writer,
    on_session_idle: Callable[[], Any] | None = None,
) -> Callable[[Any], None]:
    """Factory function that creates a reusable Copilot session event handler.

    Args:
        writer: A callable that accepts a string message for output (e.g. print, logger.info).
        on_session_idle: Optional callback invoked when the session becomes idle.

    Returns:
        An event handler function suitable for ``session.on(handler)``.
    """

    def on_event(event: Any) -> None:
        event_type = event.type

        # --- Copilot activity events (background status) ---

        if event_type == SessionEventType.ASSISTANT_TURN_START:
            write_status("Turn", typer.colors.CYAN, "Copilot is thinking...", writer)

        elif event_type == SessionEventType.ASSISTANT_INTENT:
            write_status("Intent", typer.colors.MAGENTA, event.data.intent, writer)

        elif event_type == SessionEventType.ASSISTANT_TURN_END:
            write_status(
                "Turn", typer.colors.CYAN, "Copilot finished this turn.", writer
            )

        elif event_type == SessionEventType.TOOL_EXECUTION_START:
            write_status(
                "Tool", typer.colors.YELLOW, f"Running: {event.data.tool_name}", writer
            )

        elif event_type == SessionEventType.TOOL_EXECUTION_PROGRESS:
            write_status(
                "Progress", typer.colors.YELLOW, event.data.progress_message, writer
            )

        elif event_type == SessionEventType.TOOL_EXECUTION_COMPLETE:
            if hasattr(event.data, "error") and event.data.error:
                write_status(
                    "Tool Error", typer.colors.RED, event.data.error.message, writer
                )
            else:
                result = (
                    event.data.result.content
                    if hasattr(event.data, "result") and event.data.result
                    else "Completed"
                )
                write_status("Tool", typer.colors.GREEN, result, writer)

        elif event_type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            write_status(
                "Delta content",
                typer.colors.BLUE,
                f"{event.data.delta_content}",
                writer,
            )

        elif event_type == SessionEventType.SESSION_ERROR:
            write_status("Error", typer.colors.RED, event.data.message, writer)

        # --- Session lifecycle ---

        elif event_type == SessionEventType.SESSION_IDLE:
            writer("Session completed.")
            if on_session_idle:
                on_session_idle()

    return on_event


def create_copilot_client(cli_url: str = "localhost:3000") -> CopilotClient:
    """Factory function that creates a CopilotClient.

    Args:
        cli_url: The URL of the Copilot CLI server.

    Returns:
        A configured ``CopilotClient`` instance.
    """
    return CopilotClient(
        options=CopilotClientOptions(
            cli_url=cli_url,
        ),
    )


def create_session_config(
    on_permission_request: Callable[
        [PermissionRequest, dict[str, str]], PermissionRequestResult
    ] = approve_all,
    system_message: SystemMessageAppendConfig
    | SystemMessageReplaceConfig
    | None = _get_system_message(),
    tools: list[Tool] | None = get_custom_tools(),
    streaming: bool = True,
    **kwargs: Any,
) -> SessionConfig:
    """Factory function that creates a SessionConfig.

    Args:
        on_permission_request: Permission handler (defaults to ``approve_all``).
        system_message: Optional system message config to set the assistant's behavior.
        tools: Optional list of custom tools to register for the session.
        streaming: Whether to enable streaming responses (default: True).
        **kwargs: Additional keyword arguments forwarded to ``SessionConfig``.

    Returns:
        A configured ``SessionConfig`` instance.
    """
    config = SessionConfig(
        on_permission_request=on_permission_request,
        tools=tools if tools is not None else [],
        streaming=streaming,
        **kwargs,
    )
    if system_message is not None:
        config["system_message"] = system_message
    return config


def create_message_options(
    prompt: str,
) -> MessageOptions:
    """Factory function that creates MessageOptions for a given prompt.

    Args:
        prompt: The user input prompt to send to Copilot.
    Returns:
        A configured ``MessageOptions`` instance.
    """
    return MessageOptions(
        prompt=prompt,
    )


async def run_parallel_chat(
    cli_url: str,
    queries: list[str],
    system_prompt: str,
    writer: WriterFunc = _default_writer,
) -> ReportOutput:
    """Run multiple chat queries in parallel sessions and return structured results.

    Args:
        cli_url: The URL of the Copilot CLI server.
        queries: A list of user queries to send in parallel.
        system_prompt: The system prompt to configure each session.
        writer: A callable for logging messages.

    Returns:
        A ``ReportOutput`` containing all results.
    """

    async def _process_query(client: CopilotClient, query: str) -> ReportResult:
        try:
            session_config = create_session_config(
                system_message=SystemMessageReplaceConfig(
                    mode="replace", content=system_prompt
                ),
            )
            session = await client.create_session(session_config)
            handler = create_event_handler(writer=writer)
            session.on(handler)

            reply = await session.send_and_wait(create_message_options(query))
            content = reply.data.content if reply else None
            return ReportResult(query=query, response=content)
        except Exception as e:
            return ReportResult(query=query, error=str(e))

    client = create_copilot_client(cli_url)
    await client.start()

    tasks = [_process_query(client, q) for q in queries]
    results = await asyncio.gather(*tasks)

    succeeded = sum(1 for r in results if r.response is not None)
    return ReportOutput(
        system_prompt=system_prompt,
        results=list(results),
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
    )
