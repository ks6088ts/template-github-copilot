# Getting Started

This guide covers the **common setup** shared by every SDK edition: installing the Copilot CLI and authenticating with GitHub. These steps are language-agnostic.

> After completing this page, continue with your language edition for SDK installation and run instructions:
>
> - **Python** → [Python Getting Started](python/getting_started.md)
> - **Go** → [Go Getting Started](go/getting_started.md)

---

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| Node.js (`npm`) or GitHub CLI (`gh`) | latest | Installing the Copilot CLI |
| GitHub Copilot subscription | — | Required for API access |

> Language-specific requirements (Python + uv, or Go + Make) are listed in each edition's Getting Started.

---

## Install the Copilot CLI

Every SDK edition launches the **`copilot` CLI** as a subprocess over stdio, so the binary must be available on your machine. Pick one of the following:

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

`COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, and `GITHUB_TOKEN` are honored in that order of precedence.

---

## Common Environment Variables

These variables apply to every edition. Edition- or tutorial-specific variables (for example BYOK settings) are documented in each edition's Getting Started.

| Variable | Purpose |
|----------|---------|
| `COPILOT_GITHUB_TOKEN` | GitHub PAT for the Copilot CLI (alternative to `gh auth login`) |
| `COPILOT_CLI_PATH` | Absolute path to the `copilot` binary (if not on PATH) |
| `COPILOT_CLI_URL` | Address of a running Copilot CLI server in TCP mode (e.g. `127.0.0.1:3000`) |

---

## Do You Need to Start a Server?

No. By default the SDK spawns the `copilot` CLI for you over **stdio**, so you do **not** need to start anything manually for the tutorials.

If you prefer to run the CLI once as a long-lived **TCP server** and have multiple clients connect to it, see [CLI Server Mode](server_mode.md). Each edition then connects with a `--cli-url host:port` flag.

---

## Next Steps

Common setup is done. Continue with your language edition:

| Edition | Getting Started | Tutorials |
|---------|-----------------|-----------|
| Python | [Python Getting Started](python/getting_started.md) | [Python tutorials](python/index.md) |
| Go | [Go Getting Started](go/getting_started.md) | [Go tutorials](go/index.md) |

To understand how the pieces fit together, read [Architecture](architecture.md).
