from copilot.tools import define_tool
from pydantic import BaseModel, Field

from template_github_copilot.internals.agents import (
    AgentInfo,
    create_project_client,
    list_agents,
    run_agent,
)
from template_github_copilot.settings import get_microsoft_foundry_settings


# ---------------------------------------------------------------------------
# List agents
# ---------------------------------------------------------------------------


class FoundryListAgentsInput(BaseModel):
    """Pydantic model for the Foundry list-agents tool input."""

    endpoint: str = Field(
        "",
        description=(
            "The Microsoft Foundry project endpoint. "
            "Leave empty to use the default from environment variables."
        ),
    )


@define_tool(
    description=(
        "List all available agents on Microsoft Foundry. "
        "Use this tool to discover which agents are available "
        "before routing a user query to the appropriate agent."
    ),
)
def list_foundry_agents(params: FoundryListAgentsInput) -> str:
    """Return a formatted list of agents registered in Microsoft Foundry."""
    endpoint = (
        params.endpoint
        or get_microsoft_foundry_settings().microsoft_foundry_project_endpoint
    )
    client = create_project_client(endpoint)
    result = list_agents(client)

    if result.total == 0:
        return "No agents found on Microsoft Foundry."

    def _format_agent(agent: AgentInfo) -> str:
        parts = [f"- name: {agent.name}, id: {agent.agent_id}"]
        if agent.model:
            parts[0] += f", model: {agent.model}"
        if agent.instructions:
            parts[0] += f", instructions: {agent.instructions}"
        return parts[0]

    lines = [f"Found {result.total} agent(s):"]
    lines.extend(_format_agent(a) for a in result.agents)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Call agent
# ---------------------------------------------------------------------------


class FoundryCallAgentInput(BaseModel):
    """Pydantic model for the Foundry call-agent tool input."""

    agent_name: str = Field(
        ...,
        description="The name of the Microsoft Foundry agent to invoke.",
    )
    user_message: str = Field(
        ...,
        description="The user message to send to the agent.",
    )
    conversation_id: str = Field(
        "",
        description=(
            "Optional conversation ID for multi-turn dialogue. "
            "Leave empty to start a new conversation."
        ),
    )
    endpoint: str = Field(
        "",
        description=(
            "The Microsoft Foundry project endpoint. "
            "Leave empty to use the default from environment variables."
        ),
    )


@define_tool(
    description=(
        "Call a specified agent on Microsoft Foundry with a user message "
        "and return the agent's response."
    ),
)
def call_foundry_agent(params: FoundryCallAgentInput) -> str:
    """Invoke a Microsoft Foundry agent and return its response text."""
    endpoint = (
        params.endpoint
        or get_microsoft_foundry_settings().microsoft_foundry_project_endpoint
    )
    client = create_project_client(endpoint)
    result = run_agent(
        client=client,
        agent_name=params.agent_name,
        user_message=params.user_message,
        conversation_id=params.conversation_id or None,
    )

    if result.error:
        return f"Error calling agent '{result.agent_name}': {result.error}"

    return result.output_text
