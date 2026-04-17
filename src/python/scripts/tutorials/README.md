# GitHub Copilot SDK — Tutorial Scripts

Self-contained Python CLI scripts that accompany the tutorial documentation at
`docs/copilot_sdk_tutorial/`.

Each script runs **standalone** with `python <script>.py` — no dependency on the
`template_github_copilot` package.

---

## Prerequisites

### 1. Python 3.11+

```bash
python --version   # 3.11 or later
```

### 2. Install dependencies

```bash
pip install github-copilot-sdk pydantic
# For script 06 with Entra ID auth only:
pip install azure-identity
```

Or, if you are inside `src/python` and use `uv`:

```bash
uv run python scripts/tutorials/01_chat_bot.py
```

### 3. Install and authenticate the Copilot CLI

The SDK launches the `copilot` CLI over stdio, so the binary must be installed.

```bash
# Option A: install via npm (provides the `copilot` command on PATH)
npm install -g @github/copilot

# Option B: let `gh copilot` download and manage the binary
gh copilot   # downloads on first run

# Authenticate with GitHub
gh auth login
# or: export COPILOT_GITHUB_TOKEN="<your-github-personal-access-token>"
```

> If the `copilot` binary is not on your `PATH`, set `COPILOT_CLI_PATH=/path/to/copilot`.

The scripts do **not** require a separately running Copilot CLI server. Use `--cli-url host:port` only if you have one running in TCP mode.

---

## Scripts

| Script | Tutorial | What it demonstrates |
|--------|----------|----------------------|
| `01_chat_bot.py` | [01 — CLI Chatbot](../../../docs/copilot_sdk_tutorial/tutorials/01_chat_bot.md) | CopilotClient, session creation, single prompt, interactive loop |
| `02_issue_triage.py` | [02 — Custom Tools](../../../docs/copilot_sdk_tutorial/tutorials/02_custom_tools.md) | `@define_tool`, Pydantic I/O, tool-calling agent |
| `03_streaming_review.py` | [03 — Streaming](../../../docs/copilot_sdk_tutorial/tutorials/03_streaming.md) | `ASSISTANT_MESSAGE_DELTA`, real-time streaming output |
| `04_skills_docgen.py` | [04 — Skills](../../../docs/copilot_sdk_tutorial/tutorials/04_skills.md) | `SKILL.md` files, skills directory, doc generation |
| `05_audit_hooks.py` | [05 — Hooks & Permissions](../../../docs/copilot_sdk_tutorial/tutorials/05_hooks_permissions.md) | `session.on()`, permission handler, audit log |
| `06_byok_azure_openai.py` | [06 — BYOK](../../../docs/copilot_sdk_tutorial/tutorials/06_byok.md) | `ProviderConfig`, Azure OpenAI API key & Entra ID |

---

## Quick Start

```bash
# 1. Install and authenticate the Copilot CLI (see Prerequisites above)

# 2. Run a tutorial script
python src/python/scripts/tutorials/01_chat_bot.py --help
python src/python/scripts/tutorials/01_chat_bot.py --prompt "What is GitHub Copilot?"
python src/python/scripts/tutorials/01_chat_bot.py --loop

python src/python/scripts/tutorials/02_issue_triage.py

python src/python/scripts/tutorials/03_streaming_review.py

python src/python/scripts/tutorials/04_skills_docgen.py

python src/python/scripts/tutorials/05_audit_hooks.py --prompt "Explain Python decorators"

# BYOK (requires Azure OpenAI setup)
export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deploy>"
export BYOK_API_KEY="<your-api-key>"
export BYOK_MODEL="gpt-4o"
python src/python/scripts/tutorials/06_byok_azure_openai.py
```

---

## Skills Directory

`skills/` contains example SKILL.md files used by `04_skills_docgen.py`.

```
skills/
├── docgen/
│   └── SKILL.md          # Google-style docstring generator
└── coding-standards/
    └── SKILL.md          # Coding standards checker
```

See [04 — Skills](../../../docs/copilot_sdk_tutorial/tutorials/04_skills.md) for details.
