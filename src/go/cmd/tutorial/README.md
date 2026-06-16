# GitHub Copilot SDK — Tutorial Subcommands (Go)

Go subcommands that demonstrate the [GitHub Copilot SDK for Go](https://pkg.go.dev/github.com/github/copilot-sdk/go).

Each subcommand corresponds 1:1 to a Python tutorial script under [`src/python/scripts/tutorials/`](../../../python/scripts/tutorials/), so you can compare the same recipe across both languages.

## Documentation

Setup instructions, the subcommand reference, and step-by-step tutorials are published on the documentation site. The Markdown sources live under [`docs/copilot_sdk_tutorial/go/`](../../../../docs/copilot_sdk_tutorial/go/):

- [GitHub Copilot SDK Tutorial (Go)](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/) — overview and subcommand reference
- [Getting Started](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/getting_started/) — prerequisites, building the CLI, and authentication
- [Tutorial 1: CLI Chatbot](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/tutorials/01_chat_bot/) — the `chat-bot` subcommand

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
| `tutorial issue-triage` | [`02_issue_triage.py`](../../../python/scripts/tutorials/02_issue_triage.py) | Planned | — |
| `tutorial streaming-review` | [`03_streaming_review.py`](../../../python/scripts/tutorials/03_streaming_review.py) | Planned | — |
| `tutorial skills-docgen` | [`04_skills_docgen.py`](../../../python/scripts/tutorials/04_skills_docgen.py) | Planned | — |
| `tutorial audit-hooks` | [`05_audit_hooks.py`](../../../python/scripts/tutorials/05_audit_hooks.py) | Planned | — |
| `tutorial byok-azure-openai` | [`06_byok_azure_openai.py`](../../../python/scripts/tutorials/06_byok_azure_openai.py) | Planned | — |
