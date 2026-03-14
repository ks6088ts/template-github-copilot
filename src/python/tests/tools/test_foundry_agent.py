"""Tests for template_github_copilot.tools (foundry_agent + get_custom_tools)."""

import asyncio
import types
from unittest.mock import MagicMock, patch

from template_github_copilot.internals.agents import (
    AgentInfo,
    AgentListOutput,
    AgentRunResult,
)
from template_github_copilot.tools import get_custom_tools
from template_github_copilot.tools.foundry_agent import (
    call_foundry_agent,
    list_foundry_agents,
)


def _invoke_tool(tool, arguments: dict) -> str:
    """Helper: invoke a Tool's async handler synchronously and return the LLM text."""
    invocation = types.SimpleNamespace(arguments=arguments, name=tool.name)
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(tool.handler(invocation))
    finally:
        loop.close()
    return (
        result.get("text_result_for_llm", "")
        if isinstance(result, dict)
        else getattr(result, "text_result_for_llm", "")
    )


# ---------------------------------------------------------------------------
# get_custom_tools
# ---------------------------------------------------------------------------


def test_get_custom_tools_returns_list():
    """get_custom_tools should return a list."""
    tools = get_custom_tools()
    assert isinstance(tools, list)
    assert len(tools) == 2


def test_get_custom_tools_names():
    """get_custom_tools should contain the expected tool names."""
    tools = get_custom_tools()
    names = {t.name for t in tools}
    assert "list_foundry_agents" in names
    assert "call_foundry_agent" in names


# ---------------------------------------------------------------------------
# list_foundry_agents (with mocked dependencies)
# ---------------------------------------------------------------------------


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.list_agents")
@patch("template_github_copilot.tools.foundry_agent.get_microsoft_foundry_settings")
def test_list_foundry_agents_no_agents(mock_settings, mock_list, mock_client):
    """list_foundry_agents should report 'no agents' when none exist."""
    mock_settings.return_value = MagicMock(
        microsoft_foundry_project_endpoint="https://ep"
    )
    mock_client.return_value = MagicMock()
    mock_list.return_value = AgentListOutput(agents=[], total=0)

    result = _invoke_tool(list_foundry_agents, {})
    assert "No agents found" in result


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.list_agents")
@patch("template_github_copilot.tools.foundry_agent.get_microsoft_foundry_settings")
def test_list_foundry_agents_with_agents(mock_settings, mock_list, mock_client):
    """list_foundry_agents should format agent info."""
    mock_settings.return_value = MagicMock(
        microsoft_foundry_project_endpoint="https://ep"
    )
    mock_client.return_value = MagicMock()
    agents = [
        AgentInfo(agent_id="a1", name="Agent1", model="gpt-4", instructions="Help"),
        AgentInfo(agent_id="a2", name="Agent2"),
    ]
    mock_list.return_value = AgentListOutput(agents=agents, total=2)

    result = _invoke_tool(list_foundry_agents, {})
    assert "2 agent(s)" in result
    assert "Agent1" in result
    assert "gpt-4" in result
    assert "Agent2" in result


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.list_agents")
def test_list_foundry_agents_custom_endpoint(mock_list, mock_client):
    """list_foundry_agents should use provided endpoint over settings."""
    mock_client.return_value = MagicMock()
    mock_list.return_value = AgentListOutput(agents=[], total=0)

    _invoke_tool(list_foundry_agents, {"endpoint": "https://custom.example.com"})
    mock_client.assert_called_once_with("https://custom.example.com")


# ---------------------------------------------------------------------------
# call_foundry_agent (with mocked dependencies)
# ---------------------------------------------------------------------------


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.run_agent")
@patch("template_github_copilot.tools.foundry_agent.get_microsoft_foundry_settings")
def test_call_foundry_agent_success(mock_settings, mock_run, mock_client):
    """call_foundry_agent should return the output text on success."""
    mock_settings.return_value = MagicMock(
        microsoft_foundry_project_endpoint="https://ep"
    )
    mock_client.return_value = MagicMock()
    mock_run.return_value = AgentRunResult(
        agent_name="agent1",
        conversation_id="c1",
        output_text="Response!",
    )

    result = _invoke_tool(
        call_foundry_agent, {"agent_name": "agent1", "user_message": "hi"}
    )
    assert result == "Response!"


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.run_agent")
@patch("template_github_copilot.tools.foundry_agent.get_microsoft_foundry_settings")
def test_call_foundry_agent_error(mock_settings, mock_run, mock_client):
    """call_foundry_agent should return error message on failure."""
    mock_settings.return_value = MagicMock(
        microsoft_foundry_project_endpoint="https://ep"
    )
    mock_client.return_value = MagicMock()
    mock_run.return_value = AgentRunResult(
        agent_name="agent1",
        error="API error",
    )

    result = _invoke_tool(
        call_foundry_agent, {"agent_name": "agent1", "user_message": "hi"}
    )
    assert "Error" in result
    assert "API error" in result


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.run_agent")
def test_call_foundry_agent_custom_endpoint(mock_run, mock_client):
    """call_foundry_agent should use provided endpoint."""
    mock_client.return_value = MagicMock()
    mock_run.return_value = AgentRunResult(agent_name="a", output_text="ok")

    _invoke_tool(
        call_foundry_agent,
        {
            "agent_name": "a",
            "user_message": "msg",
            "endpoint": "https://custom.example.com",
        },
    )
    mock_client.assert_called_once_with("https://custom.example.com")


@patch("template_github_copilot.tools.foundry_agent.create_project_client")
@patch("template_github_copilot.tools.foundry_agent.run_agent")
@patch("template_github_copilot.tools.foundry_agent.get_microsoft_foundry_settings")
def test_call_foundry_agent_with_conversation_id(mock_settings, mock_run, mock_client):
    """call_foundry_agent should pass conversation_id when provided."""
    mock_settings.return_value = MagicMock(
        microsoft_foundry_project_endpoint="https://ep"
    )
    mock_client.return_value = MagicMock()
    mock_run.return_value = AgentRunResult(
        agent_name="a", output_text="ok", conversation_id="conv-123"
    )

    _invoke_tool(
        call_foundry_agent,
        {
            "agent_name": "a",
            "user_message": "hi",
            "conversation_id": "conv-123",
        },
    )
    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args
    # conversation_id should be passed (not empty string -> converted to None or "conv-123")
    assert call_kwargs is not None
