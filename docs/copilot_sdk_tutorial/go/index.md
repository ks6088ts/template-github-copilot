# GitHub Copilot SDK Tutorial (Go)

A step-by-step guide to building real applications with the **GitHub Copilot SDK** for Go.

> New to the SDK? Start with the language-agnostic
> [overview and concepts](../index.md) — *what the GitHub Copilot SDK is and is
> not* — plus [common setup](../getting_started.md) for installing the Copilot
> CLI and authenticating with GitHub. This page focuses on the **Go** edition.

---

## Tutorial Structure

Each tutorial pairs a **documentation page** with a **CLI subcommand** that you can build and run directly:

| # | Tutorial | Subcommand | Status | What You Learn |
|---|----------|------------|--------|----------------|
| 1 | [CLI Chatbot](tutorials/01_chat_bot.md) | `tutorial chat-bot` | Available | Client/session creation, single prompt, streaming, interactive loop |
| 2 | [Issue Triage Bot](tutorials/02_issue_triage.md) | `tutorial issue-triage` | Available | `DefineTool`, typed tool I/O, tool-calling agent |
| 3 | [Streaming Review](tutorials/03_streaming_review.md) | `tutorial streaming-review` | Available | Streaming deltas, real-time output |
| 4 | [Skills Doc Generation](tutorials/04_skills_docgen.md) | `tutorial skills-docgen` | Available | `SkillDirectories`, `SKILL.md`, doc generation |
| 5 | [Audit Log](tutorials/05_audit_hooks.md) | `tutorial audit-hooks` | Available | Session hooks, permission handler, audit log |
| 6 | [BYOK Azure OpenAI](tutorials/06_byok_azure_openai.md) | `tutorial byok-azure-openai` | Available | `ProviderConfig`, Azure OpenAI API key & Entra ID |

> All subcommands live in [`src/go/cmd/tutorial/`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/).

---

## Quick Start

Make sure the Copilot CLI is installed and authenticated first — see the common
[Getting Started](../getting_started.md) guide. Then:

```bash
# 1. Build the CLI (uses src/go/Makefile)
cd src/go
make build

# 2. Run your first tutorial subcommand (the SDK launches the CLI on demand)
./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello, Copilot!"
```

For Go-specific setup, see [Getting Started (Go)](getting_started.md).

---

## Observability

All Go tutorial subcommands keep telemetry off by default. To export
OpenTelemetry traces, start the local collector stack and pass the `tutorial`
persistent flags:

```bash
./dist/template-github-copilot-go tutorial chat-bot \
  --otel-endpoint http://localhost:4318 \
  --otel-bsp-schedule-delay 500 \
  --prompt "Hello, Copilot!"
```

The same settings can still come from the Python-compatible environment
variables: `OTEL_EXPORTER_OTLP_ENDPOINT`,
`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, and
`OTEL_BSP_SCHEDULE_DELAY`. See [Observability with OpenTelemetry](../observability.md).

---

## Scope

**In scope:**

- GitHub Copilot SDK concepts (what it is / is not)
- Go SDK API design and interfaces
- Sample code and step-by-step guides for concrete use cases
- Streaming, interactive sessions, and connecting to a standalone CLI server

**Out of scope:**

- SDK details for other languages (see [References](../appendix/references.md))
- Copilot CLI standalone usage guide
- Production scaling and infrastructure
- GitHub OAuth App authentication flow (see [CopilotReportForge docs](../../copilot_report_forge/guide/github_oauth_app.md))

---

## Further Reading

| Document | Description |
|----------|-------------|
| [Overview](../index.md) | Language-agnostic concepts and language chooser |
| [Architecture](../architecture.md) | How the SDK, CLI server, and Copilot API interact |
| [Getting Started (Go)](getting_started.md) | Go-specific setup, building the CLI, and first run |
| [CLI Server Mode](../server_mode.md) | Run the Copilot CLI as a standalone TCP server |
| [References](../appendix/references.md) | API reference and external links |
| [Go SDK reference (pkg.go.dev)](https://pkg.go.dev/github.com/github/copilot-sdk/go) | Generated Go API documentation |
