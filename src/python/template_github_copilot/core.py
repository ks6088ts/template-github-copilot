from collections.abc import Callable
from typing import Any, TypedDict

import typer
from copilot import (
    CopilotClient,
    ExternalServerConfig,
    SubprocessConfig,
)
from copilot.generated.session_events import (
    PermissionRequest,
    SessionEventType,
)
from copilot.session import (
    PermissionRequestResult,
    SessionConfig,
    SystemMessageAppendConfig,
    SystemMessageConfig,
)
from copilot.tools import Tool

from template_github_copilot.tools import get_custom_tools


class MessageOptions(TypedDict):
    """Options for a single chat message.

    Retained as a thin abstraction over the Copilot SDK (which now takes a
    plain ``prompt`` string) so downstream callers can pass a structured
    object and keep room for additional fields in the future.
    """

    prompt: str


# Type alias for the writer function used by the event handler
WriterFunc = Callable[[str], Any]


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


def create_copilot_client(
    cli_url: str = "",
    github_token: str | None = None,
) -> CopilotClient:
    """Factory function that creates a CopilotClient.

    The Copilot SDK does **not** allow ``cli_url`` and ``github_token`` to be
    set simultaneously.  When ``cli_url`` is provided (non-empty) the client
    connects to an *external* Copilot CLI server (which manages its own
    authentication) – this is the mode used in Docker Compose.

    When ``cli_url`` is empty and ``github_token`` is given, the SDK spawns a
    *local* Copilot CLI subprocess authenticated with the token.

    Args:
        cli_url: The URL of an external Copilot CLI server
            (e.g. ``"copilot:3000"`` in Docker Compose or
            ``"localhost:3000"`` for local development).
        github_token: Optional GitHub OAuth token. Used only when
            *cli_url* is empty.

    Returns:
        A configured ``CopilotClient`` instance.
    """
    if cli_url:
        return CopilotClient(
            ExternalServerConfig(url=cli_url),
        )
    if github_token:
        return CopilotClient(
            SubprocessConfig(
                github_token=github_token,
                use_logged_in_user=False,
            ),
        )
    return CopilotClient(
        ExternalServerConfig(url="localhost:3000"),
    )


def create_session_config(
    on_permission_request: Callable[
        [PermissionRequest, dict[str, str]], PermissionRequestResult
    ] = approve_all,
    system_message: SystemMessageConfig | None = _get_system_message(),
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


async def send_and_wait(
    session: Any,
    options: MessageOptions,
    timeout: float | None = None,
) -> Any:
    """Wrapper around ``session.send_and_wait`` with a configurable default timeout.

    The timeout defaults to the ``COPILOT_SEND_TIMEOUT`` environment variable
    (loaded via project settings). Callers can still override it per-call.

    Args:
        session: A Copilot session object.
        options: Message options to send.
        timeout: Optional override for the timeout in seconds.
            When ``None``, uses ``Settings.copilot_send_timeout`` (default 300s).

    Returns:
        The response event from ``session.send_and_wait``.
    """
    if timeout is None:
        from template_github_copilot.settings.copilot import get_copilot_settings

        timeout = get_copilot_settings().copilot_send_timeout
    return await session.send_and_wait(options["prompt"], timeout=timeout)


async def create_session(
    client: CopilotClient,
    config: SessionConfig,
) -> Any:
    """Create a new Copilot session from a :class:`SessionConfig` mapping.

    The underlying SDK exposes ``CopilotClient.create_session`` as a
    keyword-only method, so this helper unpacks the ``SessionConfig`` dict
    into keyword arguments.
    """
    return await client.create_session(**config)
