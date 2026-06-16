# Observability with OpenTelemetry

The Copilot SDK can emit [OpenTelemetry](https://opentelemetry.io/) traces from
the underlying Copilot CLI. This page shows how to enable tracing in the **Go**
and **Python** tutorials and inspect the spans in Grafana using a minimal,
two-service Docker Compose stack.

Reference:
[OpenTelemetry instrumentation for Copilot SDK](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry).

---

## How it works

```text
Copilot CLI ──OTLP/HTTP :4318──▶ otel-collector ──OTLP/gRPC :4317──▶ grafana-lgtm ──▶ Grafana UI :3000
```

Telemetry is **opt-in via environment variables**, so the tutorials behave
exactly as before unless you configure an endpoint:

| Variable | Description |
|----------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP endpoint (e.g. `http://localhost:4318`). When unset, telemetry is disabled. |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | Optional `true`/`false` to capture prompt/response content in spans. |
| `OTEL_BSP_SCHEDULE_DELAY` | Span batch flush interval in ms. Keep low (e.g. `500`) — see [Troubleshooting](#troubleshooting-no-spans-arrive). |

The shared helpers that build the `TelemetryConfig`:

- **Python** — [`src/python/scripts/tutorials/_telemetry.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/_telemetry.py) (`make_client()`).
- **Go** — [`src/go/cmd/tutorial/telemetry.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/telemetry.go) (`newClientOptions()`).

---

## 1. Start the observability stack

All Docker assets live under [`docker/`](https://github.com/ks6088ts/template-github-copilot/tree/main/docker).

```bash
# from the repository root
docker compose -f docker/compose.yaml up -d
```

This launches two services:

| Service | Image | Host ports |
|---------|-------|------------|
| `otel-collector` | `otel/opentelemetry-collector-contrib` | `4317` (gRPC), `4318` (HTTP) |
| `grafana-lgtm` | `grafana/otel-lgtm` (Loki + Grafana + Tempo + Prometheus) | `3000` (Grafana UI) |

---

## 2. Point the tutorials at the collector

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
# Flush spans quickly (see "Troubleshooting" below)
export OTEL_BSP_SCHEDULE_DELAY=500
# optional:
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

### Python

```bash
cd src/python
uv run python scripts/tutorials/01_chat_bot.py --prompt "Hello, Copilot!"
```

### Go

```bash
cd src/go
make build
./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello, Copilot!"
```

---

## 3. Explore the traces

Open Grafana at [http://localhost:3000](http://localhost:3000) (login
`admin` / `admin`), then go to **Explore → Tempo** and search for recent traces.

You can also confirm spans are flowing straight from the collector logs:

```bash
docker compose -f docker/compose.yaml logs -f otel-collector
```

---

## 4. Tear down

```bash
docker compose -f docker/compose.yaml down
```

---

## Troubleshooting: no spans arrive

When the SDK launches the CLI over **stdio** (the tutorial default), it kills
the CLI with `SIGKILL` (`client.Stop()` → `process.Kill()`) the moment a
single-shot prompt finishes. The CLI batches spans and flushes on an interval
whose **default is 5 seconds**, so a short prompt is terminated before the first
flush and **no spans are ever sent**.

Set the standard OpenTelemetry batch env var so the CLI flushes before it is
killed:

```bash
export OTEL_BSP_SCHEDULE_DELAY=500   # milliseconds
```

Alternatively, run the CLI in [server mode](server_mode.md) and connect the
tutorial with `--cli-url`; the long-lived process flushes on its normal
interval. A direct `copilot -p "..."` run always works because it exits
gracefully and flushes on shutdown.

---

## Advanced: distributed trace context

The `TelemetryConfig` above is all you need to collect CLI spans. If your own
application creates its own OpenTelemetry spans and you want them linked into
the **same** distributed trace as the CLI, see the *Trace context propagation*
section of the
[official guide](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry).
For Python this also requires the `opentelemetry-api` package
(`pip install copilot-sdk[telemetry]`); Go already depends on
`go.opentelemetry.io/otel`.
