from pydantic import BaseModel, Field


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
