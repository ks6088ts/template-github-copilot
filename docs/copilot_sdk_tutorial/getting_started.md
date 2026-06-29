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

### Option C: Fine-grained PAT (recommended for CI)

A **fine-grained personal access token** with the **Copilot Requests** permission is the recommended way to authenticate non-interactively — for example on GitHub Actions.

1. Open [Fine-grained personal access tokens](https://github.com/settings/personal-access-tokens/new).
2. **Resource owner** — select your **personal account**. Do **not** select an organization: the **Copilot Requests** permission is only available on user-owned tokens.
3. **Repository access** — pick what your task needs: *Public repositories*, *All repositories*, or *Only select repositories*.
4. **Permissions → Account → Add permissions → Copilot Requests** (Read-only — this permission has only a single access level).
5. **Generate token**, then export it:

```bash
export COPILOT_GITHUB_TOKEN="github_pat_xxxxxxxxxxxxxxxxxxxx"
```

> **Note:** The token only needs **Copilot Requests** to *run* the CLI. Add **Repository** permissions only if you want Copilot to act on GitHub.com via the built-in GitHub MCP server — see [Running in GitHub Actions (CI)](#running-in-github-actions-ci).

---

## Running in GitHub Actions (CI)

You can run the Copilot CLI non-interactively inside a workflow. This repository ships a ready-to-use workflow at [`.github/workflows/github-copilot-cli.yaml`](https://github.com/ks6088ts/template-github-copilot/blob/main/.github/workflows/github-copilot-cli.yaml).

### 1. Create the token

Follow [Option C: Fine-grained PAT](#option-c-fine-grained-pat-recommended-for-ci) above.

> **Why not `GITHUB_TOKEN`?** The automatic `secrets.GITHUB_TOKEN` provided by Actions **cannot** authenticate the Copilot CLI, because **Copilot Requests** can only be granted on a *user-owned* fine-grained PAT. You must create your own PAT and store it as a secret.

### 2. Choose the permissions

| Goal | Permission to grant | Level |
|------|---------------------|-------|
| **Run the Copilot CLI** (required) | Account → **Copilot Requests** | Read-only |
| Read/write files, create branches, push | Repository → Contents | Read and write |
| Create / update pull requests | Repository → Pull requests | Read and write |
| Create / update issues | Repository → Issues | Read and write |
| Edit workflow files | Repository → Workflows | Read and write |
| (Auto-added with any repository permission) | Repository → Metadata | Read |

> If your prompt only edits the runner's checked-out workspace, **Copilot Requests alone is enough** — no repository permissions are required.

### 3. Store the token as a secret

In the repository (or organization) settings, add the token as a secret named `COPILOT_GITHUB_TOKEN`.

### 4. Reference it in the workflow

```yaml
- name: Install GitHub Copilot CLI
  run: |
    curl -fsSL https://gh.io/copilot-install | VERSION="1.0.65" bash
    echo "$HOME/.local/bin" >> "$GITHUB_PATH"

- name: Run GitHub Copilot CLI
  env:
    COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
  run: |
    copilot \
      --prompt "Summarize this week's commits" \
      --allow-all-tools --allow-all-paths --allow-all-urls \
      --model gpt-5-mini
```

> **Security:** `--allow-all-tools`, `--allow-all-paths`, and `--allow-all-urls` let Copilot run any shell command on the runner without approval. Keep this to trusted CI only, grant the PAT the **least privilege** needed, scope it to **Only select repositories**, and set a **short expiry**.

---

## Why `GITHUB_TOKEN` or `gh auth login` Won't Work

A common question is whether you can skip the static PAT and authenticate with the built-in `GITHUB_TOKEN` (or `gh auth login` using it). For the Copilot CLI/SDK, **this does not work** — and the reason is structural, not a configuration mistake:

- **`GITHUB_TOKEN` is a GitHub App installation token.** It is scoped to repository operations (contents, issues, pull requests) and is **not bound to a user account**, so it can never carry the Copilot entitlement that **Copilot Requests** represents.
- **`gh auth login` backed by `GITHUB_TOKEN` does not help either.** That authenticates the GitHub REST/GraphQL **API**, not a Copilot subscription. There is no user identity behind the token for Copilot to bill the request against.
- **The token is read, then rejected.** The Copilot CLI resolves credentials in the order `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN`. If you supply `GITHUB_TOKEN`, the CLI *loads* it, but the backend refuses the request with a "no Copilot access" error.

### "I want to avoid static tokens"

Understandable — but for the Copilot CLI/SDK a **user-owned fine-grained PAT is currently the only supported CI credential**. You cannot fully eliminate the static token; instead, minimize the blast radius:

- Grant **only** `Copilot Requests` (add repository permissions sparingly).
- Scope the token to **Only select repositories**.
- Set a **short expiry** and rotate it regularly.

> **Just need raw LLM inference?** If your goal is only to call a model (not to run the `copilot` agent), [GitHub Models](https://docs.github.com/github-models) can be invoked with the built-in `GITHUB_TOKEN` by adding `permissions: models: read` to the job — no static PAT required. Note that this is a **different API** from the Copilot CLI/SDK these tutorials use (which spawns the `copilot` binary), so it does not drop into this repository's setup as-is.

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
