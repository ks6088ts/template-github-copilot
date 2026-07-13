# References

All technical claims in this workshop are grounded in the **primary sources** below. Where the product is evolving, prefer the live commands (`/help`, `/model`, `copilot help <topic>`) over any value frozen in a document.

---

## Primary sources — GitHub official documentation

| Document | What it covers |
|----------|----------------|
| [About GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) | Concepts: modes, context management, customization, security, model usage, sandboxes, ACP |
| [Using GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) | How-to: sessions, tips, custom instructions/agents/skills, MCP, context commands |
| [Best practices for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices) | Models, plan mode, infinite sessions, delegate, workflows, advanced patterns, team guidance |
| [Installing GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli) | Install paths and prerequisites |
| [GitHub Copilot features](https://docs.github.com/en/copilot/get-started/features) | The assistive / agentic / customization / admin taxonomy across surfaces |
| [Adding custom instructions for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions) | Instruction file locations and precedence |
| [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | Authoring `SKILL.md` skills |
| [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Skill concepts |
| [Creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-custom-agents) | Agent-profile schema |
| [About the rubber duck agent](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck) | Cross-model "second opinion" critique used by `/rubber-duck` |
| [Running tasks in parallel with `/fleet`](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet) | Parallel subagent execution and `/tasks` monitoring |
| [Allowing Copilot CLI to work autonomously (autopilot)](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/autopilot) | How autopilot iterates (plan → act → test → verify) until done |
| [About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins) | Plugin marketplaces and `/plugin` management |
| [About hooks for GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/hooks) | Lifecycle hooks |
| [About GitHub Copilot Memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory) | Persistent repo memories |
| [About Model Context Protocol (MCP)](https://docs.github.com/en/copilot/concepts/context/mcp) | MCP concepts |
| [Configure MCP servers (JSON structure)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp#writing-a-json-configuration-for-mcp-servers) | `mcp-config.json` schema |
| [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review) | Automated code review |
| [About cloud and local sandboxes](https://docs.github.com/en/copilot/concepts/about-cloud-and-local-sandboxes) | Sandboxing model: local vs cloud, session lifecycle, auth, billing |
| [Configuring local sandbox settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings) | The `/sandbox` UI: General / Filesystem / Network settings and platform limits |
| [Enabling or disabling cloud sandboxes for your organization](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/enabling-or-disabling-cloud-sandboxes-for-your-organization) | Org policy: Cloud Sandbox access |
| [Billing for cloud and local sandboxes](https://docs.github.com/en/billing/concepts/product-billing/cloud-and-local-sandboxes) | Compute / Memory / Storage meters for cloud sandboxes |
| [Models and pricing for GitHub Copilot](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) | Premium requests, model costs |
| [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | Full command & flag list |
| [Copilot CLI configuration directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) | `~/.copilot` settings reference |
| [Copilot CLI ACP server](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server) | Agent Client Protocol |
| [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | When to use which customization feature |
| [Plans for GitHub Copilot](https://github.com/features/copilot/plans) | Plan comparison & pricing |

## Primary sources — GitHub repositories & packages

| Resource | Notes |
|----------|-------|
| [github/copilot-cli](https://github.com/github/copilot-cli) | Official repo: README, `changelog.md`, install script, issues, discussions |
| [`@github/copilot` on npm](https://www.npmjs.com/package/@github/copilot) | The npm distribution |
| [Homebrew cask `copilot-cli`](https://formulae.brew.sh/cask/copilot-cli) | macOS/Linux install |

## Change watchlist { #change-watchlist }

Check these sources before each workshop run. Copilot CLI changes quickly enough that static workshop material should be treated as a snapshot, not a contract.

| Area to watch | Primary source | Why it matters |
|---------------|----------------|----------------|
| CLI releases and command behavior | [`github/copilot-cli` changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | Tracks CLI versions, new slash commands (`/settings`, `/security-review`, `/worktree`), prompt-mode behavior, MCP config loading, hooks, permissions, and bug fixes |
| Copilot-wide product announcements | [GitHub Blog Changelog — Copilot label](https://github.blog/changelog/label/copilot/) | Tracks model releases/deprecations, public previews, plan changes, code review updates, sandboxes, BYOK, and usage metrics |
| Model availability and deprecations | [Supported models](https://docs.github.com/copilot/reference/ai-models/supported-models), [GitHub Blog Changelog — Copilot](https://github.blog/changelog/label/copilot/) | Model names and plan eligibility change frequently; examples should instruct learners to use `/model` rather than copy fixed names |
| BYOK / external provider models | [Using your own LLM models in GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models), [Using your LLM provider API keys with Copilot](https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/use-your-own-api-keys) | Separates client-side BYOK from enterprise-admin configured external-provider models |
| Sandboxes | [About cloud and local sandboxes](https://docs.github.com/en/copilot/concepts/about-cloud-and-local-sandboxes), [GitHub Blog sandbox announcement](https://github.blog/changelog/2026-06-02-cloud-and-local-sandboxes-for-github-copilot-now-in-public-preview) | Public-preview behavior, pricing, platform support, and policy controls may change |
| MCP and agent discovery | [MCP management](https://docs.github.com/en/copilot/concepts/mcp-management), [`github/copilot-cli` changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | MCP config locations, registry behavior, `deferTools`, and Agent finder are actively evolving |
| Code review behavior | [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review), [AGENTS.md support announcement](https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements) | Review instructions, draft PR review UX, and timeline behavior affect Demo 2 |
| Usage and billing signals | [Copilot usage metrics API](https://docs.github.com/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics?apiVersion=2026-03-10), [AI credits usage API announcement](https://github.blog/changelog/2026-06-19-ai-credits-consumed-per-user-now-in-the-copilot-usage-metrics-api) | Workshop owners need to explain AI credit consumption and admin reporting accurately |

### Recent changes reflected in this workshop

| Date | Change | Source |
|------|--------|--------|
| 2026-07-09 | GPT-5.6 Sol, Terra, and Luna available in GitHub Copilot (CLI included); Sol for Pro+/Max/Business/Enterprise, Terra and Luna for Pro and above; admins must enable policy | [GitHub Blog Changelog](https://github.blog/changelog/2026-07-09-openais-gpt-5-6-sol-terra-and-luna-are-now-available-in-github-copilot) |
| 2026-07-09 | CLI 1.0.70: GPT-5.6 model support, `/refine` command, `--sandbox`/`--no-sandbox` session flags, trusted-repo `.github/copilot/settings.json` (model/effort/context pin + deny-list extension), `preToolUse` exit code 2 denies tool calls | [copilot-cli changelog 1.0.70](https://github.com/github/copilot-cli/blob/main/changelog.md#1070---2026-07-09) |
| 2026-07-08 | Enterprise-managed OpenTelemetry export GA for Copilot CLI and VS Code: admins can mandate OTLP endpoint, transport, service name, and content-capture policy via managed settings | [GitHub Blog Changelog](https://github.blog/changelog/2026-07-08-enterprise-managed-opentelemetry-export-for-vs-code-and-cli) |
| 2026-07-08 | Managed Copilot settings now deployable via native MDM (Windows Registry, macOS managed preferences) and file-based `managed-settings.json`, in addition to server-managed channel | [GitHub Blog Changelog](https://github.blog/changelog/2026-07-08-deploy-managed-copilot-settings-via-mdm-in-vs-code-and-cli) |
| 2026-07-07 | Copilot usage metrics API adds `avg_pull_requests_minutes_to_review` and `avg_pull_requests_review_cycles` per adoption-phase cohort | [GitHub Blog Changelog](https://github.blog/changelog/2026-07-07-add-review-cycles-and-time-to-adoption-phases-in-the-usage-api) |
| 2026-07-07 | CLI 1.0.69: `/plugins` dashboard for managing installed plugins; `gemini-3.5-flash` gains minimal reasoning effort option; `/allow-all auto` requires experimental mode | [copilot-cli changelog 1.0.69](https://github.com/github/copilot-cli/blob/main/changelog.md#1069---2026-07-07) |
| 2026-07-01 | CLI 1.0.68: kimi-k2.7-code model support added | [copilot-cli changelog 1.0.68](https://github.com/github/copilot-cli/blob/main/changelog.md#1068---2026-07-01) |
| 2026-06-30 | CLI 1.0.67: Claude Sonnet 5 added as a supported model; session limits require at least 30 AI credits | [copilot-cli changelog 1.0.67](https://github.com/github/copilot-cli/blob/main/changelog.md#1067---2026-06-30) |
| 2026-06-30 | CLI 1.0.66: Claude Opus 4.8 (fast) added; Claude Opus 4.6 (fast) deprecated; `/plugins` dashboard, compact timeline highlight reel, `stayInAutopilot` setting | [copilot-cli changelog 1.0.66](https://github.com/github/copilot-cli/blob/main/changelog.md#1066---2026-06-30) |
| 2026-06-29 | Claude Opus 4.8 (fast mode) entered preview across Copilot surfaces including Copilot CLI (admin policy off by default) | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-29-claude-opus-4-8-fast-mode-is-now-in-preview-for-github-copilot) |
| 2026-06-26 | MAI-Code-1-Flash reached general availability for Copilot Business and Copilot Enterprise | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-26-mai-code-1-flash-for-copilot-business-and-copilot-enterprise) |
| 2026-06-25 | Copilot code review now uses the CLI/SDK `grep`/`rg`/`glob`/`view` file tools (~20% lower review cost) and adds org-level default Medium analysis depth | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-25-copilot-code-review-analysis-depth-and-efficiency-updates) |
| 2026-06-24 | Free and Student plans default to Copilot auto model selection only; `(Preview)` label retired from Microsoft-released models | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-24-changes-to-model-selection-for-free-and-student-plans) |
| 2026-06-24 | `/security-review` available to all users without `--experimental` (CLI 1.0.64) | [copilot-cli changelog 1.0.64](https://github.com/github/copilot-cli/blob/main/changelog.md#1064---2026-06-23) |
| 2026-06-23 | New Copilot CLI terminal interface GA: tabbed Session/Gists/Issues/Pull requests layout, `/mcp search` GitHub MCP Registry install, and `/theme` color modes | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-23-copilot-cli-new-terminal-interface-is-generally-available) |
| 2026-06-19 | `ai_credits_used` added to user-level Copilot usage metrics API reports | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-19-ai-credits-consumed-per-user-now-in-the-copilot-usage-metrics-api) |
| 2026-06-18 | Generated release notes now credit the developer alongside `@copilot` for Copilot cloud-agent PRs | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-18-generated-release-notes-credit-you-for-copilot-pull-requests) |
| 2026-06-18 | Copilot code review reads repository-root `AGENTS.md` | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements) |
| 2026-06-17 | Enterprise-admin configured external-provider models appear in Copilot CLI `/model` | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-17-copilot-cli-supports-enterprise-bring-your-own-key-byok-models) |
| 2026-06-11 | `/settings` provides a unified, schema-driven settings UI and inline setting changes | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-11-copilot-cli-configure-everything-from-one-place-with-settings) |
| 2026-06-10 | `/security-review` added as an experimental public-preview CLI command | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli) |
| 2026-06-04 | 1M-token context windows and configurable reasoning levels available on supported models | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot) |
| 2026-06-02 | Rubber duck and voice input generally available; prompt scheduling and new terminal UI under `/experimental` | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-02-copilot-cli-improved-ui-rubber-duck-prompt-scheduling-and-voice-input) |
| 2026-06-02 | Cloud and local sandboxes entered public preview | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-02-cloud-and-local-sandboxes-for-github-copilot-now-in-public-preview) |
| 2026-06-02 / 2026-06-05 / 2026-06-18 | GPT-4.1, GPT-5.2/GPT-5.2-Codex, and Opus 4.6 (fast) deprecation notices | [GitHub Blog Changelog](https://github.blog/changelog/label/copilot/) |

## Hands-on practice

| Resource | Notes |
|----------|-------|
| [Creating applications with Copilot CLI (GitHub Skills)](https://github.com/skills/create-applications-with-the-copilot-cli) | Official guided exercise: issue → app → tests → PR |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) ([gh.io/awesome-copilot](https://gh.io/awesome-copilot)) | Community collection of instructions, agents, skills, hooks, and **plugins**. Pre-registered as a Copilot plugin marketplace, so you can `copilot plugin install <name>@awesome-copilot` (or `/plugin marketplace add github/awesome-copilot`). Featured in the *Mona Mayhem* video below |

## Talks & demos { #talks--demos }

The three videos below are from the **official GitHub YouTube channel** and pair directly with this workshop. They are the primary inspiration for the inline "Watch it" callouts in [Getting Started](../getting_started.md), [Feature Deep Dive](../features.md), and [Demo Scenarios](../demos/index.md).

| Resource | Maps to | What it covers |
|----------|---------|----------------|
| [Ultimate GitHub Copilot CLI tutorial for beginners](https://www.youtube.com/watch?v=rheqk-L7Yes) | Parts 0–2 | The official *Copilot CLI for beginners* series in one video: install & `/login`, first requests, interactive vs. non-interactive modes, a slash-command tour (`/model`, `/context`, `/compact`, `/clear`, `/resume`, `/diff`, `/cwd`, `/reset-allowed-tools`), the **plan → delegate → review** loop (`/plan`, `/delegate`, `/review`), MCP (`/mcp add`, Playwright/Svelte), and instructions/agents/skills (`/init`, `.instructions.md`, `.github/skills`, `.github/agents`) |
| [Build with the Copilot CLI — Mona Mayhem](https://www.youtube.com/watch?v=c2QeGuWPnSw) | Part 3 (Demos) | A GitHub *Dev Days* hands-on workshop that builds a retro-arcade app end to end: context engineering with `/init`, **plan mode**, **autopilot vs. YOLO mode**, iterative UI debugging by pasting screenshots, the `/plugin marketplace` + [awesome-copilot](https://github.com/github/awesome-copilot), `/fleet` parallel agents, and `/delegate` to the cloud agent |
| [Less // TODO: more done with GitHub Copilot CLI](https://www.youtube.com/watch?v=zS_40Tfl75w) | Parts 0–2 + [SDK](../../copilot_sdk_tutorial/index.md) | A *Dev Days* deep dive into the three interaction modes (non-interactive/headless for CI, interactive, **server mode**), `/login` & `/user`, `/env`, Auto model selection, built-in agents (research, plan, autopilot), `/review`, `/rubber-duck` cross-model validation, `/fleet` + `/tasks`, Copilot Memory, and driving the CLI from an app via the Copilot SDK |
| [GitHub Copilot Anywhere: From Remote Control CLIs to Cloud Sandboxes (DEM305)](https://www.youtube.com/watch?v=JJmmunwXcu8) | [Sandboxing](../features.md#sandboxing) | Microsoft Developer demo. Inspiration for the [Copilot Anywhere](../features.md#sandboxing) narrative: remote-controlling the CLI (prompt mode, ACP, `/delegate`) and offloading work to cloud sandboxes you can resume from any device |

## Related material in this site

| Document | Relationship |
|----------|--------------|
| [Copilot SDK Tutorial](../../copilot_sdk_tutorial/index.md) | The programmable surface — same runtime, embedded in your code |
| [Copilot SDK · Architecture](../../copilot_sdk_tutorial/architecture.md) | How the SDK, CLI server, and Copilot API interact |
| [Copilot SDK · CLI Server Mode](../../copilot_sdk_tutorial/server_mode.md) | Running the CLI as a server |

---

## Note on workshop source decks

This workshop was informed by internal Microsoft/GitHub enablement decks provided as reference material. Those decks contain forward-looking or templated content (for example, speculative future model names and dated context-window figures) that is **deliberately not reproduced here**. Every factual claim in this workshop is instead tied to the GitHub primary sources above. Three of the supplied reference files were rights-protected (encrypted) and could not be opened; none of their content is represented here.
