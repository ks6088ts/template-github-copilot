# GitHub Copilot SDK — Tutorial Subcommands (Go)

Go subcommands that demonstrate the [GitHub Copilot SDK for Go](https://pkg.go.dev/github.com/github/copilot-sdk/go).

Each subcommand corresponds 1:1 to a Python tutorial script under [`src/python/scripts/tutorials/`](../../../python/scripts/tutorials/), so you can compare the same recipe across both languages.

## Documentation

Setup instructions, the subcommand reference, and step-by-step tutorials are published on the documentation site. The Markdown sources live under [`docs/copilot_sdk_tutorial/go/`](../../../../docs/copilot_sdk_tutorial/go/):

- [GitHub Copilot SDK Tutorial (Go)](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/) — overview and subcommand reference
- [Getting Started](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/getting_started/) — prerequisites, building the CLI, and authentication
- [Tutorial 1: CLI Chatbot](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/01_chat_bot/) — the `chat-bot` subcommand
- [Tutorial 2: Issue Triage Bot](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/02_issue_triage/) — the `issue-triage` subcommand
- [Tutorial 3: Streaming Review](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/03_streaming_review/) — the `streaming-review` subcommand
- [Tutorial 4: Skills Doc Generation](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/04_skills_docgen/) — the `skills-docgen` subcommand
- [Tutorial 5: Audit Log](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/05_audit_hooks/) — the `audit-hooks` subcommand
- [Tutorial 6: BYOK Azure OpenAI](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/06_byok_azure_openai/) — the `byok-azure-openai` subcommand

## Quick start

```bash
cd src/go

# Build the CLI
make build

# Show the available tutorial subcommands
./dist/template-github-copilot-go tutorial --help

# Run the chat-bot subcommand
./dist/template-github-copilot-go tutorial chat-bot --prompt "What is GitHub Copilot?"
```

## Subcommands

| Subcommand | Python script | Status | Docs |
|------------|---------------|--------|------|
| `tutorial chat-bot` | [`01_chat_bot.py`](../../../python/scripts/tutorials/01_chat_bot.py) | Available | [Tutorial 1: CLI Chatbot](../../../../docs/copilot_sdk_tutorial/go/tutorials/01_chat_bot.md) |
| `tutorial issue-triage` | [`02_issue_triage.py`](../../../python/scripts/tutorials/02_issue_triage.py) | Available | [Tutorial 2: Issue Triage Bot](../../../../docs/copilot_sdk_tutorial/go/tutorials/02_issue_triage.md) |
| `tutorial streaming-review` | [`03_streaming_review.py`](../../../python/scripts/tutorials/03_streaming_review.py) | Available | [Tutorial 3: Streaming Review](../../../../docs/copilot_sdk_tutorial/go/tutorials/03_streaming_review.md) |
| `tutorial skills-docgen` | [`04_skills_docgen.py`](../../../python/scripts/tutorials/04_skills_docgen.py) | Available | [Tutorial 4: Skills Doc Generation](../../../../docs/copilot_sdk_tutorial/go/tutorials/04_skills_docgen.md) |
| `tutorial audit-hooks` | [`05_audit_hooks.py`](../../../python/scripts/tutorials/05_audit_hooks.py) | Available | [Tutorial 5: Audit Log](../../../../docs/copilot_sdk_tutorial/go/tutorials/05_audit_hooks.md) |
| `tutorial byok-azure-openai` | [`06_byok_azure_openai.py`](../../../python/scripts/tutorials/06_byok_azure_openai.py) | Available | [Tutorial 6: BYOK Azure OpenAI](../../../../docs/copilot_sdk_tutorial/go/tutorials/06_byok_azure_openai.md) |

## Observability (OpenTelemetry)

Every subcommand can export OpenTelemetry traces. Set `OTEL_EXPORTER_OTLP_ENDPOINT`
to enable it (telemetry is wired via `newClientOptions()` in [`telemetry.go`](telemetry.go)):

```bash
# Start the collector + Grafana LGTM stack (from the repository root)
docker compose -f docker/compose.yaml up -d

export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_BSP_SCHEDULE_DELAY=500   # flush before the SDK kills the CLI
./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello!"

# View traces in Grafana → Explore → Tempo
open http://localhost:3000   # admin / admin
```

See [Observability with OpenTelemetry](../../../../docs/copilot_sdk_tutorial/observability.md)
and [`docker/README.md`](../../../../docker/README.md) for details.
