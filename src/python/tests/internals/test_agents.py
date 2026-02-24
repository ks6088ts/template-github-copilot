"""Tests for template_github_copilot.internals.agents (Pydantic models + helpers)."""

import types
from unittest.mock import MagicMock, patch

from template_github_copilot.internals.agents import (
    _extract_agent_info,
    create_agent,
    create_project_client,
    delete_agent,
    get_agent,
    list_agents,
    run_agent,
)


# ---------------------------------------------------------------------------
# _extract_agent_info helper
# ---------------------------------------------------------------------------


def test_extract_agent_info_with_dict_versions():
    """_extract_agent_info should handle dict-based 'versions' attribute."""
    agent = types.SimpleNamespace(
        id="agent-id",
        name="agent-name",
        versions={
            "latest": {
                "definition": {
                    "model": "gpt-4",
                    "instructions": "Do things.",
                },
                "version": "2.0",
            },
        },
    )
    info = _extract_agent_info(agent)
    assert info.agent_id == "agent-id"
    assert info.name == "agent-name"
    assert info.model == "gpt-4"
    assert info.instructions == "Do things."
    assert info.version == "2.0"


def test_extract_agent_info_with_namespace_versions():
    """_extract_agent_info should handle namespace-based 'versions' attribute."""
    definition = types.SimpleNamespace(model="gpt-3.5", instructions="Help")
    latest = types.SimpleNamespace(definition=definition, version="1.0")
    versions = types.SimpleNamespace(latest=latest)
    agent = types.SimpleNamespace(id="id2", name="ns-agent", versions=versions)

    info = _extract_agent_info(agent)
    assert info.model == "gpt-3.5"
    assert info.instructions == "Help"
    assert info.version == "1.0"


def test_extract_agent_info_no_versions():
    """_extract_agent_info should handle missing versions gracefully."""
    agent = types.SimpleNamespace(id="id3", name="no-versions")
    info = _extract_agent_info(agent)
    assert info.agent_id == "id3"
    assert info.name == "no-versions"
    assert info.model == ""
    assert info.instructions == ""
    assert info.version == ""


def test_extract_agent_info_empty_versions():
    """_extract_agent_info should handle versions with no latest."""
    agent = types.SimpleNamespace(id="id4", name="empty-ver", versions={})
    info = _extract_agent_info(agent)
    assert info.model == ""
    assert info.version == ""


def test_extract_agent_info_latest_no_definition():
    """_extract_agent_info should handle latest entry without definition."""
    agent = types.SimpleNamespace(
        id="id5",
        name="no-def",
        versions={"latest": {"version": "3.0"}},
    )
    info = _extract_agent_info(agent)
    assert info.version == "3.0"
    assert info.model == ""


# ---------------------------------------------------------------------------
# create_project_client
# ---------------------------------------------------------------------------


@patch("template_github_copilot.internals.agents.DefaultAzureCredential")
@patch("template_github_copilot.internals.agents.AIProjectClient")
def test_create_project_client(mock_client_cls, mock_cred_cls):
    """create_project_client should create an AIProjectClient."""
    mock_cred = MagicMock()
    mock_cred_cls.return_value = mock_cred
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    result = create_project_client("https://endpoint.example.com")

    mock_client_cls.assert_called_once_with(
        endpoint="https://endpoint.example.com",
        credential=mock_cred,
    )
    assert result is mock_client


# ---------------------------------------------------------------------------
# create_agent
# ---------------------------------------------------------------------------


def test_create_agent():
    """create_agent should call client.agents.create_version and return AgentInfo."""
    mock_client = MagicMock()
    mock_agent = types.SimpleNamespace(
        id="new-agent-id",
        name="my-agent",
        version="1.0",
    )
    mock_client.agents.create_version.return_value = mock_agent

    info = create_agent(
        client=mock_client,
        model="gpt-4o",
        name="my-agent",
        instructions="Be useful",
    )

    mock_client.agents.create_version.assert_called_once()
    assert info.agent_id == "new-agent-id"
    assert info.name == "my-agent"
    assert info.model == "gpt-4o"
    assert info.instructions == "Be useful"
    assert info.version == "1.0"


def test_create_agent_no_version():
    """create_agent handles agent objects without a version attribute."""
    mock_client = MagicMock()
    mock_agent = types.SimpleNamespace(
        id="agent-no-ver",
        name="agent-x",
    )
    mock_client.agents.create_version.return_value = mock_agent

    info = create_agent(
        client=mock_client,
        model="gpt-3.5",
        name="agent-x",
        instructions="Do stuff",
    )

    assert info.agent_id == "agent-no-ver"
    assert info.version == ""


# ---------------------------------------------------------------------------
# get_agent
# ---------------------------------------------------------------------------


def test_get_agent():
    """get_agent should call client.agents.get and return AgentInfo."""
    mock_client = MagicMock()
    mock_agent = types.SimpleNamespace(
        id="ga-id",
        name="ga-name",
        versions={
            "latest": {
                "definition": {
                    "model": "gpt-4",
                    "instructions": "inst",
                },
                "version": "5.0",
            }
        },
    )
    mock_client.agents.get.return_value = mock_agent

    info = get_agent(mock_client, "ga-name")

    mock_client.agents.get.assert_called_once_with(agent_name="ga-name")
    assert info.agent_id == "ga-id"
    assert info.model == "gpt-4"
    assert info.version == "5.0"


# ---------------------------------------------------------------------------
# list_agents
# ---------------------------------------------------------------------------


def test_list_agents():
    """list_agents should call client.agents.list and return AgentListOutput."""
    mock_client = MagicMock()
    agent1 = types.SimpleNamespace(id="a1", name="agent-1", versions={})
    agent2 = types.SimpleNamespace(id="a2", name="agent-2", versions={})
    mock_client.agents.list.return_value = [agent1, agent2]

    output = list_agents(mock_client)

    mock_client.agents.list.assert_called_once()
    assert output.total == 2
    assert len(output.agents) == 2
    assert output.agents[0].agent_id == "a1"
    assert output.agents[1].agent_id == "a2"


def test_list_agents_empty():
    """list_agents should handle empty list."""
    mock_client = MagicMock()
    mock_client.agents.list.return_value = []

    output = list_agents(mock_client)

    assert output.total == 0
    assert output.agents == []


# ---------------------------------------------------------------------------
# delete_agent
# ---------------------------------------------------------------------------


def test_delete_agent():
    """delete_agent should call client.agents.delete."""
    mock_client = MagicMock()
    delete_agent(mock_client, "agent-to-delete")
    mock_client.agents.delete.assert_called_once_with(agent_name="agent-to-delete")


# ---------------------------------------------------------------------------
# run_agent
# ---------------------------------------------------------------------------


def test_run_agent_success():
    """run_agent should create a conversation and return the response."""
    mock_client = MagicMock()
    mock_openai_client = MagicMock()
    mock_client.get_openai_client.return_value = mock_openai_client

    mock_conversation = MagicMock()
    mock_conversation.id = "conv-123"
    mock_openai_client.conversations.create.return_value = mock_conversation

    mock_response = MagicMock()
    mock_response.output_text = "Hello, world!"
    mock_openai_client.responses.create.return_value = mock_response

    result = run_agent(mock_client, "my-agent", "Hi there")

    assert result.agent_name == "my-agent"
    assert result.conversation_id == "conv-123"
    assert result.output_text == "Hello, world!"
    assert result.error is None

    mock_openai_client.responses.create.assert_called_once_with(
        conversation="conv-123",
        extra_body={"agent": {"name": "my-agent", "type": "agent_reference"}},
        input="Hi there",
    )


def test_run_agent_with_existing_conversation():
    """run_agent should reuse conversation_id when provided."""
    mock_client = MagicMock()
    mock_openai_client = MagicMock()
    mock_client.get_openai_client.return_value = mock_openai_client

    mock_response = MagicMock()
    mock_response.output_text = "Response text"
    mock_openai_client.responses.create.return_value = mock_response

    result = run_agent(mock_client, "agent", "msg", conversation_id="existing-conv")

    assert result.conversation_id == "existing-conv"
    assert result.output_text == "Response text"
    assert result.error is None
    # Should NOT create a new conversation
    mock_openai_client.conversations.create.assert_not_called()


def test_run_agent_error():
    """run_agent should catch exceptions and return an error result."""
    mock_client = MagicMock()
    mock_client.get_openai_client.side_effect = Exception("Connection failed")

    result = run_agent(mock_client, "agent", "msg")

    assert result.agent_name == "agent"
    assert result.error == "Connection failed"
    assert result.conversation_id == ""


def test_run_agent_error_with_conversation_id():
    """run_agent error preserves conversation_id when provided."""
    mock_client = MagicMock()
    mock_openai_client = MagicMock()
    mock_client.get_openai_client.return_value = mock_openai_client
    mock_openai_client.responses.create.side_effect = Exception("API error")

    mock_conversation = MagicMock()
    mock_conversation.id = "conv-456"
    mock_openai_client.conversations.create.return_value = mock_conversation

    result = run_agent(mock_client, "agent", "msg")

    assert result.error == "API error"
    assert result.conversation_id == "conv-456"
