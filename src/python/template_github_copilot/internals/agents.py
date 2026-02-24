from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThreadCreationOptions,
    MessageRole,
    MessageTextContent,
    RunStatus,
    ThreadMessageOptions,
    ThreadRun,
)
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """Information about an agent."""

    agent_id: str = Field(..., description="The ID of the agent.")
    name: str = Field("", description="The name of the agent.")
    model: str = Field("", description="The model used by the agent.")
    instructions: str = Field("", description="The instructions for the agent.")


class AgentRunResult(BaseModel):
    """Result of running an agent."""

    agent_id: str = Field(..., description="The ID of the agent used.")
    thread_id: str = Field(..., description="The ID of the thread.")
    run_id: str = Field(..., description="The ID of the run.")
    messages: list[str] = Field(
        default_factory=list, description="The assistant messages from the run."
    )
    error: str | None = Field(None, description="Error message if the run failed.")


class AgentListOutput(BaseModel):
    """Structured output for listing agents."""

    agents: list[AgentInfo] = Field(default_factory=list, description="List of agents.")
    total: int = Field(0, description="Total number of agents.")


def create_agents_client(endpoint: str) -> AgentsClient:
    """Create an AgentsClient with DefaultAzureCredential.

    Args:
        endpoint: The Microsoft Foundry project endpoint.

    Returns:
        An authenticated AgentsClient instance.
    """
    return AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )


def create_agent(
    client: AgentsClient,
    model: str,
    name: str,
    instructions: str,
) -> Agent:
    """Create a new agent.

    Args:
        client: The AgentsClient instance.
        model: The model to use (e.g. "gpt-4o").
        name: The name of the agent.
        instructions: The system instructions for the agent.

    Returns:
        The created Agent object.
    """
    return client.create_agent(
        model=model,
        name=name,
        instructions=instructions,
    )


def get_agent(client: AgentsClient, agent_id: str) -> Agent:
    """Get an agent by ID.

    Args:
        client: The AgentsClient instance.
        agent_id: The ID of the agent to retrieve.

    Returns:
        The Agent object.
    """
    return client.get_agent(agent_id=agent_id)


def list_agents(client: AgentsClient) -> AgentListOutput:
    """List all agents.

    Args:
        client: The AgentsClient instance.

    Returns:
        AgentListOutput with all agents.
    """
    agent_infos = [
        AgentInfo(
            agent_id=a.id,
            name=a.name or "",
            model=a.model,
            instructions=a.instructions or "",
        )
        for a in client.list_agents()
    ]
    return AgentListOutput(agents=agent_infos, total=len(agent_infos))


def delete_agent(client: AgentsClient, agent_id: str) -> None:
    """Delete an agent by ID.

    Args:
        client: The AgentsClient instance.
        agent_id: The ID of the agent to delete.
    """
    client.delete_agent(agent_id=agent_id)  # type: ignore[unresolved-attribute]


def run_agent(
    client: AgentsClient,
    agent_id: str,
    user_message: str,
) -> AgentRunResult:
    """Run an agent with a user message.

    Creates a thread with the user message, runs the agent to completion,
    and returns the assistant's response messages.

    Args:
        client: The AgentsClient instance.
        agent_id: The ID of the agent to run.
        user_message: The user message to send.

    Returns:
        AgentRunResult with the run details and assistant messages.
    """
    try:
        run: ThreadRun = client.create_thread_and_process_run(  # type: ignore[unresolved-attribute]
            agent_id=agent_id,
            thread=AgentThreadCreationOptions(
                messages=[
                    ThreadMessageOptions(
                        role=MessageRole.USER,
                        content=user_message,
                    ),
                ],
            ),
        )

        if run.status == RunStatus.FAILED:
            return AgentRunResult(
                agent_id=agent_id,
                thread_id=run.thread_id,
                run_id=run.id,
                error=f"Run failed: {run.last_error}",
            )

        messages = client.messages.list(thread_id=run.thread_id)
        assistant_messages = [
            content_part.text.value
            for msg in messages
            if msg.role == MessageRole.AGENT
            for content_part in msg.content
            if isinstance(content_part, MessageTextContent) and content_part.text
        ]

        return AgentRunResult(
            agent_id=agent_id,
            thread_id=run.thread_id,
            run_id=run.id,
            messages=assistant_messages,
        )
    except Exception as e:
        return AgentRunResult(
            agent_id=agent_id,
            thread_id="",
            run_id="",
            error=str(e),
        )
