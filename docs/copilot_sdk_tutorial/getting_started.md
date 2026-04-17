# Getting Started

This guide covers everything you need to set up a local development environment and run the tutorial scripts.

---

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| Python | 3.11+ | Runtime |
| pip / uv | latest | Package management |
| Node.js (`npm`) or GitHub CLI (`gh`) | latest | Installing the Copilot CLI |
| GitHub Copilot subscription | — | Required for API access |

---

## Installation

### Install the SDK

```bash
pip install github-copilot-sdk
```

If you are working inside `src/python` and use **uv**:

```bash
# uv reads pyproject.toml — the SDK is already listed as a dependency
cd src/python
uv sync
```

To run tutorial scripts with `pydantic` (required for script 02):

```bash
pip install github-copilot-sdk pydantic
```

For BYOK with Entra ID authentication (script 06):

```bash
pip install github-copilot-sdk azure-identity
```

---

## Authenticate with GitHub

The Copilot CLI needs a GitHub account with Copilot access.

### Option A: GitHub CLI auth (recommended)

```bash
gh auth login
# The Copilot CLI will use your gh CLI credentials automatically.
```

### Option B: Personal Access Token (PAT)

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Generate a token with the `copilot` scope (or `read:user` + Copilot-enabled org)
3. Export it:

```bash
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

---

## Install the Copilot CLI

The SDK launches the **`copilot` CLI** as a subprocess over stdio, so the binary must be available on your machine. Pick one of the following:

```bash
# Option A: npm (installs the `copilot` command on PATH)
npm install -g @github/copilot

# Option B: gh copilot (downloads and manages the binary)
gh copilot   # On first run, downloads the CLI under ~/.local/share/gh/copilot
```

Verify it is runnable:

```bash
copilot --version
# or, if you used gh copilot:
gh copilot -- --version
```

> **Tip:** If `copilot` is not on your PATH, tell the SDK where to find the binary:
>
> ```bash
> export COPILOT_CLI_PATH="/absolute/path/to/copilot"
> ```

The tutorial scripts do **not** require a separately running Copilot CLI server — the SDK starts one for you on demand via stdio. An optional `--cli-url host:port` flag is provided if you already have a Copilot CLI running in TCP mode.

---

## Run Your First Script

```bash
python src/python/scripts/tutorials/01_chat_bot.py --prompt "What is GitHub Copilot?"
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

All tutorial scripts accept `--cli-url` (default: *stdio*). Script 06 also reads BYOK settings from environment variables:

| Variable | Purpose | Used by |
|----------|---------|---------|
| `COPILOT_GITHUB_TOKEN` | GitHub PAT for the Copilot CLI (alternative to `gh auth login`) | Copilot CLI subprocess |
| `COPILOT_CLI_PATH` | Absolute path to the `copilot` binary (if not on PATH) | SDK subprocess launcher |
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
