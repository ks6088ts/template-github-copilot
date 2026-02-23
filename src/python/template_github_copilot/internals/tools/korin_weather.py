from copilot.tools import define_tool
from pydantic import BaseModel, Field


class KorinLocation(BaseModel):
    """Pydantic model for the KORIN weather tool input."""

    city: str = Field("MOBARA", description="The city on KORIN to get the weather for.")


@define_tool(description="Get the weather forecast for KORIN planet.")
def get_korin_weather(location: KorinLocation) -> str:
    """Custom tool that returns a static weather forecast for KORIN."""
    return f"The weather on KORIN in {location.city} is sunny with a chance of meteor showers."
