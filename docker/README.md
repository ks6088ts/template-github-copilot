# Observability stack (OpenTelemetry Collector + Grafana LGTM)

A minimal, two-service Docker Compose stack for verifying the OpenTelemetry
traces emitted by the GitHub Copilot SDK tutorials (Go and Python).

```text
Copilot CLI ──OTLP/HTTP :4318──▶ otel-collector ──OTLP/gRPC :4317──▶ grafana-lgtm ──▶ Grafana UI :3000
```

| Service | Image | Purpose | Host ports |
|---------|-------|---------|------------|
| `otel-collector` | `otel/opentelemetry-collector-contrib` | Single OTLP ingest endpoint; forwards to Grafana LGTM | `4317` (gRPC), `4318` (HTTP) |
| `grafana-lgtm` | `grafana/otel-lgtm` | All-in-one Loki + Grafana + Tempo + Prometheus backend | `3000` (Grafana UI) |

## Quick start

```bash
# 1. Start the stack (from the repository root)
docker compose -f docker/compose.yaml up -d

# 2. Point the tutorials at the collector (standard OTel env var)
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
# Flush spans quickly: the SDK kills the CLI after a single prompt, so the
# default 5s batch interval would lose spans. Keep this low.
export OTEL_BSP_SCHEDULE_DELAY=500
# Optional: capture prompt/response content in spans
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true

# 3a. Run a Python tutorial
cd src/python && uv run python scripts/tutorials/01_chat_bot.py --prompt "Hello!"

# 3b. ...or a Go tutorial
cd src/go && make build && ./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello!"

# 4. Explore traces in Grafana → Explore → Tempo data source
open http://localhost:3000   # login: admin / admin

# 5. Tear down
docker compose -f docker/compose.yaml down
```

## How telemetry is wired

Both tutorial suites enable telemetry only when `OTEL_EXPORTER_OTLP_ENDPOINT`
is set, so they behave exactly as before when the stack is not running.

- **Python**: `src/python/scripts/tutorials/_telemetry.py` builds a
  `TelemetryConfig` and is used by every `NN_*.py` script via `make_client()`.
- **Go**: `src/go/cmd/tutorial/telemetry.go` builds a `copilot.TelemetryConfig`
  and is wired into every `tutorial` subcommand via `newClientOptions()`.

The SDK passes the endpoint to the Copilot CLI process, which exports its
spans over OTLP. The collector then fans them out to Grafana LGTM.

## Verifying without Grafana

The collector also logs a summary via its `debug` exporter:

```bash
docker compose -f docker/compose.yaml logs -f otel-collector
```

You should see `TracesExporter` / spans activity once a tutorial runs.

## Troubleshooting: "no spans arrive"

When the SDK launches the CLI over **stdio** (the tutorial default), it
terminates the CLI with `SIGKILL` (`client.Stop()` → `process.Kill()`) as soon
as a single-shot prompt finishes. The CLI's OTLP exporter batches spans and
flushes on an interval whose **default is 5 seconds**, so a short prompt is
killed long before the first flush and **no spans are ever sent**.

Fixes (either works):

- **Lower the flush interval** (simplest) — set the standard OTel env var so the
  CLI flushes before it is killed:

  ```bash
  export OTEL_BSP_SCHEDULE_DELAY=500   # milliseconds
  ```

- **Use server mode** — run the CLI as a persistent server and connect the
  tutorial with `--cli-url`. The process stays alive and flushes normally. See
  [CLI Server Mode](../docs/copilot_sdk_tutorial/server_mode.md).

A direct `copilot -p "..."` run always works because that process exits
gracefully and flushes on shutdown.

## References

- [OpenTelemetry instrumentation for Copilot SDK](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry)
- [grafana/otel-lgtm](https://github.com/grafana/docker-otel-lgtm)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
