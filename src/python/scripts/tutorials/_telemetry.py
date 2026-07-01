#!/usr/bin/env python3
"""Shared OpenTelemetry helper for the Copilot SDK tutorial scripts.

Enabling telemetry is opt-in via CLI options or environment variables, so every
tutorial behaves exactly as before unless a collector endpoint is configured:

    OTEL_EXPORTER_OTLP_ENDPOINT
        OTLP HTTP endpoint (e.g. http://localhost:4318). When unset, telemetry
        is disabled and ``make_client`` returns a plain client.
    OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT
        Optional bool ("1", "true", "yes", ...) to capture prompt/response
        content in spans.
    OTEL_BSP_SCHEDULE_DELAY
        Optional span batch flush interval in milliseconds.

Spin up a local collector + Grafana stack with::

    docker compose -f docker/compose.yaml up -d
    uv run python scripts/tutorials/01_chat_bot.py \
        --otel-endpoint http://localhost:4318 \
        --otel-bsp-schedule-delay 500

See: docs/copilot_sdk_tutorial/observability.md
https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry
"""

import argparse
import os

from copilot import (
    CopilotClient,
    RuntimeConnection,
    TelemetryConfig,
)

_OTEL_ENDPOINT_ENV = "OTEL_EXPORTER_OTLP_ENDPOINT"
_OTEL_CAPTURE_CONTENT_ENV = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
_OTEL_BSP_SCHEDULE_DELAY_ENV = "OTEL_BSP_SCHEDULE_DELAY"
_TRUTHY = {"1", "true", "yes", "on", "y", "t"}
_FALSEY = {"0", "false", "no", "off", "n", "f"}
_BOOL_CHOICES = sorted(_TRUTHY | _FALSEY)


def add_telemetry_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared OpenTelemetry options to a tutorial script parser."""
    group = parser.add_argument_group("observability")
    group.add_argument(
        "--otel-endpoint",
        default=None,
        help=(
            "Optional OTLP HTTP endpoint for tutorial telemetry "
            f"(also reads {_OTEL_ENDPOINT_ENV}). When empty, telemetry is disabled."
        ),
    )
    group.add_argument(
        "--otel-capture-content",
        choices=_BOOL_CHOICES,
        default=None,
        type=str.lower,
        help=(
            "Optional true/false value to capture prompt and response content "
            f"in spans (also reads {_OTEL_CAPTURE_CONTENT_ENV})."
        ),
    )
    group.add_argument(
        "--otel-bsp-schedule-delay",
        default=None,
        type=int,
        help=(
            "Optional span batch flush interval in milliseconds "
            f"(sets {_OTEL_BSP_SCHEDULE_DELAY_ENV} for the launched Copilot CLI)."
        ),
    )


def apply_telemetry_arguments(args: argparse.Namespace) -> None:
    """Apply explicit OpenTelemetry CLI options to the process environment."""
    endpoint = getattr(args, "otel_endpoint", None)
    if endpoint:
        os.environ[_OTEL_ENDPOINT_ENV] = endpoint

    capture_content = getattr(args, "otel_capture_content", None)
    if capture_content is not None:
        os.environ[_OTEL_CAPTURE_CONTENT_ENV] = capture_content

    bsp_schedule_delay = getattr(args, "otel_bsp_schedule_delay", None)
    if bsp_schedule_delay is not None:
        os.environ[_OTEL_BSP_SCHEDULE_DELAY_ENV] = str(bsp_schedule_delay)


def telemetry_config() -> TelemetryConfig | None:
    """Build a ``TelemetryConfig`` from environment variables.

    Returns ``None`` (telemetry disabled) when ``OTEL_EXPORTER_OTLP_ENDPOINT``
    is not set.
    """
    endpoint = os.environ.get(_OTEL_ENDPOINT_ENV)
    if not endpoint:
        return None

    config: TelemetryConfig = {
        "otlp_endpoint": endpoint,
        "exporter_type": "otlp-http",
    }

    capture = os.environ.get(_OTEL_CAPTURE_CONTENT_ENV)
    if capture is not None:
        config["capture_content"] = capture.strip().lower() in _TRUTHY

    return config


def make_client(cli_url: str | None) -> CopilotClient:
    """Create a ``CopilotClient`` with optional telemetry and connection.

    When ``cli_url`` is provided the client connects to an already-running
    Copilot CLI runtime; otherwise the SDK launches the bundled CLI over stdio.
    Telemetry is attached automatically when configured via the environment.
    """
    kwargs: dict = {}
    if cli_url:
        kwargs["connection"] = RuntimeConnection.for_uri(cli_url)

    telemetry = telemetry_config()
    if telemetry is not None:
        kwargs["telemetry"] = telemetry

    return CopilotClient(**kwargs)
