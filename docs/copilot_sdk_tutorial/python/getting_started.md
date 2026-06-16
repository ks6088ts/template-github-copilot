# Getting Started (Python)

This guide covers the **Python-specific** setup for running the tutorial
scripts. For installing the Copilot CLI and authenticating with GitHub — shared
by every language edition — follow the common
[Getting Started](../getting_started.md) guide first.

---

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| Python | 3.13+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Package management |
| Node.js (`npm`) or GitHub CLI (`gh`) | latest | Installing the Copilot CLI |
| GitHub Copilot subscription | — | Required for API access |

---

## Installation

### Install the SDK and tutorial dependencies

All packages used by the tutorial scripts (`github-copilot-sdk`, `pydantic`,
`azure-identity`, …) are declared in [`src/python/pyproject.toml`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/pyproject.toml). Install them with a single `uv sync` command:

```bash
cd src/python
uv sync --all-groups
```

> `uv sync` creates a virtual environment under `.venv/` and installs every
> dependency pinned in `uv.lock`. Use `uv run <command>` to run tools inside
> that environment without activating it manually.

> **CLI, authentication, and server mode:** installing the `copilot` CLI,
> signing in with `gh auth login` or `COPILOT_GITHUB_TOKEN`, and running the CLI
> as a TCP server are covered once in the common
> [Getting Started](../getting_started.md) and [CLI Server Mode](../server_mode.md)
> guides. The SDK launches the CLI for you over stdio, so no server is required
> to run the tutorials.

---

## Run Your First Script

Run tutorial scripts with `uv run python` from the `src/python` directory so
they execute inside the managed virtual environment:

```bash
cd src/python
uv run python scripts/tutorials/01_chat_bot.py --prompt "What is GitHub Copilot?"
```

Expected output (streaming):

```
GitHub Copilot is an AI-powered coding assistant developed by GitHub and OpenAI...
```

---

## Project Layout

```
src/python/scripts/tutorials/
├── README.md                   # Script index and run instructions
├── 01_chat_bot.py              # Tutorial 1: CLI chatbot
├── 02_issue_triage.py          # Tutorial 2: Issue triage with custom tools
├── 03_streaming_review.py      # Tutorial 3: Streaming code review
├── 04_skills_docgen.py         # Tutorial 4: Skills-based doc generation
├── 05_audit_hooks.py           # Tutorial 5: Audit log via session hooks
├── 06_byok_azure_openai.py     # Tutorial 6: BYOK with Azure OpenAI
└── skills/
    ├── docgen/SKILL.md
    └── coding-standards/SKILL.md
```

---

## Environment Variables

All tutorial scripts accept `--cli-url` (default: *stdio*). The common CLI
variables (`COPILOT_GITHUB_TOKEN`, `COPILOT_CLI_PATH`, `COPILOT_CLI_URL`) are
described in the common [Getting Started](../getting_started.md). Script 06 also
reads these BYOK settings:

| Variable | Purpose | Used by |
|----------|---------|---------|
| `BYOK_BASE_URL` | Azure OpenAI deployment base URL | Script 06 |
| `BYOK_API_KEY` | Azure OpenAI API key | Script 06 (api-key auth) |
| `BYOK_MODEL` | Model/deployment name | Script 06 |

---

## Next Steps

Now that your environment is ready, work through the tutorials in order:

1. [CLI Chatbot](tutorials/01_chat_bot.md) — build your first Copilot-powered script
2. [Custom Tools](tutorials/02_custom_tools.md) — extend the agent with your own tools
3. [Streaming](tutorials/03_streaming.md) — consume tokens in real time
4. [Skills](tutorials/04_skills.md) — use SKILL.md to define reusable agent behaviours
5. [Hooks & Permissions](tutorials/05_hooks_permissions.md) — observe and control every action
6. [BYOK](tutorials/06_byok.md) — swap in Azure OpenAI as the LLM backend
