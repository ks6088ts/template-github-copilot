# Demo 5 · MCP server integration

**Theme:** extensibility. **Time:** ~25 min.
**Features:** `/mcp`, `/mcp add`, user/workspace MCP config, per-server tool permissions.

> **Story so far:** CI now reviews every PR. **This demo:** extend Copilot with the **Playwright MCP server** so it can drive the *running* app in a real browser and validate the **Reset button** you built in [Demo 1](01_issue_to_pr.md).

The **Model Context Protocol (MCP)** is the open standard that lets Copilot reach external tools and data sources. The CLI ships with the **GitHub MCP server pre-configured**, and you can add more to extend what Copilot can do ([Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli); [About MCP](https://docs.github.com/en/copilot/concepts/context/mcp)).

```mermaid
graph LR
    CLI[Copilot CLI] -->|built-in| GH[GitHub MCP server]
    CLI -->|/mcp add| PW[Playwright MCP server]
    CLI -->|/mcp add| X2[Your internal MCP server]
    GH --> Tools1[issues · PRs · Actions]
    PW --> Tools2[open page · click · assert]
```

---

## Prerequisites

- Authenticated CLI.
- Node.js available (the Playwright MCP server runs via `npx`). Use any server you trust; the steps below use the official Playwright MCP server as a concrete example.

---

## Steps

### 1. List what's already wired up

```text
> /mcp
```

The **GitHub** server appears by default — that is what powered Demos 1–2 ([Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)).

### 2. Add a server interactively

```text
> /mcp add
```

Fill in the fields, moving between them with ++tab++, then press ++ctrl+s++ to save ([Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)).

### 3. Or edit the config file directly

User-level server definitions are stored in `mcp-config.json`, by default under `~/.copilot` (override the location with `COPILOT_HOME`) ([Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)). Recent CLI releases also load workspace MCP config such as `.github/mcp.json`; check the changelog before teaching a fixed config layout ([copilot-cli changelog 1.0.61](https://github.com/github/copilot-cli/blob/main/changelog.md#1061---2026-06-09)). A local (stdio) server entry for the [Playwright MCP server](https://github.com/microsoft/playwright-mcp) looks like this — confirm the latest package and the canonical JSON structure in the [MCP configuration reference](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp#writing-a-json-configuration-for-mcp-servers):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

!!! warning "Only add servers you trust"
    An MCP server can expose powerful tools to the agent. Vet the source, pin versions, and pass secrets via environment variables — never hard-code them.

### Troubleshooting MCP startup

If Copilot cannot use a server, diagnose the server before changing your prompt:

1. Run `/mcp` and inspect whether the server is enabled, authenticated, and exposing the expected tools.
2. Run the server command outside Copilot to verify startup time and stderr output (e.g. `npx -y @playwright/mcp@latest --help`).
3. Confirm environment variables and OAuth credentials are passed to the server process, not hard-coded into config.
4. Disable unused servers; large tool lists add token and startup overhead. The `deferTools` option added in CLI 1.0.63 keeps selected MCP tools available even when tool search is enabled ([copilot-cli changelog 1.0.63](https://github.com/github/copilot-cli/blob/main/changelog.md#1063---2026-06-15)).

### 4. Use the new tools to drive the app

Start the dev server in another terminal so there's something to drive ([README](https://github.com/ks6088ts/template-typescript-react)):

```bash
pnpm dev   # serves the app at http://localhost:5173
```

Then ask Copilot to exercise the Reset button end to end. Naming the server in your prompt helps Copilot pick the right tool ([About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)):

```text
> Use the playwright MCP server to open http://localhost:5173, click the counter once so it reads "Count is 1", then click the Reset button and confirm the counter returns to "Count is 0".
```

You just validated the feature from Demo 1 against a live browser — without writing a test by hand.

### 5. Govern MCP tools with permissions

Allow or deny tools at the server or tool level ([About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli#using-the-approval-options)):

```bash
# Allow everything from playwright EXCEPT installing browsers
copilot --allow-tool='playwright' --deny-tool='playwright(browser_install)'
```

Find a server's exact name and tools by running `/mcp` and selecting it ([About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)).

!!! note "Org policy limitations"
    Some organization-level MCP policies (e.g. *MCP servers in Copilot*, *MCP Registry URL*) are **not yet enforced** by the CLI. Know this before relying on them for governance ([Security considerations](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli#known-mcp-server-policy-limitations)).

---

## What you learned

- The GitHub MCP server is built in; `/mcp add`, user config, and workspace config extend the agent.
- The Playwright MCP server lets Copilot drive the running SPA and verify UI behavior like the Reset button.
- Per-server/per-tool allow/deny flags govern MCP access.

## Take it further

- Add a domain-specific server (database, observability, internal API) and have Copilot answer questions it otherwise couldn't — for example, a Grafana MCP server to query the telemetry this app emits into the `docker/` LGTM stack.
- Compare with how the [Copilot SDK](../../copilot_sdk_tutorial/index.md) wires tools programmatically.

Next: [Demo 6 · Custom agents & skills](06_custom_agents_skills.md).
