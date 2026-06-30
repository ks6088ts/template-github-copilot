import argparse

from scripts.tutorials._telemetry import (
    add_telemetry_arguments,
    apply_telemetry_arguments,
    telemetry_config,
)


def test_telemetry_config_disabled_without_endpoint(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.delenv(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", raising=False
    )

    assert telemetry_config() is None


def test_apply_telemetry_arguments_enables_config(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.delenv(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", raising=False
    )
    monkeypatch.delenv("OTEL_BSP_SCHEDULE_DELAY", raising=False)

    parser = argparse.ArgumentParser()
    add_telemetry_arguments(parser)
    args = parser.parse_args(
        [
            "--otel-endpoint",
            "http://localhost:4318",
            "--otel-capture-content",
            "true",
            "--otel-bsp-schedule-delay",
            "500",
        ]
    )

    apply_telemetry_arguments(args)
    config = telemetry_config()

    assert config == {
        "otlp_endpoint": "http://localhost:4318",
        "exporter_type": "otlp-http",
        "capture_content": True,
    }
    assert args.otel_bsp_schedule_delay == 500
