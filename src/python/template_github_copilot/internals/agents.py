from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """Information about an agent."""

    agent_id: str = Field(..., description="The ID of the agent.")
    name: str = Field("", description="The name of the agent.")
    model: str = Field("", description="The model used by the agent.")
    instructions: str = Field("", description="The instructions for the agent.")
    version: str = Field("", description="The version of the agent.")


class AgentRunResult(BaseModel):
    """Result of running an agent."""

    agent_name: str = Field(..., description="The name of the agent used.")
    conversation_id: str = Field("", description="The ID of the conversation.")
    output_text: str = Field("", description="The assistant's response text.")
    error: str | None = Field(None, description="Error message if the run failed.")


class AgentListOutput(BaseModel):
    """Structured output for listing agents."""

    agents: list[AgentInfo] = Field(default_factory=list, description="List of agents.")
    total: int = Field(0, description="Total number of agents.")


def create_project_client(endpoint: str) -> AIProjectClient:
    """Create an AIProjectClient with DefaultAzureCredential.

    Args:
        endpoint: The Microsoft Foundry project endpoint.

    Returns:
        An authenticated AIProjectClient instance.
    """
    return AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )


def create_agent(
    client: AIProjectClient,
    model: str,
    name: str,
    instructions: str,
) -> AgentInfo:
    """Create a new agent version.

    Args:
        client: The AIProjectClient instance.
        model: The model to use (e.g. "gpt-4o").
        name: The name of the agent.
        instructions: The system instructions for the agent.

    Returns:
        AgentInfo with the created agent details.
    """
    agent = client.agents.create_version(
        agent_name=name,
        definition=PromptAgentDefinition(
            model=model,
            instructions=instructions,
        ),
    )
    return AgentInfo(
        agent_id=agent.id,
        name=agent.name or "",
        model=model,
        instructions=instructions,
        version=getattr(agent, "version", ""),
    )


def _extract_agent_info(agent: object) -> AgentInfo:
    """Extract AgentInfo from an AgentDetails object.

    The Azure AI Foundry SDK returns agent details with model, instructions,
    and version nested under ``versions.latest.definition``.

    Args:
        agent: An AgentDetails object returned by the SDK.

    Returns:
        AgentInfo populated from the nested structure.
    """
    model = ""
    instructions = ""
    version = ""
    versions = getattr(agent, "versions", None)
    if versions:
        latest = (
            versions.get("latest")
            if isinstance(versions, dict)
            else getattr(versions, "latest", None)
        )
        if latest:
            definition = (
                latest.get("definition")
                if isinstance(latest, dict)
                else getattr(latest, "definition", None)
            )
            if definition:
                model = (
                    definition.get("model")
                    if isinstance(definition, dict)
                    else getattr(definition, "model", "")
                ) or ""
                instructions = (
                    definition.get("instructions")
                    if isinstance(definition, dict)
                    else getattr(definition, "instructions", "")
                ) or ""
            version = (
                latest.get("version")
                if isinstance(latest, dict)
                else getattr(latest, "version", "")
            ) or ""
    return AgentInfo(
        agent_id=getattr(agent, "id", ""),
        name=getattr(agent, "name", "") or "",
        model=model,
        instructions=instructions,
        version=version,
    )


def get_agent(client: AIProjectClient, agent_name: str) -> AgentInfo:
    """Get an agent by name.

    Args:
        client: The AIProjectClient instance.
        agent_name: The name of the agent to retrieve.

    Returns:
        AgentInfo with the agent details.
    """
    agent = client.agents.get(agent_name=agent_name)
    return _extract_agent_info(agent)


def list_agents(client: AIProjectClient) -> AgentListOutput:
    """List all agents.

    Args:
        client: The AIProjectClient instance.

    Returns:
        AgentListOutput with all agents.
    """
    agent_infos = [_extract_agent_info(a) for a in client.agents.list()]
    return AgentListOutput(agents=agent_infos, total=len(agent_infos))


def delete_agent(client: AIProjectClient, agent_name: str) -> None:
    """Delete an agent by name.

    Args:
        client: The AIProjectClient instance.
        agent_name: The name of the agent to delete.
    """
    client.agents.delete(agent_name=agent_name)


def run_agent(
    client: AIProjectClient,
    agent_name: str,
    user_message: str,
    conversation_id: str | None = None,
) -> AgentRunResult:
    """Run an agent with a user message.

    Creates a conversation (if not provided), sends the user message
    to the agent via the OpenAI client, and returns the response.

    Args:
        client: The AIProjectClient instance.
        agent_name: The name of the agent to run.
        user_message: The user message to send.
        conversation_id: Optional existing conversation ID for multi-turn.

    Returns:
        AgentRunResult with the response details.
    """
    try:
        # The get_openai_client method is added by azure.ai.projects._patch at runtime
        openai_client = client.get_openai_client()  # type: ignore[unresolved-attribute]  # ty: ignore[unresolved-attribute]

        if conversation_id is None:
            conversation = openai_client.conversations.create()
            conversation_id = conversation.id

        response = openai_client.responses.create(
            conversation=conversation_id,
            extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
            input=user_message,
        )

        return AgentRunResult(
            agent_name=agent_name,
            conversation_id=conversation_id,
            output_text=response.output_text,
        )
    except Exception as e:
        return AgentRunResult(
            agent_name=agent_name,
            conversation_id=conversation_id or "",
            error=str(e),
        )
