# Getting Started

This guide covers everything you need to set up a local development environment and run the tutorial scripts.

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

The tutorial scripts do **not** require a separately running Copilot CLI server — the SDK starts one for you on demand via stdio. An optional `--cli-url host:port` flag is provided if you already have a Copilot CLI running in TCP mode. See **Run the Copilot CLI in Server Mode** below for how to start one.

### Update the Copilot CLI

The CLI is distributed as the npm package `@github/copilot`. Keep it current to pick up the latest SDK-compatible features and fixes.

```bash
# Update to the latest version
npm install -g @github/copilot@latest

# Pin a specific version (replace @latest with @<version>)
npm install -g @github/copilot@0.0.339
```

Helpful checks:

```bash
copilot --version                          # show the installed version
npm view @github/copilot versions --json   # list all available versions
```

> **Tip:** While the CLI is running, the `/update` slash command also checks for and applies updates.

---

## Run the Copilot CLI in Server Mode (optional)

> For a complete reference — flag-by-flag explanation, log levels, permission
> scoping, securing the server with `COPILOT_CONNECTION_TOKEN`, and Docker
> deployment — see [CLI Server Mode](server_mode.md).

By default the SDK spawns the `copilot` CLI for you over stdio, so **you do not
need to start anything manually**. If you prefer to run the CLI once as a
long-lived **TCP server** and have every script connect to it, start it in
server mode:

```bash
# Authenticate first (see "Authenticate with GitHub" above)
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Start the Copilot CLI as a TCP server on port 3000
copilot \
  --server \
  --port 3000 \
  --log-level all \
  --allow-all-tools --allow-all-paths --allow-all-urls \
  --model gpt-5-mini
```

From the repository, the same command is wrapped in a Make target:

```bash
cd src/python
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
make copilot           # runs `copilot --server --port 3000 ...`
```

| Flag | Purpose |
|------|---------|
| `--server` | Run the CLI as a long-lived server instead of an interactive session |
| `--port 3000` | TCP port the server listens on |
| `--log-level all` | Verbose logging (handy while learning) |
| `--allow-all-tools` / `--allow-all-paths` / `--allow-all-urls` | Pre-approve tool, file, and network access so the server runs unattended |
| `--model gpt-5-mini` | Default model the server uses (override with `COPILOT_MODEL`) |

Then point any tutorial script at the running server with `--cli-url`:

```bash
# In another terminal
cd src/python
uv run python scripts/tutorials/01_chat_bot.py \
  --prompt "What is GitHub Copilot?" \
  --cli-url localhost:3000
```

> **Heads up:** `--allow-all-*` disables interactive permission prompts. Use it
> for local experimentation only — never expose this server to an untrusted
> network.

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
