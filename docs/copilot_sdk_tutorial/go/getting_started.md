# Getting Started (Go)

This guide covers the **Go-specific** setup: building the CLI and running the
tutorial subcommands. For installing the Copilot CLI and authenticating with
GitHub — shared by every language edition — follow the common
[Getting Started](../getting_started.md) guide first.

---

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| [Go](https://go.dev/doc/install) | 1.26+ | Runtime and build toolchain |
| [GNU Make](https://www.gnu.org/software/make/) | latest | Build targets |
| Node.js (`npm`) or GitHub CLI (`gh`) | latest | Installing the Copilot CLI |
| GitHub Copilot subscription | — | Required for API access |

Verify your Go toolchain:

```bash
go version   # go1.26 or later
```

---

## Build the CLI

The tutorial subcommands are part of the Go CLI. Build it with the project's Makefile:

```bash
cd src/go

# Build the CLI into ./dist/
make build

# Show the available tutorial subcommands
./dist/template-github-copilot-go tutorial --help
```

These subcommands do **not** require a separately running Copilot CLI server — the SDK starts one for you on demand via stdio. Use `--cli-url host:port` only if you already have a Copilot CLI running in TCP mode (see [CLI Server Mode](../server_mode.md)).

---

## Run Your First Subcommand

```bash
cd src/go
./dist/template-github-copilot-go tutorial chat-bot --prompt "What is GitHub Copilot?"
```

Expected output (streaming):

```text
GitHub Copilot is an AI-powered coding assistant developed by GitHub and OpenAI...
```

---

## Global Flags

The root command exposes a global `--verbose`/`-v` flag (inherited by every subcommand) that lowers the log level to `DEBUG`, surfacing diagnostic logs such as the Copilot client connection mode and session lifecycle:

```bash
./dist/template-github-copilot-go tutorial chat-bot --verbose --prompt "Hello!"
```

---

## Project Layout

```text
src/go/cmd/tutorial/
├── README.md      # Subcommand index (points to these docs)
├── tutorial.go    # `tutorial` parent command group
└── chatbot.go     # Tutorial 1: CLI chatbot (chat-bot subcommand)
```

---

## Environment Variables

The Go CLI relies on the common Copilot variables (`COPILOT_GITHUB_TOKEN`,
`COPILOT_CLI_PATH`, `COPILOT_CLI_URL`) documented in the common
[Getting Started](../getting_started.md). It does not add any Go-specific
environment variables.

---

## Next Steps

Now that your environment is ready, work through the tutorials:

1. [CLI Chatbot](tutorials/01_chat_bot.md) — build your first Copilot-powered Go program
