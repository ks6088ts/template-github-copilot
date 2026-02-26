import asyncio

from copilot import CopilotClient
from copilot.types import ProviderConfig, SystemMessageReplaceConfig
from pydantic import BaseModel, Field

from template_github_copilot.core import (
    WriterFunc,
    _default_writer,
    create_copilot_client,
    create_event_handler,
    create_message_options,
    create_session_config,
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


async def run_parallel_chat(
    cli_url: str,
    queries: list[str],
    system_prompt: str,
    writer: WriterFunc = _default_writer,
    provider: ProviderConfig | None = None,
    model: str | None = None,
    github_token: str | None = None,
) -> ReportOutput:
    """Run multiple chat queries in parallel sessions and return structured results.

    Args:
        cli_url: The URL of the Copilot CLI server.
        queries: A list of user queries to send in parallel.
        system_prompt: The system prompt to configure each session.
        writer: A callable for logging messages.
        provider: Optional ``ProviderConfig`` for BYOK providers.
        model: Optional model identifier (e.g. ``"gpt-4o"``).
        github_token: Optional GitHub OAuth token. When provided, the client
            authenticates via this token instead of ``cli_url``.

    Returns:
        A ``ReportOutput`` containing all results.
    """

    async def _process_query(client: CopilotClient, query: str) -> ReportResult:
        try:
            extra_kwargs: dict = {}
            if provider is not None:
                extra_kwargs["provider"] = provider
            if model is not None:
                extra_kwargs["model"] = model
            session_config = create_session_config(
                system_message=SystemMessageReplaceConfig(
                    mode="replace", content=system_prompt
                ),
                **extra_kwargs,
            )
            session = await client.create_session(session_config)
            handler = create_event_handler(writer=writer)
            session.on(handler)

            reply = await session.send_and_wait(create_message_options(query))
            content = reply.data.content if reply else None
            return ReportResult(query=query, response=content)
        except Exception as e:
            return ReportResult(query=query, error=str(e))

    client = create_copilot_client(cli_url, github_token=github_token)
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
