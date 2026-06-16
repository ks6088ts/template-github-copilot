# GitHub Copilot SDK Tutorial (Python)

A step-by-step guide to building real applications with the **GitHub Copilot SDK** for Python.

> New to the SDK? Start with the language-agnostic
> [overview and concepts](../index.md) — *what the GitHub Copilot SDK is and is
> not*, plus [common setup](../getting_started.md) for installing the Copilot CLI
> and authenticating with GitHub. This page focuses on the **Python** edition.

---

## Tutorial Structure

Each tutorial pairs a **documentation page** with a **self-contained CLI script** that you can run directly:

| # | Tutorial | Script | What You Learn |
|---|----------|--------|----------------|
| 1 | [CLI Chatbot](tutorials/01_chat_bot.md) | [`01_chat_bot.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/01_chat_bot.py) | CopilotClient, sessions, single prompt, interactive loop |
| 2 | [Issue Triage Bot](tutorials/02_custom_tools.md) | [`02_issue_triage.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/02_issue_triage.py) | Custom tools with `@define_tool`, Pydantic I/O |
| 3 | [Streaming Review](tutorials/03_streaming.md) | [`03_streaming_review.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/03_streaming_review.py) | Streaming with `ASSISTANT_MESSAGE_DELTA` |
| 4 | [Skills Doc Generation](tutorials/04_skills.md) | [`04_skills_docgen.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/04_skills_docgen.py) | Agent Skills via `SKILL.md` files |
| 5 | [Audit Log](tutorials/05_hooks_permissions.md) | [`05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py) | Session hooks, permission handling |
| 6 | [BYOK Azure OpenAI](tutorials/06_byok.md) | [`06_byok_azure_openai.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/06_byok_azure_openai.py) | Bring Your Own Key with Azure OpenAI |

> All scripts live in [`src/python/scripts/tutorials/`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/).

---

## Quick Start

Make sure the Copilot CLI is installed and authenticated first — see the common
[Getting Started](../getting_started.md) guide. Then:

```bash
# 1. Install SDK and tutorial dependencies (uses src/python/pyproject.toml)
cd src/python
uv sync --all-groups

# 2. Run your first tutorial script (the SDK launches the CLI on demand)
uv run python scripts/tutorials/01_chat_bot.py --prompt "Hello, Copilot!"
```

For Python-specific setup, see [Getting Started (Python)](getting_started.md).

---

## Scope

**In scope:**

- GitHub Copilot SDK concepts (what it is / is not)
- Architecture and operation principles
- Python SDK API design and interfaces
- Sample code and step-by-step guides for concrete use cases
- Agent Skills, Custom Tools, Session Hooks, Permission Handling, Streaming, BYOK

**Out of scope:**

- TypeScript / .NET SDK details (see [References](../appendix/references.md))
- Copilot CLI standalone usage guide
- Production scaling and infrastructure
- GitHub OAuth App authentication flow (see [CopilotReportForge docs](../../copilot_report_forge/guide/github_oauth_app.md))
- `template_github_copilot` package internals (tutorial scripts are self-contained)

---

## Further Reading

| Document | Description |
|----------|-------------|
| [Overview](../index.md) | Language-agnostic concepts and language chooser |
| [Architecture](../architecture.md) | How the SDK, CLI server, and Copilot API interact |
| [Getting Started (Python)](getting_started.md) | Python-specific setup and first run |
| [CLI Server Mode](../server_mode.md) | Run the Copilot CLI as a standalone TCP server |
| [References](../appendix/references.md) | API reference and external links |
