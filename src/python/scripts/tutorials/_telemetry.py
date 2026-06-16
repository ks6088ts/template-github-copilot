#!/usr/bin/env python3
"""Shared OpenTelemetry helper for the Copilot SDK tutorial scripts.

Enabling telemetry is opt-in via environment variables, so every tutorial
behaves exactly as before unless a collector endpoint is configured:

    OTEL_EXPORTER_OTLP_ENDPOINT
        OTLP HTTP endpoint (e.g. http://localhost:4318). When unset, telemetry
        is disabled and ``make_client`` returns a plain client.
    OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT
        Optional bool ("1", "true", "yes", ...) to capture prompt/response
        content in spans.

Spin up a local collector + Grafana stack with::

    docker compose -f docker/compose.yaml up -d
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

See: docs/copilot_sdk_tutorial/observability.md
https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry
"""

import os

from copilot import (
    CopilotClient,
    RuntimeConnection,
    TelemetryConfig,
)

_TRUTHY = {"1", "true", "yes", "on", "y", "t"}


def telemetry_config() -> TelemetryConfig | None:
    """Build a ``TelemetryConfig`` from environment variables.

    Returns ``None`` (telemetry disabled) when ``OTEL_EXPORTER_OTLP_ENDPOINT``
    is not set.
    """
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return None

    config: TelemetryConfig = {
        "otlp_endpoint": endpoint,
        "exporter_type": "otlp-http",
    }

    capture = os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
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
