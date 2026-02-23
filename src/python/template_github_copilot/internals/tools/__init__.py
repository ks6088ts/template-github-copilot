from copilot.types import Tool

from template_github_copilot.internals.tools.korin_weather import get_korin_weather


def get_custom_tools() -> list[Tool]:
    """Return the list of all registered custom tools."""
    return [
        get_korin_weather,
    ]


__all__ = [
    "get_custom_tools",
    "get_korin_weather",
]
