from copilot.types import Tool

from template_github_copilot.tools.foundry_agent import (
    call_foundry_agent,
    list_foundry_agents,
)


def get_custom_tools() -> list[Tool]:
    """Return the list of all registered custom tools."""
    return [
        list_foundry_agents,
        call_foundry_agent,
    ]


__all__ = [
    "get_custom_tools",
    "list_foundry_agents",
    "call_foundry_agent",
]
