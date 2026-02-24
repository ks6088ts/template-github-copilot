"""Tests for template_github_copilot.services.reports (Pydantic models + async)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from template_github_copilot.services.reports import (
    ReportOutput,
    run_parallel_chat,
)


# ---------------------------------------------------------------------------
# run_parallel_chat (async)
# ---------------------------------------------------------------------------


def _make_mock_reply(content: str):
    """Create a mock reply object with data.content."""
    reply = MagicMock()
    reply.data.content = content
    return reply


@patch("template_github_copilot.services.reports.create_copilot_client")
def test_run_parallel_chat_success(mock_create_client):
    """run_parallel_chat should return results for all queries."""
    mock_client = AsyncMock()
    mock_create_client.return_value = mock_client

    mock_session = AsyncMock()
    mock_client.create_session = AsyncMock(return_value=mock_session)

    mock_reply = _make_mock_reply("answer")
    mock_session.send_and_wait = AsyncMock(return_value=mock_reply)

    writer = MagicMock()
    output = asyncio.run(
        run_parallel_chat(
            cli_url="http://localhost:8080",
            queries=["q1", "q2"],
            system_prompt="Be helpful",
            writer=writer,
        )
    )

    assert isinstance(output, ReportOutput)
    assert output.total == 2
    assert output.succeeded == 2
    assert output.failed == 0
    assert output.system_prompt == "Be helpful"
    assert all(r.response == "answer" for r in output.results)


@patch("template_github_copilot.services.reports.create_copilot_client")
def test_run_parallel_chat_empty_queries(mock_create_client):
    """run_parallel_chat should handle empty query list."""
    mock_client = AsyncMock()
    mock_create_client.return_value = mock_client

    output = asyncio.run(
        run_parallel_chat(
            cli_url="http://localhost:8080",
            queries=[],
            system_prompt="prompt",
        )
    )

    assert output.total == 0
    assert output.succeeded == 0
    assert output.failed == 0


@patch("template_github_copilot.services.reports.create_copilot_client")
def test_run_parallel_chat_with_error(mock_create_client):
    """run_parallel_chat should capture errors per query."""
    mock_client = AsyncMock()
    mock_create_client.return_value = mock_client

    mock_session = AsyncMock()
    mock_client.create_session = AsyncMock(return_value=mock_session)
    mock_session.send_and_wait = AsyncMock(side_effect=Exception("timeout"))

    output = asyncio.run(
        run_parallel_chat(
            cli_url="http://localhost:8080",
            queries=["q1"],
            system_prompt="prompt",
        )
    )

    assert output.total == 1
    assert output.failed == 1
    assert output.succeeded == 0
    assert output.results[0].error == "timeout"


@patch("template_github_copilot.services.reports.create_copilot_client")
def test_run_parallel_chat_no_reply(mock_create_client):
    """run_parallel_chat should handle None reply."""
    mock_client = AsyncMock()
    mock_create_client.return_value = mock_client

    mock_session = AsyncMock()
    mock_client.create_session = AsyncMock(return_value=mock_session)
    mock_session.send_and_wait = AsyncMock(return_value=None)

    output = asyncio.run(
        run_parallel_chat(
            cli_url="http://localhost:8080",
            queries=["q1"],
            system_prompt="prompt",
        )
    )

    assert output.total == 1
    assert output.results[0].response is None
    assert output.failed == 1


@patch("template_github_copilot.services.reports.create_copilot_client")
def test_run_parallel_chat_mixed_results(mock_create_client):
    """run_parallel_chat should handle mix of success and failure."""
    mock_client = AsyncMock()
    mock_create_client.return_value = mock_client

    call_count = 0

    async def create_session_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        session = AsyncMock()
        if call_count % 2 == 0:
            session.send_and_wait = AsyncMock(side_effect=Exception("error"))
        else:
            reply = _make_mock_reply("ok")
            session.send_and_wait = AsyncMock(return_value=reply)
        return session

    mock_client.create_session = AsyncMock(side_effect=create_session_side_effect)

    output = asyncio.run(
        run_parallel_chat(
            cli_url="http://localhost:8080",
            queries=["a", "b", "c"],
            system_prompt="p",
        )
    )

    assert output.total == 3
    assert output.succeeded + output.failed == 3
